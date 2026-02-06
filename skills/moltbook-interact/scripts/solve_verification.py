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
    
    values = []
    for phrase, num in sorted(word_to_num.items(), key=lambda x: -len(x[0])):
        if phrase in clean:
            values.append(num)
            clean = clean.replace(phrase, '', 1)
    
    if len(values) == 0:
        return None
    
    # Detect operation
    if 'times' in challenge_text.lower() or 'multiply' in challenge_text.lower():
        # Multiplication
        result = 1
        for v in values:
            result *= v
        return result
    elif 'total' in challenge_text.lower() or 'sum' in challenge_text.lower():
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
