"""
Example usage of the SEO Expert Agent
Demonstrates various capabilities of the SEO agent.
"""

from seo_agent import SEOExpertAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def example_keyword_analysis(agent: SEOExpertAgent):
    """Example: Analyze keywords for SEO."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Keyword Analysis")
    print("="*70)
    
    keywords = ["digital marketing", "SEO services", "content marketing"]
    result = agent.analyze_keywords(
        keywords=keywords,
        target_audience="small business owners looking to improve online presence"
    )
    
    print(f"\nKeywords analyzed: {keywords}")
    print(f"\nAnalysis:\n{result['analysis']}")


def example_content_audit(agent: SEOExpertAgent):
    """Example: Audit content for SEO."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Content SEO Audit")
    print("="*70)
    
    sample_content = """
    Python Web Development: A Complete Guide
    
    Python is one of the most popular programming languages for web development.
    In this comprehensive guide, we'll explore Flask and Django frameworks.
    
    Flask is a lightweight framework perfect for small applications, while Django
    provides a full-featured framework for complex web applications.
    
    Both frameworks offer excellent documentation and active communities.
    """
    
    result = agent.audit_content(
        content=sample_content,
        target_keyword="python web development",
        url="https://example.com/python-web-development"
    )
    
    print(f"\nContent preview: {result['content_preview']}")
    print(f"\nAudit Results:\n{result['audit_results']}")


def example_meta_description(agent: SEOExpertAgent):
    """Example: Generate meta descriptions."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Generate Meta Descriptions")
    print("="*70)
    
    result = agent.generate_meta_description(
        title="Best SEO Tools for 2024",
        content="Discover the top SEO tools that can help improve your search rankings...",
        target_keyword="SEO tools"
    )
    
    print(f"\nTitle: {result['title']}")
    print(f"\nMeta Descriptions:\n{result['meta_descriptions']}")


def example_title_tags(agent: SEOExpertAgent):
    """Example: Generate title tag suggestions."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Title Tag Suggestions")
    print("="*70)
    
    content = "Learn how to optimize your website for search engines with our comprehensive SEO guide."
    result = agent.suggest_title_tags(
        content=content,
        target_keyword="SEO optimization"
    )
    
    print(f"\nTarget Keyword: {result['target_keyword']}")
    print(f"\nTitle Suggestions:\n{result['title_suggestions']}")


def example_seo_question(agent: SEOExpertAgent):
    """Example: Ask SEO questions."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Answer SEO Question")
    print("="*70)
    
    question = "What are the most important on-page SEO factors in 2024?"
    answer = agent.answer_seo_question(question)
    
    print(f"\nQ: {question}")
    print(f"\nA: {answer}")


def example_local_seo(agent: SEOExpertAgent):
    """Example: Local SEO optimization."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Local SEO Optimization")
    print("="*70)
    
    result = agent.optimize_for_local_seo(
        business_name="Joe's Pizza",
        location="New York, NY",
        business_type="Restaurant"
    )
    
    print(f"\nBusiness: {result['business_name']}")
    print(f"Location: {result['location']}")
    print(f"\nRecommendations:\n{result['recommendations']}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("SEO EXPERT AGENT - EXAMPLE USAGE")
    print("="*70)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY not found!")
        print("\nPlease set your OpenAI API key:")
        print("1. Create a .env file with: OPENAI_API_KEY=your-api-key-here")
        print("2. Or export it: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Initialize the agent
        agent = SEOExpertAgent()
        print("\n✓ SEO Expert Agent initialized successfully")
        
        # Run examples
        example_keyword_analysis(agent)
        example_seo_question(agent)
        example_meta_description(agent)
        example_title_tags(agent)
        example_local_seo(agent)
        
        # Uncomment to run content audit (uses API credits)
        # example_content_audit(agent)
        
        print("\n" + "="*70)
        print("All examples completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

