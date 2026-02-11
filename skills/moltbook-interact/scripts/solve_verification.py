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
    
    # Word-by-word matching (split on non-alpha, then match each word)
    # NOTE: Greedy substring matching on stripped text was removed because it
    # found false positives like "ten" inside "antenna" (caused 42 instead of 32,
    # got us suspended from Moltbook for 1 day — 2026-02-11)
    text_clean = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    words = text_clean.split()

    numbers = []
    i = 0
    while i < len(words):
        word = normalize_word(words[i])
        matched_key = match_word(word)
        
        # If no match, try merging with next 1-2 words (handles split obfuscation
        # like "tW/eN tY" → ["tw", "en", "ty"] → "twenty")
        if not matched_key and i + 1 < len(words):
            merged2 = word + normalize_word(words[i+1])
            matched_key = match_word(merged2)
            if matched_key:
                i += 1  # consumed extra word
            elif i + 2 < len(words):
                merged3 = merged2 + normalize_word(words[i+2])
                matched_key = match_word(merged3)
                if matched_key:
                    i += 2  # consumed two extra words
        
        if matched_key:
            num = word_to_num[matched_key]
            # Check for compound (e.g., "forty five")
            if i + 1 < len(words):
                next_word = normalize_word(words[i+1])
                next_matched = match_word(next_word)
                # Also try merge for the units part
                if not next_matched and i + 2 < len(words):
                    merged_next = next_word + normalize_word(words[i+2])
                    next_matched = match_word(merged_next)
                    if next_matched and word_to_num[next_matched] < 10:
                        num += word_to_num[next_matched]
                        i += 2
                        numbers.append(num)
                        i += 1
                        continue
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
