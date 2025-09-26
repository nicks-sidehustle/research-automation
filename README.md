# Research Automation System

A comprehensive research automation toolkit that conducts web research and generates structured reports and content for blogs, podcasts, video scripts, and ebooks.

## Features

- **Automated Research**: Conducts comprehensive web research on any topic
- **Multiple Content Formats**: Generates content for blogs, podcasts, videos, and ebooks
- **Structured Reports**: Creates detailed research reports with citations and analysis
- **Content Templates**: Professional templates for different content types
- **Export Options**: Multiple output formats (Markdown, JSON, PDF, DOCX)
- **Quality Control**: Built-in fact-checking and bias detection
- **Social Media**: Auto-generates social media content from research

## Quick Start

1. **Installation**
   ```bash
   git clone <repository-url>
   cd research-automation
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Basic Usage**
   ```bash
   # Conduct research and generate all content formats
   python src/research/research_orchestrator.py --topic "Artificial Intelligence in Healthcare" --content-type blog

   # Generate specific content format from existing research
   python src/export/content_formatter.py --report outputs/reports/ai_healthcare_20240101.json --format podcast
   ```

## Project Structure

```
research-automation/
├── src/
│   ├── research/           # Research automation modules
│   ├── analysis/          # Data analysis and synthesis
│   └── export/            # Content formatting and export
├── templates/             # Content templates
│   ├── blog/             # Blog article templates
│   ├── podcast/          # Podcast script templates
│   ├── script/           # Video script templates
│   └── ebook/            # Ebook chapter templates
├── outputs/              # Generated content
│   ├── reports/          # Research reports (JSON)
│   ├── summaries/        # Research summaries (Markdown)
│   ├── blog/             # Blog articles
│   ├── podcast/          # Podcast scripts
│   ├── video/            # Video scripts
│   ├── ebook/            # Ebook chapters
│   └── social/           # Social media content
├── config/               # Configuration files
├── docs/                 # Documentation
└── examples/             # Example outputs
```

## Usage Examples

### 1. Research Orchestrator

```bash
# Basic research
python src/research/research_orchestrator.py \
  --topic "Sustainable Energy Solutions" \
  --content-type blog \
  --depth medium \
  --audience "general public"

# Advanced research with focus areas
python src/research/research_orchestrator.py \
  --topic "Machine Learning in Finance" \
  --content-type podcast \
  --depth deep \
  --audience "professionals" \
  --focus "risk management" "algorithmic trading" "regulatory compliance"
```

### 2. Content Formatter

```bash
# Generate all content formats
python src/export/content_formatter.py \
  --report outputs/reports/ml_finance_20240101.json \
  --format all

# Generate specific format
python src/export/content_formatter.py \
  --report outputs/reports/ml_finance_20240101.json \
  --format podcast \
  --output-dir custom_output
```

## Content Types

### Blog Articles
- SEO-optimized structure
- 1,500-2,500 words
- Includes statistics and case studies
- Call-to-action sections
- Related resources

### Podcast Scripts
- 20-45 minute episodes
- Conversational tone
- Music and SFX cues
- Segment structure
- Show notes included

### Video Scripts
- 5-15 minute videos
- Visual direction cues
- Engagement prompts
- YouTube optimization
- Thumbnail suggestions

### Ebook Chapters
- 3,000-5,000 words per chapter
- Academic formatting
- Exercises and reflection questions
- Professional layout
- Citation management

### Social Media Content
- Platform-specific optimization
- Multiple post variations
- Hashtag recommendations
- Engagement strategies

## Configuration

### Research Settings (`config/research_config.json`)

```json
{
  "research_settings": {
    "default_depth": "medium",
    "max_sources_per_query": 10,
    "fact_check_enabled": true,
    "bias_detection_enabled": true
  },
  "content_types": {
    "blog": {
      "word_count_range": [1500, 2500],
      "tone": "informative",
      "seo_focus": true
    }
  }
}
```

### Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key for AI-powered research and content generation

Optional:
- `ANTHROPIC_API_KEY`: Claude API for additional AI capabilities
- `GOOGLE_AI_API_KEY`: Google AI for enhanced research
- `SERPAPI_KEY`: For web search integration
- `UNSPLASH_ACCESS_KEY`: For image suggestions

## API Integration

The system supports multiple AI providers:

- **OpenAI GPT-4**: Primary research and content generation
- **Anthropic Claude**: Alternative content generation
- **Google AI**: Research enhancement and fact-checking

## Quality Control

### Built-in Features
- Fact verification against multiple sources
- Bias detection and mitigation
- Citation tracking and management
- Readability scoring
- Plagiarism detection (optional)

### Quality Metrics
- Minimum source requirements
- Research depth validation
- Content originality checks
- Factual accuracy verification

## Output Formats

### Research Reports (JSON)
```json
{
  "metadata": {
    "topic": "Research Topic",
    "generated_at": "2024-01-01T12:00:00",
    "content_type": "blog"
  },
  "executive_summary": "...",
  "key_findings": [...],
  "export_formats": {...}
}
```

### Content Formats
- **Markdown**: Easy editing and version control
- **JSON**: Structured data for applications
- **PDF**: Professional presentation
- **DOCX**: Microsoft Word compatibility

## Workflow Examples

### 1. Blog Content Pipeline
```bash
# Research → Blog Article → Social Media
python src/research/research_orchestrator.py --topic "Remote Work Productivity" --content-type blog
python src/export/content_formatter.py --report latest_report.json --format all
```

### 2. Podcast Production Pipeline
```bash
# Research → Podcast Script → Show Notes
python src/research/research_orchestrator.py --topic "Cryptocurrency Trends" --content-type podcast --depth deep
python src/export/content_formatter.py --report latest_report.json --format podcast
```

### 3. Educational Content Pipeline
```bash
# Research → Ebook Chapter → Course Materials
python src/research/research_orchestrator.py --topic "Digital Marketing Strategies" --content-type ebook --audience professionals
python src/export/content_formatter.py --report latest_report.json --format ebook
```

## Advanced Features

### Custom Templates
Create custom content templates in the `templates/` directory using the provided template variables.

### Batch Processing
Process multiple research topics:
```bash
# Process topics from file
python scripts/batch_research.py --topics-file topics.txt --output-dir batch_output
```

### API Integration
Integrate with your existing content management systems:
```python
from src.research.research_orchestrator import ResearchOrchestrator
from src.export.content_formatter import ContentFormatter

# Use as Python modules
orchestrator = ResearchOrchestrator()
formatter = ContentFormatter()
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Adjust rate limiting in config
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **API Key Errors**: Verify keys in `.env` file
4. **Output Directory**: Ensure write permissions

### Support

- Check the `docs/` directory for detailed documentation
- Review `examples/` for sample outputs
- Submit issues via GitHub issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

[License information here]

## Roadmap

- [ ] Web interface for research management
- [ ] Integration with content management systems
- [ ] Advanced citation management
- [ ] Multi-language support
- [ ] Real-time collaboration features
- [ ] API endpoint for external integrations