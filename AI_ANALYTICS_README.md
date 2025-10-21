# AI Analytics Dashboard - Setup Guide

## Overview
The AI Analytics Dashboard allows admins to query store data using natural language. The system uses OpenAI's GPT models to analyze transactions, inventory, and promo codes, then generates appropriate visualizations automatically.

## Quick Start

### 1. Get an OpenAI API Key
1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you won't be able to see it again!)

### 2. Configure the Application
1. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
   ```

3. Save the file

### 3. Install Dependencies
```bash
source env/bin/activate
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

### 5. Access AI Analytics
1. Log in to the Admin panel
2. Navigate to the "Dashboard" tab
3. Scroll down to "🤖 AI Analytics Assistant"
4. Start asking questions!

## Example Queries

### Sales Analysis
- "What are the top 5 best-selling products?"
- "Show me total revenue by product category"
- "Which customers spent the most?"
- "What is the average order value?"

### Inventory Management
- "Which products are low in stock?"
- "Show me products with zero inventory"
- "What's the total value of inventory by category?"

### Promo Code Analysis
- "How many times was each promo code used?"
- "Which promo code generated the most revenue?"

### Custom Queries
Feel free to ask any question about your store data! The AI will:
- Analyze the relevant data
- Generate appropriate visualizations
- Provide insights and summaries

## Features

### Smart Caching
- Recent queries are cached to avoid redundant API calls
- Cache stores up to 10 most recent queries
- Significant cost savings for repeated questions

### Error Handling
- Automatic retry on transient failures
- Clear error messages for common issues
- Detailed error logs in expandable sections

### Visualization Types
The AI can generate:
- **Metrics**: Single KPI values (revenue, counts, etc.)
- **Bar Charts**: Compare categories
- **Line Charts**: Show trends over time
- **Data Tables**: Detailed tabular data
- **Text Insights**: Summaries and recommendations

## Configuration

### Model Selection
Edit `config.py` to change the AI model:
```python
OPENAI_MODEL = "gpt-4o-mini"  # Cost-effective (default)
# OPENAI_MODEL = "gpt-4o"     # More capable, higher cost
```

### Token Limits
Adjust response length in `config.py`:
```python
MAX_TOKENS = 2000  # Adjust as needed
```

### Temperature
Control response creativity:
```python
TEMPERATURE = 0.3  # Lower = more deterministic (recommended)
```

## Cost Management

### Estimated Costs (GPT-4o-mini)
- Input: ~$0.15 per 1M tokens
- Output: ~$0.60 per 1M tokens
- **Average cost per query**: $0.01 - $0.03
- **Monthly estimate (50 queries)**: $0.50 - $1.50

### Cost Optimization Tips
1. Use caching (already enabled)
2. Ask specific questions
3. Use GPT-4o-mini instead of GPT-4o
4. Select only relevant data sources

## Troubleshooting

### "AI Analytics is currently unavailable"
**Problem**: API key not configured
**Solution**: 
1. Check if `.env` file exists
2. Verify API key format: `OPENAI_API_KEY=sk-...`
3. Restart the application

### "Invalid API key"
**Problem**: API key is incorrect or expired
**Solution**:
1. Verify the key at [platform.openai.com](https://platform.openai.com)
2. Generate a new key if needed
3. Update `.env` file

### "Rate limit exceeded"
**Problem**: Too many requests in short time
**Solution**:
1. Wait a moment before retrying
2. Check your OpenAI usage limits
3. Consider upgrading your OpenAI plan

### "Query is too long"
**Problem**: Question exceeds 500 character limit
**Solution**: Break down your question into smaller, focused queries

## Data Privacy

### What Gets Sent to OpenAI
- Your natural language question
- Relevant store data (transactions, inventory, promo codes)
- **NOT sent**: Passwords, API keys, system files

### Data Handling
- Data is sent only when you click "Analyze"
- Responses are cached locally in session state
- No data is permanently stored by OpenAI (per their API policy)

### Recommendations
- Don't include sensitive customer information in queries
- Review OpenAI's data usage policy
- Consider using sample/anonymized data for testing

## Advanced Usage

### Custom Prompts
Edit `assets/prompts/analytics_system_prompt.txt` to:
- Change the AI's tone or style
- Add specific business context
- Include custom analysis guidelines

### Component Schema
Modify `assets/prompts/streamlit_component_schema.json` to:
- Add new visualization types
- Customize component behavior
- Define custom data formats

## Support

### Common Issues
1. **No visualizations appear**: Check browser console for errors
2. **Slow responses**: Large datasets take longer to analyze
3. **Unexpected results**: Try rephrasing your question

### Getting Help
1. Check error details in expandable sections
2. Review this guide's troubleshooting section
3. Verify your OpenAI API status

## Version
- **Feature Version**: 1.0
- **Last Updated**: October 21, 2025
- **Compatible with**: Streamlit 1.50.0+, Python 3.12+
