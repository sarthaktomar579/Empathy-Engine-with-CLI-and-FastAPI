# The Empathy Engine (Challenge 1)

This project solves Challenge 1 by turning text into expressive speech.

It does:
- Text input via CLI
- Emotion detection (positive / neutral / negative)
- Emotion-to-voice mapping
- Vocal modulation of at least two parameters (`rate`, `volume`)
- Audio file output (`.wav`)

## Quick setup

```powershell
python -m pip install -r requirements.txt
```

## Run

```powershell
python empathy_engine.py --text "Amazing news! We just won the biggest contract this quarter." --output output.wav
```

You will see:
- detected emotion score
- chosen voice configuration
- generated output file path

## Run API (FastAPI)

Start server:

```powershell
uvicorn api:app --reload
```

Test API request:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/synthesize -ContentType "application/json" -Body '{"text":"Thank you for your patience. We are fixing this right now."}'
```

Then open returned `audio_url` in browser, for example:
- `http://127.0.0.1:8000/audio/<generated_file>.wav`

## Design choices

- **Emotion model**: VADER sentiment analysis for fast, offline classification.
- **Voice mapping**:
  - positive -> faster rate, higher volume
  - neutral -> balanced rate and volume
  - negative -> slower rate, softer volume
- **TTS engine**: `pyttsx3` for local, no-API-key synthesis.

## Notes

- On Windows, `pyttsx3` works with installed SAPI voices.
- If output file is locked by another app, close the app and run again.
