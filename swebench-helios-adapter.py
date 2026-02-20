#!/usr/bin/env python3
"""
SWE-bench Helios Adapter
Generates patches for SWE-bench instances using Claude Opus via Anthropic API.
Output format matches SWE-bench predictions jsonl: {"instance_id": ..., "model_name_or_path": ..., "model_patch": ...}
"""

import json
import os
import sys
import time
import subprocess
import tempfile
import anthropic

# Config
MODEL = "claude-opus-4-6"
MODEL_NAME = "helios-opus-4-6"
MAX_TURNS = 25
TIMEOUT_PER_COMMAND = 30

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an expert software engineer solving a GitHub issue by producing a minimal patch.

You have access to a bash shell in the repository root.

To execute a command:
<bash>command here</bash>

WORKFLOW:
1. Spend 3-5 turns exploring: find relevant files, understand the bug
2. Make the fix by editing files directly with sed/python/etc via bash
3. Verify with `git diff` to confirm changes look correct
4. Output the final patch in a <patch> tag

When done, output:
<patch>
your unified diff here (copy from git diff output)
</patch>

Rules:
- Make MINIMAL changes — only fix the reported issue
- Do NOT change test files
- Do NOT add new dependencies
- IMPORTANT: You MUST produce a <patch> tag before your turns run out
- If you've made edits, run `git diff` and wrap the output in <patch> tags"""


def run_in_repo(cmd, repo_dir, timeout=TIMEOUT_PER_COMMAND):
    """Run a command in the repo directory."""
    try:
        r = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout,
            cwd=repo_dir
        )
        out = r.stdout[:3000]  # Truncate large outputs
        if r.stderr and r.returncode != 0:
            out += f"\n[stderr]: {r.stderr[:1000]}"
        return out.strip() if out.strip() else "(no output)"
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"


def clone_and_checkout(repo, base_commit, work_dir):
    """Clone repo and checkout the base commit."""
    repo_url = f"https://github.com/{repo}.git"
    repo_dir = os.path.join(work_dir, repo.replace("/", "__"))
    
    if os.path.exists(repo_dir):
        # Reset to base commit
        subprocess.run(["git", "checkout", "-f", base_commit], cwd=repo_dir,
                       capture_output=True, timeout=60)
        subprocess.run(["git", "clean", "-fdx"], cwd=repo_dir,
                       capture_output=True, timeout=60)
        return repo_dir
    
    # Full clone needed to reach arbitrary commits
    r = subprocess.run(
        ["git", "clone", repo_url, repo_dir],
        capture_output=True, text=True, timeout=600
    )
    if r.returncode != 0:
        print(f"  Clone failed: {r.stderr[:200]}")
        return repo_dir
    
    checkout = subprocess.run(["git", "checkout", "-f", base_commit], cwd=repo_dir,
                   capture_output=True, text=True, timeout=60)
    if checkout.returncode != 0:
        print(f"  Checkout failed: {checkout.stderr[:200]}")
    return repo_dir


def solve_instance(instance, work_dir):
    """Use Claude to generate a patch for one SWE-bench instance."""
    import re
    
    instance_id = instance["instance_id"]
    repo = instance["repo"]
    base_commit = instance["base_commit"]
    problem = instance["problem_statement"]
    hints = instance.get("hints_text", "")
    
    print(f"\n{'='*60}")
    print(f"Instance: {instance_id}")
    print(f"Repo: {repo}, Commit: {base_commit[:12]}")
    print(f"Problem: {problem[:100]}...")
    
    # Clone and checkout
    try:
        repo_dir = clone_and_checkout(repo, base_commit, work_dir)
    except Exception as e:
        print(f"  ERROR cloning: {e}")
        return {"instance_id": instance_id, "model_name_or_path": MODEL_NAME, "model_patch": ""}
    
    # Build the prompt
    task = f"""Fix the following GitHub issue in the {repo} repository.

## Issue
{problem}
"""
    if hints:
        task += f"\n## Hints\n{hints[:500]}\n"
    
    task += f"\nThe repository is checked out at commit {base_commit[:12]}. Explore the code and produce a patch."
    
    messages = [{"role": "user", "content": task}]
    
    for turn in range(MAX_TURNS):
        resp = client.messages.create(
            model=MODEL, max_tokens=4096, system=SYSTEM_PROMPT, messages=messages
        )
        text = resp.content[0].text
        
        # Check for patch
        patch_match = re.search(r'<patch>(.*?)</patch>', text, re.DOTALL)
        bash_match = re.search(r'<bash>(.*?)</bash>', text, re.DOTALL)
        
        if bash_match:
            cmd = bash_match.group(1).strip()
            truncated = text[:text.index('</bash>') + len('</bash>')]
            output = run_in_repo(cmd, repo_dir)
            messages.append({"role": "assistant", "content": truncated})
            messages.append({"role": "user", "content": f"```\n{output}\n```"})
            
            print(f"  Turn {turn+1}: bash '{cmd[:80]}'")
        elif patch_match:
            # Model says it's done — grab the REAL diff from git
            git_diff = subprocess.run(
                ["git", "diff"], capture_output=True, text=True, cwd=repo_dir
            ).stdout.strip()
            
            if git_diff:
                print(f"  Patch ready at turn {turn+1} ({len(git_diff)} bytes from git diff)")
                return {"instance_id": instance_id, "model_name_or_path": MODEL_NAME, "model_patch": git_diff}
            else:
                # Model produced a patch tag but didn't actually edit — try applying the tag content
                patch = patch_match.group(1).strip()
                r = subprocess.run(
                    ["git", "apply", "--check", "-"],
                    input=patch, capture_output=True, text=True, cwd=repo_dir
                )
                if r.returncode == 0:
                    subprocess.run(["git", "apply", "-"], input=patch, capture_output=True, text=True, cwd=repo_dir)
                    git_diff = subprocess.run(["git", "diff"], capture_output=True, text=True, cwd=repo_dir).stdout.strip()
                    print(f"  Patch applied from tag at turn {turn+1} ({len(git_diff)} bytes)")
                    return {"instance_id": instance_id, "model_name_or_path": MODEL_NAME, "model_patch": git_diff}
                else:
                    print(f"  ⚠ Patch tag didn't apply, no git diff — continuing")
                    messages.append({"role": "assistant", "content": text})
                    messages.append({"role": "user",
                        "content": "The patch didn't apply. Edit the file directly with sed/python, then I'll capture git diff."})
                    continue
        else:
            # No bash or patch — model is thinking/explaining
            print(f"  Turn {turn+1}: [no-action] '{text[:80]}...'")
            messages.append({"role": "assistant", "content": text})
            if turn >= MAX_TURNS - 5:
                messages.append({"role": "user", "content": "You are running out of turns! Make your edit NOW with sed/python and then run `git diff` and wrap the output in <patch> tags."})
            else:
                messages.append({"role": "user", "content": "Please make the code edit now using bash (sed, python, etc), then run `git diff`."})
    
    # Last resort: check if the agent made changes via git diff
    git_diff = subprocess.run(
        ["git", "diff"], capture_output=True, text=True, cwd=repo_dir
    ).stdout.strip()
    if git_diff:
        print(f"  ⚠ Max turns but found git diff ({len(git_diff)} bytes) — using it as patch")
        return {"instance_id": instance_id, "model_name_or_path": MODEL_NAME, "model_patch": git_diff}
    
    print(f"  ✗ Max turns reached without patch")
    return {"instance_id": instance_id, "model_name_or_path": MODEL_NAME, "model_patch": ""}


def main():
    from swebench.harness.utils import load_swebench_dataset
    
    # Parse args
    dataset = "princeton-nlp/SWE-bench_Lite"
    split = "test"
    start = 0
    count = 5
    
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    if len(sys.argv) > 2:
        start = int(sys.argv[2])
    
    instances = load_swebench_dataset(dataset, split=split)
    instances = instances[start:start + count]
    
    print(f"SWE-bench Helios Adapter")
    print(f"Dataset: {dataset}, Split: {split}")
    print(f"Instances: {start} to {start + count - 1} ({len(instances)} total)")
    print(f"Model: {MODEL}")
    
    work_dir = os.path.expanduser("~/Projects/swe-bench/repos")
    os.makedirs(work_dir, exist_ok=True)
    
    predictions = []
    t0 = time.time()
    
    for inst in instances:
        pred = solve_instance(inst, work_dir)
        predictions.append(pred)
    
    elapsed = time.time() - t0
    
    # Save predictions
    outfile = os.path.expanduser(f"~/.openclaw/workspace/swebench-predictions-{start}-{start+count}.jsonl")
    with open(outfile, "w") as f:
        for p in predictions:
            f.write(json.dumps(p) + "\n")
    
    # Summary
    with_patch = sum(1 for p in predictions if p["model_patch"])
    print(f"\n{'='*60}")
    print(f"DONE: {with_patch}/{len(predictions)} instances got patches")
    print(f"Time: {elapsed:.0f}s ({elapsed/len(predictions):.0f}s per instance)")
    print(f"Predictions saved to {outfile}")
    print(f"\nTo evaluate: python -m swebench.harness.run_evaluation \\")
    print(f"  --predictions_path {outfile} \\")
    print(f"  --swe_bench_tasks {dataset} \\")
    print(f"  --run_id helios-baseline")


if __name__ == "__main__":
    main()
