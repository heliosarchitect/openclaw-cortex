#!/usr/bin/env python3
"""
Solve Moltbook verification challenges
"""
import sys
import json
import re
import requests

def parse_challenge(challenge_text):
    """Parse math challenge and solve it."""
    # Clean up the obfuscated text
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', challenge_text.lower())
    # Collapse 3+ repeated characters (nEeWwToOnS -> newtons, but keep 'three', 'teen')
    clean = re.sub(r'(.)\1{2,}', r'\1', clean)
    
    # Extract number words
    word_to_num = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
        'one hundred': 100, 'twenty one': 21, 'twenty two': 22, 'twenty three': 23,
        'twenty four': 24, 'twenty five': 25, 'twenty six': 26, 'twenty seven': 27,
        'twenty eight': 28, 'twenty nine': 29, 'thirty one': 31, 'thirty two': 32,
        'thirty three': 33, 'thirty four': 34, 'thirty five': 35, 'thirty six': 36,
        'thirty seven': 37, 'thirty eight': 38, 'thirty nine': 39
    }
    
    # Check for newton patterns (including obfuscated like neewwtoons)
    has_newton = bool(re.search(r'n[e]+[w]+[t]+[o]+[n]+[s]?', clean)) or 'newton' in clean
    
    # Force-related questions: only count numbers followed by 'newton'
    if has_newton or 'force' in clean:
        force_values = []
        newton_pattern = r'n[e]+[w]+[t]+[o]+[n]+[s]?'
        
        # Look for patterns like "twenty three newtons" or "7 newtons"
        # Only match if newton appears within 15 chars after the number (to avoid false matches)
        for phrase, num in sorted(word_to_num.items(), key=lambda x: -len(x[0])):
            # Check if number word is followed by newton within ~15 chars (not 30)
            idx = clean.find(phrase)
            if idx >= 0:
                after = clean[idx+len(phrase):idx+len(phrase)+15]  # Only look AFTER the number
                if 'newton' in after or re.search(newton_pattern, after):
                    force_values.append(num)
                    clean = clean[:idx] + '#' * len(phrase) + clean[idx+len(phrase):]  # Use # to mark used
        
        # Also check for digit patterns like "23 newtons"
        digit_matches = re.findall(r'(\d+)\s*' + newton_pattern, clean)
        for d in digit_matches:
            force_values.append(int(d))
        
        if force_values:
            return sum(force_values)
    
    # Fallback: extract all numbers
    values = []
    for phrase, num in sorted(word_to_num.items(), key=lambda x: -len(x[0])):
        if phrase in clean:
            values.append(num)
            clean = clean.replace(phrase, '', 1)
    
    if len(values) == 0:
        return None
    
    # Detect operation
    lower_text = challenge_text.lower()
    if 'times' in lower_text or 'multipl' in lower_text or 'product' in lower_text:
        # Multiplication
        result = 1
        for v in values:
            result *= v
        return result
    elif 'total' in lower_text or 'sum' in lower_text or 'add' in lower_text:
        # Addition
        return sum(values)
    else:
        # Default to addition
        return sum(values)

def verify_comment(verification_data, api_key):
    """Solve verification and submit answer."""
    challenge = verification_data['challenge']
    code = verification_data['code']
    
    # Solve the challenge
    answer = parse_challenge(challenge)
    if answer is None:
        print(f"❌ Could not solve challenge: {challenge}", file=sys.stderr)
        return False
    
    # Submit verification
    response = requests.post(
        'https://www.moltbook.com/api/v1/verify',
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        },
        json={
            'verification_code': code,
            'answer': f'{answer:.2f}'
        }
    )
    
    result = response.json()
    if result.get('success'):
        print(f"✅ Verification successful: {result.get('message')}")
        return True
    else:
        print(f"❌ Verification failed: {result.get('message')}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: solve_verification.py <api_key> <verification_json>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    verification_json = sys.argv[2]
    
    try:
        verification_data = json.loads(verification_json)
        success = verify_comment(verification_data, api_key)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
