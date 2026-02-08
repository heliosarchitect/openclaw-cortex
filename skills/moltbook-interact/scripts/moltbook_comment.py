#!/usr/bin/env python3
"""Post a comment to Moltbook with automatic CAPTCHA solving"""
import json
import requests
import re
import sys
import os

# Load API key
CONFIG_FILE = os.path.expanduser("~/.config/moltbook/credentials.json")
with open(CONFIG_FILE) as f:
    API_KEY = json.load(f)['api_key']

API_BASE = "https://www.moltbook.com/api/v1"

def decode_text(challenge):
    """Pre-process: remove symbols, collapse repeated letters"""
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', challenge)
    clean = clean.lower()
    clean = re.sub(r'(.)\1+', r'\1', clean)
    return ' '.join(clean.split())

def solve_captcha(challenge):
    """Use llama3.1-lexi to solve the math"""
    decoded = decode_text(challenge)
    
    prompt = f"""Solve this math word problem. Extract the numbers and operation, then calculate.

Problem: {decoded}

Rules:
- "total", "combined", "adds", "sum" = ADD the numbers
- "slows", "loses", "minus", "difference" = SUBTRACT  
- "product", "times", "multiply" = MULTIPLY
- Word numbers: "twenty three" = 23, "fifteen" = 15, etc.

Show your work briefly, then give the final answer.
Format: ANSWER: XX.XX"""

    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.1-lexi", "prompt": prompt, "stream": False},
            timeout=60
        )
        result = resp.json().get('response', '').strip()
        
        match = re.search(r'ANSWER:\s*(\d+\.?\d*)', result, re.IGNORECASE)
        if match:
            return f"{float(match.group(1)):.2f}"
        
        match = re.search(r'(\d+\.?\d*)', result)
        if match:
            return f"{float(match.group(1)):.2f}"
        
        return "0.00"
    except Exception as e:
        print(f"Ollama error: {e}")
        return "0.00"

def post_comment(post_id, content):
    """Post a comment and handle verification"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # Create comment
    resp = requests.post(
        f"{API_BASE}/posts/{post_id}/comments",
        headers=headers,
        json={"content": content}
    )
    data = resp.json()
    
    if not data.get('verification_required'):
        return data
    
    # Solve CAPTCHA
    challenge = data['verification']['challenge']
    code = data['verification']['code']
    
    print(f"🔐 Solving CAPTCHA...")
    print(f"   Challenge: {challenge[:60]}...")
    
    answer = solve_captcha(challenge)
    print(f"   Answer: {answer}")
    
    # Submit verification
    verify_resp = requests.post(
        f"{API_BASE}/verify",
        headers=headers,
        json={"verification_code": code, "answer": answer}
    )
    return verify_resp.json()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: moltbook_comment.py POST_ID CONTENT")
        sys.exit(1)
    
    post_id = sys.argv[1]
    content = ' '.join(sys.argv[2:])
    
    result = post_comment(post_id, content)
    print(json.dumps(result, indent=2))
