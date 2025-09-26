#!/usr/bin/env python3
"""
Content Formatter - Export research data to various content formats
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import openai

class ContentFormatter:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def load_research_report(self, report_path: str) -> Dict:
        """Load research report from JSON file"""
        with open(report_path, 'r') as f:
            return json.load(f)

    def generate_blog_article(self, report: Dict, style: str = "informative") -> str:
        """Generate complete blog article from research"""
        prompt = f"""
        Create a comprehensive blog article based on this research report:

        Topic: {report['metadata']['topic']}
        Executive Summary: {report['executive_summary']}
        Key Findings: {json.dumps(report['key_findings'], indent=2)}

        Style: {style}
        Target Audience: {report['metadata']['target_audience']}

        Create a {style} blog article with:
        1. Compelling headline
        2. Engaging introduction with hook
        3. Well-structured body with subheadings
        4. Data-backed content using the research findings
        5. Practical takeaways
        6. Strong conclusion with CTA
        7. SEO-optimized for the topic

        Write in markdown format, approximately 1500-2000 words.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )

        return response.choices[0].message.content

    def generate_podcast_script(self, report: Dict, hosts: List[str] = ["Host"]) -> str:
        """Generate podcast script from research"""
        hosts_str = ", ".join(hosts)

        prompt = f"""
        Create a detailed podcast script based on this research:

        Topic: {report['metadata']['topic']}
        Research Data: {json.dumps(report, indent=2)}

        Hosts: {hosts_str}
        Target Length: 20-30 minutes
        Style: Conversational, informative, engaging

        Include:
        1. Show intro with hook
        2. Topic introduction and why it matters
        3. Main segments covering key findings
        4. Discussion between hosts
        5. Practical applications
        6. Listener Q&A segment (simulated)
        7. Key takeaways
        8. Show outro with CTA

        Format with clear speaker labels and timing notes.
        Include [MUSIC], [SFX], and [PAUSE] cues where appropriate.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content

    def generate_video_script(self, report: Dict, duration: int = 600) -> str:
        """Generate video script from research"""
        prompt = f"""
        Create a video script for a {duration}-second video based on this research:

        Topic: {report['metadata']['topic']}
        Research Summary: {report['executive_summary']}
        Key Points: {json.dumps(report['key_findings'], indent=2)}

        Video Style: Educational, engaging, YouTube-optimized
        Target Audience: {report['metadata']['target_audience']}

        Include:
        1. Attention-grabbing hook (first 5 seconds)
        2. Clear problem/topic introduction
        3. Main content points with visual cues
        4. Examples and case studies
        5. Call-to-action
        6. End screen suggestions

        Format with:
        - Timecodes [00:00]
        - Visual direction [SHOW: description]
        - Audio cues [MUSIC], [SFX]
        - Text overlay suggestions [TEXT: "Key Point"]

        Keep language conversational and include engagement prompts.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content

    def generate_ebook_chapter(self, report: Dict, chapter_number: int = 1) -> str:
        """Generate ebook chapter from research"""
        prompt = f"""
        Create Chapter {chapter_number} of an ebook based on this research:

        Chapter Topic: {report['metadata']['topic']}
        Research Data: {json.dumps(report, indent=2)}

        Ebook Style: Comprehensive, authoritative, practical
        Target Audience: {report['metadata']['target_audience']}

        Create a complete chapter with:
        1. Chapter introduction
        2. Learning objectives
        3. Detailed content sections with subheadings
        4. Case studies and examples
        5. Key takeaways box
        6. Action items
        7. Chapter summary
        8. Transition to next chapter

        Length: 3000-4000 words
        Format: Professional, well-structured markdown
        Include practical exercises and reflection questions.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content

    def generate_social_media_content(self, report: Dict) -> Dict[str, List[str]]:
        """Generate social media content from research"""
        prompt = f"""
        Create social media content based on this research:

        Topic: {report['metadata']['topic']}
        Key Findings: {json.dumps(report['key_findings'][:5], indent=2)}

        Generate content for multiple platforms:

        Return JSON with:
        - twitter: Array of 5 tweet-length posts (280 chars max)
        - linkedin: Array of 3 professional posts (1300 chars max)
        - instagram: Array of 3 posts with caption and hashtags
        - youtube_shorts: Array of 3 short video concepts (60 seconds)

        Make content engaging, informative, and platform-appropriate.
        Include relevant hashtags and call-to-actions.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse social media content"}

    def export_all_formats(self, report_path: str, output_dir: str = "outputs"):
        """Export research to all content formats"""
        report = self.load_research_report(report_path)
        topic = report['metadata']['topic'].replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create output directories
        formats = ['blog', 'podcast', 'video', 'ebook', 'social']
        for fmt in formats:
            os.makedirs(f"{output_dir}/{fmt}", exist_ok=True)

        # Generate all formats
        print("Generating blog article...")
        blog_content = self.generate_blog_article(report)
        with open(f"{output_dir}/blog/{topic}_{timestamp}.md", 'w') as f:
            f.write(blog_content)

        print("Generating podcast script...")
        podcast_script = self.generate_podcast_script(report)
        with open(f"{output_dir}/podcast/{topic}_{timestamp}.md", 'w') as f:
            f.write(podcast_script)

        print("Generating video script...")
        video_script = self.generate_video_script(report)
        with open(f"{output_dir}/video/{topic}_{timestamp}.md", 'w') as f:
            f.write(video_script)

        print("Generating ebook chapter...")
        ebook_chapter = self.generate_ebook_chapter(report)
        with open(f"{output_dir}/ebook/{topic}_{timestamp}.md", 'w') as f:
            f.write(ebook_chapter)

        print("Generating social media content...")
        social_content = self.generate_social_media_content(report)
        with open(f"{output_dir}/social/{topic}_{timestamp}.json", 'w') as f:
            json.dump(social_content, f, indent=2)

        print(f"All formats exported to {output_dir}/")

# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Content Formatter')
    parser.add_argument('--report', required=True, help='Path to research report JSON')
    parser.add_argument('--format', choices=['blog', 'podcast', 'video', 'ebook', 'social', 'all'],
                       default='all', help='Content format to generate')
    parser.add_argument('--output-dir', default='outputs', help='Output directory')

    args = parser.parse_args()

    formatter = ContentFormatter()

    if args.format == 'all':
        formatter.export_all_formats(args.report, args.output_dir)
    else:
        report = formatter.load_research_report(args.report)

        if args.format == 'blog':
            content = formatter.generate_blog_article(report)
        elif args.format == 'podcast':
            content = formatter.generate_podcast_script(report)
        elif args.format == 'video':
            content = formatter.generate_video_script(report)
        elif args.format == 'ebook':
            content = formatter.generate_ebook_chapter(report)
        elif args.format == 'social':
            content = json.dumps(formatter.generate_social_media_content(report), indent=2)

        print(content)