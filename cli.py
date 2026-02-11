import argparse
from pathlib import Path

from empathy_engine import EmpathyEngine, get_default_output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The Empathy Engine: synthesize emotionally aware speech from text."
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to speak. If omitted, you will be prompted to enter it interactively.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=get_default_output_path(),
        help="Path to output audio file (default: ./output/empathy_output.wav).",
    )

    args = parser.parse_args()

    if args.text is None:
        print("Enter the text you want the Empathy Engine to speak:")
        args.text = input("> ").strip()

    engine = EmpathyEngine()
    emotion_result, voice_profile, output_path = engine.synthesize_to_file(args.text, args.output)

    print(f"\nEmotion classification : {emotion_result.emotion.value}")
    print(f"Emotion intensity      : {emotion_result.intensity:.2f} (raw compound={emotion_result.raw_compound:.3f})")
    print(f"Applied voice settings : rate={voice_profile.rate}, volume={voice_profile.volume:.2f}")
    print(f"Audio saved to         : {output_path.resolve()}")


if __name__ == "__main__":
    main()

