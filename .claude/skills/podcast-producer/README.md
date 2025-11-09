# Podcast Producer Skill

Convert markdown podcast scripts into professional audio podcasts using text-to-speech.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
sudo apt-get install ffmpeg  # or brew install ffmpeg on macOS

# Produce a podcast
python .claude/skills/podcast-producer/scripts/produce_podcast.py \
  --script "outputs/podcast/your_script.md" \
  --output "outputs/podcast/audio"
```

## Using the Skill in Claude Code

Simply ask Claude to produce a podcast from a script:

> "Can you produce a podcast from the script we just generated?"
> "Create audio for the healthcare upskilling podcast script"
> "Generate a podcast episode from the latest research"

Claude will automatically use this skill to convert your markdown podcast scripts into MP3 audio files.

## Features

✅ Multi-voice support (HOST, CO-HOST, GUEST, NARRATOR)
✅ Different accents for each speaker (US, Australian, UK English)
✅ Automatic pause insertion
✅ Music and sound effect placeholders
✅ Professional MP3 export (128kbps)
✅ Progress tracking and caching

## Script Format

```markdown
# Podcast Title

**HOST:** Welcome to the show!

**CO-HOST:** Thanks for having me.

[PAUSE: 2 seconds]

**HOST:** Let's dive into today's topic...

[MUSIC: Upbeat transition]
```

## Output

- **Format**: MP3 (128kbps, mono)
- **Location**: `outputs/podcast/audio/`
- **Naming**: `{script_name}_PODCAST.mp3`

## Documentation

- **SKILL.md** - Detailed skill instructions for Claude
- **REFERENCE.md** - Technical reference and API documentation
- **requirements.txt** - Python dependencies

## Example

Generated podcast from research script:
- **Duration**: ~7 minutes
- **File Size**: ~6 MB
- **Voices**: US English (HOST), Australian English (CO-HOST)

## Limitations

- Uses Google Text-to-Speech (free, basic quality)
- Music/SFX are placeholders (requires manual mixing)
- For professional quality, consider premium TTS services (ElevenLabs, Azure)

## Future Enhancements

- [ ] Premium TTS integration (ElevenLabs)
- [ ] Automatic music bed mixing
- [ ] Emotion/tone annotations
- [ ] Direct upload to podcast hosts

---

**Version**: 1.0
**Created**: 2025-11-09
