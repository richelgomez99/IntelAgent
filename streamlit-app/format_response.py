"""
Format AI responses into beautiful, structured displays
"""
import streamlit as st
import re
from components import (
    executive_summary_card,
    section_header,
    insight_card,
    prediction_card,
    confidence_badge,
    key_takeaways_card,
    analysis_accordion_section
)

def format_strategic_response(response_text):
    """
    Parse and beautifully format the AI's strategic analysis response
    Extracts sections and displays them with cards, metrics, and structure
    """
    
    # Try to identify sections in the response
    sections = parse_sections(response_text)
    
    # Extract key takeaways from executive summary
    takeaways = extract_key_takeaways(response_text)
    
    if sections:
        display_formatted_sections(sections, takeaways)
    else:
        # Fallback to enhanced text display
        st.markdown(response_text)


def parse_sections(text):
    """Extract structured sections from the response"""
    sections = {}
    
    # Common section patterns - must match section headers, not just words in text
    patterns = {
        # Executive Summary: stops at next ## header or explicit "Strategic Reasoning" section
        'executive_summary': r'(?:##?\s*)?(?:Executive Summary|🎯 Executive Summary)[\s:]*\n(.+?)(?=\n##\s+(?:Strategic Reasoning|📊|🧠|Step|Predictions)|$)',
        # Strategic Reasoning: everything between Strategic Reasoning and Predictions headers
        'strategic_reasoning': r'(?:##?\s*)?(?:Strategic Reasoning|Detailed Strategic Analysis|🧠)[\s:]*\n(.+?)(?=\n##\s+(?:Predictions|Evidence-Based Predictions|🔮|Step 3)|$)',
        # Predictions: from Predictions header to end
        'predictions': r'(?:##?\s*)?(?:Predictions|Evidence-Based Predictions|Strategic Predictions|🔮)[\s:]*\n(.+?)$',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()
    
    return sections if sections else None


def extract_key_takeaways(text: str) -> list:
    """Extract key takeaways/insights from the response"""
    takeaways = []
    
    # Look for bullet points or numbered insights
    patterns = [
        r'[-•▸]\s+([^\n]{30,150})',  # Bullet points with substantial content
        r'\d+\.\s+([^\n]{30,150})',  # Numbered lists
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        takeaways.extend([match.strip() for match in matches if len(match.strip()) > 30])
    
    # Also try to extract from specific sections like "Key Takeaways:"
    takeaway_section = re.search(r'Key Takeaways:(.+?)(?=\n##|$)', text, re.DOTALL | re.IGNORECASE)
    if takeaway_section:
        content = takeaway_section.group(1)
        lines = [line.strip(' -•▸') for line in content.split('\n') if line.strip() and len(line.strip()) > 20]
        takeaways.extend(lines[:5])  # Limit to 5
    
    # Deduplicate and limit
    seen = set()
    unique_takeaways = []
    for t in takeaways:
        if t.lower() not in seen and len(unique_takeaways) < 6:
            seen.add(t.lower())
            unique_takeaways.append(t)
    
    return unique_takeaways


def display_formatted_sections(sections, takeaways=None):
    """Display sections with beautiful formatting using custom components"""
    
    # Executive Summary at top - use custom card
    if 'executive_summary' in sections:
        executive_summary_card(sections['executive_summary'])
        
        # Display key takeaways if extracted
        if takeaways:
            key_takeaways_card(takeaways)
    
    # Strategic Reasoning - enhanced with tabs and cards
    if 'strategic_reasoning' in sections:
        section_header("Detailed Strategic Analysis", "🧠")
        
        reasoning = sections['strategic_reasoning']
        
        # Extract sub-sections
        subsections = extract_analysis_subsections(reasoning)
        
        if subsections and len(subsections) > 1:
            # Show tabs for different analysis types
            tab_names = list(subsections.keys())
            tabs = st.tabs([format_tab_name(name) for name in tab_names])
            
            for tab, (name, content) in zip(tabs, subsections.items()):
                with tab:
                    # Display in expandable card for better organization
                    st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 1.5rem;
                        border-radius: 8px;
                        border: 1px solid #E0E0E0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    ">
                    """, unsafe_allow_html=True)
                    
                    # Parse bullet points and highlights
                    display_analysis_content(content, name)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Display full analysis in expandable section
            st.markdown(f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                margin-bottom: 1rem;
            ">
            """, unsafe_allow_html=True)
            st.markdown(reasoning)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Predictions with confidence levels
    if 'predictions' in sections:
        section_header("Strategic Predictions", "🔮")
        display_predictions(sections['predictions'])


def extract_analysis_subsections(text):
    """Extract analysis subsections like Patent Analysis, Hiring Patterns, etc."""
    subsections = {}
    
    # Look for bold headings with specific analysis sections
    # Pattern: **Title Analysis:** or **Title:**
    patterns = [
        r'\*\*([^*]+Analysis[^*]*)\*\*[\s:]*\n(.+?)(?=\n\*\*[^*]+Analysis|\n\*\*Cross-Signal|$)',
        r'\*\*([^*]+Pattern[^*]*)\*\*[\s:]*\n(.+?)(?=\n\*\*[^*]+|\n##|$)',
        r'\*\*Cross-Signal Correlation:\*\*(.+?)(?=\n##|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
        for match in matches:
            if len(match.groups()) == 2:
                title = match.group(1).strip()
                content = match.group(2).strip()
            else:
                title = "Cross-Signal Correlation"
                content = match.group(1).strip()
            
            if content:  # Only add if there's actual content
                subsections[title] = content
    
    return subsections


def display_analysis_content(content, section_name=""):
    """Display analysis content with highlighting and cards"""
    
    # Extract key insights (bullet points)
    lines = content.split('\n')
    insights = []
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_text:
                insights.append(' '.join(current_text))
                current_text = []
            continue
            
        # Highlight key points
        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
            # This is a bullet point
            clean_line = line.lstrip('-•* ')
            
            # Check if it's a highlighted insight
            if any(keyword in clean_line.lower() for keyword in ['critical', 'key', 'important', 'significant', 'strategic']):
                if current_text:
                    insights.append(' '.join(current_text))
                    current_text = []
                
                # Extract title from first few words
                words = clean_line.split()
                if len(words) > 10:
                    title = ' '.join(words[:6]) + "..."
                else:
                    title = clean_line[:50]
                
                # Use insight card for important items
                color = "blue" if "patent" in section_name.lower() else \
                        "purple" if "hiring" in section_name.lower() or "job" in section_name.lower() else \
                        "orange" if "news" in section_name.lower() else \
                        "green" if "github" in section_name.lower() else "blue"
                
                insight_card(title, clean_line, "💡", color)
            else:
                st.markdown(f"- {clean_line}")
        else:
            current_text.append(line)
    
    # Display any remaining text
    if current_text:
        st.markdown(' '.join(current_text))


def display_predictions(predictions_text):
    """Display predictions with confidence indicators using cards"""
    
    # Parse predictions by timeframe
    timeframes = {
        '30-Day Forecast': r'30-Day[^:]*:(.+?)(?=60-Day|90-Day|$)',
        '60-Day Forecast': r'60-Day[^:]*:(.+?)(?=90-Day|$)',
        '90-Day Forecast': r'90-Day[^:]*:(.+?)$'
    }
    
    cols = st.columns(3)
    
    for idx, (timeframe, pattern) in enumerate(timeframes.items()):
        match = re.search(pattern, predictions_text, re.DOTALL | re.IGNORECASE)
        
        if match:
            prediction = match.group(1).strip()
            
            # Extract confidence if mentioned
            confidence = 'medium'
            if 'high confidence' in prediction.lower():
                confidence = 'high'
            elif 'low confidence' in prediction.lower() or 'lower confidence' in prediction.lower():
                confidence = 'low'
            
            with cols[idx]:
                # Use custom prediction card
                st.markdown(f"""
                <div style="
                    background: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                    height: 100%;
                ">
                    <h4 style="margin: 0 0 0.5rem 0; color: #1E88E5;">🔮 {timeframe}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                confidence_badge(confidence)
                
                with st.expander("📋 View Details", expanded=False):
                    # Display full prediction without truncation
                    st.markdown(prediction)


def format_tab_name(name):
    """Format subsection name for tab display"""
    # Remove "Analysis" suffix for cleaner tabs
    name = name.replace(' Analysis', '').replace(' Pattern', '')
    
    # Add appropriate emoji
    emoji_map = {
        'patent': '📜',
        'hiring': '👥',
        'job': '👥',
        'news': '📰',
        'github': '💻',
        'cross-signal': '🔗',
        'correlation': '🔗'
    }
    
    for key, emoji in emoji_map.items():
        if key in name.lower():
            return f"{emoji} {name}"
    
    return name
