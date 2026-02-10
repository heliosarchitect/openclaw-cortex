#!/home/bonsaihorn/Projects/xtts-api-server/venv_xtts/bin/python3
"""
Call Matthew using Google Voice API
"""
import sys
from googlevoice import Voice

def call_matthew():
    """Place a call to Matthew via Google Voice"""
    try:
        print("🌞 Helios calling Matthew via Google Voice...")
        
        # Initialize Google Voice
        voice = Voice()
        
        # Login (will use stored credentials or prompt)
        voice.login()
        
        # Matthew's number
        matthew_number = '+18033169860'
        
        # Place the call
        print(f"📞 Calling {matthew_number}...")
        voice.call(matthew_number)
        
        print("✅ Call initiated!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = call_matthew()
    sys.exit(0 if success else 1)
