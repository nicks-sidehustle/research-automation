---
name: podcast-producer
description: Convert podcast scripts to professional audio podcasts using text-to-speech. Use when the user wants to generate audio from markdown podcast scripts, create voice narration, or produce actual podcast episodes from written content.
---

# Podcast Producer

This skill converts written podcast scripts (markdown format) into professional audio podcast episodes using text-to-speech technology.

## When to Use This Skill

- User wants to convert a podcast script to audio
- User asks to "produce", "generate", or "create" a podcast from a script
- User wants to hear what their podcast script sounds like
- User needs audio files for podcast distribution

## Capabilities

1. **Script Processing**: Reads and parses markdown podcast scripts
2. **Text-to-Speech Conversion**: Converts script text to natural-sounding speech
3. **Multi-Voice Support**: Uses different voices for hosts, guests, and narrators
4. **Audio Editing**: Combines segments, adds pauses, and optimizes audio quality
5. **Music Integration**: Adds intro/outro music and transitions where specified
6. **Export Formats**: Produces MP3 files ready for podcast distribution

## Instructions

### Step 1: Identify the Script
- Locate the podcast script file (usually in `outputs/podcast/` directory)
- Verify the script format is markdown with clear speaker labels
- Extract the script title and timestamp for naming

### Step 2: Install Required Dependencies
Check if text-to-speech libraries are installed. If not, install:
```bash
pip install gTTS pydub
```

Also check for ffmpeg (required for audio processing):
```bash
which ffmpeg || echo "Please install ffmpeg: sudo apt-get install ffmpeg"
```

### Step 3: Generate the Podcast
Use the podcast production script to convert the script to audio:
```bash
python .claude/skills/podcast-producer/scripts/produce_podcast.py \
  --script "path/to/script.md" \
  --output "outputs/podcast/audio/" \
  --format mp3
```

### Step 4: Verify Output
- Check that the audio file was created
- Report the file location, duration, and size to the user
- Offer to play a sample or show audio metadata

## Script Format Requirements

The podcast script should follow this structure:
```markdown
# Podcast Title

[MUSIC: Theme music - upbeat and energetic]

**HOST**: Welcome to the show...

**GUEST**: Thanks for having me...

[PAUSE: 2 seconds]

**NARRATOR**: This episode is brought to you by...
```

## Supported Tags

- `[MUSIC: description]` - Music cues (noted but requires manual audio files)
- `[PAUSE: X seconds]` - Add silence between segments
- `[SFX: description]` - Sound effects (noted in output)
- `**SPEAKER:**` - Different speakers get different voice characteristics

## Output

Creates:
- MP3 audio file (podcast-ready format)
- Metadata file with episode information
- Production log with timing and voice details

## Limitations

- Music and sound effects are noted but require separate audio files to be mixed in
- Voice variety depends on available TTS engines
- Long scripts may take several minutes to process
- Best quality requires premium TTS services (can integrate with APIs)

## Examples

**User**: "Can you produce a podcast from the script we just generated?"

**Action**:
1. Find the most recent podcast script in outputs/podcast/
2. Run the podcast producer
3. Generate MP3 file
4. Report completion with file details

**User**: "Create audio for the healthcare upskilling podcast script"

**Action**:
1. Locate the specific script about healthcare upskilling
2. Process with appropriate voice settings
3. Export professional-quality audio
4. Provide download link or file path

## Advanced Features

- **Voice Selection**: Can use different TTS engines (gTTS, pyttsx3, edge-tts, or API-based)
- **Speed Control**: Adjust speaking rate for better listening experience
- **Quality Levels**: Choose between fast/draft mode and high-quality production
- **Batch Processing**: Convert multiple scripts in one operation

## Troubleshooting

- **No audio output**: Check ffmpeg installation and file permissions
- **Poor quality**: Consider using premium TTS APIs (ElevenLabs, Google Cloud, Azure)
- **Missing voices**: Install additional TTS engines or voice packs
- **Large files**: Adjust compression settings or split long episodes

## Future Enhancements

- Integration with ElevenLabs for ultra-realistic voices
- Automatic music library integration
- Multi-track editing with automated mixing
- Direct upload to podcast hosting platforms
