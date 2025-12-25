"""
SEO Expert Agent using OpenAI
An intelligent agent that provides SEO analysis, recommendations, and optimization strategies.
"""

import os
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Shared system prompt so other modules (e.g., streaming server) can reuse it
SEO_SYSTEM_PROMPT = """You are an expert SEO consultant with over 10 years of experience in search engine optimization. 
You specialize in:
- On-page SEO optimization
- Keyword research and analysis
- Technical SEO audits
- Content optimization
- Link building strategies
- Local SEO
- E-commerce SEO
- SEO reporting and analytics

You provide actionable, data-driven recommendations based on current SEO best practices and Google's guidelines.
Always be specific, practical, and prioritize recommendations by impact and effort required."""


class SEOExpertAgent:
    """
    An AI-powered SEO expert agent that provides comprehensive SEO analysis and recommendations.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the SEO Expert Agent.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY env variable.
            model: OpenAI model to use (default: gpt-4)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.system_prompt = SEO_SYSTEM_PROMPT

    @staticmethod
    def get_system_prompt() -> str:
        """Expose the base system prompt for reuse without instantiating the agent."""
        return SEO_SYSTEM_PROMPT
    
    def _call_openai(self, user_message: str, temperature: float = 0.7) -> str:
        """
        Make a call to OpenAI API.
        
        Args:
            user_message: The user's query or request
            temperature: Sampling temperature (0-1)
            
        Returns:
            The assistant's response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    def analyze_keywords(self, keywords: List[str], target_audience: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze keywords and provide SEO insights.
        
        Args:
            keywords: List of keywords to analyze
            target_audience: Optional target audience description
            
        Returns:
            Dictionary with keyword analysis and recommendations
        """
        keywords_str = ", ".join(keywords)
        audience_context = f"Target audience: {target_audience}" if target_audience else ""
        
        prompt = f"""Analyze the following keywords for SEO purposes:
Keywords: {keywords_str}
{audience_context}

Provide a comprehensive analysis including:
1. Keyword difficulty assessment (Low/Medium/High)
2. Search volume potential (estimated)
3. Competition level
4. Keyword intent (Informational/Commercial/Transactional/Navigational)
5. Long-tail keyword suggestions
6. Related keyword opportunities
7. Content ideas based on these keywords

Format your response as a structured analysis."""
        
        analysis = self._call_openai(prompt, temperature=0.5)
        
        return {
            "keywords": keywords,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def audit_content(self, content: str, target_keyword: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform SEO audit on content.
        
        Args:
            content: The content to audit
            target_keyword: Primary target keyword (optional)
            url: URL of the content (optional)
            
        Returns:
            Dictionary with audit results and recommendations
        """
        keyword_context = f"Target keyword: {target_keyword}" if target_keyword else ""
        url_context = f"URL: {url}" if url else ""
        
        prompt = f"""Perform a comprehensive SEO audit on the following content:
{url_context}
{keyword_context}

Content:
{content[:3000]}  # Limit content length

Evaluate:
1. Keyword optimization (density, placement, LSI keywords)
2. Content quality and readability
3. On-page SEO elements (headings, meta descriptions, alt text)
4. Content structure and formatting
5. Internal linking opportunities
6. Content length and depth
7. User intent alignment
8. Mobile-friendliness considerations

Provide specific, actionable recommendations prioritized by impact."""
        
        audit_results = self._call_openai(prompt, temperature=0.5)
        
        return {
            "content_preview": content[:500],
            "target_keyword": target_keyword,
            "url": url,
            "audit_results": audit_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_meta_description(self, title: str, content: str, target_keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate SEO-optimized meta description.
        
        Args:
            title: Page title
            content: Page content
            target_keyword: Target keyword to include
            
        Returns:
            Dictionary with meta description options
        """
        keyword_context = f"Include the keyword: {target_keyword}" if target_keyword else ""
        
        prompt = f"""Generate 3 SEO-optimized meta descriptions for:
Title: {title}
{keyword_context}

Requirements:
- 150-160 characters
- Include a call-to-action
- Compelling and click-worthy
- Include target keyword naturally
- Unique and descriptive

Provide 3 variations with brief explanations for each."""
        
        meta_descriptions = self._call_openai(prompt, temperature=0.8)
        
        return {
            "title": title,
            "target_keyword": target_keyword,
            "meta_descriptions": meta_descriptions,
            "timestamp": datetime.now().isoformat()
        }
    
    def suggest_title_tags(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """
        Suggest optimized title tags.
        
        Args:
            content: Page content
            target_keyword: Target keyword
            
        Returns:
            Dictionary with title tag suggestions
        """
        prompt = f"""Generate 5 SEO-optimized title tag options for content targeting the keyword: {target_keyword}

Content preview:
{content[:1000]}

Requirements:
- 50-60 characters
- Include target keyword near the beginning
- Compelling and click-worthy
- Include brand name if relevant
- Unique and descriptive

Provide 5 variations with brief explanations."""
        
        title_suggestions = self._call_openai(prompt, temperature=0.8)
        
        return {
            "target_keyword": target_keyword,
            "title_suggestions": title_suggestions,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_competitor(self, competitor_url: str, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze competitor SEO strategy.
        
        Args:
            competitor_url: URL of competitor to analyze
            focus_areas: Specific areas to focus on (e.g., ['keywords', 'content', 'links'])
            
        Returns:
            Dictionary with competitor analysis
        """
        focus_context = f"Focus on: {', '.join(focus_areas)}" if focus_areas else "Provide comprehensive analysis"
        
        prompt = f"""Analyze the SEO strategy of this competitor:
URL: {competitor_url}
{focus_context}

Analyze:
1. On-page SEO elements (title, meta description, headings)
2. Content strategy and quality
3. Keyword targeting
4. Internal linking structure
5. Technical SEO considerations
6. Content gaps and opportunities
7. Competitive advantages and weaknesses

Provide actionable insights and opportunities to outperform this competitor."""
        
        analysis = self._call_openai(prompt, temperature=0.5)
        
        return {
            "competitor_url": competitor_url,
            "focus_areas": focus_areas,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_seo_report(self, website_url: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate comprehensive SEO report.
        
        Args:
            website_url: URL of website to analyze
            analysis_type: Type of analysis (comprehensive, quick, technical)
            
        Returns:
            Dictionary with SEO report
        """
        prompt = f"""Generate a {analysis_type} SEO report for: {website_url}

Include:
1. Executive Summary
2. Technical SEO Audit
3. On-Page SEO Analysis
4. Content Quality Assessment
5. Keyword Performance
6. Competitor Comparison
7. Priority Recommendations (High/Medium/Low impact)
8. Action Plan with timelines

Format as a professional SEO audit report."""
        
        report = self._call_openai(prompt, temperature=0.5)
        
        return {
            "website_url": website_url,
            "analysis_type": analysis_type,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    
    def answer_seo_question(self, question: str) -> str:
        """
        Answer any SEO-related question.
        
        Args:
            question: The SEO question to answer
            
        Returns:
            Detailed answer from the SEO expert
        """
        return self._call_openai(question, temperature=0.7)
    
    def optimize_for_local_seo(self, business_name: str, location: str, business_type: str) -> Dict[str, Any]:
        """
        Provide local SEO optimization recommendations.
        
        Args:
            business_name: Name of the business
            location: Business location
            business_type: Type of business
            
        Returns:
            Dictionary with local SEO recommendations
        """
        prompt = f"""Provide comprehensive local SEO optimization strategy for:
Business Name: {business_name}
Location: {location}
Business Type: {business_type}

Include:
1. Google Business Profile optimization
2. Local keyword targeting
3. NAP (Name, Address, Phone) consistency
4. Local content strategy
5. Local link building opportunities
6. Review management strategy
7. Local schema markup recommendations
8. Citation building strategy

Provide actionable, prioritized recommendations."""
        
        recommendations = self._call_openai(prompt, temperature=0.6)
        
        return {
            "business_name": business_name,
            "location": location,
            "business_type": business_type,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Example usage of the SEO Expert Agent."""
    print("SEO Expert Agent - Example Usage\n")
    
    # Initialize the agent
    # Make sure to set OPENAI_API_KEY environment variable
    try:
        agent = SEOExpertAgent()
        print("✓ SEO Expert Agent initialized successfully\n")
        
        # Example 1: Keyword Analysis
        print("=" * 60)
        print("Example 1: Keyword Analysis")
        print("=" * 60)
        keywords = ["python programming", "web development"]
        result = agent.analyze_keywords(keywords, target_audience="developers")
        print(f"Analyzed keywords: {keywords}")
        print(f"\nAnalysis:\n{result['analysis']}\n")
        
        # Example 2: Answer SEO Question
        print("=" * 60)
        print("Example 2: Answer SEO Question")
        print("=" * 60)
        answer = agent.answer_seo_question("What is the ideal keyword density for SEO?")
        print(f"Q: What is the ideal keyword density for SEO?")
        print(f"A: {answer}\n")
        
        # Example 3: Generate Meta Description
        print("=" * 60)
        print("Example 3: Generate Meta Description")
        print("=" * 60)
        meta_result = agent.generate_meta_description(
            title="Python Web Development Guide",
            content="Learn Python web development with Flask and Django",
            target_keyword="python web development"
        )
        print(f"Meta Descriptions:\n{meta_result['meta_descriptions']}\n")
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

