#!/usr/bin/env python3
"""
Moltbook verification solver - handles obfuscated number words.
"""
import requests
import json
import sys
import re

def dedupe_chars(s):
    """Remove consecutive duplicate characters: 'foouur' -> 'four'."""
    if not s:
        return s
    result = [s[0]]
    for c in s[1:]:
        if c != result[-1]:
            result.append(c)
    return ''.join(result)

def normalize_word(word):
    """Remove non-alpha and normalize obfuscated words. Try raw first, then deduped."""
    # Remove non-alpha
    word = re.sub(r'[^a-zA-Z]', '', word.lower())
    if not word:
        return ""
    
    # Return as-is first (preserves valid doubles like 'ee' in 'fourteen')
    # Caller will try dictionary lookup; if it fails, dedupe_chars is available
    return word

def parse_numbers(text):
    """Extract numbers from obfuscated challenge text."""
    word_to_num = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
    }
    
    def match_word(w):
        """Try raw word first, then deduped. Returns matched key or None."""
        if w in word_to_num:
            return w
        deduped = dedupe_chars(w)
        if deduped in word_to_num:
            return deduped
        return None
    
    # Strategy 1: Strip ALL non-alpha, lowercase, then use sliding window to find number words
    stripped = re.sub(r'[^a-zA-Z]', '', text).lower()
    
    # Greedily extract number words from the stripped string
    all_number_words = sorted(word_to_num.keys(), key=len, reverse=True)
    # Also add deduped variants
    found_numbers_s1 = []
    remaining = stripped
    while remaining:
        matched = False
        for nw in all_number_words:
            # Try exact match at start
            if remaining.startswith(nw):
                found_numbers_s1.append(word_to_num[nw])
                remaining = remaining[len(nw):]
                matched = True
                break
            # Try deduped match: expand nw to see if remaining starts with an obfuscated version
            # e.g., remaining="foortyy..." should match "forty"
            deduped_prefix = dedupe_chars(remaining[:len(nw)*3])  # generous prefix
            if deduped_prefix.startswith(nw):
                # Find how many chars of remaining produce this deduped prefix
                for end in range(len(nw), min(len(remaining)+1, len(nw)*3+1)):
                    if dedupe_chars(remaining[:end]) == nw:
                        found_numbers_s1.append(word_to_num[nw])
                        remaining = remaining[end:]
                        matched = True
                        break
                    elif dedupe_chars(remaining[:end]).startswith(nw) and len(dedupe_chars(remaining[:end])) > len(nw):
                        # Went past — use previous
                        found_numbers_s1.append(word_to_num[nw])
                        remaining = remaining[end-1:]
                        matched = True
                        break
                if matched:
                    break
        if not matched:
            remaining = remaining[1:]  # skip one char
    
    if found_numbers_s1:
        return found_numbers_s1
    
    # Strategy 2 (fallback): Split on spaces, try word-by-word matching
    text_clean = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    words = text_clean.split()

    numbers = []
    i = 0
    while i < len(words):
        word = normalize_word(words[i])
        matched_key = match_word(word)
        if matched_key:
            num = word_to_num[matched_key]
            # Check for compound (e.g., "forty five")
            if i + 1 < len(words):
                next_word = normalize_word(words[i+1])
                next_matched = match_word(next_word)
                if next_matched and word_to_num[next_matched] < 10:
                    num += word_to_num[next_matched]
                    i += 1
            numbers.append(num)
        i += 1
    
    return numbers

def determine_operation(text):
    """Determine math operation from challenge text."""
    text = text.lower()
    
    if 'product' in text or 'multipl' in text or 'times' in text:
        return 'multiply'
    elif 'loses' in text or 'subtract' in text or 'minus' in text or 'difference' in text or 'fewer' in text or 'less' in text:
        return 'subtract'
    elif 'divid' in text or 'split' in text:
        return 'divide'
    else:  # 'total', 'adds', 'sum', 'combined', 'force', etc.
        return 'add'

def solve(challenge):
    """Solve a verification challenge."""
    numbers = parse_numbers(challenge)
    operation = determine_operation(challenge)
    
    if not numbers:
        return None
    
    if operation == 'multiply':
        result = numbers[0] * numbers[1] if len(numbers) >= 2 else numbers[0]
    elif operation == 'subtract':
        result = numbers[0] - numbers[1] if len(numbers) >= 2 else numbers[0]
    else:  # add
        result = sum(numbers)
    
    return f"{result:.2f}"

def verify(api_key, code, answer):
    """Submit verification answer."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        "https://www.moltbook.com/api/v1/verify",
        headers=headers,
        json={"verification_code": code, "answer": answer}
    )
    return resp.json()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: solve_verification.py <api_key> <verification_json>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    verification = json.loads(sys.argv[2])
    
    challenge = verification.get("challenge", "")
    code = verification.get("code", "")
    
    print(f"Challenge: {challenge}")
    answer = solve(challenge)
    print(f"Answer: {answer}")
    
    if answer:
        result = verify(api_key, code, answer)
        print(json.dumps(result, indent=2))
    else:
        print("Could not parse challenge")
