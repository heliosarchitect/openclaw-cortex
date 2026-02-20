#!/usr/bin/env python3
"""
AgentBench OS Interaction Harness — Docker Edition
Runs each task inside the appropriate Docker container (local-os/default, local-os/packages, local-os/ubuntu).
"""

import json
import os
import subprocess
import time
import re
import uuid
import anthropic

TASK_FILE = os.path.expanduser("~/Projects/agent-bench/data/os_interaction/data/dev.json")
SCRIPTS_DIR = os.path.expanduser("~/Projects/agent-bench/data/os_interaction/scripts/dev")

with open(TASK_FILE) as f:
    ALL_TASKS = json.load(f)

client = anthropic.Anthropic()
MODEL = "claude-opus-4-6"

def get_image_for_task(task):
    """Determine which Docker image a task needs."""
    create = task.get("create", {})
    if isinstance(create, (list, str)):
        create = {}
    local = create.get("local", None)
    if local:
        return f"local-os/{local}"
    # Infer from labels
    labels = task.get("labels", [])
    if "packages" in labels:
        return "local-os/packages"
    return "local-os/default"

def get_init_code(task):
    """Get initialization code for a task."""
    create = task.get("create", {})
    if isinstance(create, (list, str)):
        return None
    init = create.get("init", {})
    if isinstance(init, dict):
        return init.get("code", None)
    if isinstance(init, str):
        return init
    return None

def get_start_code(task):
    """Get background process start code for a task."""
    return task.get("start", None)

def start_container(image, init_code=None, start_code=None):
    """Start a Docker container, run init code, then start background processes. Returns container ID."""
    cid = subprocess.run(
        ["docker", "run", "-d", "--rm", image, "sleep", "300"],
        capture_output=True, text=True
    ).stdout.strip()
    if not cid:
        return None
    if init_code:
        subprocess.run(
            ["docker", "exec", cid, "bash", "-c", init_code],
            capture_output=True, text=True, timeout=30
        )
    if start_code:
        subprocess.run(
            ["docker", "exec", "-d", cid, "bash", "-c", start_code],
            capture_output=True, text=True, timeout=10
        )
        time.sleep(2)  # Let background process start and produce some output
    return cid

def stop_container(cid):
    """Stop and remove container."""
    subprocess.run(["docker", "kill", cid], capture_output=True, timeout=10)

def docker_exec(cid, cmd, timeout=15):
    """Execute a command in the container."""
    try:
        r = subprocess.run(
            ["docker", "exec", cid, "bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1

def get_agent_answer(task_desc, cid, max_turns=12):
    """Multi-turn agent loop executing commands inside the Docker container."""
    system = """You are an AI agent solving OS/Linux tasks. You have access to a bash shell on a Linux system.

To execute a command, write it in a <bash> tag:
<bash>ls -la /home</bash>

You will receive the output, then can run more commands.

When you have the final answer, write it in an <answer> tag:
<answer>your answer here</answer>

Rules:
- Give ONLY the requested value in the answer tag (a number, string, etc.)
- Do NOT include units, explanations, or extra text in the answer
- Execute commands to gather information before answering"""

    messages = [{"role": "user", "content": f"Task: {task_desc}"}]

    for turn in range(max_turns):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, system=system, messages=messages
        )
        text = resp.content[0].text

        bash_match = re.search(r'<bash>(.*?)</bash>', text, re.DOTALL)
        
        # If there's a bash command, ALWAYS execute it first — even if there's also an answer tag.
        # The model often pre-fills answers without actually running the command.
        if bash_match:
            cmd = bash_match.group(1).strip()
            stdout, stderr, rc = docker_exec(cid, cmd)
            output = stdout
            if stderr and rc != 0:
                output += f"\n[stderr]: {stderr}"
            if not output:
                output = "(no output)"
            # Truncate assistant text after the first </bash> to prevent hallucinated outputs
            truncated = text[:text.index('</bash>') + len('</bash>')]
            messages.append({"role": "assistant", "content": truncated})
            messages.append({"role": "user", "content": f"Command output:\n{output}"})
        else:
            # No bash tag — check for answer
            answer_match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
            if answer_match:
                return answer_match.group(1).strip(), turn + 1, text
            return text.strip().split('\n')[-1].strip(), turn + 1, text

    return "FAILED_MAX_TURNS", max_turns, ""

def evaluate_task(task_idx, agent_answer, cid):
    """Evaluate agent answer. Runs example code inside the container for ground truth."""
    task = ALL_TASKS[task_idx]
    evaluation = task["evaluation"]

    if "match" in evaluation:
        expected = str(evaluation["match"]).strip()
        answer = agent_answer.strip()
        if answer == expected:
            return True, f"exact match: '{expected}'"
        try:
            if float(answer) == float(expected):
                return True, f"numeric match: {expected}"
        except (ValueError, TypeError):
            pass
        return False, f"expected '{expected}', got '{answer}'"

    if "check" in evaluation:
        check = evaluation["check"]
        if isinstance(check, list):
            for c in check:
                if c and isinstance(c, dict) and "file" in c:
                    check = c
                    break
            else:
                return None, "no checker found in list"

        if isinstance(check, dict) and "file" in check:
            # Get expected answer by running example code in the container
            example = evaluation.get("example", {})
            example_code = None
            if isinstance(example, dict) and "code" in example:
                example_code = example["code"]
            elif isinstance(example, str):
                example_code = example

            if example_code:
                expected_stdout, _, _ = docker_exec(cid, example_code)
                # Use the checker script (runs on host, comparing strings)
                checker = os.path.join(SCRIPTS_DIR, check["file"])
                if not os.path.exists(checker):
                    return None, f"checker not found: {checker}"

                lang = check.get("language", "python")
                if lang == "python":
                    r = subprocess.run(
                        ["python3", checker, expected_stdout, agent_answer],
                        capture_output=True, text=True, timeout=10
                    )
                else:
                    r = subprocess.run(
                        ["bash", checker, expected_stdout, agent_answer],
                        capture_output=True, text=True, timeout=10
                    )
                if r.returncode == 0:
                    return True, f"checker passed (expected ~'{expected_stdout}')"
                return False, f"checker failed (expected ~'{expected_stdout}', got '{agent_answer}') checker_out={r.stdout} {r.stderr}"

            return None, "no example code to generate expected"

    return None, "unknown evaluation type"


def main():
    import sys
    # Optional: pass task indices as args, otherwise run all
    if len(sys.argv) > 1:
        task_indices = [int(x) for x in sys.argv[1:]]
    else:
        task_indices = list(range(len(ALL_TASKS)))

    results = []
    print(f"Running {len(task_indices)} OS tasks in Docker containers against {MODEL}")
    print("=" * 60)

    for idx in task_indices:
        task = ALL_TASKS[idx]
        desc = task["description"]
        image = get_image_for_task(task)
        init_code = get_init_code(task)
        start_code = get_start_code(task)
        labels = task.get("labels", [])

        print(f"\nTask {idx}: {desc[:80]}...")
        print(f"  Image: {image}, Init: {'yes' if init_code else 'no'}, Start: {'yes' if start_code else 'no'}, Labels: {labels}")

        # Start container
        cid = start_container(image, init_code, start_code)
        if not cid:
            print(f"  ERROR: Failed to start container {image}")
            results.append({
                "task_idx": idx, "description": desc[:100], "labels": labels,
                "answer": "CONTAINER_FAILED", "status": "ERROR", "detail": f"failed to start {image}",
                "turns": 0, "elapsed": 0
            })
            continue

        try:
            t0 = time.time()
            answer, turns, raw = get_agent_answer(desc, cid)
            elapsed = time.time() - t0

            passed, detail = evaluate_task(idx, answer, cid)
            status = "PASS" if passed else ("SKIP" if passed is None else "FAIL")

            print(f"  Answer: {answer[:80]}")
            print(f"  Result: {status} ({detail})")
            print(f"  Turns: {turns}, Time: {elapsed:.1f}s")
            if raw:
                print(f"  [RAW first 200]: {raw[:200]}")

            results.append({
                "task_idx": idx, "description": desc[:100], "labels": labels,
                "answer": answer[:200], "status": status, "detail": detail,
                "turns": turns, "elapsed": round(elapsed, 1), "image": image
            })
        finally:
            stop_container(cid)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    total = len(results)
    print(f"RESULTS: {passed}/{total} passed | {failed} failed | {skipped} skipped | {errors} errors")
    print(f"SCORE: {passed/total*100:.1f}%" if total > 0 else "No tasks run")

    output = {
        "model": MODEL,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {"passed": passed, "failed": failed, "skipped": skipped, "errors": errors, "total": total},
        "tasks": results
    }

    outfile = os.path.expanduser("~/.openclaw/workspace/agentbench-os-results-docker.json")
    with open(outfile, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {outfile}")

if __name__ == "__main__":
    main()
