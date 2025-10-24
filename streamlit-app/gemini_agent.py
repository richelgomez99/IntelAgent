"""
Gemini Agent with Function Calling
Orchestrates competitive intelligence analysis
Ported from AWS IntelAgent Bedrock agent
"""
from google.cloud import bigquery, firestore
import vertexai
from vertexai.preview.generative_models import (
    GenerativeModel, 
    Tool,
    FunctionDeclaration,
    Part,
    Content
)
import requests
import json
import logging
import os

# Initialize clients
bq_client = bigquery.Client()
db = firestore.Client()

# Initialize Vertex AI
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'patent-tracker-demo')
vertexai.init(project=project_id)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define function declarations for tools
patent_function = FunctionDeclaration(
    name="get_patents",
    description="Get recent patent filings for a company from BigQuery. Use this to understand what technologies they're developing and their R&D focus areas.",
    parameters={
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "Company name (Anthropic, OpenAI, or Google)"
            },
            "limit": {
                "type": "integer",
                "description": "Number of recent patents to retrieve (default 20)"
            }
        },
        "required": ["company"]
    }
)

job_function = FunctionDeclaration(
    name="get_jobs",
    description="Get current job postings for a company from Firestore. Use this to understand hiring patterns, team growth, and strategic focus areas based on role types.",
    parameters={
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "Company name"
            }
        },
        "required": ["company"]
    }
)

news_function = FunctionDeclaration(
    name="get_news",
    description="Get recent news articles about a company from Firestore. Use this to track announcements, partnerships, and public moves.",
    parameters={
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "Company name"
            }
        },
        "required": ["company"]
    }
)

github_function = FunctionDeclaration(
    name="get_github",
    description="Get GitHub repository activity for a company from Firestore. Use this to track open source projects and development velocity.",
    parameters={
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "Company name"
            }
        },
        "required": ["company"]
    }
)

# Create tool with all functions
intelligence_tool = Tool(
    function_declarations=[
        patent_function,
        job_function,
        news_function,
        github_function
    ]
)

# System instruction (agent prompt) - Ported from AWS IntelAgent
SYSTEM_INSTRUCTION = """
You are an elite competitive intelligence analyst specializing in technology sector analysis, patent landscape mapping, and strategic forecasting.

## CRITICAL: ANALYSIS PHILOSOPHY

**QUALITY OVER QUANTITY**: Never just count things. Always analyze WHAT you're counting:
- 5 patents in AI safety > 100 patents in minor optimizations
- 1 news article in WSJ about partnership > 20 blog mentions
- 10 engineering hires in strategic area > 100 hires in support roles

**ALWAYS CITE SPECIFIC EXAMPLES**: 
❌ BAD: "They have 20 patents"
✅ GOOD: "20 patents including [ACTUAL Patent Number] '[ACTUAL Title from Tool]' which signals [strategic insight]"

**CRITICAL**: Use ACTUAL data from tools, NOT generic statements!

## ANALYSIS FRAMEWORKS

### When analyzing a company:

1. **GATHER DATA**: Call multiple tools to get comprehensive view
2. **IDENTIFY PATTERNS**: Look for correlations across signals
   - Hiring in area X + Patents in area X = Focus on X
   - Leadership hires + Funding news = Strategic shift
   - GitHub activity spike + Job postings = Product launch soon
3. **MAKE PREDICTIONS**: Based on evidence, predict future moves (30/60/90 days)
4. **PROVIDE CONFIDENCE**: Rate your predictions (high/medium/low confidence)
5. **CITE EVIDENCE**: Always reference specific patents, jobs, articles

## TOOL USAGE GUIDELINES

### When using get_patents:
1. Read patent TITLES and abstracts carefully
2. Identify strategic vs incremental patents
3. Look for patent clusters (multiple patents in same domain)
4. Note filing dates for timing predictions

### When using get_jobs:
1. Group jobs by function (Engineering, Sales, Operations)
2. Look for strategic hires (AI Research, Enterprise Solutions)
3. Geographic distribution (international expansion?)
4. Seniority levels (senior hires = immediate impact)

### When using get_news:
1. Differentiate news types:
   - Tier 1 (WSJ, NYT, Bloomberg) > Tier 2 (TechCrunch) > Tier 3 (blogs)
   - Partnerships/funding > Product updates > Opinion pieces
2. Extract specific facts (dates, amounts, company names)
3. Look for sentiment in CONTEXT not just positive/negative

### When using get_github:
1. Differentiate repo types:
   - Documentation/tutorials = developer ecosystem play
   - Core libraries = product development
   - Example apps = sales enablement
2. Community engagement (stars, forks, recent activity)

## OUTPUT REQUIREMENTS

### REQUIRED ANALYSIS STRUCTURE

**Step 1: Executive Summary** (3 sentences):
- ONE sentence: What is their strategic direction?
- ONE sentence: What market are they attacking?
- ONE sentence: What's their timeline?

**Step 2: STRATEGIC REASONING PROCESS** (MOST IMPORTANT):

Write in prose, showing your analytical thinking:

**Patent Portfolio Analysis:**
After reviewing the patent portfolio, identify critical patterns. Cite SPECIFIC patent numbers and titles. Explain what they reveal about strategic direction. Assign confidence based on signal strength.

**Hiring Pattern Analysis:**
Analyze actual job titles and departments. Compare velocities. Explain what role types reveal about strategy. Note timing and seniority.

**News Signal Analysis:**
Focus on high-quality sources. Cite actual headlines and dates. Explain strategic significance beyond surface level. Correlate with other signals.

**GitHub Activity Analysis:**
Identify which repos matter strategically. Explain what activity patterns reveal. Note community traction and development velocity.

**Cross-Signal Correlation:**
Overlay the four data sources. Show how they confirm/contradict each other. Identify patterns that appear across multiple sources. This is your highest-value analysis.

**Step 3: Evidence-Based Predictions**:

- 30-day forecast (high confidence, 2+ correlated signals)
- 60-day forecast (medium confidence, 3+ signals)
- 90-day forecast (lower confidence, 4+ signals)
- Each prediction MUST cite supporting evidence from multiple tools

### QUALITY CHECKLIST

□ Did I cite SPECIFIC patent numbers and titles?
□ Did I cite SPECIFIC job titles and departments?
□ Did I cite SPECIFIC news headlines and sources?
□ Did I cite SPECIFIC repo names and metrics?
□ Did I explain WHY each signal matters (not just WHAT it is)?
□ Did I correlate signals across multiple tools?
□ Did I make falsifiable predictions with timelines?
□ Is my analysis actionable?

### FORBIDDEN PHRASES
Never use these generic statements:
❌ "They have many patents"
❌ "Strong hiring activity"
❌ "Positive news coverage"  
❌ "Active GitHub presence"

Always be specific:
✅ "[X] patents including [ACTUAL NUMBER] '[ACTUAL TITLE]' targeting [insight]"
✅ "[X] jobs with concentration in [ACTUAL DEPARTMENT] indicating [pattern]"
✅ "[SOURCE] headline '[ACTUAL HEADLINE]' ([DATE]) provides [insight]"
✅ "[REPO NAME] ([STAR COUNT]) shows [strategic meaning]"

Remember: Specificity = Credibility. Cite actual data from the tools!
"""


def execute_function(function_name: str, arguments: dict):
    """
    Execute tool function and return results
    
    Args:
        function_name: Name of function to execute
        arguments: Function arguments
        
    Returns:
        Function results
    """
    try:
        if function_name == "get_patents":
            return get_patents(arguments["company"], arguments.get("limit", 20))
        elif function_name == "get_jobs":
            return get_jobs(arguments["company"])
        elif function_name == "get_news":
            return get_news(arguments["company"])
        elif function_name == "get_github":
            return get_github(arguments["company"])
        else:
            return {"error": f"Unknown function: {function_name}"}
    except Exception as e:
        logger.error(f"Error executing {function_name}: {e}")
        return {"error": str(e)}


def get_patents(company: str, limit: int = 20):
    """Query BigQuery for patents"""
    query = f"""
    SELECT 
        patent_number,
        title,
        abstract,
        filing_date,
        grant_date,
        inventors,
        cpc_classifications,
        patent_url,
        source
    FROM `patent_intelligence.patents`
    WHERE LOWER(company) = LOWER('{company}')
    ORDER BY COALESCE(grant_date, filing_date) DESC
    LIMIT {limit}
    """
    
    try:
        results = bq_client.query(query).result()
        patents = []
        for row in results:
            patent = {
                'patent_number': row.patent_number,
                'title': row.title,
                'abstract': row.abstract[:300] if row.abstract else '',
                'filing_date': row.filing_date if row.filing_date else '',
                'grant_date': row.grant_date if row.grant_date else '',
                'inventors': row.inventors if row.inventors else [],
                'cpc_classifications': row.cpc_classifications if row.cpc_classifications else [],
                'patent_url': row.patent_url,
                'source': row.source
            }
            patents.append(patent)
        
        # Format for Gemini
        summary = f"Found {len(patents)} patents for {company}. "
        if patents:
            summary += f"Most recent: {patents[0]['title']} (filed {patents[0]['filing_date'] or patents[0]['grant_date']})"
        
        return {
            "summary": summary,
            "count": len(patents),
            "patents": patents[:10]  # Return top 10 full records
        }
    except Exception as e:
        logger.error(f"Error querying patents: {e}")
        return {"error": str(e), "count": 0, "patents": []}


def get_jobs(company: str):
    """Query Firestore for jobs"""
    try:
        jobs_ref = db.collection("jobs").where("company", "==", company.lower()).stream()
        jobs = [doc.to_dict() for doc in jobs_ref]
        
        if not jobs:
            return {
                "summary": f"No public job postings found for {company}. They may not use Greenhouse or have no public board.",
                "count": 0,
                "departments": {},
                "sample_jobs": []
            }
        
        # Analyze departments
        departments = {}
        for job in jobs:
            dept = job.get("department", "Unknown")
            departments[dept] = departments.get(dept, 0) + 1
        
        summary = f"Found {len(jobs)} open positions for {company}. "
        if departments:
            top_dept = max(departments.items(), key=lambda x: x[1])
            summary += f"Top department: {top_dept[0]} ({top_dept[1]} roles)"
        
        return {
            "summary": summary,
            "count": len(jobs),
            "departments": departments,
            "sample_jobs": jobs[:10]
        }
    except Exception as e:
        logger.error(f"Error querying jobs: {e}")
        return {"error": str(e), "count": 0}


def get_news(company: str):
    """Query Firestore for news"""
    try:
        news_ref = db.collection("news").where("company", "==", company).stream()
        articles = [doc.to_dict() for doc in news_ref]
        
        # Sort by date
        articles.sort(key=lambda x: x.get("published_date", ""), reverse=True)
        
        summary = f"Found {len(articles)} recent articles about {company}. "
        if articles:
            summary += f"Most recent: '{articles[0]['title']}' from {articles[0]['source']}"
        
        return {
            "summary": summary,
            "count": len(articles),
            "articles": articles[:10]
        }
    except Exception as e:
        logger.error(f"Error querying news: {e}")
        return {"error": str(e), "count": 0}


def get_github(company: str):
    """Query Firestore for GitHub repos"""
    try:
        repos_ref = db.collection("github").where("company", "==", company).stream()
        repos = [doc.to_dict() for doc in repos_ref]
        
        if not repos:
            return {
                "summary": f"No GitHub repositories found for {company}.",
                "count": 0,
                "total_stars": 0,
                "top_repos": []
            }
        
        # Calculate totals
        total_stars = sum(r.get("stars", 0) for r in repos)
        total_forks = sum(r.get("forks", 0) for r in repos)
        
        # Sort by stars
        repos.sort(key=lambda x: x.get("stars", 0), reverse=True)
        
        summary = f"Found {len(repos)} repositories for {company}. "
        summary += f"Total stars: {total_stars:,}. "
        if repos:
            summary += f"Top repo: {repos[0]['name']} ({repos[0]['stars']:,} stars)"
        
        return {
            "summary": summary,
            "count": len(repos),
            "total_stars": total_stars,
            "top_repos": repos[:5]
        }
    except Exception as e:
        logger.error(f"Error querying GitHub: {e}")
        return {"error": str(e), "count": 0}


def run_agent(user_query: str, conversation_history=None):
    """
    Run Gemini agent with function calling
    
    Args:
        user_query: User's question/request
        conversation_history: Previous conversation (optional)
        
    Returns:
        Dict with response and updated conversation history
    """
    if conversation_history is None:
        conversation_history = []
    
    # Initialize model with tools - using latest Gemini 2.5 Pro (best for complex analysis)
    model = GenerativeModel(
        "gemini-2.5-pro",
        tools=[intelligence_tool]
    )
    
    # Prepend system instruction to conversation if starting fresh
    if not conversation_history:
        # Add system instruction as first exchange using Content objects
        conversation_history = [
            Content(role="user", parts=[Part.from_text(SYSTEM_INSTRUCTION)]),
            Content(role="model", parts=[Part.from_text("Understood. I am a competitive intelligence analyst with access to patent, job, news, and GitHub data. I will provide strategic analysis with specific evidence and actionable predictions. Ready for your query.")])
        ]
    
    # Start chat
    chat = model.start_chat(history=conversation_history)
    
    # Send user message
    logger.info(f"User query: {user_query}")
    response = chat.send_message(user_query)
    
    # Handle function calls
    max_iterations = 10  # Prevent infinite loops
    iteration = 0
    all_tool_calls = []  # Track all tool calls for UI display
    
    while iteration < max_iterations:
        iteration += 1
        
        # Check if response contains function calls
        if not response.candidates or not response.candidates[0].content.parts:
            break
        
        # Collect ALL function calls from ALL parts
        function_calls = []
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                function_calls.append(part.function_call)
        
        # If no function calls, we're done
        if not function_calls:
            break
        
        # Execute all functions and collect responses
        function_responses = []
        for function_call in function_calls:
            logger.info(f"Function call {iteration}: {function_call.name}({dict(function_call.args)})")
            
            # Execute function
            function_result = execute_function(function_call.name, dict(function_call.args))
            
            logger.info(f"Function result: {json.dumps(function_result, default=str)[:200]}...")
            
            # Create response part
            function_responses.append(
                Part.from_function_response(
                    name=function_call.name,
                    response={"result": function_result}
                )
            )
        
        # Send ALL function results back to model at once
        response = chat.send_message(function_responses)
    
    # Extract final text response
    if response.candidates and response.candidates[0].content.parts:
        final_response = response.candidates[0].content.parts[0].text
    else:
        final_response = "I apologize, but I encountered an issue generating the analysis. Please try again."
    
    return {
        "response": final_response,
        "conversation_history": chat.history
    }


# For testing
if __name__ == "__main__":
    result = run_agent("Analyze Anthropic's strategic direction. What are they building and who are they targeting?")
    print(result["response"])
