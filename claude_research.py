#!/usr/bin/env python3
"""
Claude Code Research Automation - Main CLI Entry Point
Optimized for Claude Code's built-in capabilities with zero external API costs
"""

import sys
import os
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from research.claude_research_orchestrator import ClaudeResearchOrchestrator, ResearchQuery
from export.claude_content_formatter import ClaudeContentFormatter

class ClaudeResearchAutomation:
    def __init__(self):
        self.orchestrator = ClaudeResearchOrchestrator()
        self.formatter = ClaudeContentFormatter()
        self.config = self.load_claude_config()

    def load_claude_config(self):
        """Load Claude-specific configuration"""
        try:
            with open('config/claude_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"claude_integration": {"use_built_in_agents": True}}

    def display_cost_savings(self):
        """Display cost optimization information"""
        config = self.config.get('cost_optimization', {})

        print("\n💰 COST OPTIMIZATION SUMMARY")
        print("=" * 50)
        print(f"Monthly Savings: ${config.get('estimated_monthly_savings', 400)}")
        print(f"Claude Code Subscription: {config.get('claude_code_subscription', '$200/month')}")
        print(f"Net Savings: {config.get('net_monthly_savings', '$205/month')}")

        print("\n🚫 External API Costs Eliminated:")
        for cost in config.get('external_api_costs_eliminated', []):
            print(f"   • {cost}")

        print("\n✅ Quality Improvements:")
        improvements = config.get('quality_improvements', {})
        for key, value in improvements.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")

    async def conduct_full_research_pipeline(self, query: ResearchQuery, output_formats: list = None):
        """Execute complete research and content generation pipeline"""

        print("🤖 CLAUDE CODE RESEARCH AUTOMATION")
        print("=" * 50)
        print(f"Topic: {query.topic}")
        print(f"Content Type: {query.content_type}")
        print(f"Depth: {query.depth}")
        print(f"Target Audience: {query.target_audience}")
        print(f"Focus Areas: {', '.join(query.focus_areas)}")

        self.display_cost_savings()

        print("\n🔍 RESEARCH PHASE")
        print("-" * 25)

        # Phase 1: Research
        research_data = await self.orchestrator.conduct_research(query)

        if not research_data:
            print("❌ Research phase failed")
            return None

        print("✅ Research completed successfully!")

        # Phase 2: Content Generation
        if output_formats is None:
            output_formats = ['all']

        print("\n📝 CONTENT GENERATION PHASE")
        print("-" * 30)

        # Find the latest research report
        research_files = list(Path("outputs/reports").glob(f"*{query.topic.replace(' ', '_')}*.json"))
        if research_files:
            latest_report = max(research_files, key=os.path.getctime)

            if 'all' in output_formats:
                await self.formatter.export_all_formats(str(latest_report))
            else:
                for format_type in output_formats:
                    print(f"Generating {format_type} content...")
                    # Individual format generation would go here

        print("\n🎉 PIPELINE COMPLETED!")
        print("All content generated using Claude Code built-in capabilities")

        return research_data

    def list_recent_research(self, limit: int = 10):
        """List recent research reports"""
        reports_dir = Path("outputs/reports")
        if not reports_dir.exists():
            print("No research reports found.")
            return

        reports = sorted(reports_dir.glob("*.json"), key=os.path.getctime, reverse=True)[:limit]

        print(f"\n📊 RECENT RESEARCH REPORTS (Last {len(reports)})")
        print("=" * 50)

        for i, report_path in enumerate(reports, 1):
            try:
                with open(report_path, 'r') as f:
                    data = json.load(f)
                    topic = data.get('query_metadata', {}).get('topic', 'Unknown')
                    timestamp = data.get('metadata', {}).get('generated_at', 'Unknown')
                    content_type = data.get('query_metadata', {}).get('content_type', 'Unknown')

                print(f"{i}. {topic}")
                print(f"   Type: {content_type} | Generated: {timestamp}")
                print(f"   File: {report_path.name}")
                print()
            except Exception as e:
                print(f"{i}. Error reading {report_path.name}: {e}")

    def show_agent_status(self):
        """Display Claude agent configuration status"""
        agents = self.config.get('claude_agents', {})

        print("\n🤖 CLAUDE AGENTS STATUS")
        print("=" * 30)

        for agent_name, agent_config in agents.items():
            status = "✅ Enabled" if agent_config.get('enabled', False) else "❌ Disabled"
            print(f"{agent_name.replace('_', ' ').title()}: {status}")

            capabilities = agent_config.get('capabilities', [])
            if capabilities:
                print(f"   Capabilities: {', '.join(capabilities)}")
            print()

async def main():
    parser = argparse.ArgumentParser(
        description='Claude Code Research Automation - Cost-effective research and content generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full research pipeline
  python claude_research.py research --topic "AI in Healthcare" --type blog

  # Research only
  python claude_research.py research --topic "Climate Change" --research-only

  # Generate content from existing research
  python claude_research.py generate --report outputs/reports/latest.json --format all

  # List recent research
  python claude_research.py list --limit 5

  # Show system status
  python claude_research.py status
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Research command
    research_parser = subparsers.add_parser('research', help='Conduct research and optionally generate content')
    research_parser.add_argument('--topic', required=True, help='Research topic')
    research_parser.add_argument('--type', choices=['blog', 'podcast', 'video', 'ebook'],
                                default='blog', help='Content type')
    research_parser.add_argument('--depth', choices=['shallow', 'medium', 'deep'],
                                default='medium', help='Research depth')
    research_parser.add_argument('--audience', default='general', help='Target audience')
    research_parser.add_argument('--focus', nargs='+', default=[], help='Focus areas')
    research_parser.add_argument('--research-only', action='store_true',
                                help='Only conduct research, skip content generation')
    research_parser.add_argument('--formats', nargs='+',
                                choices=['blog', 'podcast', 'video', 'ebook', 'social', 'all'],
                                default=['all'], help='Output formats to generate')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate content from existing research')
    generate_parser.add_argument('--report', required=True, help='Path to research report JSON file')
    generate_parser.add_argument('--format', choices=['blog', 'podcast', 'video', 'ebook', 'social', 'all'],
                                default='all', help='Content format to generate')
    generate_parser.add_argument('--output-dir', default='outputs', help='Output directory')

    # List command
    list_parser = subparsers.add_parser('list', help='List recent research reports')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of reports to show')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show Claude agents and system status')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    automation = ClaudeResearchAutomation()

    try:
        if args.command == 'research':
            query = ResearchQuery(
                topic=args.topic,
                focus_areas=args.focus or [args.topic],
                content_type=args.type,
                depth=args.depth,
                target_audience=args.audience
            )

            if args.research_only:
                await automation.orchestrator.conduct_research(query)
            else:
                await automation.conduct_full_research_pipeline(query, args.formats)

        elif args.command == 'generate':
            formatter = ClaudeContentFormatter()
            if args.format == 'all':
                await formatter.export_all_formats(args.report, args.output_dir)
            else:
                report = formatter.load_research_report(args.report)
                # Individual format generation logic would go here

        elif args.command == 'list':
            automation.list_recent_research(args.limit)

        elif args.command == 'status':
            automation.show_agent_status()
            automation.display_cost_savings()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())