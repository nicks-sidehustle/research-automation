#!/usr/bin/env python3
"""
Podcast Producer - Convert markdown podcast scripts to audio files
"""

import argparse
import re
import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import hashlib

try:
    from gtts import gTTS
    from pydub import AudioSegment
except ImportError as e:
    print(f"Error: Missing required library: {e}")
    print("Please install: pip install gTTS pydub")
    sys.exit(1)


class PodcastProducer:
    """Convert podcast scripts to audio"""

    # Voice characteristics for different speakers
    VOICE_SETTINGS = {
        'HOST': {'lang': 'en', 'tld': 'com', 'slow': False},        # US English
        'CO-HOST': {'lang': 'en', 'tld': 'com.au', 'slow': False},  # Australian English
        'GUEST': {'lang': 'en', 'tld': 'co.uk', 'slow': False},     # UK English
        'NARRATOR': {'lang': 'en', 'tld': 'us', 'slow': False},     # US English
        'DEFAULT': {'lang': 'en', 'tld': 'com', 'slow': False},
    }

    def __init__(self, script_path: str, output_dir: str = "outputs/podcast/audio"):
        self.script_path = Path(script_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)

    def parse_script(self) -> List[Tuple[str, str, str]]:
        """
        Parse markdown script into segments
        Returns: List of (type, content, metadata) tuples
        """
        with open(self.script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        segments = []

        # Extract title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            segments.append(('TITLE', title_match.group(1), ''))

        # Parse content line by line
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Music cue: [MUSIC: description]
            music_match = re.match(r'\[MUSIC:\s*(.+?)\]', line)
            if music_match:
                segments.append(('MUSIC', music_match.group(1), ''))
                continue

            # Pause: [PAUSE: X seconds]
            pause_match = re.match(r'\[PAUSE:\s*(\d+(?:\.\d+)?)\s*seconds?\]', line)
            if pause_match:
                segments.append(('PAUSE', pause_match.group(1), ''))
                continue

            # Sound effect: [SFX: description]
            sfx_match = re.match(r'\[SFX:\s*(.+?)\]', line)
            if sfx_match:
                segments.append(('SFX', sfx_match.group(1), ''))
                continue

            # Speaker dialogue: **SPEAKER:** text (colon inside bold)
            speaker_match = re.match(r'\*\*([A-Z\s\-]+):\*\*\s*(.+)', line)
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                text = speaker_match.group(2).strip()
                segments.append(('SPEECH', text, speaker))
                continue

            # Regular paragraph (narrator)
            if not line.startswith('#') and not line.startswith('['):
                segments.append(('SPEECH', line, 'NARRATOR'))

        return segments

    def text_to_speech(self, text: str, speaker: str, segment_id: int) -> Path:
        """Convert text to speech audio file"""
        # Get voice settings for speaker
        voice_config = self.VOICE_SETTINGS.get(speaker, self.VOICE_SETTINGS['DEFAULT'])

        # Create unique filename
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        audio_file = self.temp_dir / f"segment_{segment_id:04d}_{speaker}_{text_hash}.mp3"

        # Skip if already exists
        if audio_file.exists():
            print(f"  Using cached: {audio_file.name}")
            return audio_file

        print(f"  Generating: {speaker} - {text[:50]}...")

        try:
            tts = gTTS(
                text=text,
                lang=voice_config['lang'],
                tld=voice_config['tld'],
                slow=voice_config['slow']
            )
            tts.save(str(audio_file))
            return audio_file
        except Exception as e:
            print(f"  Warning: TTS failed for segment {segment_id}: {e}")
            return None

    def create_silence(self, duration_seconds: float, segment_id: int) -> Path:
        """Create a silent audio segment"""
        audio_file = self.temp_dir / f"segment_{segment_id:04d}_PAUSE_{duration_seconds}s.mp3"

        if audio_file.exists():
            return audio_file

        print(f"  Creating {duration_seconds}s pause...")
        silence = AudioSegment.silent(duration=int(duration_seconds * 1000))
        silence.export(str(audio_file), format="mp3")
        return audio_file

    def combine_audio_segments(self, audio_files: List[Path], output_path: Path) -> Dict:
        """Combine all audio segments into final podcast"""
        print("\n📻 Combining audio segments...")

        combined = AudioSegment.empty()

        for audio_file in audio_files:
            if audio_file and audio_file.exists():
                try:
                    segment = AudioSegment.from_mp3(str(audio_file))
                    combined += segment
                    # Add small pause between segments for natural flow
                    combined += AudioSegment.silent(duration=500)  # 0.5 second
                except Exception as e:
                    print(f"  Warning: Could not load {audio_file}: {e}")

        # Export final podcast
        print(f"\n💾 Exporting to: {output_path}")
        combined.export(
            str(output_path),
            format="mp3",
            bitrate="128k",
            tags={
                'title': self.script_path.stem,
                'artist': 'Research Automation Podcast',
                'genre': 'Podcast'
            }
        )

        # Calculate metadata
        duration_ms = len(combined)
        duration_min = duration_ms / 1000 / 60
        file_size_mb = output_path.stat().st_size / (1024 * 1024)

        return {
            'duration_ms': duration_ms,
            'duration_min': duration_min,
            'file_size_mb': file_size_mb,
            'path': output_path
        }

    def produce(self, cleanup_temp: bool = True) -> Dict:
        """Main production pipeline"""
        print(f"🎙️  PODCAST PRODUCER")
        print(f"=" * 60)
        print(f"Script: {self.script_path.name}")
        print(f"Output: {self.output_dir}\n")

        # Parse script
        print("📝 Parsing script...")
        segments = self.parse_script()
        print(f"   Found {len(segments)} segments\n")

        # Generate audio for each segment
        print("🔊 Generating audio segments...")
        audio_files = []

        for idx, (seg_type, content, metadata) in enumerate(segments):
            if seg_type == 'SPEECH':
                audio_file = self.text_to_speech(content, metadata, idx)
                if audio_file:
                    audio_files.append(audio_file)

            elif seg_type == 'PAUSE':
                audio_file = self.create_silence(float(content), idx)
                audio_files.append(audio_file)

            elif seg_type == 'MUSIC':
                print(f"  [Music cue noted: {content}]")
                # Add 3 second placeholder
                audio_file = self.create_silence(3.0, idx)
                audio_files.append(audio_file)

            elif seg_type == 'SFX':
                print(f"  [Sound effect noted: {content}]")
                # Add 1 second placeholder
                audio_file = self.create_silence(1.0, idx)
                audio_files.append(audio_file)

        # Combine all segments
        output_filename = f"{self.script_path.stem}_PODCAST.mp3"
        output_path = self.output_dir / output_filename

        metadata = self.combine_audio_segments(audio_files, output_path)

        # Cleanup temp files
        if cleanup_temp:
            print("\n🧹 Cleaning up temporary files...")
            for temp_file in self.temp_dir.glob("*.mp3"):
                temp_file.unlink()

        # Print results
        print(f"\n" + "=" * 60)
        print(f"✅ PODCAST PRODUCTION COMPLETE!")
        print(f"=" * 60)
        print(f"Output File: {metadata['path']}")
        print(f"Duration: {metadata['duration_min']:.2f} minutes")
        print(f"File Size: {metadata['file_size_mb']:.2f} MB")
        print(f"\n🎧 Your podcast is ready to publish!\n")

        return metadata


def main():
    parser = argparse.ArgumentParser(
        description='Convert podcast scripts to audio files'
    )
    parser.add_argument(
        '--script',
        required=True,
        help='Path to the markdown podcast script'
    )
    parser.add_argument(
        '--output',
        default='outputs/podcast/audio',
        help='Output directory for audio files (default: outputs/podcast/audio)'
    )
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Keep temporary audio segment files'
    )

    args = parser.parse_args()

    # Verify script exists
    if not Path(args.script).exists():
        print(f"Error: Script file not found: {args.script}")
        sys.exit(1)

    # Produce podcast
    producer = PodcastProducer(args.script, args.output)
    metadata = producer.produce(cleanup_temp=not args.keep_temp)

    return 0


if __name__ == '__main__':
    sys.exit(main())
