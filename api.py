from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from empathy_engine import EMOTION_CONFIG, detect_emotion, synthesize_to_file


app = FastAPI(title="Empathy Engine API", version="1.0.0")
analyzer = SentimentIntensityAnalyzer()

OUTPUT_DIR = Path("outputs").resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/audio", StaticFiles(directory=str(OUTPUT_DIR)), name="audio")


class SynthesizeRequest(BaseModel):
    text: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Empathy Engine Demo</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 760px; margin: 40px auto; padding: 0 16px; }
    textarea { width: 100%; min-height: 120px; font-size: 16px; padding: 10px; }
    button { margin-top: 12px; padding: 10px 16px; font-size: 16px; cursor: pointer; }
    .card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-top: 16px; }
    .muted { color: #666; font-size: 14px; }
    .error { color: #b00020; }
  </style>
</head>
<body>
  <h1>Empathy Engine</h1>
  <p class="muted">Type text, then generate expressive speech.</p>

  <textarea id="textInput">We are excited to help you today.</textarea><br>
  <button onclick="generateAudio()">Generate Audio</button>

  <div class="card">
    <p id="meta" class="muted">No audio generated yet.</p>
    <audio id="player" controls style="width: 100%;"></audio>
    <p id="err" class="error"></p>
  </div>

  <script>
    async function generateAudio() {
      const text = document.getElementById("textInput").value.trim();
      const meta = document.getElementById("meta");
      const player = document.getElementById("player");
      const err = document.getElementById("err");
      err.textContent = "";

      if (!text) {
        err.textContent = "Please enter some text first.";
        return;
      }

      try {
        meta.textContent = "Generating audio...";
        const res = await fetch("/synthesize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text })
        });

        const data = await res.json();
        if (!res.ok) {
          err.textContent = data.detail || "Request failed.";
          meta.textContent = "Failed.";
          return;
        }

        meta.textContent = `Emotion: ${data.emotion} | Score: ${Number(data.compound_score).toFixed(3)} | Rate: ${data.rate} | Volume: ${data.volume}`;
        player.src = data.audio_url + "?t=" + Date.now();
        await player.play();
      } catch (e) {
        err.textContent = "Could not connect to server.";
        meta.textContent = "Failed.";
      }
    }
  </script>
</body>
</html>
"""


@app.post("/synthesize")
def synthesize(req: SynthesizeRequest) -> dict[str, str | float]:
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    emotion, score = detect_emotion(text, analyzer)
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}.wav"
    output_path = OUTPUT_DIR / filename

    synthesize_to_file(text, emotion, output_path)

    config = EMOTION_CONFIG[emotion]
    return {
        "emotion": emotion,
        "compound_score": score,
        "rate": config["rate"],
        "volume": config["volume"],
        "audio_file": filename,
        "audio_url": f"/audio/{filename}",
    }
