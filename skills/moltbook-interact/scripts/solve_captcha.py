#!/usr/bin/env python3
"""Moltbook CAPTCHA solver using local Ollama LLM"""
import json
import requests
import re
import sys

def decode_text(challenge):
    """Pre-process: remove symbols, collapse repeated letters"""
    # Remove special chars
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', challenge)
    # Lowercase
    clean = clean.lower()
    # Collapse repeated letters (loooobster -> lobster)
    clean = re.sub(r'(.)\1+', r'\1', clean)
    # Clean whitespace
    clean = ' '.join(clean.split())
    return clean

def solve_with_ollama(challenge, model="llama3.1-lexi"):
    """Use local LLM to solve the math"""
    decoded = decode_text(challenge)
    
    prompt = f"""Solve this math word problem. Extract the numbers and operation, then calculate.

Problem: {decoded}

Rules:
- "total", "combined", "adds", "sum" = ADD the numbers
- "slows", "loses", "minus", "difference" = SUBTRACT  
- "product", "times", "multiply" = MULTIPLY
- Word numbers: "twenty three" = 23, "fifteen" = 15, etc.

Show your work briefly, then give the final answer as just a number with 2 decimals.
Format: ANSWER: XX.XX"""

    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        result = resp.json().get('response', '').strip()
        
        # Look for ANSWER: pattern first
        match = re.search(r'ANSWER:\s*(\d+\.?\d*)', result, re.IGNORECASE)
        if match:
            return f"{float(match.group(1)):.2f}"
        
        # Fallback: find any number
        match = re.search(r'(\d+\.?\d*)', result)
        if match:
            return f"{float(match.group(1)):.2f}"
        
        return "0.00"
    except Exception as e:
        return f"ERROR: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        challenge = ' '.join(sys.argv[1:])
        print(f"Decoded: {decode_text(challenge)}")
        print(f"Answer: {solve_with_ollama(challenge)}")
    else:
        # Test cases
        tests = [
            "A] lOoOoBbSsTtEr ClAw FoRcE iS tWeNtY tHrEe NeWtOnS aNd AnOtHeR iS fIfTeEn, WhAt Is ThE tOtAl?",
            "A lobster swims at twenty three meters and slows by five, whats the new velocity?",
        ]
        for t in tests:
            print(f"Challenge: {t[:50]}...")
            print(f"Decoded: {decode_text(t)}")
            print(f"Answer: {solve_with_ollama(t)}")
            print()
