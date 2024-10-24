"""
Report Export Functionality
Generates downloadable reports in multiple formats
"""
from datetime import datetime
from typing import Dict, List, Any
import json

def generate_markdown_report(company: str, response: str, tool_calls: List[Dict[str, Any]]) -> str:
    """Generate a Markdown formatted report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract metrics from tool calls
    metrics = {}
    for call in tool_calls:
        source = call['name'].replace('get_', '').title()
        count = call.get('result', {}).get('count', 0)
        metrics[source] = count
    
    total_data_points = sum(metrics.values())
    
    # Build the markdown
    md = f"""# Competitive Intelligence Report: {company}

**Generated:** {timestamp}  
**Analysis Type:** Multi-Source Strategic Intelligence  
**Data Sources:** {len(tool_calls)} ({', '.join(metrics.keys())})  
**Total Data Points Analyzed:** {total_data_points}

---

## 📊 Data Collection Summary

"""
    
    for source, count in metrics.items():
        icon = {
            'Patents': '📜',
            'Jobs': '👥',
            'News': '📰',
            'Github': '💻'
        }.get(source, '📊')
        md += f"- **{icon} {source}:** {count} items analyzed\n"
    
    md += f"\n---\n\n## 🧠 Strategic Analysis\n\n{response}\n\n---\n\n"
    
    # Add detailed data sources section
    md += "## 📋 Detailed Data Sources\n\n"
    
    for i, call in enumerate(tool_calls, 1):
        md += f"### {i}. {call['name'].replace('_', ' ').title()}\n\n"
        md += f"**Parameters:**\n```json\n{json.dumps(call['args'], indent=2)}\n```\n\n"
        
        result = call.get('result', {})
        if 'summary' in result:
            md += f"**Result:** {result['summary']}\n\n"
        
        if 'count' in result:
            md += f"**Items Found:** {result['count']}\n\n"
    
    # Footer
    md += f"""---

## 📝 Methodology

This report was generated using AI-powered competitive intelligence analysis combining:

1. **Patent Analysis** - USPTO patent filings via Google Patents API
2. **Hiring Intelligence** - Job postings from Greenhouse career pages
3. **News Monitoring** - Google News RSS feed analysis
4. **Developer Activity** - GitHub repository tracking

The analysis uses Google's Gemini 2.5 Pro model with function calling to orchestrate 
data collection and synthesis strategic insights across multiple sources.

---

**Patent Tracker** | Powered by Google Cloud, Vertex AI & Gemini  
*Generated on {timestamp}*
"""
    
    return md


def generate_html_report(company: str, response: str, tool_calls: List[Dict[str, Any]]) -> str:
    """Generate an HTML formatted report with styling"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract metrics
    metrics = {}
    for call in tool_calls:
        source = call['name'].replace('get_', '').title()
        count = call.get('result', {}).get('count', 0)
        metrics[source] = count
    
    total_data_points = sum(metrics.values())
    
    # Convert markdown-style response to HTML paragraphs
    response_html = response.replace('\n\n', '</p><p>').replace('\n', '<br>')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Competitive Intelligence Report: {company}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            background: #FAFAFA;
            color: #212121;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1E88E5, #7C4DFF);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
        }}
        
        .header h1 {{
            margin: 0 0 1rem 0;
            font-size: 2rem;
        }}
        
        .header .meta {{
            opacity: 0.95;
            font-size: 0.95rem;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .metric-card {{
            background: white;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .metric-card .icon {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .metric-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: #1E88E5;
            margin-bottom: 0.25rem;
        }}
        
        .metric-card .label {{
            font-size: 0.85rem;
            color: #757575;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .section {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            border-left: 4px solid #1E88E5;
        }}
        
        .section h2 {{
            color: #1E88E5;
            margin-top: 0;
            border-bottom: 2px solid #E0E0E0;
            padding-bottom: 0.5rem;
        }}
        
        .analysis {{
            background: linear-gradient(to right, rgba(30, 136, 229, 0.05), transparent);
        }}
        
        .footer {{
            text-align: center;
            color: #757575;
            padding: 2rem 0;
            border-top: 1px solid #E0E0E0;
            margin-top: 3rem;
        }}
        
        .tool-call {{
            background: #F5F5F5;
            border: 1px solid #E0E0E0;
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
        }}
        
        .tool-call h4 {{
            margin: 0 0 0.5rem 0;
            color: #7C4DFF;
        }}
        
        code {{
            background: #F5F5F5;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .section {{
                box-shadow: none;
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Competitive Intelligence Report</h1>
        <h2 style="margin: 0 0 1rem 0; font-weight: 500;">{company}</h2>
        <div class="meta">
            <div><strong>Generated:</strong> {timestamp}</div>
            <div><strong>Analysis Type:</strong> Multi-Source Strategic Intelligence</div>
            <div><strong>Data Sources:</strong> {len(tool_calls)} ({', '.join(metrics.keys())})</div>
            <div><strong>Total Data Points:</strong> {total_data_points}</div>
        </div>
    </div>
    
    <div class="metrics">
"""
    
    # Add metric cards
    icons = {
        'Patents': '📜',
        'Jobs': '👥',
        'News': '📰',
        'Github': '💻'
    }
    
    for source, count in metrics.items():
        icon = icons.get(source, '📊')
        html += f"""
        <div class="metric-card">
            <div class="icon">{icon}</div>
            <div class="value">{count}</div>
            <div class="label">{source}</div>
        </div>
"""
    
    html += f"""
    </div>
    
    <div class="section analysis">
        <h2>🧠 Strategic Analysis</h2>
        <p>{response_html}</p>
    </div>
    
    <div class="section">
        <h2>📋 Data Sources</h2>
"""
    
    # Add tool call details
    for i, call in enumerate(tool_calls, 1):
        result = call.get('result', {})
        summary = result.get('summary', 'No summary available')
        count = result.get('count', 0)
        
        html += f"""
        <div class="tool-call">
            <h4>{i}. {call['name'].replace('_', ' ').title()}</h4>
            <p><strong>Result:</strong> {summary}</p>
            <p><strong>Items Found:</strong> {count}</p>
        </div>
"""
    
    html += f"""
    </div>
    
    <div class="footer">
        <p><strong>Patent Tracker</strong> | Powered by Google Cloud, Vertex AI & Gemini</p>
        <p style="font-size: 0.9rem;">Generated on {timestamp}</p>
    </div>
</body>
</html>
"""
    
    return html


def generate_json_export(company: str, response: str, tool_calls: List[Dict[str, Any]]) -> str:
    """Generate a JSON export with full data"""
    
    export_data = {
        "metadata": {
            "company": company,
            "generated_at": datetime.now().isoformat(),
            "report_type": "competitive_intelligence",
            "version": "1.0"
        },
        "summary": {
            "total_sources": len(tool_calls),
            "total_data_points": sum(call.get('result', {}).get('count', 0) for call in tool_calls)
        },
        "analysis": response,
        "data_sources": tool_calls
    }
    
    return json.dumps(export_data, indent=2, default=str)
