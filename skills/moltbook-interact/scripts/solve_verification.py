#!/usr/bin/env python3
"""
Moltbook verification solver - handles obfuscated number words.
"""
import requests
import json
import sys
import re

def normalize_word(word):
    """Remove repeated characters and normalize obfuscated words."""
    # Remove non-alpha
    word = re.sub(r'[^a-zA-Z]', '', word.lower())
    if not word:
        return ""
    
    # Remove consecutive duplicates (e.g., "fortyy" -> "forty", "tweelve" -> "twelve")
    result = word[0]
    for char in word[1:]:
        if char != result[-1]:
            result += char
    
    return result

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
    
    # Clean text
    text_clean = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    words = text_clean.split()
    
    numbers = []
    i = 0
    while i < len(words):
        word = normalize_word(words[i])
        if word in word_to_num:
            num = word_to_num[word]
            # Check for compound (e.g., "forty five")
            if i + 1 < len(words):
                next_word = normalize_word(words[i+1])
                if next_word in word_to_num and word_to_num[next_word] < 10:
                    num += word_to_num[next_word]
                    i += 1
            numbers.append(num)
        i += 1
    
    return numbers

def determine_operation(text):
    """Determine math operation from challenge text."""
    text = text.lower()
    
    if 'product' in text or 'multipl' in text:
        return 'multiply'
    elif 'loses' in text or 'subtract' in text or 'minus' in text or 'difference' in text:
        return 'subtract'
    else:  # 'total', 'adds', 'sum', 'combined', etc.
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
