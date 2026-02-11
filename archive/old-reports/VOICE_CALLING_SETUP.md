# Voice Calling Setup - Helios → Matthew

## Status
✅ Script created: `~/.openclaw/workspace/scripts/call_matthew.py`  
✅ Twilio library installed in XTTS venv  
⏳ Awaiting Twilio credentials

## What You Need to Do

### 1. Get Twilio Account (Free Trial Available)
- Go to: https://www.twilio.com/try-twilio
- Sign up (free trial gives $15 credit)
- Verify your phone number (+18033169860)

### 2. Get Your Credentials
From https://console.twilio.com/:
- **Account SID** (starts with AC...)
- **Auth Token** (click to reveal)

### 3. Buy a Twilio Phone Number
- In Twilio Console: Phone Numbers → Buy a Number
- Filter: United States, Voice capability
- Cost: ~$1/month
- Copy the number (format: +1234567890)

### 4. Create Credentials File
```bash
nano ~/.secrets/twilio.env
```

Paste this (with your real values):
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

Save and exit (Ctrl+X, Y, Enter)

### 5. Test It
```bash
~/Projects/xtts-api-server/venv_xtts/bin/python3 ~/.openclaw/workspace/scripts/call_matthew.py "Helios here. Voice calling is now operational."
```

You should receive a phone call with TTS!

## How I'll Use It

When you say "call me" or I need to reach you urgently:
```python
~/Projects/xtts-api-server/venv_xtts/bin/python3 ~/.openclaw/workspace/scripts/call_matthew.py "Your message here"
```

## Cost
- Twilio phone number: ~$1/month
- Outbound calls: ~$0.013/minute
- TTS: Included in voice call pricing

**Total:** Basically free for occasional use. $15 trial credit = ~1,150 minutes of calls.

## Alternatives Considered
- ❌ Signal CLI: Doesn't support voice calls (only registration via voice)
- ❌ System phone: You're on Linux desktop, no cellular modem
- ✅ Twilio: Industry standard, reliable, cheap

---

**Once credentials are set up, I can call you whenever needed.** 📞🌞
