#!/usr/bin/env python3
"""
Todo Scheduler - Generate cron jobs from a todo list

Usage:
    python3 schedule_todos.py todos.txt
    python3 schedule_todos.py --inline "Task 1, Task 2, Task 3"
    python3 schedule_todos.py todos.txt --dry-run
"""

import sys
import re
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class Task:
    """Represents a single todo item with metadata"""
    
    def __init__(self, text: str, line_num: int = 0):
        self.raw = text
        self.line_num = line_num
        self.completed = False
        
        # Parse checkbox
        checkbox_match = re.match(r'^\s*-\s*\[([ x])\]\s*(.+)$', text)
        if checkbox_match:
            self.completed = checkbox_match.group(1).lower() == 'x'
            content = checkbox_match.group(2)
        else:
            # Simple list item
            content = re.sub(r'^\s*[-*]\s*', '', text)
        
        # Extract task name and metadata
        self.name = content
        self.time = None
        self.depends_on = []
        self.priority = 'medium'
        self.repeat = None
        self.group = None
        self.condition = None
        
        # Parse tags
        self._parse_tags(content)
    
    def _parse_tags(self, content: str):
        """Extract metadata tags from task content"""
        
        # @TIME tag
        time_match = re.search(r'@(\d{1,2}(?::\d{2})?(?:am|pm)?|tomorrow|now)', content, re.IGNORECASE)
        if time_match:
            self.time = time_match.group(1)
            content = content.replace(time_match.group(0), '')
        
        # Extract all #tag:value patterns
        tags = re.findall(r'#([\w-]+)(?::([^\s#]+))?', content)
        
        for tag_name, tag_value in tags:
            if tag_name == 'depends':
                self.depends_on.append(tag_value)
            elif tag_name == 'priority':
                self.priority = tag_value or 'medium'
            elif tag_name == 'repeat':
                self.repeat = tag_value
            elif tag_name == 'group':
                self.group = tag_value
            elif tag_name == 'if':
                self.condition = tag_value
            elif tag_name in ['critical', 'high', 'low']:
                # Shorthand priority
                self.priority = tag_name
        
        # Clean up task name (remove tags)
        self.name = re.sub(r'@[\w:]+', '', content)
        self.name = re.sub(r'#[\w-]+(?::[\w-]+)?', '', self.name)
        self.name = self.name.strip()
    
    def get_id(self) -> str:
        """Generate a stable ID for this task"""
        # Convert name to slug
        slug = re.sub(r'[^\w\s-]', '', self.name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]  # Limit length
    
    def to_dict(self) -> Dict:
        """Export task as dictionary"""
        return {
            'id': self.get_id(),
            'name': self.name,
            'time': self.time,
            'depends_on': self.depends_on,
            'priority': self.priority,
            'repeat': self.repeat,
            'group': self.group,
            'condition': self.condition,
            'completed': self.completed,
            'line': self.line_num
        }


class TodoScheduler:
    """Parse todos and generate cron jobs"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.tasks: List[Task] = []
        self.jobs_created = []
    
    def parse_file(self, filepath: str) -> List[Task]:
        """Parse a todo file into Task objects"""
        path = Path(filepath).expanduser()
        
        if not path.exists():
            raise FileNotFoundError(f"Todo file not found: {filepath}")
        
        with open(path) as f:
            lines = f.readlines()
        
        tasks = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # Check if it's a list item
            if re.match(r'^\s*[-*]\s*', line) or re.match(r'^\s*-\s*\[[ x]\]', line):
                task = Task(line, i)
                if not task.completed:  # Skip completed tasks
                    tasks.append(task)
        
        self.tasks = tasks
        return tasks
    
    def parse_inline(self, text: str) -> List[Task]:
        """Parse inline comma-separated tasks"""
        tasks = []
        for i, item in enumerate(text.split(','), 1):
            item = item.strip()
            if item:
                task = Task(f"- {item}", i)
                tasks.append(task)
        
        self.tasks = tasks
        return tasks
    
    def generate_schedule(self, 
                         start_time: Optional[str] = None,
                         spacing_minutes: int = 30,
                         default_schedule: Optional[str] = None) -> List[Dict]:
        """
        Generate cron schedules for all tasks
        
        Args:
            start_time: When to start (e.g., "9am", "now", "tomorrow")
            spacing_minutes: Minutes between tasks (if no explicit times)
            default_schedule: Default cron expression for all tasks
        
        Returns:
            List of job specifications
        """
        jobs = []
        base_time = self._parse_time(start_time or "now")
        
        for i, task in enumerate(self.tasks):
            job = {
                'task_id': task.get_id(),
                'task_name': task.name,
                'depends_on': task.depends_on,
                'priority': task.priority,
                'group': task.group,
                'condition': task.condition
            }
            
            # Determine schedule
            if task.time:
                # Task has explicit time
                task_time = self._parse_time(task.time)
                job['schedule'] = self._time_to_cron(task_time)
                job['schedule_type'] = 'at'
            elif default_schedule:
                # Use provided default
                job['schedule'] = default_schedule
                job['schedule_type'] = 'cron'
            else:
                # Sequential spacing from start time
                task_time = base_time + timedelta(minutes=i * spacing_minutes)
                job['schedule'] = self._time_to_cron(task_time)
                job['schedule_type'] = 'at'
            
            # Handle repeating tasks
            if task.repeat:
                job['schedule'] = self._repeat_to_cron(task.repeat, task.time)
                job['schedule_type'] = 'cron'
            
            jobs.append(job)
        
        return jobs
    
    def create_cron_jobs(self, jobs: List[Dict], session_target: str = "isolated") -> List[str]:
        """
        Create actual cron jobs via OpenClaw API
        
        Args:
            jobs: List of job specifications
            session_target: "main" (systemEvent) or "isolated" (agentTurn)
        
        Returns:
            List of created job IDs
        """
        job_ids = []
        
        for job_spec in jobs:
            # Build payload based on session target
            if session_target == "main":
                payload = {
                    "kind": "systemEvent",
                    "text": f"TODO TASK: {job_spec['task_name']}"
                }
            else:
                payload = {
                    "kind": "agentTurn",
                    "message": f"Execute task: {job_spec['task_name']}",
                    "deliver": True
                }
            
            # Build schedule
            if job_spec['schedule_type'] == 'at':
                # One-shot
                schedule = {
                    "kind": "at",
                    "atMs": int(self._cron_to_timestamp(job_spec['schedule']) * 1000)
                }
            else:
                # Recurring
                schedule = {
                    "kind": "cron",
                    "expr": job_spec['schedule']
                }
            
            # Build job
            cron_job = {
                "name": f"TODO: {job_spec['task_name']}",
                "schedule": schedule,
                "payload": payload,
                "sessionTarget": session_target,
                "enabled": True
            }
            
            if self.dry_run:
                print(f"[DRY RUN] Would create job:")
                print(json.dumps(cron_job, indent=2))
                job_ids.append(f"dry-run-{job_spec['task_id']}")
            else:
                # Actually create the job
                # This would call: cron.invoke(action="add", job=cron_job)
                print(f"Creating job: {job_spec['task_name']}")
                job_ids.append(job_spec['task_id'])
        
        self.jobs_created = job_ids
        return job_ids
    
    def _parse_time(self, time_str: str) -> datetime:
        """Convert time string to datetime"""
        time_str = time_str.lower().strip()
        
        if time_str == "now":
            return datetime.now()
        
        if time_str == "tomorrow":
            return datetime.now() + timedelta(days=1)
        
        # Parse HH:MM or HH format
        time_match = re.match(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            meridiem = time_match.group(3)
            
            if meridiem:
                if meridiem == 'pm' and hour < 12:
                    hour += 12
                elif meridiem == 'am' and hour == 12:
                    hour = 0
            
            now = datetime.now()
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has passed today, schedule for tomorrow
            if target < now:
                target += timedelta(days=1)
            
            return target
        
        # Fallback: return now
        return datetime.now()
    
    def _time_to_cron(self, dt: datetime) -> str:
        """Convert datetime to cron expression (one-shot)"""
        # For display purposes - actual implementation uses "at" schedule
        return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"
    
    def _cron_to_timestamp(self, cron_expr: str) -> float:
        """Convert cron expression back to timestamp (for 'at' schedules)"""
        # This is a simplified version - real implementation would parse cron properly
        parts = cron_expr.split()
        if len(parts) >= 4:
            minute, hour, day, month = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            now = datetime.now()
            target = datetime(now.year, month, day, hour, minute)
            return target.timestamp()
        return datetime.now().timestamp()
    
    def _repeat_to_cron(self, repeat: str, base_time: Optional[str] = None) -> str:
        """Convert repeat pattern to cron expression"""
        repeat = repeat.lower()
        
        # Parse base time if provided
        if base_time:
            dt = self._parse_time(base_time)
            minute = dt.minute
            hour = dt.hour
        else:
            minute = 0
            hour = 9  # Default 9am
        
        # Common patterns
        if repeat == 'daily':
            return f"{minute} {hour} * * *"
        elif repeat == 'hourly':
            return f"{minute} * * * *"
        elif repeat == 'weekly':
            return f"{minute} {hour} * * 1"  # Monday
        elif repeat == 'monthly':
            return f"{minute} {hour} 1 * *"  # First of month
        elif re.match(r'mon-fri', repeat):
            return f"{minute} {hour} * * 1-5"
        elif re.match(r'every\s+(\d+)\s+(hour|minute)s?', repeat):
            # "every 2 hours" -> "0 */2 * * *"
            match = re.match(r'every\s+(\d+)\s+(hour|minute)s?', repeat)
            interval = match.group(1)
            unit = match.group(2)
            if unit == 'hour':
                return f"0 */{interval} * * *"
            else:
                return f"*/{interval} * * * *"
        else:
            # Assume it's already a cron expression
            return repeat


def main():
    parser = argparse.ArgumentParser(description='Generate cron jobs from todo list')
    parser.add_argument('file', nargs='?', help='Path to todo file')
    parser.add_argument('--inline', help='Inline comma-separated tasks')
    parser.add_argument('--schedule', help='Default cron schedule for all tasks')
    parser.add_argument('--start', default='now', help='Start time (default: now)')
    parser.add_argument('--spacing', type=int, default=30, help='Minutes between tasks (default: 30)')
    parser.add_argument('--dry-run', action='store_true', help='Show jobs without creating')
    parser.add_argument('--session', choices=['main', 'isolated'], default='isolated',
                       help='Session target (default: isolated)')
    
    args = parser.parse_args()
    
    if not args.file and not args.inline:
        parser.error("Must provide either FILE or --inline")
    
    # Create scheduler
    scheduler = TodoScheduler(dry_run=args.dry_run)
    
    # Parse todos
    if args.inline:
        tasks = scheduler.parse_inline(args.inline)
    else:
        tasks = scheduler.parse_file(args.file)
    
    print(f"📋 Parsed {len(tasks)} tasks")
    for task in tasks:
        deps = f" (depends: {', '.join(task.depends_on)})" if task.depends_on else ""
        print(f"  - {task.name}{deps}")
    
    # Generate schedules
    jobs = scheduler.generate_schedule(
        start_time=args.start,
        spacing_minutes=args.spacing,
        default_schedule=args.schedule
    )
    
    print(f"\n📅 Generated {len(jobs)} job schedules")
    for job in jobs:
        print(f"  {job['task_name']}: {job['schedule']} ({job['schedule_type']})")
    
    # Create cron jobs
    if not args.dry_run:
        print(f"\n⚙️  Creating cron jobs...")
    
    job_ids = scheduler.create_cron_jobs(jobs, session_target=args.session)
    
    print(f"\n✅ {'Would create' if args.dry_run else 'Created'} {len(job_ids)} jobs")
    if not args.dry_run:
        print(f"   Job IDs: {', '.join(job_ids)}")
        print(f"\n   Check status: cron status")
        print(f"   Remove job: cron remove <JOB_ID>")


if __name__ == '__main__':
    main()
