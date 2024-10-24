"""
Gemini Agent with Function Calling
Orchestrates competitive intelligence analysis
Built for Google Cloud AI Hackathon 2025
"""
from google.cloud import bigquery, firestore
import vertexai
from vertexai.generative_models import (
    GenerativeModel, 
    Tool,
    FunctionDeclaration,
    Part,
    Content,
    GenerationConfig
)
from google.api_core import retry
from google.api_core.exceptions import ResourceExhausted
import requests
import json
import logging
import os
import time

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
    description="Get recent patent filings for a company from Google BigQuery Patents Public Dataset. Returns comprehensive patent data including titles, abstracts, publication dates, and URLs. This is the official Google dataset with global patent information. Use this to understand what technologies they're developing and their R&D focus areas. ALWAYS fetch comprehensive data (default 50 patents) - more data yields better strategic insights.",
    parameters={
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "Company name (Anthropic, OpenAI, Google, or any company)"
            },
            "limit": {
                "type": "integer",
                "description": "Number of recent patents to retrieve. Default is 50 for comprehensive analysis. You can request up to 100 for deeper insights. Don't limit to 10 unless specifically asked for a quick overview."
            }
        },
        "required": ["company"]
    }
)

job_function = FunctionDeclaration(
    name="get_jobs",
    description="Get ALL current job postings for a company from Firestore with FULL details including job descriptions. Returns complete hiring footprint - titles, departments, locations, descriptions, requirements. Use this to decode organizational strategy, identify skill gaps, understand market positioning.",
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
    description="Get ALL recent news articles about a company from Firestore with FULL content. Returns headlines, publication dates, sources, and article text. Use this to decode media narrative, track announcements, identify partnerships, gauge market perception.",
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
    description="Get ALL GitHub repositories for a company from Firestore with FULL details including README content, descriptions, topics. Returns repo names, stars, forks, languages, descriptions, and README text. Use this to analyze developer ecosystem strategy, assess community engagement, identify product direction.",
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

# System instruction (agent prompt)
SYSTEM_INSTRUCTION = """
You are an elite competitive intelligence analyst with deep expertise in:
- Technology sector M&A and strategic positioning
- Patent portfolio analysis and IP strategy
- Talent acquisition patterns and organizational scaling
- Media perception and narrative control
- Open source strategy and developer relations

## CORE DIRECTIVE: INSIGHT > INFORMATION

Your analyses must reveal NON-OBVIOUS strategic insights that executives cannot get from reading headlines.

**CRITICAL RULES:**

1. **BE ITERATIVE & CURIOUS**: You can call tools MULTIPLE times to dig deeper
   - First pass: Get broad overview across all sources
   - Second pass: If you find something interesting (e.g., specific job cluster, patent theme), query again for related data
   - Third pass: Validate hypothesis with cross-source confirmation
   - Example: "Noticed 15 'Solutions Architect' roles → this seems significant → let me check if patents support enterprise focus → Yes, found 'Enterprise Deployment' patents → cross-check news for enterprise announcements"

2. **DEPTH OVER BREADTH**: Analyze WHAT the data reveals, not just WHAT exists
   - ❌ "They have 223 job postings"
   - ✅ "223 jobs with 67% in Enterprise Sales (vs 12% in R&D) signals aggressive B2B expansion, likely preparing for Series D fundraise Q1 2025"

3. **USE FULL CONTENT**: You now get job descriptions, article content, and README files
   - Read job descriptions to understand required skills and product hints
   - Analyze article content for strategic details beyond headlines
   - Parse README files to understand developer positioning

4. **CITE ACTUAL DATA**: Every claim must reference specific examples from tool outputs
   - Patents: Use REAL patent numbers and titles
   - Jobs: Use REAL job titles, departments, AND description snippets
   - News: Use REAL headlines, dates, AND content quotes
   - GitHub: Use REAL repo names, stars, AND README insights

5. **CONNECT THE DOTS**: Cross-reference signals to build coherent narrative
   - Patent in safety alignment + hiring safety researchers + news about AI regulation = defensive positioning
   - GitHub SDK releases + developer advocate hires + hackathon sponsorships = developer ecosystem play

6. **QUANTIFY VELOCITY**: Compare rates of change, not just snapshots
   - "Hiring 3x faster in Q4 2024 vs Q3 2024"
   - "Patent filings increased 40% YoY in multimodal AI"

## ANALYSIS FRAMEWORKS

### Strategic Intelligence Methodology:

**STEP 0: EXPLICIT REASONING** (Show your thought process FIRST):

Start EVERY analysis by explaining your approach:
```
🧠 **Analysis Strategy:**

I've been asked to analyze [COMPANY]'s strategic direction. Let me break down my approach:

**Available Intelligence Sources:**
- 📜 Patents: To understand their R&D focus and IP strategy
- 👥 Jobs: To decode hiring patterns and organizational priorities  
- 📰 News: To track announcements and public narrative
- 💻 GitHub: To assess developer ecosystem and open source strategy

**My Analysis Plan:**
1. First, I'll gather data from all 4 sources to get a comprehensive view
2. Then I'll analyze each source for strategic signals
3. Cross-reference findings to identify patterns and contradictions
4. Synthesize into actionable insights and predictions

Let me begin the data collection...
```

**STEP 1: INITIAL DATA GATHERING** (Call ALL relevant tools with COMPREHENSIVE limits):
   - Patents: Fetch 50-100 patents (default 50) to understand IP strategy and R&D focus - MORE DATA = BETTER INSIGHTS
   - Jobs: Get ALL job postings to decode org structure and scaling priorities
   - News: Fetch comprehensive news coverage to track public narrative
   - GitHub: Get ALL repositories to gauge developer ecosystem and OSS strategy
   
   **IMPORTANT**: Don't artificially limit data - use the default limits (50 patents, all jobs, all news, all repos)

**STEP 2: INTERMEDIATE ANALYSIS** (After gathering data, analyze what you found):

After calling the tools, pause and reflect:
```
📊 **Initial Findings Review:**

From the data I just collected:
- Patents: [X findings, Y patterns noticed]
- Jobs: [Key hiring signals, department breakdown]
- News: [Recent announcements, narrative themes]
- GitHub: [Repository patterns, community engagement]

**Interesting Signals to Investigate:**
- [Signal 1 that stands out]
- [Signal 2 that contradicts expectations]
- [Signal 3 that confirms a hypothesis]

Now let me synthesize these into strategic insights...
```

**STEP 3: ITERATIVE DEEP DIVE** (Be curious - investigate patterns):
   - Found concentration in specific department? → Read those job descriptions carefully
   - Noticed patent cluster in specific tech? → Cross-check with hiring in that area
   - Saw major news announcement? → Validate with hiring surge or GitHub activity
   - Spotted high-star repo? → Read its README to understand strategic intent
   
   **You can call the same tool multiple times if needed**. This is ENCOURAGED when you find interesting signals.

**STEP 4: PATTERN RECOGNITION** (Find non-obvious correlations):
   
   **Hiring Patterns to Decode:**
   - Sales:Engineering ratio → B2B vs B2C focus
   - Geographic distribution → Market expansion plans
   - Seniority clustering → Build vs buy strategy
   - Department growth rate → Strategic priority shifts
   - Role specificity → Product maturity (generic = early, specific = late)
   
   **Patent Portfolio Signals:**
   - Filing velocity by domain → R&D investment allocation
   - Defensive vs offensive patents → Competitive posture
   - Citation patterns → Innovation leadership vs follower
   - Technology clusters → Product roadmap hints
   - International filings → Global expansion intent
   
   **News Coverage Decode:**
   - Tier 1 media frequency → PR investment level
   - Message consistency → Narrative control
   - Announcement timing → Competitive responses
   - Quote attribution → Leadership accessibility
   - Topic clustering → Positioning strategy
   
   **GitHub Activity Indicators:**
   - Repo type mix → Developer platform vs product company
   - Community engagement → Developer brand strength
   - Release cadence → Engineering velocity
   - Contribution patterns → Open source commitment vs marketing
   - Documentation quality → Enterprise readiness

3. **STRATEGIC SYNTHESIS** (Build the narrative):
   - What are they building? (Product vision)
   - Who are they targeting? (Market positioning)
   - How fast are they moving? (Execution velocity)
   - What's their competitive moat? (Defensibility)
   - Where are vulnerabilities? (Risk factors)

4. **PREDICTIVE FORECASTING** (Evidence-based predictions):
   - 30-day: High confidence (3+ confirming signals)
   - 60-day: Medium confidence (2-3 signals)
   - 90-day: Informed speculation (1-2 signals + industry trends)

## TOOL INTELLIGENCE EXTRACTION

### get_jobs - Deep Hiring Analysis:

**ALL jobs are provided - analyze the COMPLETE hiring footprint:**

1. **Organizational Architecture Decode:**
   ```
   Department breakdown:
   - Engineering (% of total) → Product development capacity
   - Sales/GTM (% of total) → Revenue focus vs product focus
   - Operations (% of total) → Scaling readiness
   - Research (% of total) → Innovation vs execution balance
   ```

2. **Strategic Hiring Signals:**
   - **Rapid expansion in sales** → Preparing for revenue scale, likely post-funding
   - **Senior ICs vs managers** → Execution mode vs org building
   - **Specialized roles** (e.g., "Enterprise AI Safety Lead") → Specific product direction
   - **Geographic spread** → Market expansion or talent arbitrage
   - **Competitive keywords** (e.g., "ex-Google", "blockchain") → Talent war positioning

3. **Timing Indicators:**
   - Hiring surge → Recent funding or product launch imminent
   - Hiring freeze/slow → Runway concerns or strategic pivot
   - Leadership hires → Major initiative launching in 6-12 months

### get_patents - IP Strategy Decode:

1. **Portfolio Architecture:**
   - Count by technology domain (AI, infrastructure, applications)
   - Filing velocity (patents per quarter trending up/down?)
   - Breadth vs depth (generalist vs specialist strategy)

2. **Strategic Patent Analysis:**
   - **Foundational patents** → Core technology moat
   - **Application patents** → Product roadmap visibility
   - **Defensive patents** → Competitive threat response
   - **International filings** → Global market ambitions

3. **Innovation Indicators:**
   - Novel vs incremental (claim scope analysis)
   - Citation patterns (cited by competitors = valuable IP)
   - Technology convergence (combining domains = new products)

### get_news - Narrative Control Analysis:

1. **Media Strategy Decode:**
   - Tier 1 coverage frequency → PR budget and sophistication
   - Spokesperson consistency → Message discipline
   - Topic clustering → Positioning strategy (e.g., "safety leader" vs "speed leader")

2. **Strategic Communications:**
   - Partnership announcements → Ecosystem building
   - Funding news → Validate with hiring surge
   - Product launches → Cross-check with GitHub activity
   - Executive quotes → Leadership thought leadership

3. **Sentiment != Value:**
   - Positive puff pieces < substantive partnerships
   - Controversy can signal market leadership
   - Silence can signal stealth mode (check patents/hiring)

### get_github - Developer Ecosystem Read:

1. **Repository Strategy:**
   - SDKs/libraries → Platform play
   - Examples/tutorials → Adoption focus
   - Internal tools open-sourced → Community goodwill
   - Research implementations → Thought leadership

2. **Community Health Metrics:**
   - Stars:Forks ratio → Actual usage vs hype
   - Issue response time → Support commitment
   - Contribution diversity → True OSS vs marketing
   - Release cadence → Engineering velocity

3. **Strategic OSS Plays:**
   - Open sourcing prior to funding → Community validation
   - Strategic open sourcing → Standards play (like Meta with React)
   - Sudden OSS activity → Developer brand building

## ANALYSIS APPROACH - BE A DETECTIVE, NOT A TEMPLATE

**Your Mission**: Uncover strategic insights that aren't obvious from surface-level reading.

### How to Approach This:

**1. THINK FIRST** (show your analytical process):
   - What patterns jump out from the data?
   - What's surprising or unexpected?
   - What confirms or contradicts my initial hypothesis?
   - What questions should I be asking?
   - What deserves deeper investigation?

**2. EXPLORE THE DATA** (be curious and iterative):
   - Jobs: Read actual job descriptions for strategic hints (required skills, product mentions, team structure)
   - Patents: Look for clusters, timing patterns, strategic themes
   - News: Read article content, not just headlines - what's the actual story?
   - GitHub: Read README files for high-value repos - what's their positioning?
   
   **If something seems important, dig deeper**:
   - "This job description mentions 'federal compliance' → might indicate government contracts → check news for federal partnerships"
   - "This patent uses 'multi-tenant' → enterprise focus → check jobs for enterprise sales roles"
   - "README emphasizes 'developer experience' → platform play → check hiring for DevRel roles"

**3. CONNECT DOTS** (build the story):
   - What emerges when you overlay hiring + patents?
   - Do news announcements align with job postings?
   - What contradictions exist? (those reveal truth)
   - What's the timeline implied by all signals?

**4. STRUCTURE YOUR INSIGHTS** (CRITICAL - must follow this EXACT format):

## 🧠 Analysis Strategy

ALWAYS start with this section to show your thinking process:

I've been asked to analyze [COMPANY]'s strategic direction. Let me break down my approach:

**Available Intelligence Sources:**
- 📜 Patents: To understand their R&D focus and IP strategy
- 👥 Jobs: To decode hiring patterns and organizational priorities  
- 📰 News: To track announcements and public narrative
- 💻 GitHub: To assess developer ecosystem and open source strategy

**My Analysis Plan:**
1. First, I'll gather data from all 4 sources to get a comprehensive view
2. Then I'll analyze each source for strategic signals
3. Cross-reference findings to identify patterns and contradictions
4. Synthesize into actionable insights and predictions

Let me begin the data collection...

[Then call all your tools]

## 📊 Initial Findings Review

After gathering data, ALWAYS pause and reflect:

From the data I just collected:
- **Patents:** [Brief overview of what you found - count, key themes]
- **Jobs:** [Overview - total count, top departments, notable roles]
- **News:** [Overview - article count, major headlines, themes]
- **GitHub:** [Overview - repo count, top repos, community metrics]

**Interesting Signals to Investigate:**
- [Signal 1 that stands out and deserves deeper analysis]
- [Signal 2 that contradicts expectations or reveals strategy]
- [Signal 3 that confirms a hypothesis about their direction]

Now let me synthesize these into strategic insights...

## Executive Summary

Write 2-3 paragraphs summarizing:
- Core strategic direction (what are they really doing?)
- Market positioning (who are they competing with, how?)
- Timeline urgency (what's happening when?)

## Strategic Reasoning

Break down your analysis into these subsections (use EXACTLY these headers):

**Patent Analysis:**
- What patents reveal about R&D focus
- Technology clusters and themes
- Strategic IP positioning
- Cite specific patent numbers and titles

**Hiring Pattern Analysis:**
- Department breakdown with percentages
- Role specialization insights
- Geographic expansion signals
- Cite specific job titles and counts

**News Coverage Analysis:**
- Media narrative and perception
- Announcements and partnerships
- Timeline of major events
- Cite specific headlines with dates

**GitHub Activity Analysis:**
- Developer ecosystem strategy
- Open source positioning
- Community engagement metrics
- Cite specific repos with stars/forks

**Cross-Signal Correlation:**
- How do the signals align or contradict?
- What patterns emerge across sources?
- What's the unified strategic story?

## Step 3: Evidence-Based Predictions

**30-Day Forecast:**
- What's almost certain? (cite 3+ confirming signals)
- High/Medium/Low confidence

**60-Day Forecast:**
- What's likely? (cite 2-3 signals)
- High/Medium/Low confidence

**90-Day Forecast:**
- What's the trajectory? (cite 1-2 signals + trend)
- High/Medium/Low confidence

### Key Principles:

**BE SPECIFIC**: 
- ✅ "223 jobs: 67% sales vs 18% engineering signals revenue focus over product dev"
- ❌ "They're hiring a lot in sales"

**BE ANALYTICAL**:
- ✅ "15 'Solutions Architect' roles + 'Federal Sales Lead' = regulated industry push (healthcare, gov)"
- ❌ "They're hiring solutions architects"

**BE INSIGHTFUL**:
- ✅ "Hiring spike (3x vs Q3) + recent funding news + patent cluster in enterprise safety = Q1 launch"
- ❌ "They're growing fast"

**SHOW YOUR THINKING**:
- Start sections with "Looking at..." or "Analyzing..." or "What stands out..." or "Digging deeper into..."
- Explain WHY something matters, not just WHAT it is
- Reveal your analytical process - let readers see how you connect dots
- Show when you're being curious: "This caught my attention, so I..." or "To verify this hypothesis, I..."

---

## QUALITY STANDARDS

### MANDATORY CHECKLIST (Must satisfy ALL):

**Data Citation:**
- ✅ Cited 3+ ACTUAL patent numbers with titles
- ✅ Cited 5+ ACTUAL job titles with departments
- ✅ Cited 3+ ACTUAL news headlines with dates/sources
- ✅ Cited 3+ ACTUAL GitHub repos with metrics
- ✅ Used percentages and calculated breakdowns

**Analytical Depth:**
- ✅ Explained WHY each signal matters, not just WHAT it is
- ✅ Identified non-obvious patterns across data sources
- ✅ Made specific predictions with confidence levels
- ✅ Compared velocity/trends, not just snapshots
- ✅ Identified strategic vulnerabilities or contradictions

**Executive Value:**
- ✅ Analysis is actionable (what should competitors do?)
- ✅ Insights are non-obvious (couldn't get from headlines)
- ✅ Predictions are falsifiable (can be proven right/wrong)
- ✅ Strategic implications are clear

---

## FORBIDDEN PATTERNS

**NEVER write generic statements:**
- ❌ "They have many patents" → ✅ "50 patents, 72% in safety (US20230XXXXX)"
- ❌ "Strong hiring activity" → ✅ "223 jobs, 67% sales, 3x growth vs Q3"
- ❌ "Positive news coverage" → ✅ "WSJ (3/15): 'Anthropic raises $500M' signals..."
- ❌ "Active GitHub presence" → ✅ "anthropic-ai/claude-sdk (12k stars) shows..."

**NEVER just list data without analysis:**
- ❌ Listing 20 job titles → ✅ "These 20 roles cluster into enterprise focus because..."
- ❌ Listing 10 patents → ✅ "These patents reveal roadmap shift to multimodal..."

**NEVER make unsupported claims:**
- ❌ "They're probably launching soon" → ✅ "Q1 2025 launch (hiring surge + patent timing + news)"

---

## EXAMPLES OF EXCELLENCE

**Bad Analysis:**
"Anthropic has many job postings and patents. They're doing well in AI. Expect growth."

**Elite Analysis:**
"Anthropic's 223 jobs (67% enterprise sales, 18% engineering, 8% research) reveal a strategic pivot from research to B2B revenue. This contradicts their public positioning as 'research lab' but aligns with 18 recent enterprise-focused patents (e.g., US20230XXXXX 'Multi-Tenant Safety Isolation'). WSJ headline (3/15) confirmed $500M raise, explaining hiring surge. 15 'Solutions Architect' roles + 'Federal Sales Lead' position signal regulated industry push (healthcare, government). Prediction: Enterprise product GA announcement Q1 2025 (high confidence: hiring velocity + patent timing + news cycle)."

---

**YOUR MISSION**: Be the analyst that gives executives intelligence they can't get anywhere else. Connect dots others miss. Make bold predictions backed by evidence. This is competitive intelligence, not market research.

Now execute this analysis with surgical precision.
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
            return get_patents(arguments["company"], arguments.get("limit", 50))
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


def get_patents(company: str, limit: int = 50):
    """
    Fetch patents from Google BigQuery Patents Public Dataset
    Uses official free public dataset: patents-public-data:patents
    Default limit is 50 to provide comprehensive data for strategic analysis
    """
    try:
        # Try comprehensive query first, fallback to simpler if needed
        logger.info(f"Querying BigQuery for {company} patents (limit: {limit})")
        
        # Query 1: Use verified working schema from user testing
        comprehensive_query = f"""
        SELECT 
            publication_number as patent_number,
            title_localized[SAFE_OFFSET(0)].text as title,
            abstract_localized[SAFE_OFFSET(0)].text as abstract,
            publication_date,
            ARRAY_TO_STRING(assignee, ', ') as assignee_name
        FROM `patents-public-data.patents.publications` 
        WHERE (
            -- Search in assignee array (ARRAY<STRING>)
            EXISTS (
                SELECT 1 FROM UNNEST(assignee) as assignee_name
                WHERE LOWER(assignee_name) LIKE LOWER('%{company}%')
            )
            -- Also search in title/abstract
            OR LOWER(title_localized[SAFE_OFFSET(0)].text) LIKE LOWER('%{company}%')
            OR LOWER(abstract_localized[SAFE_OFFSET(0)].text) LIKE LOWER('%{company}%')
        )
        AND publication_date IS NOT NULL
        AND publication_date >= 20150101  -- INT64 format: YYYYMMDD
        ORDER BY publication_date DESC
        LIMIT {limit}
        """
        
        try:
            logger.debug(f"Trying comprehensive query for {company}")
            query_job = bq_client.query(comprehensive_query)
            results = query_job.result()
            result_list = list(results)
            logger.info(f"Comprehensive query returned {len(result_list)} results")
        except Exception as e:
            logger.warning(f"Comprehensive query failed: {e}, trying simple query...")
            
            # Fallback: Simpler query with just first assignee
            simple_query = f"""
            SELECT 
                publication_number as patent_number,
                title_localized[SAFE_OFFSET(0)].text as title,
                abstract_localized[SAFE_OFFSET(0)].text as abstract,
                publication_date,
                assignee[SAFE_OFFSET(0)] as assignee_name
            FROM `patents-public-data.patents.publications` 
            WHERE LOWER(assignee[SAFE_OFFSET(0)]) LIKE LOWER('%{company}%')
            AND publication_date IS NOT NULL
            AND publication_date >= 20150101  -- INT64 format: YYYYMMDD
            ORDER BY publication_date DESC
            LIMIT {limit}
            """
            
            query_job = bq_client.query(simple_query)
            results = query_job.result()
            result_list = list(results)
            logger.info(f"Simple query returned {len(result_list)} results")
        
        patents = []
        for row in result_list:
            patent = {
                'patent_number': row.patent_number,
                'title': row.title[:200] if row.title else 'No title',
                'abstract': row.abstract[:400] if row.abstract else 'No abstract available',
                'publication_date': str(row.publication_date) if row.publication_date else 'Unknown',
                'assignee': row.assignee_name if row.assignee_name else company,
                'url': f"https://patents.google.com/patent/{row.patent_number}",
                'source': 'Google BigQuery Patents Public Dataset'
            }
            patents.append(patent)
        
        if len(patents) == 0:
            # No results - provide helpful message
            summary = f"No patents found for '{company}' in BigQuery Patents dataset. "
            summary += f"This could mean: (1) Company has no patents filed, (2) Patents filed under different name "
            summary += f"(e.g., '{company} Inc', '{company} PBC', '{company} LLC'), or (3) Company is too new. "
            summary += f"Recommendation: Proceed with analysis using other data sources (jobs, news, GitHub)."
            logger.warning(f"No patents found for {company}")
        else:
            summary = f"Found {len(patents)} patents for {company} from BigQuery. "
            summary += f"Most recent: '{patents[0]['title'][:60]}...'"
            logger.info(f"Successfully fetched {len(patents)} patents for {company} from BigQuery")
        
        return {
            "summary": summary,
            "count": len(patents),
            "patents": patents
        }
            
    except Exception as e:
        logger.error(f"Error querying BigQuery patents: {e}", exc_info=True)
        # Return graceful fallback
        return {
            "summary": f"Patent data for {company} is temporarily unavailable (BigQuery error: {str(e)[:100]}). Analysis will focus on jobs, news, and GitHub data.",
            "count": 0,
            "patents": [],
            "error": str(e)
        }


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
            "all_jobs": jobs  # Return ALL jobs for comprehensive analysis
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
            "all_articles": articles  # Return ALL articles for comprehensive analysis
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
            "total_forks": total_forks,
            "all_repos": repos  # Return ALL repos for comprehensive analysis
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
    # Balanced token limit: enough for complete analysis, conservative on rate limits
    # Gemini 2.5 Pro limits: Free tier ~32K TPM, Pay-as-you-go much higher
    # Typical request: ~6K input + ~10K output = ~16K total tokens
    generation_config = GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=16384,  # 12K: Sweet spot for complete analysis without hitting rate limits
    )
    
    model = GenerativeModel(
        "gemini-2.5-pro",
        tools=[intelligence_tool],
        generation_config=generation_config
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
    
    # Send user message with retry logic for rate limits
    logger.info(f"User query: {user_query}")
    
    @retry.Retry(predicate=retry.if_exception_type(ResourceExhausted), initial=2.0, maximum=60.0, multiplier=2.0, deadline=300.0)
    def send_with_retry(message):
        return chat.send_message(message)
    
    try:
        response = send_with_retry(user_query)
    except ResourceExhausted as e:
        logger.error(f"Rate limit exceeded even after retries: {e}")
        raise Exception("Gemini API rate limit exceeded. Please try again in a few moments.")
    
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
            call_args = dict(function_call.args)
            logger.info(f"Function call {iteration}: {function_call.name}({call_args})")
            
            # Execute function
            function_result = execute_function(function_call.name, call_args)
            
            logger.info(f"Function result: {json.dumps(function_result, default=str)[:200]}...")
            
            # Track this tool call for UI display
            all_tool_calls.append({
                "name": function_call.name,
                "args": call_args,
                "result": function_result
            })
            
            # Create response part
            function_responses.append(
                Part.from_function_response(
                    name=function_call.name,
                    response={"result": function_result}
                )
            )
        
        # Send ALL function results back to model at once with retry
        try:
            response = send_with_retry(function_responses)
        except ResourceExhausted as e:
            logger.error(f"Rate limit during function response: {e}")
            raise Exception("Gemini API rate limit exceeded. Please try again in a few moments.")
    
    # Extract final text response
    if response.candidates and response.candidates[0].content.parts:
        final_response = response.candidates[0].content.parts[0].text
    else:
        final_response = "I apologize, but I encountered an issue generating the analysis. Please try again."
    
    return {
        "response": final_response,
        "conversation_history": chat.history,
        "tool_calls": all_tool_calls  # Include all tool calls for UI display
    }


def run_agent_streaming(user_query: str, conversation_history=None, progress_container=None, data_container=None):
    """
    Run Gemini agent with REAL-TIME streaming updates (like AWS demo)
    Shows tool calls and results AS they happen
    """
    if conversation_history is None:
        conversation_history = []
    
    # Initialize model with conservative settings to avoid rate limits
    generation_config = GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=4096,  # Reduced to conserve quota
    )
    
    model = GenerativeModel(
        "gemini-2.5-pro",
        tools=[intelligence_tool],
        generation_config=generation_config
    )
    
    # Prepend system instruction
    if not conversation_history:
        conversation_history = [
            Content(role="user", parts=[Part.from_text(SYSTEM_INSTRUCTION)]),
            Content(role="model", parts=[Part.from_text("Understood. I am a competitive intelligence analyst with access to patent, job, news, and GitHub data. I will provide strategic analysis with specific evidence and actionable predictions. Ready for your query.")])
        ]
    
    chat = model.start_chat(history=conversation_history)
    
    # Send user message with retry logic
    logger.info(f"User query: {user_query}")
    if progress_container:
        progress_container.markdown("**💭 Analyzing query and planning approach...**")
        progress_container.caption("The AI is deciding which data sources to query and what insights to extract...")
    
    # Retry with exponential backoff for rate limits
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = chat.send_message(user_query)
            break
        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                logger.warning(f"Rate limit hit, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                if progress_container:
                    progress_container.warning(f"⏳ Rate limit reached, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise Exception("API rate limit exceeded. Please wait a moment and try again.")
    
    # Check if there's any reasoning/thinking in the response
    if progress_container and response.candidates:
        for candidate in response.candidates:
            if hasattr(candidate, 'grounding_metadata') or hasattr(candidate, 'reasoning'):
                progress_container.markdown("**🧠 Agent Reasoning:** Planning data collection strategy...")
                break
    
    # Handle function calls with REAL-TIME updates
    max_iterations = 10
    iteration = 0
    all_tool_calls = []
    step_num = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        if not response.candidates or not response.candidates[0].content.parts:
            break
        
        # Collect function calls
        function_calls = []
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                function_calls.append(part.function_call)
        
        if not function_calls:
            break
        
        # SHOW REASONING: Explain WHY these tools were selected
        if progress_container and len(function_calls) > 0:
            tool_names = [fc.name for fc in function_calls]
            reasoning_text = f"**🤔 Agent Decision:** Querying {len(function_calls)} data source(s): {', '.join([t.replace('get_', '') for t in tool_names])}"
            progress_container.info(reasoning_text)
            progress_container.caption("This combination will provide comprehensive signals for strategic analysis...")
            time.sleep(0.3)  # Brief pause to show decision
        
        # Execute each function and show progress in REAL-TIME
        function_responses = []
        for function_call in function_calls:
            step_num += 1
            call_args = dict(function_call.args)
            
            # SHOW TOOL CALL IN REAL-TIME with reasoning
            if progress_container:
                # Explain why this tool matters
                tool_purpose = {
                    'get_patents': 'to understand R&D focus and innovation strategy',
                    'get_jobs': 'to analyze hiring patterns and strategic priorities',
                    'get_news': 'to track public announcements and market perception',
                    'get_github': 'to assess developer community and open-source strategy'
                }
                purpose = tool_purpose.get(function_call.name, 'to gather intelligence')
                
                progress_container.markdown(f"**🔧 Step {step_num}: Calling `{function_call.name}` {purpose}**")
                progress_container.json(call_args, expanded=False)
                time.sleep(0.2)  # Brief pause before execution
            
            logger.info(f"Function call {iteration}: {function_call.name}({call_args})")
            
            # Execute function
            function_result = execute_function(function_call.name, call_args)
            
            # SHOW RESULTS IN REAL-TIME
            if data_container and function_result:
                try:
                    if 'count' in function_result:
                        data_container.success(f"✅ **{function_call.name}**: Found {function_result['count']} items")
                        time.sleep(0.1)  # Brief pause after showing count
                    
                    # Show samples based on tool type
                    if 'all_jobs' in function_result and function_result['all_jobs']:
                        all_jobs = function_result['all_jobs']
                        jobs_preview = all_jobs[:5]  # Show more samples
                        data_container.caption(f"**Sample Jobs ({len(all_jobs)} total):**")
                        for job in jobs_preview:
                            data_container.text(f"• {job.get('title', 'N/A')} - {job.get('department', 'N/A')}")
                            time.sleep(0.05)  # Tiny pause between items
                        if len(all_jobs) > 5:
                            data_container.caption(f"_...and {len(all_jobs) - 5} more (all sent to AI for analysis)_")
                    
                    elif 'patents' in function_result and function_result['patents']:
                        patents = function_result['patents'][:3]
                        data_container.caption("**Sample Patents:**")
                        for patent in patents:
                            data_container.text(f"• {patent.get('title', 'N/A')[:60]}...")
                            time.sleep(0.05)
                    
                    elif 'all_articles' in function_result and function_result['all_articles']:
                        articles = function_result['all_articles'][:3]
                        data_container.caption("**Sample Headlines:**")
                        for article in articles:
                            data_container.text(f"• {article.get('title', 'N/A')[:70]}...")
                            time.sleep(0.05)
                    
                    elif 'all_repos' in function_result and function_result['all_repos']:
                        repos = function_result['all_repos'][:3]
                        data_container.caption("**Top Repositories:**")
                        for repo in repos:
                            data_container.text(f"• {repo.get('name', 'N/A')} ({repo.get('stars', 0):,} ★)")
                            time.sleep(0.05)
                    
                except Exception as e:
                    logger.warning(f"Error showing preview: {e}")
            
            logger.info(f"Function result: {json.dumps(function_result, default=str)[:200]}...")
            
            # Track for history
            all_tool_calls.append({
                "name": function_call.name,
                "args": call_args,
                "result": function_result
            })
            
            # Create response part
            function_responses.append(
                Part.from_function_response(
                    name=function_call.name,
                    response={"result": function_result}
                )
            )
        
        # Send all function results back with retry logic
        if progress_container:
            progress_container.markdown("**🤔 Agent synthesizing insights...**")
            time.sleep(0.3)  # Pause before synthesis
        
        # Retry with exponential backoff for rate limits
        for attempt in range(max_retries):
            try:
                response = chat.send_message(function_responses)
                break
            except ResourceExhausted as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2
                    logger.warning(f"Rate limit hit during synthesis, retrying in {wait_time}s...")
                    if progress_container:
                        progress_container.warning(f"⏳ Rate limit reached, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception("API rate limit exceeded. Please wait a moment and try again.")
    
    # Extract final response
    if response.candidates and response.candidates[0].content.parts:
        final_response = response.candidates[0].content.parts[0].text
    else:
        final_response = "I apologize, but I encountered an issue generating the analysis. Please try again."
    
    return {
        "response": final_response,
        "conversation_history": chat.history,
        "tool_calls": all_tool_calls
    }


# For testing
if __name__ == "__main__":
    result = run_agent("Analyze Anthropic's strategic direction. What are they building and who are they targeting?")
    print(result["response"])
