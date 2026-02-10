#!/usr/bin/env python3
"""
Voice call Matthew using Twilio API + TTS
Requires: Twilio credentials in ~/.secrets/twilio.env
"""
import os
import sys
from pathlib import Path

# Load Twilio credentials
secrets_file = Path.home() / ".secrets" / "twilio.env"
if secrets_file.exists():
    with open(secrets_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
MATTHEW_PHONE = os.getenv('MATTHEW_PHONE', '+18033169860')

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    print("❌ Missing Twilio credentials!")
    print("\nCreate ~/.secrets/twilio.env with:")
    print("TWILIO_ACCOUNT_SID=your_account_sid")
    print("TWILIO_AUTH_TOKEN=your_auth_token")
    print("TWILIO_PHONE_NUMBER=+1234567890")
    print("\nGet credentials from: https://console.twilio.com/")
    sys.exit(1)

from twilio.rest import Client

def call_matthew(message: str):
    """
    Make a voice call to Matthew with TTS message.
    
    Args:
        message: Text to speak during call
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # TwiML: Text-to-Speech instructions for the call
    twiml = f"""
    <Response>
        <Say voice="Google.en-US-Wavenet-D">{message}</Say>
        <Pause length="1"/>
        <Say>Call ending. Goodbye.</Say>
    </Response>
    """
    
    try:
        call = client.calls.create(
            to=MATTHEW_PHONE,
            from_=TWILIO_PHONE_NUMBER,
            twiml=twiml
        )
        
        print(f"✅ Call initiated: {call.sid}")
        print(f"📞 Calling {MATTHEW_PHONE}")
        print(f"📢 Message: {message}")
        return call.sid
        
    except Exception as e:
        print(f"❌ Call failed: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: call_matthew.py <message>")
        print("Example: call_matthew.py 'Helios here. I figured out the queued message issue.'")
        sys.exit(1)
    
    message = ' '.join(sys.argv[1:])
    call_matthew(message)
