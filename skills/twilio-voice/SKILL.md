# Twilio Voice Integration for OpenClaw

A comprehensive voice calling integration that enables Helios (the OpenClaw AI assistant) to make and receive phone calls via Twilio's programmable voice platform.

## Overview

This skill provides bi-directional voice communication capabilities:
- **Inbound Calls**: Receive calls on your Twilio number, interact with callers using speech-to-text and text-to-speech
- **Outbound Calls**: Programmatically make calls with AI-generated content
- **OpenClaw Integration**: Events flow through OpenClaw's event system for seamless AI assistant interaction

## Features

- 📞 **Inbound Call Handling**: Answer calls, greet callers, collect speech/DTMF input
- 📞 **Outbound Call Generation**: Make calls programmatically with custom messages  
- 🎤 **Speech-to-Text**: Convert caller speech to text using Twilio's STT providers
- 🔊 **Text-to-Speech**: Respond with natural-sounding AI voices (Polly voices available)
- 🔗 **OpenClaw Events**: Integrate with OpenClaw's event system for AI processing
- 🔒 **Webhook Security**: Validate Twilio webhook signatures for security
- 📊 **Call Status Tracking**: Monitor call progress and completion

## Architecture

```
Caller ↔ Twilio Cloud ↔ FastAPI Webhook Server ↔ OpenClaw Event System ↔ Helios AI
```

1. **Inbound Call Flow**:
   - Caller dials Twilio number
   - Twilio sends webhook to your server
   - Server generates TwiML response (greeting + speech collection)
   - User speaks → Speech-to-text → OpenClaw event → Helios processes → TTS response
   
2. **Outbound Call Flow**:
   - CLI command or API triggers call
   - Twilio initiates call to target number
   - On answer, server provides TwiML with AI message
   - Interactive conversation can follow

## Installation

### 1. Install Dependencies

```bash
cd ~/Projects/twilio-openclaw
pip install -r requirements.txt
```

### 2. Configure Twilio Account

1. **Create Twilio Account**: Visit [twilio.com](https://www.twilio.com/try-twilio)
2. **Buy a Phone Number**: 
   - Go to [Phone Numbers Console](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
   - Click "Buy a number"
   - Choose a number with Voice capability
3. **Get Account Credentials**:
   - Account SID: From [Twilio Console](https://console.twilio.com/)
   - Auth Token: From [Twilio Console](https://console.twilio.com/)

### 3. Set Up Environment

```bash
cd ~/Projects/twilio-openclaw
cp config.template.env .env
# Edit .env with your Twilio credentials
```

Required environment variables:
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here  
TWILIO_PHONE_NUMBER=+1234567890
WEBHOOK_URL=https://your-domain.ngrok.io
```

### 4. Expose Webhook Server (Development)

Install and run ngrok to expose your local server:
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) to your `.env` file as `WEBHOOK_URL`.

### 5. Configure Twilio Webhook

1. Go to [Phone Numbers Console](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. Click on your Twilio phone number
3. In the Voice Configuration section:
   - **A call comes in**: Webhook
   - **URL**: `https://your-domain.ngrok.io/voice/inbound`
   - **HTTP Method**: POST
4. Click "Save configuration"

## Usage

### Start the Webhook Server

```bash
cd ~/Projects/twilio-openclaw
python server.py
```

The server will start on `http://0.0.0.0:8000` with the following endpoints:
- `POST /voice/inbound` - Handle incoming calls  
- `POST /voice/process` - Process user speech/DTMF input
- `GET|POST /voice/outbound` - Handle outbound call TwiML
- `POST /voice/status` - Receive call status updates
- `GET /voice/test` - Test TTS generation

### Make Outbound Calls

Using the CLI script:
```bash
# Basic call
openclaw-call "+1 (555) 123-4567"

# Call with custom message
openclaw-call 5551234567 "Hello, this is Helios calling with your appointment reminder."

# Test configuration
openclaw-call --test +15551234567

# Use different voice
openclaw-call --voice Polly.Matthew +15551234567 "This is a test call."
```

### Receive Inbound Calls

1. Call your Twilio phone number
2. You'll hear: "Hello! You've reached the OpenClaw AI assistant, Helios. How can I help you today?"
3. Speak your question or press keys
4. Helios will respond with relevant information
5. The conversation continues until you say "goodbye" or hang up

## OpenClaw Event Integration

The integration sends events to OpenClaw's event system using the `openclaw-event` script:

### Event Types

- **`inbound_call`**: New call received
- **`user_input`**: User spoke or pressed keys  
- **`call_status`**: Call status changed (completed, busy, etc.)

### Event Data Structure

```json
{
  "event_type": "user_input",
  "from_number": "+15551234567",
  "to_number": "+15559876543", 
  "call_sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "call_status": "in-progress",
  "speech_result": "What is the weather like today?",
  "digits": null,
  "confidence": 0.95
}
```

### Custom Event Handling

Extend the `generate_ai_response()` function in `server.py` to:
1. Send user input to Helios via OpenClaw events
2. Wait for Helios to process and respond  
3. Return the AI-generated response for TTS

```python
async def generate_ai_response(user_input: str, caller_number: str, call_sid: str) -> str:
    # Send to Helios via OpenClaw
    await send_to_helios({
        "user_input": user_input,
        "caller": caller_number,
        "call_id": call_sid,
        "context": "phone_call"
    })
    
    # Wait for Helios response
    response = await wait_for_helios_response(call_sid)
    
    return response.get("message", "I'm processing your request...")
```

## Configuration Options

### TwiML Voice Options

```python
response.say(text, voice='Polly.Joanna', rate='medium', pitch='medium')
```

Available voices include:
- `Polly.Joanna` (female, US English) 
- `Polly.Matthew` (male, US English)
- `Polly.Amy` (female, British English)
- `alice`, `man`, `woman` (classic Twilio voices)

### Speech Recognition

```python
gather = Gather(
    input='speech dtmf',      # Accept speech and/or keypad input
    language='en-US',         # Language for STT
    speechTimeout=5,          # Seconds to wait after speech stops
    timeout=10,               # Total timeout for any input
    hints='keyword1, phrase', # Improve recognition accuracy
    speechModel='default'     # STT model: default, phone_call, etc.
)
```

### Webhook Security

Production deployments should validate webhook signatures:
```python
def validate_twilio_request(request, signature, url, params):
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    return validator.validate(url, params, signature)
```

## Production Deployment

### 1. Use Production ASGI Server

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8000
```

### 2. HTTPS Certificate

Twilio requires HTTPS for webhooks. Use:
- **Cloud hosting**: AWS, GCP, Heroku (handles HTTPS)
- **Reverse proxy**: nginx with Let's Encrypt certificate
- **Load balancer**: With SSL termination

### 3. Environment Variables

Set environment variables on your production system instead of using `.env` files.

### 4. Monitoring

- Monitor call logs in [Twilio Console](https://console.twilio.com/us1/monitor/logs/calls)
- Set up error tracking (Sentry, etc.)
- Monitor webhook response times

## Troubleshooting

### Common Issues

**"Webhook responded with invalid TwiML"**
- Check that endpoints return valid XML responses
- Ensure Content-Type is `application/xml`
- Validate TwiML with Twilio's debugger

**"No audio on calls"**
- Verify TTS voice names are correct
- Check volume levels in TwiML
- Test with the `/voice/test` endpoint

**"Speech recognition not working"**
- Ensure `input='speech'` or `input='speech dtmf'`  
- Check language codes match spoken language
- Add relevant hints for better accuracy

**"Webhook signature validation fails"**
- Verify `TWILIO_AUTH_TOKEN` is correct
- Check that request URL matches exactly
- Ensure webhook URL is publicly accessible

### Debug Mode

Run with debug logging:
```bash
python server.py --verbose
```

Test webhook endpoints:
```bash
curl -X POST http://localhost:8000/voice/inbound \
  -d "CallSid=test123&From=+15551234567&To=+15559876543&CallStatus=ringing"
```

## API Reference

### Webhook Endpoints

#### `POST /voice/inbound`
Handle incoming calls, provide initial greeting and input collection.

**Parameters** (form data):
- `CallSid`: Unique call identifier
- `From`: Caller's phone number  
- `To`: Your Twilio number
- `CallStatus`: Call status (ringing, answered, etc.)
- `SpeechResult`: Transcribed speech (if available)
- `Digits`: DTMF input (if available)

**Response**: TwiML XML

#### `POST /voice/process`  
Process user input and generate AI responses.

**Parameters**: Same as `/voice/inbound`
**Response**: TwiML XML with AI response

#### `POST /voice/status`
Receive call status updates.

**Parameters**:
- `CallSid`, `CallStatus`, `From`, `To`
- `CallDuration`: Call duration in seconds

**Response**: JSON status

### CLI Commands

#### `openclaw-call`
Make outbound calls via Twilio API.

```bash
openclaw-call [OPTIONS] PHONE_NUMBER [MESSAGE]

Options:
  --voice TEXT        Voice for TTS (default: Polly.Joanna)
  --webhook-url TEXT  Override webhook URL
  --test             Test configuration without calling
  --verbose, -v      Enable verbose logging
```

## Examples

### Basic Inbound Call Flow

1. Caller dials your Twilio number
2. Twilio → `POST /voice/inbound`
3. Server responds with TwiML:
   ```xml
   <Response>
     <Gather input="speech dtmf" action="/voice/process">
       <Say>Hello! You've reached Helios. How can I help?</Say>
     </Gather>
   </Response>
   ```
4. Caller speaks: "What's the weather?"
5. Twilio → `POST /voice/process` with `SpeechResult="What's the weather?"`
6. Server → OpenClaw event → Helios processes → Response
7. Server responds with TwiML:
   ```xml
   <Response>
     <Say>The current weather is sunny and 72 degrees.</Say>
     <Gather input="speech dtmf" action="/voice/process">
       <Say>Anything else I can help with?</Say>
     </Gather>
   </Response>
   ```

### Custom Outbound Message

```bash
openclaw-call "+1-555-123-4567" \
  "Hi, this is Helios calling to remind you about your appointment tomorrow at 3 PM. Please call back if you need to reschedule."
```

Generates TwiML:
```xml
<Response>
  <Say voice="Polly.Joanna">
    Hi, this is Helios calling to remind you about your appointment tomorrow at 3 PM. 
    Please call back if you need to reschedule.
  </Say>
  <Gather input="speech dtmf" action="/voice/process">
    <Say>Is there anything else I can help you with?</Say>
  </Gather>
</Response>
```

## Advanced Features

### Multi-language Support

Configure different languages per call:
```python
gather = Gather(
    language='es-US',  # Spanish (US)
    speechModel='phone_call'
)
gather.say("Hola, soy Helios. ¿Cómo puedo ayudarte?", language='es-US')
```

### Call Recording

Enable call recording:
```python
response.record(
    action='/call-recording',
    maxLength=300,  # 5 minutes max
    finishOnKey='#'
)
```

### Conference Calls

Set up conference calls:
```python
response.dial().conference('helios-conference-room')
```

### Integration with External APIs

```python
async def generate_ai_response(user_input: str, caller_number: str, call_sid: str) -> str:
    # Example: Get weather data
    if 'weather' in user_input.lower():
        weather_data = await get_weather_data()
        return f"The current weather is {weather_data['condition']} with a temperature of {weather_data['temp']} degrees."
    
    # Example: Calendar integration  
    if 'appointment' in user_input.lower():
        appointments = await get_user_appointments(caller_number)
        return f"Your next appointment is {appointments[0]['title']} on {appointments[0]['date']}."
    
    # Default: Send to Helios AI
    return await query_helios_ai(user_input, caller_number)
```

This integration provides a solid foundation for voice-enabled AI interactions through the phone system, making Helios accessible via traditional voice calls.

## Version

- **Version**: 1.0.0
- **Last Updated**: February 16, 2026
- **OpenClaw Compatibility**: v1.0+
- **Twilio API Version**: 2010-04-01