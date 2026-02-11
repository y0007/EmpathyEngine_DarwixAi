from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pyttsx3


class Emotion(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class EmotionResult:
    emotion: Emotion
    intensity: float  # 0.0–1.0 scaled magnitude
    raw_compound: float


class EmotionDetector:
    """
    Simple sentiment-based emotion detector using VADER.
    Maps text to POSITIVE / NEGATIVE / NEUTRAL with an intensity score.
    """

    def __init__(self) -> None:
        self._analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> EmotionResult:
        scores = self._analyzer.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.2:
            emotion = Emotion.POSITIVE
        elif compound <= -0.2:
            emotion = Emotion.NEGATIVE
        else:
            emotion = Emotion.NEUTRAL

        intensity = min(1.0, abs(compound))
        return EmotionResult(emotion=emotion, intensity=intensity, raw_compound=compound)


@dataclass
class VoiceProfile:
    rate: int
    volume: float  # 0.0–1.0


class EmpathyEngine:
    """
    Core Empathy Engine:
    - detects emotion from text
    - maps emotion to vocal parameters (rate, volume)
    - synthesizes speech to an audio file
    """

    def __init__(self, voice_id: str | None = None) -> None:
        self.detector = EmotionDetector()
        self.engine = pyttsx3.init()

        # Capture the default rate and volume to use as a neutral baseline.
        self.base_rate: int = int(self.engine.getProperty("rate") or 200)
        self.base_volume: float = float(self.engine.getProperty("volume") or 1.0)

        if voice_id is not None:
            self.engine.setProperty("voice", voice_id)

    def emotion_to_voice(self, result: EmotionResult) -> VoiceProfile:
        """
        Map emotion and intensity to TTS parameters.

        Design:
        - POSITIVE: faster and slightly louder as intensity grows
        - NEGATIVE: slower and slightly softer as intensity grows
        - NEUTRAL: baseline rate and volume
        """
        intensity = result.intensity

        if result.emotion is Emotion.POSITIVE:
            # Up to +25% faster, +15% louder
            rate = int(self.base_rate * (1.0 + 0.25 * intensity))
            volume = min(1.0, self.base_volume + 0.15 * intensity)
        elif result.emotion is Emotion.NEGATIVE:
            # Down to -25% slower, -20% softer
            rate = int(self.base_rate * (1.0 - 0.25 * intensity))
            volume = max(0.3, self.base_volume - 0.2 * intensity)
        else:  # NEUTRAL
            rate = self.base_rate
            volume = self.base_volume

        return VoiceProfile(rate=rate, volume=volume)

    def synthesize_to_file(self, text: str, output_path: str | Path) -> Tuple[EmotionResult, VoiceProfile, Path]:
        """
        Analyze emotion, configure TTS engine, and synthesize audio to file.

        Returns (emotion_result, voice_profile, output_path).
        """
        if not text or not text.strip():
            raise ValueError("Input text must not be empty.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        emotion_result = self.detector.analyze(text)
        voice_profile = self.emotion_to_voice(emotion_result)

        self.engine.setProperty("rate", voice_profile.rate)
        self.engine.setProperty("volume", voice_profile.volume)

        # pyttsx3 prefers .wav, but name is up to caller.
        self.engine.save_to_file(text, str(output_path))
        self.engine.runAndWait()

        return emotion_result, voice_profile, output_path


def get_default_output_path() -> Path:
    """
    Default output path: ./output/empathy_output.wav
    """
    return Path("output") / "empathy_output.wav"
