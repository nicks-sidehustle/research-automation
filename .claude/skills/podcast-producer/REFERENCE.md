# Podcast Producer - Technical Reference

## Overview

The Podcast Producer skill converts markdown-formatted podcast scripts into professional MP3 audio files using text-to-speech technology.

## Dependencies

### Required Python Packages

```bash
pip install gTTS pydub
```

### System Requirements

- **ffmpeg** - Required for audio processing
  ```bash
  # Ubuntu/Debian
  sudo apt-get install ffmpeg

  # macOS
  brew install ffmpeg
  ```

## Architecture

### Components

1. **Script Parser** - Extracts structured content from markdown
2. **TTS Engine** - Converts text to speech (using Google TTS)
3. **Audio Processor** - Combines segments and exports MP3
4. **Metadata Generator** - Creates episode information

### Processing Pipeline

```
Markdown Script → Parse Segments → Generate Audio → Combine Segments → Export MP3
```

## Script Format Specification

### Speaker Dialogue

```markdown
**SPEAKER_NAME**: Dialogue text here
```

Supported speaker roles:
- `HOST` - Main podcast host (US English)
- `GUEST` - Guest speaker (UK English)
- `NARRATOR` - Voiceover narration (US English)
- Custom speaker names (default voice)

### Control Tags

#### Music Cues
```markdown
[MUSIC: Theme music - upbeat and energetic]
```
Currently adds 3-second placeholder. For actual music, manually mix audio files.

#### Pauses
```markdown
[PAUSE: 2 seconds]
[PAUSE: 1.5 seconds]
```
Creates silent segments for natural breaks.

#### Sound Effects
```markdown
[SFX: Door closing]
[SFX: Phone ringing]
```
Currently adds 1-second placeholder. For actual effects, manually mix audio files.

## Voice Configuration

Edit `VOICE_SETTINGS` in `produce_podcast.py` to customize voices:

```python
VOICE_SETTINGS = {
    'HOST': {
        'lang': 'en',      # Language code
        'tld': 'com',      # TLD for accent (com=US, co.uk=UK, etc.)
        'slow': False      # Slower speech rate
    }
}
```

Available TLDs for English:
- `com` - United States
- `co.uk` - United Kingdom
- `com.au` - Australia
- `ca` - Canada
- `co.in` - India

## Output Specifications

### Audio Format
- **Format**: MP3
- **Bitrate**: 128 kbps
- **Sample Rate**: 24 kHz (gTTS default)
- **Channels**: Mono

### File Naming
Pattern: `{script_name}_PODCAST.mp3`

Example: `Most_valuable_upskill_training_..._20251109_005103_PODCAST.mp3`

### Metadata Tags
- Title: Script filename
- Artist: "Research Automation Podcast"
- Genre: "Podcast"

## Performance

### Processing Time

Typical performance on modern hardware:
- **Short scripts** (5-10 min): 30-60 seconds
- **Medium scripts** (20-30 min): 2-4 minutes
- **Long scripts** (45-60 min): 5-10 minutes

### File Sizes

Approximate sizes at 128 kbps:
- **10 minutes**: ~10 MB
- **30 minutes**: ~30 MB
- **60 minutes**: ~60 MB

## Advanced Usage

### Batch Processing

Process multiple scripts:

```bash
for script in outputs/podcast/*.md; do
    python .claude/skills/podcast-producer/scripts/produce_podcast.py \
        --script "$script" \
        --output "outputs/podcast/audio"
done
```

### Custom Voice Engines

The script can be extended to use other TTS engines:

#### ElevenLabs (Premium)
High-quality, realistic voices with emotion control.

```python
from elevenlabs import generate, save

audio = generate(
    text=text,
    voice="Josh",  # Premium voice
    model="eleven_monolingual_v1"
)
save(audio, audio_file)
```

#### Azure Cognitive Services (Premium)
Microsoft's neural TTS with SSML support.

```python
import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
result = synthesizer.speak_text_async(text).get()
```

#### pyttsx3 (Offline)
Offline TTS using system voices (lower quality).

```python
import pyttsx3

engine = pyttsx3.init()
engine.save_to_file(text, str(audio_file))
engine.runAndWait()
```

### Audio Post-Processing

Enhance audio quality with pydub effects:

```python
from pydub.effects import normalize, compress_dynamic_range

# Normalize volume
audio = normalize(audio)

# Compress dynamic range
audio = compress_dynamic_range(audio)

# Fade in/out
audio = audio.fade_in(2000).fade_out(2000)
```

## Troubleshooting

### Common Issues

#### 1. "gTTS error: Connection refused"
**Cause**: Network connectivity issue or rate limiting
**Solution**:
- Check internet connection
- Add delay between TTS requests
- Use cached segments (automatic)

#### 2. "ffmpeg not found"
**Cause**: pydub requires ffmpeg for audio processing
**Solution**:
```bash
sudo apt-get install ffmpeg
```

#### 3. "Poor audio quality"
**Cause**: gTTS uses basic TTS engine
**Solution**:
- Use premium TTS service (ElevenLabs, Azure, Google Cloud)
- Increase bitrate in export settings
- Apply audio normalization

#### 4. "Voices sound the same"
**Cause**: Limited voice variation in gTTS
**Solution**:
- Use different TLD settings
- Implement premium TTS with multiple voices
- Manually edit with voice actors

### Debug Mode

Keep temporary files for debugging:

```bash
python .claude/skills/podcast-producer/scripts/produce_podcast.py \
    --script "script.md" \
    --keep-temp
```

Temp files location: `outputs/podcast/audio/temp/`

## Limitations

### Current Limitations

1. **Voice Quality**: gTTS provides basic quality; premium services recommended for professional use
2. **Music/SFX**: Placeholders only; requires manual audio mixing
3. **Emotion**: Limited emotional expression in speech
4. **Pacing**: No dynamic pacing control
5. **Accents**: Limited accent variety per speaker

### Recommended for Production

For professional podcast production, consider:

1. **Premium TTS**: ElevenLabs, Azure Neural TTS, Google Cloud TTS
2. **Audio Editing**: Adobe Audition, Audacity, Reaper
3. **Music Library**: Epidemic Sound, AudioJungle, Artlist
4. **Hosting**: Buzzsprout, Libsyn, Anchor

## Future Enhancements

Planned features:

- [ ] Multi-voice premium TTS integration (ElevenLabs)
- [ ] Automatic music bed mixing
- [ ] Sound effect library integration
- [ ] SSML support for advanced control
- [ ] Emotion/tone annotations
- [ ] Variable speaking rates per segment
- [ ] Background noise/ambience
- [ ] Direct upload to podcast hosts
- [ ] Transcription generation
- [ ] Chapter markers for long episodes

## API Reference

### PodcastProducer Class

```python
class PodcastProducer:
    def __init__(self, script_path: str, output_dir: str)
    def parse_script(self) -> List[Tuple[str, str, str]]
    def text_to_speech(self, text: str, speaker: str, segment_id: int) -> Path
    def create_silence(self, duration_seconds: float, segment_id: int) -> Path
    def combine_audio_segments(self, audio_files: List[Path], output_path: Path) -> Dict
    def produce(self, cleanup_temp: bool = True) -> Dict
```

### Return Metadata

```python
{
    'duration_ms': int,        # Duration in milliseconds
    'duration_min': float,     # Duration in minutes
    'file_size_mb': float,     # File size in megabytes
    'path': Path               # Path to output file
}
```

## License

This skill is part of the Research Automation project and follows the same license.

## Support

For issues or questions:
1. Check this reference documentation
2. Review the SKILL.md for usage examples
3. Examine script format in existing podcast scripts
4. Test with a minimal script first

## Version History

- **v1.0** (2025-11-09): Initial release
  - Basic TTS conversion
  - Multiple speaker support
  - Pause and placeholder support
  - MP3 export
