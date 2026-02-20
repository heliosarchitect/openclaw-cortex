#!/usr/bin/env python3
"""
AgentBench OS Interaction — Docker-based Harness
Runs ALL OS tasks inside proper Docker containers using Claude claude-opus-4-6 via Anthropic API.
"""

import json
import glob
import os
import subprocess
import time
import re
import sys
import traceback
import anthropic

# Config
MODEL = "claude-opus-4-6"
MAX_TURNS = 8
DOCKER_TIMEOUT = 30
REPO = os.path.expanduser("~/Projects/agent-bench")
DATA_DIR = f"{REPO}/data/os_interaction/data"
SCRIPTS_DIR = f"{REPO}/data/os_interaction/scripts"

client = anthropic.Anthropic()

def load_all_tasks():
    """Load all tasks from sets 1-7."""
    all_tasks = []
    for i in range(1, 8):
        files = sorted(glob.glob(f"{DATA_DIR}/{i}/*.json"))
        script_dir = f"{SCRIPTS_DIR}/{i}"
        for f in files:
            with open(f) as fp:
                data = json.load(fp)
            tasks = data if isinstance(data, list) else [data]
            for j, t in enumerate(tasks):
                t['_set'] = i
                t['_file'] = os.path.basename(f)
                t['_task_idx'] = j
                t['_script_dir'] = script_dir
                t['_id'] = f"set{i}-{os.path.basename(f).replace('.json','')}-{j}"
                all_tasks.append(t)
    return all_tasks


def create_container(task):
    """Create and start a Docker container for the task, run init if needed."""
    create = task.get('create', {})
    image = f"local-os/{create.get('local', 'default')}"
    container_name = f"agentbench-{task['_id']}-{int(time.time())}"
    
    # Create container
    cmd = ["docker", "run", "-d", "--name", container_name, image, "sleep", "300"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None, f"docker run failed: {r.stderr}"
    
    container_id = r.stdout.strip()
    
    # Run init
    init = create.get('init', None)
    if init:
        if isinstance(init, dict) and 'file' in init:
            # Copy init script from script_dir and run it
            init_path = os.path.join(task['_script_dir'], init['file'])
            if os.path.exists(init_path):
                subprocess.run(["docker", "cp", init_path, f"{container_id}:/tmp/init.sh"], 
                             capture_output=True, timeout=10)
                subprocess.run(["docker", "exec", container_id, "bash", "/tmp/init.sh"],
                             capture_output=True, timeout=30)
        elif isinstance(init, str):
            # Inline init script
            subprocess.run(["docker", "exec", container_id, "bash", "-c", init],
                         capture_output=True, timeout=30)
    
    # Run start command if present
    start = task.get('start', None)
    if start:
        subprocess.run(["docker", "exec", "-d", container_id, "bash", "-c", start],
                     capture_output=True, timeout=10)
        time.sleep(1)  # Let it start
    
    return container_id, None


def docker_exec(container_id, cmd, timeout=DOCKER_TIMEOUT):
    """Execute a command in the container."""
    try:
        r = subprocess.run(
            ["docker", "exec", container_id, "bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        out = r.stdout
        if r.stderr and r.returncode != 0:
            out += f"\n[stderr]: {r.stderr}"
        return out.strip() if out.strip() else "(no output)", r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1
    except Exception as e:
        return f"ERROR: {e}", -1


def cleanup_container(container_id):
    """Remove container."""
    subprocess.run(["docker", "rm", "-f", container_id], capture_output=True, timeout=10)


def get_agent_answer(task, container_id):
    """Multi-turn agent loop using Anthropic API."""
    system = """You are an AI agent solving OS/Linux tasks inside a Docker container. You have bash access.

To execute a command, write it in a <bash> tag:
<bash>command here</bash>

When you have the final answer, write it in an <answer> tag:
<answer>your answer here</answer>

Rules:
- Be precise and concise with answers
- For numeric answers, return just the number
- For yes/no, return just yes or no
- Execute commands to gather info before answering
- You have root access in an Ubuntu container"""

    messages = [{"role": "user", "content": f"Task: {task['description']}"}]
    
    for turn in range(MAX_TURNS):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system,
                messages=messages
            )
        except Exception as e:
            return f"API_ERROR: {e}", turn + 1

        text = resp.content[0].text
        
        # Check for final answer
        answer_match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
        if answer_match:
            return answer_match.group(1).strip(), turn + 1
        
        # Check for bash command
        bash_match = re.search(r'<bash>(.*?)</bash>', text, re.DOTALL)
        if bash_match:
            cmd = bash_match.group(1).strip()
            output, rc = docker_exec(container_id, cmd)
            
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", "content": f"Output:\n{output}"})
        else:
            # No tags — extract last line as answer
            return text.strip().split('\n')[-1].strip(), turn + 1
    
    return "FAILED_MAX_TURNS", MAX_TURNS


def evaluate(task, agent_answer, container_id=None):
    """Evaluate using match or check scripts. Uses the SAME container for example code."""
    evaluation = task.get('evaluation', {})
    
    # Direct match
    if 'match' in evaluation:
        expected = str(evaluation['match']).strip()
        answer = agent_answer.strip()
        if answer == expected:
            return True, f"exact match: '{expected}'"
        try:
            if float(answer) == float(expected):
                return True, f"numeric match: {expected}"
        except:
            pass
        return False, f"expected '{expected}', got '{answer}'"
    
    # Check with example code
    if 'check' in evaluation and 'example' in evaluation:
        check = evaluation['check']
        example = evaluation['example']
        
        # Find the checker
        checker_info = None
        if isinstance(check, list):
            for c in check:
                if c and isinstance(c, dict) and 'file' in c:
                    checker_info = c
                    break
        elif isinstance(check, dict) and 'file' in check:
            checker_info = check
        
        if not checker_info:
            return None, "no checker found"
        
        checker_path = os.path.join(task['_script_dir'], checker_info['file'])
        if not os.path.exists(checker_path):
            return None, f"checker not found: {checker_path}"
        
        # Get expected answer by running example code in the SAME container
        expected = None
        if isinstance(example, dict) and 'code' in example:
            example_code = example['code']
        elif isinstance(example, str):
            example_code = example
        else:
            example_code = None
        
        if example_code and container_id:
            expected_out, _ = docker_exec(container_id, example_code)
            expected = expected_out
        elif example_code:
            return None, "no container for example code"
        
        if expected is None:
            return None, "no expected value"
        
        # Run checker locally
        try:
            r = subprocess.run(
                ["python3", checker_path, expected, agent_answer],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                return True, f"checker passed (expected≈{expected[:50]})"
            else:
                return False, f"checker failed (expected≈{expected[:50]}, got={agent_answer[:50]})"
        except Exception as e:
            return None, f"checker error: {e}"
    
    return None, "unknown eval type"


def main():
    tasks = load_all_tasks()
    print(f"Loaded {len(tasks)} total OS tasks")
    
    # Skip tasks that need containers we don't have (all should be fine now)
    results = []
    passed = failed = skipped = errors = 0
    
    for i, task in enumerate(tasks):
        tid = task['_id']
        desc = task['description'][:80]
        print(f"\n[{i+1}/{len(tasks)}] {tid}: {desc}...")
        sys.stdout.flush()
        
        container_id = None
        try:
            # Create container
            t0 = time.time()
            container_id, err = create_container(task)
            if not container_id:
                print(f"  SKIP: {err}")
                results.append({"id": tid, "status": "SKIP", "detail": err, "elapsed": 0})
                skipped += 1
                continue
            
            # Get agent answer
            answer, turns = get_agent_answer(task, container_id)
            elapsed = time.time() - t0
            
            # Evaluate (pass container so example code runs in same env)
            result, detail = evaluate(task, answer, container_id)
            
            if result is True:
                status = "PASS"
                passed += 1
            elif result is False:
                status = "FAIL"
                failed += 1
            else:
                status = "SKIP"
                skipped += 1
            
            print(f"  Answer: {answer[:60]}")
            print(f"  {status}: {detail}")
            print(f"  Turns: {turns}, Time: {elapsed:.1f}s")
            
            results.append({
                "id": tid,
                "set": task['_set'],
                "description": desc,
                "labels": task.get('labels', []),
                "answer": answer[:200],
                "status": status,
                "detail": detail,
                "turns": turns,
                "elapsed": round(elapsed, 1)
            })
            
        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()
            results.append({"id": tid, "status": "ERROR", "detail": str(e), "elapsed": 0})
            errors += 1
        finally:
            if container_id:
                cleanup_container(container_id)
        
        # Progress & incremental save
        total_done = passed + failed + skipped + errors
        if total_done % 5 == 0:
            print(f"\n--- Progress: {total_done}/{len(tasks)} | P:{passed} F:{failed} S:{skipped} E:{errors} ---\n")
            # Incremental save
            interim = {
                "model": MODEL,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "summary": {"passed": passed, "failed": failed, "skipped": skipped, "errors": errors, "total": total_done},
                "tasks": results
            }
            with open(os.path.expanduser("~/.openclaw/workspace/agentbench-os-docker-results.json"), "w") as f:
                json.dump(interim, f, indent=2)
        
        sys.stdout.flush()
    
    # Summary
    total = len(results)
    print(f"\n{'='*60}")
    print(f"FINAL: {passed}/{total} passed ({100*passed/total:.1f}%)")
    print(f"  Passed: {passed}, Failed: {failed}, Skipped: {skipped}, Errors: {errors}")
    
    # Per-set breakdown
    from collections import defaultdict
    by_set = defaultdict(lambda: {"pass": 0, "fail": 0, "skip": 0, "error": 0, "total": 0})
    for r in results:
        s = r.get('set', '?')
        by_set[s]['total'] += 1
        by_set[s][r['status'].lower()] += 1
    
    print("\nPer-set breakdown:")
    for s in sorted(by_set.keys()):
        b = by_set[s]
        pct = 100 * b['pass'] / b['total'] if b['total'] else 0
        print(f"  Set {s}: {b['pass']}/{b['total']} ({pct:.0f}%)")
    
    output = {
        "model": MODEL,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {"passed": passed, "failed": failed, "skipped": skipped, "errors": errors, "total": total},
        "by_set": dict(by_set),
        "tasks": results
    }
    
    outfile = os.path.expanduser("~/.openclaw/workspace/agentbench-os-docker-results.json")
    with open(outfile, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {outfile}")
    
    return output

if __name__ == "__main__":
    main()
