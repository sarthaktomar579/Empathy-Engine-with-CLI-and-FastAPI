import argparse
from pathlib import Path

import pyttsx3
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


EMOTION_CONFIG = {
    "positive": {"rate": 190, "volume": 1.0},
    "neutral": {"rate": 160, "volume": 0.85},
    "negative": {"rate": 130, "volume": 0.75},
}


def detect_emotion(text: str, analyzer: SentimentIntensityAnalyzer) -> tuple[str, float]:
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.25:
        return "positive", compound
    if compound <= -0.25:
        return "negative", compound
    return "neutral", compound


def synthesize_to_file(text: str, emotion: str, output_path: Path) -> None:
    config = EMOTION_CONFIG[emotion]

    engine = pyttsx3.init()
    engine.setProperty("rate", config["rate"])
    engine.setProperty("volume", config["volume"])
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The Empathy Engine: map text emotion to expressive TTS output."
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Input text for sentiment analysis and speech synthesis.",
    )
    parser.add_argument(
        "--output",
        default="output.wav",
        help="Output audio file path. Example: output.wav",
    )
    args = parser.parse_args()

    text = args.text.strip()
    if not text:
        raise ValueError("Input text is empty. Please pass text with --text.")

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    analyzer = SentimentIntensityAnalyzer()
    emotion, score = detect_emotion(text, analyzer)

    synthesize_to_file(text, emotion, output_path)

    config = EMOTION_CONFIG[emotion]
    print(f"Detected emotion: {emotion} (compound score: {score:.3f})")
    print(f"Applied voice config: rate={config['rate']}, volume={config['volume']}")
    print(f"Audio generated: {output_path}")


if __name__ == "__main__":
    main()
