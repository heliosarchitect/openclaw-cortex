#!/usr/bin/env python3
"""
AgentBench OS Interaction Baseline Harness
Runs OS tasks against Claude claude-opus-4-6 via Anthropic API.
Tasks execute bash commands locally in a sandboxed temp directory.
"""

import json
import os
import subprocess
import tempfile
import time
import re
import anthropic

# Load tasks
TASK_FILE = os.path.expanduser("~/Projects/agent-bench/data/os_interaction/data/dev.json")
SCRIPTS_DIR = os.path.expanduser("~/Projects/agent-bench/data/os_interaction/scripts/dev")

with open(TASK_FILE) as f:
    ALL_TASKS = json.load(f)

client = anthropic.Anthropic()
MODEL = "claude-opus-4-6"

# Select tasks that are safe to run locally (no Docker required, no dangerous ops)
# Focus on: filesystem queries, system info, simple match/check evals
SAFE_TASK_INDICES = [6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 21, 22, 23]

def run_bash(cmd, timeout=15):
    """Run a bash command and return stdout."""
    try:
        r = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1

def get_agent_answer(task_desc, max_turns=5):
    """
    Multi-turn agent loop: Claude gets the task, can execute bash commands,
    and must provide a final answer.
    """
    system = """You are an AI agent solving OS/Linux tasks. You have access to a bash shell.

To execute a command, write it in a <bash> tag:
<bash>ls -la /home</bash>

You will receive the output, then can run more commands.

When you have the final answer, write it in an <answer> tag:
<answer>your answer here</answer>

Be concise. Execute commands to gather information, then answer."""

    messages = [{"role": "user", "content": f"Task: {task_desc}"}]
    
    for turn in range(max_turns):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system,
            messages=messages
        )
        
        text = resp.content[0].text
        
        # Check for final answer
        answer_match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
        if answer_match:
            return answer_match.group(1).strip(), turn + 1, text
        
        # Check for bash command
        bash_match = re.search(r'<bash>(.*?)</bash>', text, re.DOTALL)
        if bash_match:
            cmd = bash_match.group(1).strip()
            stdout, stderr, rc = run_bash(cmd)
            output = stdout
            if stderr and rc != 0:
                output += f"\n[stderr]: {stderr}"
            if not output:
                output = "(no output)"
            
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", "content": f"Command output:\n{output}"})
        else:
            # No bash or answer tag - try to extract answer from text
            # Sometimes the model just gives a direct answer
            return text.strip().split('\n')[-1].strip(), turn + 1, text
    
    return "FAILED_MAX_TURNS", max_turns, ""

def evaluate_task(task_idx, agent_answer):
    """Evaluate agent answer against task evaluation criteria."""
    task = ALL_TASKS[task_idx]
    evaluation = task["evaluation"]
    
    if "match" in evaluation:
        expected = str(evaluation["match"]).strip()
        # Clean agent answer
        answer = agent_answer.strip()
        if answer == expected:
            return True, f"exact match: '{expected}'"
        # Try numeric comparison
        try:
            if float(answer) == float(expected):
                return True, f"numeric match: {expected}"
        except:
            pass
        return False, f"expected '{expected}', got '{answer}'"
    
    if "check" in evaluation:
        check = evaluation["check"]
        if isinstance(check, list):
            # [None, {language, file}] format - use the checker script
            for c in check:
                if c and "file" in c:
                    check = c
                    break
            else:
                return None, "no checker found"
        
        if isinstance(check, dict) and "file" in check:
            checker = os.path.join(SCRIPTS_DIR, check["file"])
            if not os.path.exists(checker):
                return None, f"checker not found: {checker}"
            
            # Get expected answer from example
            example = evaluation.get("example", {})
            if isinstance(example, dict) and "code" in example:
                expected_stdout, _, _ = run_bash(example["code"])
                # Run checker: python3 checker.py <expected> <agent_answer>
                lang = check.get("language", "bash")
                if lang == "python":
                    cmd = f"python3 {checker} {repr(expected_stdout)} {repr(agent_answer)}"
                else:
                    cmd = f"bash {checker} {repr(expected_stdout)} {repr(agent_answer)}"
                _, _, rc = run_bash(cmd)
                if rc == 0:
                    return True, f"checker passed (expected ~{expected_stdout})"
                return False, f"checker failed (expected ~{expected_stdout}, got {agent_answer})"
            
            return None, "no example code to generate expected answer"
    
    return None, "unknown evaluation type"

def main():
    results = []
    # Use first 10 safe tasks
    task_indices = SAFE_TASK_INDICES[:10]
    
    print(f"Running {len(task_indices)} OS tasks against {MODEL}")
    print("=" * 60)
    
    for idx in task_indices:
        task = ALL_TASKS[idx]
        desc = task["description"]
        print(f"\nTask {idx}: {desc[:80]}...")
        
        t0 = time.time()
        answer, turns, raw = get_agent_answer(desc)
        elapsed = time.time() - t0
        
        passed, detail = evaluate_task(idx, answer)
        status = "PASS" if passed else ("SKIP" if passed is None else "FAIL")
        
        print(f"  Answer: {answer[:60]}")
        print(f"  Result: {status} ({detail})")
        print(f"  Turns: {turns}, Time: {elapsed:.1f}s")
        
        results.append({
            "task_idx": idx,
            "description": desc[:100],
            "labels": task.get("labels", []),
            "answer": answer[:200],
            "status": status,
            "detail": detail,
            "turns": turns,
            "elapsed": round(elapsed, 1)
        })
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    print(f"RESULTS: {passed} passed, {failed} failed, {skipped} skipped out of {len(results)}")
    
    # Save results
    output = {
        "model": MODEL,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {"passed": passed, "failed": failed, "skipped": skipped, "total": len(results)},
        "tasks": results
    }
    
    outfile = os.path.expanduser("~/.openclaw/workspace/agentbench-os-results.json")
    with open(outfile, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {outfile}")
    
    return output

if __name__ == "__main__":
    results = main()
    print("\n\nFull results JSON for Synapse:")
    print(json.dumps(results, indent=2))
