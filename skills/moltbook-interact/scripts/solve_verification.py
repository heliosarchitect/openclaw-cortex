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
    # Extract numbers and operation
    # Format: "A claw exerts X newtons and B claw exerts Y newtons, what is the total force?"
    
    numbers = re.findall(r'\b(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|one hundred|twenty five|thirty five|forty five|fifty five|sixty five|seventy five|eighty five|ninety five|\d+(?:\.\d+)?)\b', challenge_text.lower())
    
    # Convert word numbers to digits
    word_to_num = {
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
        'one hundred': 100,
        'twenty five': 25, 'thirty five': 35, 'forty five': 45,
        'fifty five': 55, 'sixty five': 65, 'seventy five': 75,
        'eighty five': 85, 'ninety five': 95
    }
    
    values = []
    for num in numbers:
        if num in word_to_num:
            values.append(word_to_num[num])
        else:
            try:
                values.append(float(num))
            except ValueError:
                pass
    
    # Most challenges are simple addition
    if 'total' in challenge_text.lower() or 'sum' in challenge_text.lower():
        return sum(values)
    
    return None

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
