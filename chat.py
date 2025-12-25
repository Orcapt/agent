"""
Interactive Chat Interface for SEO Expert Agent
Provides a natural conversational interface to chat with the SEO expert.
"""

import os
import sys
from seo_agent import SEOExpertAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_welcome():
    """Print welcome message."""
    print("\n" + "="*70)
    print("🔍 SEO EXPERT AGENT - Chat Mode")
    print("="*70)
    print("\nHi! I'm your SEO expert assistant. I can help you with:")
    print("  • Keyword research and analysis")
    print("  • Content SEO audits and optimization")
    print("  • Meta descriptions and title tags")
    print("  • Local SEO strategies")
    print("  • Competitor analysis")
    print("  • SEO questions and best practices")
    print("\nJust chat with me naturally! Type 'exit' or 'quit' to end the conversation.")
    print("-"*70 + "\n")


def detect_intent(user_input):
    """
    Detect user intent from natural language input.
    Returns a tuple (intent, extracted_data)
    """
    user_lower = user_input.lower()
    
    # Keyword analysis intent
    if any(word in user_lower for word in ['keyword', 'analyze keyword', 'keyword research', 'keywords']):
        return 'keyword', None
    
    # Content audit intent
    if any(word in user_lower for word in ['audit', 'review content', 'check content', 'analyze content', 'seo audit']):
        return 'audit', None
    
    # Meta description intent
    if any(word in user_lower for word in ['meta description', 'meta desc', 'description']):
        return 'meta', None
    
    # Title tag intent
    if any(word in user_lower for word in ['title tag', 'title', 'suggest title']):
        return 'title', None
    
    # Competitor analysis intent
    if any(word in user_lower for word in ['competitor', 'analyze competitor', 'competitor analysis']):
        return 'competitor', None
    
    # SEO report intent
    if any(word in user_lower for word in ['seo report', 'report', 'audit report', 'website audit']):
        return 'report', None
    
    # Local SEO intent
    if any(word in user_lower for word in ['local seo', 'local', 'local business', 'google business']):
        return 'local', None
    
    # General question
    return 'question', None


def extract_keywords(user_input):
    """Extract keywords from user input."""
    # Simple extraction - look for patterns like "keywords: x, y, z" or quoted keywords
    import re
    
    # Look for quoted keywords
    quoted = re.findall(r'"([^"]+)"', user_input)
    if quoted:
        return quoted
    
    # Look for "keywords:" pattern
    if 'keyword' in user_input.lower():
        # Try to extract after "keyword" or "keywords"
        match = re.search(r'keyword[s]?[:\s]+([^\.\n]+)', user_input, re.IGNORECASE)
        if match:
            keywords_str = match.group(1).strip()
            # Split by comma
            keywords = [k.strip() for k in keywords_str.split(',')]
            return keywords[:5]  # Limit to 5 keywords
    
    return None


def extract_url(text):
    """Extract URL from text."""
    import re
    url_pattern = r'https?://[^\s]+|www\.[^\s]+'
    matches = re.findall(url_pattern, text)
    return matches[0] if matches else None


def chat_loop(agent):
    """Main chat loop."""
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("\n👋 Thanks for chatting! Good luck with your SEO optimization!\n")
                break
            
            # Check for help
            if user_input.lower() in ['help', '?']:
                print("\n" + "-"*70)
                print("I can help you with various SEO tasks. Just ask naturally, for example:")
                print("  • 'Analyze keywords: python, web development'")
                print("  • 'What is keyword density?'")
                print("  • 'Generate meta description for: Python Guide'")
                print("  • 'Audit this content: [paste your content]'")
                print("  • 'Help me with local SEO for my restaurant in New York'")
                print("-"*70 + "\n")
                continue
            
            # Detect intent
            intent, _ = detect_intent(user_input)
            
            # Process based on intent
            print("\n🤔 Thinking...")
            
            if intent == 'keyword':
                keywords = extract_keywords(user_input)
                if keywords:
                    print(f"📊 Analyzing keywords: {', '.join(keywords)}")
                    result = agent.analyze_keywords(keywords)
                    print(f"\n{result['analysis']}")
                else:
                    # Ask for keywords
                    print("I'd be happy to analyze keywords for you!")
                    print("Please provide the keywords you'd like me to analyze (comma-separated):")
                    keywords_input = input("Keywords: ").strip()
                    if keywords_input:
                        keywords = [k.strip() for k in keywords_input.split(',')]
                        result = agent.analyze_keywords(keywords)
                        print(f"\n{result['analysis']}")
            
            elif intent == 'audit':
                # Check if content is provided
                if len(user_input) > 100:  # Likely contains content
                    print("📋 Auditing your content...")
                    result = agent.audit_content(content=user_input)
                    print(f"\n{result['audit_results']}")
                else:
                    print("I'd be happy to audit your content!")
                    print("Please paste the content you'd like me to audit:")
                    content = input("Content: ").strip()
                    if content:
                        keyword = input("Target keyword (optional): ").strip() or None
                        result = agent.audit_content(content=content, target_keyword=keyword)
                        print(f"\n{result['audit_results']}")
            
            elif intent == 'meta':
                print("I can help you generate meta descriptions!")
                title = input("Page title: ").strip()
                if title:
                    content = input("Page content (brief): ").strip()
                    keyword = input("Target keyword (optional): ").strip() or None
                    if content:
                        result = agent.generate_meta_description(
                            title=title,
                            content=content,
                            target_keyword=keyword
                        )
                        print(f"\n{result['meta_descriptions']}")
            
            elif intent == 'title':
                print("I can help you generate title tags!")
                content = input("Page content (brief): ").strip()
                if content:
                    keyword = input("Target keyword: ").strip()
                    if keyword:
                        result = agent.suggest_title_tags(
                            content=content,
                            target_keyword=keyword
                        )
                        print(f"\n{result['title_suggestions']}")
            
            elif intent == 'competitor':
                url = extract_url(user_input)
                if url:
                    print(f"🏆 Analyzing competitor: {url}")
                    result = agent.analyze_competitor(url)
                    print(f"\n{result['analysis']}")
                else:
                    print("I can analyze competitor SEO!")
                    url = input("Competitor URL: ").strip()
                    if url:
                        print("\n🏆 Analyzing...")
                        result = agent.analyze_competitor(url)
                        print(f"\n{result['analysis']}")
            
            elif intent == 'report':
                url = extract_url(user_input)
                if url:
                    print(f"📊 Generating SEO report for: {url}")
                    result = agent.generate_seo_report(url)
                    print(f"\n{result['report']}")
                else:
                    print("I can generate an SEO report!")
                    url = input("Website URL: ").strip()
                    if url:
                        print("\n📊 Generating report...")
                        result = agent.generate_seo_report(url)
                        print(f"\n{result['report']}")
            
            elif intent == 'local':
                print("I can help with local SEO!")
                business = input("Business name: ").strip()
                if business:
                    location = input("Location (City, State): ").strip()
                    if location:
                        business_type = input("Business type: ").strip()
                        if business_type:
                            result = agent.optimize_for_local_seo(
                                business_name=business,
                                location=location,
                                business_type=business_type
                            )
                            print(f"\n{result['recommendations']}")
            
            else:
                # General question - use the agent's Q&A capability
                answer = agent.answer_seo_question(user_input)
                print(f"\n💡 {answer}")
            
            # Store in conversation history
            conversation_history.append({
                'user': user_input,
                'intent': intent
            })
        
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for chatting! Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 Thanks for chatting! Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Sorry, I encountered an error: {str(e)}")
            print("Please try again or rephrase your question.\n")


def main():
    """Main function."""
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
        print("✅ Agent ready!")
        
        # Print welcome
        print_welcome()
        
        # Start chat loop
        chat_loop(agent)
    
    except Exception as e:
        print(f"\n❌ Error initializing agent: {e}\n")


if __name__ == "__main__":
    main()

