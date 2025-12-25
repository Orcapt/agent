# SEO Expert Agent

An intelligent AI-powered SEO expert agent built with Python and OpenAI. This agent provides comprehensive SEO analysis, recommendations, and optimization strategies to help improve your website's search engine rankings.

## Features

- 🔍 **Keyword Analysis**: Analyze keywords for difficulty, search volume, intent, and opportunities
- 📝 **Content Audit**: Comprehensive SEO audit of your content with actionable recommendations
- 🏷️ **Meta Description Generation**: Create SEO-optimized meta descriptions
- 📌 **Title Tag Optimization**: Generate multiple title tag variations
- 🏢 **Local SEO**: Specialized local SEO optimization strategies
- 🎯 **Competitor Analysis**: Analyze competitor SEO strategies
- 📊 **SEO Reports**: Generate comprehensive SEO audit reports
- 💬 **SEO Q&A**: Ask any SEO-related questions and get expert answers

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```
   
   Or export it as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-openai-api-key-here'
   ```
   
   Get your API key from: https://platform.openai.com/api-keys

## Run with Docker

Build the image and start the interactive chat interface:

```bash
docker build -t seo-agent .
docker run --rm -it --env-file .env seo-agent
```

If you prefer passing the key directly:

```bash
docker run --rm -it -e OPENAI_API_KEY=your-key-here seo-agent
```

## Usage

### Basic Usage

```python
from seo_agent import SEOExpertAgent

# Initialize the agent
agent = SEOExpertAgent()

# Analyze keywords
result = agent.analyze_keywords(
    keywords=["python programming", "web development"],
    target_audience="developers"
)
print(result['analysis'])

# Answer SEO questions
answer = agent.answer_seo_question("What is the ideal keyword density?")
print(answer)

# Generate meta descriptions
meta_result = agent.generate_meta_description(
    title="Python Web Development Guide",
    content="Learn Python web development...",
    target_keyword="python web development"
)
print(meta_result['meta_descriptions'])
```

### Run Example Script

```bash
python example_usage.py
```

### Interactive Chat Mode (Recommended)

For a natural conversational interface, run:

```bash
python chat.py
```

This starts a chat session where you can:
- Chat naturally with the SEO expert
- Ask questions in plain English
- Get guided help for complex tasks
- Type `help` for assistance
- Type `exit` or `quit` to end the conversation

**Example chat session:**
```
You: What is keyword density?
Agent: [Provides detailed answer]

You: Analyze keywords: python, web development
Agent: [Analyzes keywords]

You: Help me with local SEO
Agent: [Guides you through local SEO setup]
```

### Command-Based Interactive Mode

For a command-based interface, run:

```bash
python interactive.py
```

This provides structured commands:
- `keyword <keywords>` - Analyze keywords
- `audit <content>` - Audit content
- `ask <question>` - Ask SEO questions
- `help` - Show all commands
- `exit` - Quit

**Example command session:**
```
SEO Agent> keyword python,web development developers
SEO Agent> ask What is keyword density?
SEO Agent> exit
```

### Available Methods

#### Keyword Analysis
```python
agent.analyze_keywords(
    keywords=["keyword1", "keyword2"],
    target_audience="your target audience"
)
```

#### Content SEO Audit
```python
agent.audit_content(
    content="Your content here...",
    target_keyword="primary keyword",
    url="https://example.com/page"
)
```

#### Generate Meta Descriptions
```python
agent.generate_meta_description(
    title="Page Title",
    content="Page content...",
    target_keyword="target keyword"
)
```

#### Suggest Title Tags
```python
agent.suggest_title_tags(
    content="Your content...",
    target_keyword="target keyword"
)
```

#### Competitor Analysis
```python
agent.analyze_competitor(
    competitor_url="https://competitor.com",
    focus_areas=["keywords", "content", "links"]
)
```

#### Generate SEO Report
```python
agent.generate_seo_report(
    website_url="https://yourwebsite.com",
    analysis_type="comprehensive"  # or "quick" or "technical"
)
```

#### Local SEO Optimization
```python
agent.optimize_for_local_seo(
    business_name="Your Business",
    location="City, State",
    business_type="Business Type"
)
```

#### Ask SEO Questions
```python
agent.answer_seo_question("Your SEO question here")
```

## Configuration

### Using Different OpenAI Models

By default, the agent uses `gpt-4`. You can specify a different model:

```python
agent = SEOExpertAgent(model="gpt-4-turbo-preview")
# or
agent = SEOExpertAgent(model="gpt-3.5-turbo")
```

### Custom API Key

```python
agent = SEOExpertAgent(api_key="your-custom-api-key")
```

## Requirements

- Python 3.8+
- OpenAI API key
- See `requirements.txt` for Python dependencies

## Project Structure

```
Agent1/
├── seo_agent.py          # Main SEO agent class
├── example_usage.py       # Example usage script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Cost Considerations

This agent uses the OpenAI API, which charges based on usage:
- **GPT-4**: More expensive but higher quality responses
- **GPT-3.5-turbo**: More cost-effective for simpler queries

Monitor your usage at: https://platform.openai.com/usage

## Examples

### Example 1: Keyword Research
```python
from seo_agent import SEOExpertAgent

agent = SEOExpertAgent()
result = agent.analyze_keywords(
    keywords=["digital marketing", "SEO services"],
    target_audience="small businesses"
)
print(result['analysis'])
```

### Example 2: Content Optimization
```python
content = "Your blog post content here..."
result = agent.audit_content(
    content=content,
    target_keyword="main keyword",
    url="https://yoursite.com/blog/post"
)
print(result['audit_results'])
```

### Example 3: Local Business SEO
```python
result = agent.optimize_for_local_seo(
    business_name="Joe's Pizza",
    location="New York, NY",
    business_type="Restaurant"
)
print(result['recommendations'])
```

## Contributing

Feel free to extend this agent with additional SEO capabilities:
- Schema markup generation
- Technical SEO checks
- Backlink analysis
- SERP feature optimization
- And more!

## License

This project is open source and available for use.

## Disclaimer

This agent provides SEO recommendations based on best practices and AI analysis. Always verify recommendations with current SEO guidelines and test changes before implementing them on production websites.

