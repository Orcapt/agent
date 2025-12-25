"""
Interactive CLI for SEO Expert Agent
Provides a user-friendly terminal interface to interact with the SEO agent.
"""

import os
import sys
from seo_agent import SEOExpertAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print("🔍 SEO EXPERT AGENT - Interactive Mode")
    print("="*70)
    print("Type 'help' for available commands or 'exit' to quit\n")


def print_help():
    """Print help menu."""
    print("\n" + "-"*70)
    print("AVAILABLE COMMANDS:")
    print("-"*70)
    print("1. keyword <keyword1,keyword2,...> [target_audience]")
    print("   Example: keyword python,web development developers")
    print("   Analyze keywords for SEO")
    print()
    print("2. audit <content> [target_keyword] [url]")
    print("   Example: audit 'Your content here' python-web-dev https://example.com")
    print("   Audit content for SEO")
    print()
    print("3. meta <title> <content> [target_keyword]")
    print("   Example: meta 'Page Title' 'Page content...' keyword")
    print("   Generate meta descriptions")
    print()
    print("4. title <content> <target_keyword>")
    print("   Example: title 'Your content...' target-keyword")
    print("   Generate title tag suggestions")
    print()
    print("5. competitor <url> [focus_areas]")
    print("   Example: competitor https://example.com keywords,content")
    print("   Analyze competitor SEO")
    print()
    print("6. report <url> [type]")
    print("   Example: report https://example.com comprehensive")
    print("   Generate SEO report (type: comprehensive/quick/technical)")
    print()
    print("7. local <business_name> <location> <business_type>")
    print("   Example: local 'Joe Pizza' 'New York, NY' Restaurant")
    print("   Get local SEO recommendations")
    print()
    print("8. ask <question>")
    print("   Example: ask What is keyword density?")
    print("   Ask any SEO question")
    print()
    print("9. help - Show this help menu")
    print("10. exit - Exit the program")
    print("-"*70 + "\n")


def parse_keyword_command(args):
    """Parse keyword analysis command."""
    if len(args) < 1:
        print("❌ Error: Please provide keywords separated by commas")
        return None
    
    keywords = [k.strip() for k in args[0].split(',')]
    target_audience = ' '.join(args[1:]) if len(args) > 1 else None
    
    return {
        'keywords': keywords,
        'target_audience': target_audience
    }


def parse_audit_command(args):
    """Parse content audit command."""
    if len(args) < 1:
        print("❌ Error: Please provide content to audit")
        return None
    
    content = args[0]
    target_keyword = args[1] if len(args) > 1 else None
    url = args[2] if len(args) > 2 else None
    
    return {
        'content': content,
        'target_keyword': target_keyword,
        'url': url
    }


def parse_meta_command(args):
    """Parse meta description command."""
    if len(args) < 2:
        print("❌ Error: Please provide title and content")
        return None
    
    title = args[0]
    content = args[1]
    target_keyword = args[2] if len(args) > 2 else None
    
    return {
        'title': title,
        'content': content,
        'target_keyword': target_keyword
    }


def parse_title_command(args):
    """Parse title tag command."""
    if len(args) < 2:
        print("❌ Error: Please provide content and target keyword")
        return None
    
    content = args[0]
    target_keyword = args[1]
    
    return {
        'content': content,
        'target_keyword': target_keyword
    }


def parse_competitor_command(args):
    """Parse competitor analysis command."""
    if len(args) < 1:
        print("❌ Error: Please provide competitor URL")
        return None
    
    url = args[0]
    focus_areas = args[1].split(',') if len(args) > 1 else None
    
    return {
        'url': url,
        'focus_areas': focus_areas
    }


def parse_report_command(args):
    """Parse SEO report command."""
    if len(args) < 1:
        print("❌ Error: Please provide website URL")
        return None
    
    url = args[0]
    analysis_type = args[1] if len(args) > 1 else 'comprehensive'
    
    return {
        'url': url,
        'analysis_type': analysis_type
    }


def parse_local_command(args):
    """Parse local SEO command."""
    if len(args) < 3:
        print("❌ Error: Please provide business_name, location, and business_type")
        return None
    
    business_name = args[0]
    location = args[1]
    business_type = ' '.join(args[2:])
    
    return {
        'business_name': business_name,
        'location': location,
        'business_type': business_type
    }


def parse_ask_command(args):
    """Parse ask command."""
    if len(args) < 1:
        print("❌ Error: Please provide a question")
        return None
    
    return ' '.join(args)


def handle_command(agent, command, args):
    """Handle user commands."""
    try:
        if command == 'keyword':
            params = parse_keyword_command(args)
            if params:
                print("\n🔍 Analyzing keywords...")
                result = agent.analyze_keywords(**params)
                print(f"\n📊 Keyword Analysis:\n{result['analysis']}\n")
        
        elif command == 'audit':
            params = parse_audit_command(args)
            if params:
                print("\n🔍 Auditing content...")
                result = agent.audit_content(**params)
                print(f"\n📋 Audit Results:\n{result['audit_results']}\n")
        
        elif command == 'meta':
            params = parse_meta_command(args)
            if params:
                print("\n🔍 Generating meta descriptions...")
                result = agent.generate_meta_description(**params)
                print(f"\n📝 Meta Descriptions:\n{result['meta_descriptions']}\n")
        
        elif command == 'title':
            params = parse_title_command(args)
            if params:
                print("\n🔍 Generating title tags...")
                result = agent.suggest_title_tags(**params)
                print(f"\n📌 Title Suggestions:\n{result['title_suggestions']}\n")
        
        elif command == 'competitor':
            params = parse_competitor_command(args)
            if params:
                print("\n🔍 Analyzing competitor...")
                result = agent.analyze_competitor(**params)
                print(f"\n🏆 Competitor Analysis:\n{result['analysis']}\n")
        
        elif command == 'report':
            params = parse_report_command(args)
            if params:
                print("\n🔍 Generating SEO report...")
                result = agent.generate_seo_report(**params)
                print(f"\n📊 SEO Report:\n{result['report']}\n")
        
        elif command == 'local':
            params = parse_local_command(args)
            if params:
                print("\n🔍 Generating local SEO recommendations...")
                result = agent.optimize_for_local_seo(**params)
                print(f"\n📍 Local SEO Recommendations:\n{result['recommendations']}\n")
        
        elif command == 'ask':
            question = parse_ask_command(args)
            if question:
                print("\n🔍 Thinking...")
                answer = agent.answer_seo_question(question)
                print(f"\n💡 Answer:\n{answer}\n")
        
        elif command == 'help':
            print_help()
        
        elif command == 'exit':
            print("\n👋 Goodbye! Happy optimizing!\n")
            sys.exit(0)
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Type 'help' for available commands\n")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")


def main():
    """Main interactive loop."""
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY not found!")
        print("\nPlease set your OpenAI API key:")
        print("1. Create a .env file with: OPENAI_API_KEY=your-api-key-here")
        print("2. Or export it: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Initialize agent
        print("\n⏳ Initializing SEO Expert Agent...")
        agent = SEOExpertAgent()
        print("✅ Agent ready!\n")
        
        # Print header
        print_header()
        
        # Interactive loop
        while True:
            try:
                # Get user input
                user_input = input("SEO Agent> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split(' ', 1)
                command = parts[0].lower()
                args = parts[1].split(' ') if len(parts) > 1 else []
                
                # Handle command
                handle_command(agent, command, args)
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Happy optimizing!\n")
                sys.exit(0)
            except EOFError:
                print("\n\n👋 Goodbye! Happy optimizing!\n")
                sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error initializing agent: {e}\n")


if __name__ == "__main__":
    main()

