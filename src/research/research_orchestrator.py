#!/usr/bin/env python3
"""
Research Orchestrator - Main research automation system
Conducts web research and generates structured reports for content projects
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import openai
from dataclasses import dataclass

@dataclass
class ResearchQuery:
    topic: str
    focus_areas: List[str]
    content_type: str  # blog, podcast, script, ebook
    depth: str  # shallow, medium, deep
    target_audience: str

class ResearchOrchestrator:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load research configuration"""
        try:
            with open('config/research_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "default_depth": "medium",
                "max_sources": 10,
                "output_formats": ["markdown", "json"]
            }

    async def conduct_research(self, query: ResearchQuery) -> Dict:
        """Main research orchestration method"""
        print(f"Starting research on: {query.topic}")

        # Generate research plan
        research_plan = await self.generate_research_plan(query)

        # Conduct web research
        research_data = await self.gather_research_data(research_plan)

        # Analyze and synthesize findings
        synthesis = await self.synthesize_findings(research_data, query)

        # Generate structured report
        report = await self.generate_report(synthesis, query)

        # Save outputs
        self.save_research_outputs(report, query)

        return report

    async def generate_research_plan(self, query: ResearchQuery) -> Dict:
        """Generate a structured research plan"""
        prompt = f"""
        Create a comprehensive research plan for the topic: "{query.topic}"

        Content type: {query.content_type}
        Focus areas: {', '.join(query.focus_areas)}
        Research depth: {query.depth}
        Target audience: {query.target_audience}

        Generate a JSON research plan with:
        1. Key research questions (5-10)
        2. Search strategies and keywords
        3. Source types to prioritize
        4. Information gaps to address
        5. Fact-checking priorities

        Return only valid JSON.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse research plan"}

    async def gather_research_data(self, research_plan: Dict) -> Dict:
        """Gather research data from various sources"""
        # This would integrate with web search APIs, databases, etc.
        # For now, using AI to simulate comprehensive research

        search_queries = research_plan.get('search_strategies', {}).get('keywords', [])

        research_data = {
            "sources": [],
            "key_findings": [],
            "statistics": [],
            "expert_quotes": [],
            "contradictions": []
        }

        # Simulate research gathering - in production this would use actual APIs
        for query in search_queries[:5]:  # Limit for demo
            data_point = await self.simulate_research_query(query)
            research_data["sources"].extend(data_point.get("sources", []))
            research_data["key_findings"].extend(data_point.get("findings", []))

        return research_data

    async def simulate_research_query(self, query: str) -> Dict:
        """Simulate web research for a specific query"""
        prompt = f"""
        Conduct research on: "{query}"

        Provide realistic research findings in JSON format with:
        - sources: Array of credible source citations
        - findings: Key facts and insights discovered
        - statistics: Relevant numerical data points
        - trends: Current trends related to this query

        Make the data realistic and cite actual sources where possible.
        Return only valid JSON.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"sources": [], "findings": []}

    async def synthesize_findings(self, research_data: Dict, query: ResearchQuery) -> Dict:
        """Analyze and synthesize research findings"""
        prompt = f"""
        Analyze and synthesize research findings for: "{query.topic}"

        Research Data: {json.dumps(research_data, indent=2)}

        Content Type: {query.content_type}
        Target Audience: {query.target_audience}

        Create a synthesis with:
        1. Executive summary
        2. Key themes and patterns
        3. Supporting evidence
        4. Conflicting viewpoints
        5. Gaps in knowledge
        6. Actionable insights
        7. Content recommendations specific to {query.content_type}

        Return as structured JSON.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"error": "Failed to synthesize findings"}

    async def generate_report(self, synthesis: Dict, query: ResearchQuery) -> Dict:
        """Generate final structured research report"""
        timestamp = datetime.now().isoformat()

        report = {
            "metadata": {
                "topic": query.topic,
                "content_type": query.content_type,
                "research_depth": query.depth,
                "target_audience": query.target_audience,
                "generated_at": timestamp,
                "focus_areas": query.focus_areas
            },
            "executive_summary": synthesis.get("executive_summary", ""),
            "key_findings": synthesis.get("key_themes", []),
            "supporting_evidence": synthesis.get("supporting_evidence", []),
            "content_recommendations": synthesis.get("content_recommendations", {}),
            "source_bibliography": [],
            "export_formats": {
                "blog_ready": self.format_for_blog(synthesis, query),
                "podcast_script": self.format_for_podcast(synthesis, query),
                "video_script": self.format_for_video(synthesis, query),
                "ebook_chapter": self.format_for_ebook(synthesis, query)
            }
        }

        return report

    def format_for_blog(self, synthesis: Dict, query: ResearchQuery) -> Dict:
        """Format research for blog article"""
        return {
            "title": f"Complete Guide to {query.topic}",
            "subtitle": synthesis.get("executive_summary", "")[:200],
            "outline": synthesis.get("key_themes", []),
            "call_to_action": f"Learn more about {query.topic}",
            "seo_keywords": query.focus_areas
        }

    def format_for_podcast(self, synthesis: Dict, query: ResearchQuery) -> Dict:
        """Format research for podcast script"""
        return {
            "episode_title": f"Deep Dive: {query.topic}",
            "intro_hook": synthesis.get("executive_summary", "")[:150],
            "main_segments": synthesis.get("key_themes", []),
            "discussion_points": synthesis.get("actionable_insights", []),
            "outro_summary": "Key takeaways from today's research"
        }

    def format_for_video(self, synthesis: Dict, query: ResearchQuery) -> Dict:
        """Format research for video script"""
        return {
            "video_title": f"Everything You Need to Know About {query.topic}",
            "thumbnail_text": query.topic,
            "script_segments": synthesis.get("key_themes", []),
            "visual_cues": ["charts", "infographics", "talking head"],
            "call_to_action": "Subscribe for more research deep dives"
        }

    def format_for_ebook(self, synthesis: Dict, query: ResearchQuery) -> Dict:
        """Format research for ebook chapter"""
        return {
            "chapter_title": query.topic,
            "chapter_summary": synthesis.get("executive_summary", ""),
            "sections": synthesis.get("key_themes", []),
            "case_studies": synthesis.get("supporting_evidence", []),
            "chapter_conclusion": synthesis.get("actionable_insights", [])
        }

    def save_research_outputs(self, report: Dict, query: ResearchQuery):
        """Save research outputs in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_safe = query.topic.replace(" ", "_").replace("/", "_")

        # Save JSON report
        json_path = f"outputs/reports/{topic_safe}_{timestamp}.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Save markdown summary
        md_path = f"outputs/summaries/{topic_safe}_{timestamp}.md"
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, 'w') as f:
            f.write(self.generate_markdown_summary(report))

        print(f"Research saved to: {json_path}")
        print(f"Summary saved to: {md_path}")

    def generate_markdown_summary(self, report: Dict) -> str:
        """Generate markdown summary of research"""
        md = f"""# Research Report: {report['metadata']['topic']}

**Generated:** {report['metadata']['generated_at']}
**Content Type:** {report['metadata']['content_type']}
**Target Audience:** {report['metadata']['target_audience']}

## Executive Summary
{report['executive_summary']}

## Key Findings
"""
        for finding in report['key_findings']:
            md += f"- {finding}\n"

        md += "\n## Content Recommendations\n"
        for content_type, recommendations in report['export_formats'].items():
            md += f"\n### {content_type.replace('_', ' ').title()}\n"
            if isinstance(recommendations, dict):
                for key, value in recommendations.items():
                    md += f"- **{key}:** {value}\n"

        return md

# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Research Orchestrator')
    parser.add_argument('--topic', required=True, help='Research topic')
    parser.add_argument('--content-type', choices=['blog', 'podcast', 'script', 'ebook'],
                       default='blog', help='Target content type')
    parser.add_argument('--depth', choices=['shallow', 'medium', 'deep'],
                       default='medium', help='Research depth')
    parser.add_argument('--audience', default='general', help='Target audience')
    parser.add_argument('--focus', nargs='+', default=[], help='Focus areas')

    args = parser.parse_args()

    query = ResearchQuery(
        topic=args.topic,
        focus_areas=args.focus or [args.topic],
        content_type=args.content_type,
        depth=args.depth,
        target_audience=args.audience
    )

    orchestrator = ResearchOrchestrator()

    # Run research
    async def main():
        await orchestrator.conduct_research(query)

    asyncio.run(main())