"""
Reusable UI Components for Patent Tracker
"""
import streamlit as st
from typing import Dict, List, Any

def metric_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """Display a styled metric card"""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 2.5rem; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.metric(label, value, delta)


def insight_card(title: str, content: str, icon: str = "💡", color: str = "blue"):
    """Display an insight card with custom styling"""
    color_map = {
        "blue": "#1E88E5",
        "purple": "#7C4DFF",
        "green": "#43A047",
        "orange": "#FB8C00",
        "red": "#E53935"
    }
    
    border_color = color_map.get(color, "#1E88E5")
    
    st.markdown(f"""
    <div style="
        border-left: 4px solid {border_color};
        background: linear-gradient(to right, rgba(30, 136, 229, 0.05), transparent);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    ">
        <h4 style="margin: 0 0 0.5rem 0; color: {border_color};">{icon} {title}</h4>
        <p style="margin: 0; color: #424242;">{content}</p>
    </div>
    """, unsafe_allow_html=True)


def data_source_badge(source_name: str, count: int, icon: str = "📊"):
    """Display a data source badge with count"""
    st.markdown(f"""
    <div style="
        display: inline-block;
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <span style="font-size: 1.2rem;">{icon}</span>
        <span style="font-weight: 600; margin-left: 0.5rem;">{source_name}</span>
        <span style="
            background: linear-gradient(135deg, #1E88E5, #7C4DFF);
            color: white;
            border-radius: 12px;
            padding: 0.2rem 0.6rem;
            margin-left: 0.5rem;
            font-size: 0.85rem;
            font-weight: 600;
        ">{count}</span>
    </div>
    """, unsafe_allow_html=True)


def confidence_badge(confidence: str):
    """Display a confidence level badge"""
    colors = {
        "high": ("🟢", "#43A047"),
        "medium": ("🔵", "#1E88E5"),
        "low": ("🟡", "#FB8C00")
    }
    
    emoji, color = colors.get(confidence.lower(), ("🔵", "#1E88E5"))
    
    st.markdown(f"""
    <span style="
        background: {color};
        color: white;
        border-radius: 12px;
        padding: 0.3rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    ">{emoji} {confidence.upper()}</span>
    """, unsafe_allow_html=True)


def prediction_card(timeframe: str, prediction: str, confidence: str = "medium"):
    """Display a prediction card with timeframe and confidence"""
    st.markdown(f"""
    <div style="
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    ">
        <h4 style="margin: 0 0 0.5rem 0; color: #1E88E5;">🔮 {timeframe}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    confidence_badge(confidence)
    st.markdown(f"<p style='margin-top: 0.5rem; color: #424242;'>{prediction}</p>", unsafe_allow_html=True)


def executive_summary_card(content: str):
    """Display the executive summary in a prominent card"""
    # Clean up markdown formatting for display
    import re
    # Remove markdown bold/italic that doesn't render in HTML
    display_content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
    display_content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', display_content)
    # Convert line breaks
    display_content = display_content.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(30, 136, 229, 0.1), rgba(124, 77, 255, 0.1));
        border: 2px solid #1E88E5;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.15);
    ">
        <h3 style="margin: 0 0 1rem 0; color: #1E88E5;">🎯 Executive Summary</h3>
        <div style="font-size: 1.05rem; line-height: 1.7; color: #424242;">
            {display_content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def metrics_dashboard(metrics: Dict[str, int]):
    """Display a row of key metrics"""
    st.markdown("### 📊 Key Metrics")
    
    cols = st.columns(len(metrics))
    
    icons = {
        "Patents": "📜",
        "Jobs": "👥",
        "News": "📰",
        "GitHub": "💻",
        "Total": "📊"
    }
    
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            icon = icons.get(label, "📊")
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 1.5rem;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 2rem; font-weight: 700; color: #1E88E5; margin-bottom: 0.25rem;">{value}</div>
                <div style="font-size: 0.85rem; color: #757575; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def follow_up_button(question: str, key: str):
    """Display a follow-up question button"""
    if st.button(f"💬 {question}", key=key, use_container_width=True):
        return question
    return None


def section_header(title: str, icon: str = "📋"):
    """Display a styled section header"""
    st.markdown(f"""
    <div style="
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E0E0E0;
    ">
        <h2 style="margin: 0; color: #1E88E5;">{icon} {title}</h2>
    </div>
    """, unsafe_allow_html=True)


def status_indicator(status: str, message: str):
    """Display a status indicator"""
    status_config = {
        "success": ("✅", "#43A047", "rgba(67, 160, 71, 0.1)"),
        "warning": ("⚠️", "#FB8C00", "rgba(251, 140, 0, 0.1)"),
        "error": ("❌", "#E53935", "rgba(229, 57, 53, 0.1)"),
        "info": ("ℹ️", "#1E88E5", "rgba(30, 136, 229, 0.1)")
    }
    
    emoji, color, bg = status_config.get(status, ("ℹ️", "#1E88E5", "rgba(30, 136, 229, 0.1)"))
    
    st.markdown(f"""
    <div style="
        background: {bg};
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    ">
        <span style="font-size: 1.2rem; margin-right: 0.5rem;">{emoji}</span>
        <span style="color: #424242;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def download_button(label: str, data: str, filename: str, mime: str = "text/markdown"):
    """Styled download button"""
    return st.download_button(
        label=f"📥 {label}",
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True
    )


def tool_call_summary_card(tool_calls: List[Dict[str, Any]]):
    """Display a summary card of all tool calls"""
    if not tool_calls:
        return
    
    total_items = sum(call.get('result', {}).get('count', 0) for call in tool_calls)
    sources = list(set(call['name'].replace('get_', '').title() for call in tool_calls))
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(to right, rgba(124, 77, 255, 0.1), transparent);
        border: 1px solid #7C4DFF;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 0.5rem 0; color: #7C4DFF;">🛠️ Data Collection Summary</h4>
        <p style="margin: 0; color: #424242;">
            Queried <strong>{len(tool_calls)}</strong> data sources ({', '.join(sources)}) 
            and analyzed <strong>{total_items}</strong> total data points.
        </p>
    </div>
    """, unsafe_allow_html=True)


def tool_results_card_enhanced(tool_calls: List[Dict[str, Any]]):
    """Enhanced tool results visualization with progress bars and insights"""
    if not tool_calls:
        return
    
    st.markdown("""
    <div style="
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    ">
        <h3 style="margin: 0 0 1.5rem 0; color: #1E88E5;">🔍 Data Collection Summary</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create grid layout for data sources
    cols = st.columns(min(len(tool_calls), 4))
    
    icons = {
        "get_patents": ("📜", "Patents"),
        "get_jobs": ("👥", "Jobs"),
        "get_news": ("📰", "News"),
        "get_github": ("💻", "GitHub")
    }
    
    for idx, call in enumerate(tool_calls):
        with cols[idx % len(cols)]:
            function_name = call.get('name', '')
            icon, display_name = icons.get(function_name, ("📊", function_name.replace('get_', '').title()))
            count = call.get('result', {}).get('count', 0)
            summary = call.get('result', {}).get('summary', '')
            
            # Extract key insight from summary
            key_insight = ""
            if summary:
                # Try to extract first meaningful line
                lines = summary.split('.')[0:2]
                key_insight = '. '.join(lines)[:80] + "..." if len('. '.join(lines)) > 80 else '. '.join(lines)
            
            # Calculate progress bar (visual indicator)
            max_expected = {"Patents": 50, "Jobs": 300, "News": 100, "GitHub": 50}
            expected = max_expected.get(display_name, 50)
            progress = min(100, int((count / expected) * 100)) if expected > 0 else 0
            
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                min-height: 180px;
            ">
                <div style="font-size: 2rem; text-align: center; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 0.9rem; font-weight: 600; color: #757575; text-align: center; margin-bottom: 0.5rem;">{display_name.upper()}</div>
                
                <!-- Progress bar -->
                <div style="
                    background: #F0F0F0;
                    border-radius: 10px;
                    height: 8px;
                    margin: 0.5rem 0;
                    overflow: hidden;
                ">
                    <div style="
                        background: linear-gradient(90deg, #1E88E5, #7C4DFF);
                        height: 100%;
                        width: {progress}%;
                        border-radius: 10px;
                        transition: width 0.3s ease;
                    "></div>
                </div>
                
                <div style="font-size: 1.8rem; font-weight: 700; color: #1E88E5; text-align: center; margin: 0.5rem 0;">{count}</div>
                <div style="font-size: 0.75rem; color: #757575; text-align: center;">items found</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed expandable section
    with st.expander("📋 View Detailed Data", expanded=False):
        for idx, call in enumerate(tool_calls, 1):
            function_name = call.get('name', 'unknown')
            icon, display_name = icons.get(function_name, ("📊", function_name.replace('get_', '').title()))
            
            st.markdown(f"### {icon} {display_name} - Call #{idx}")
            
            # Parameters
            st.markdown("**Parameters:**")
            st.json(call.get('args', {}), expanded=False)
            
            # Results
            if 'result' in call:
                result = call['result']
                if 'summary' in result:
                    st.success(f"**Summary:** {result['summary']}")
                if 'count' in result:
                    st.info(f"📊 **Total Items:** {result['count']}")
                if 'sample_data' in result and result['sample_data']:
                    st.markdown("**Sample Data:**")
                    st.json(result['sample_data'][:3], expanded=False)  # Show first 3 items
            
            if idx < len(tool_calls):
                st.divider()


def reasoning_timeline(phases: List[Dict[str, Any]]):
    """Display agent reasoning as a visual timeline/workflow"""
    st.markdown("""
    <div style="
        background: linear-gradient(to bottom, #F8F9FA, white);
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 1rem 0; color: #1E88E5;">🧠 Agent Workflow</h4>
    </div>
    """, unsafe_allow_html=True)
    
    phase_icons = {
        "strategy": "🎯",
        "collection": "📥",
        "analysis": "🔍",
        "synthesis": "🧩",
        "predictions": "🔮"
    }
    
    for idx, phase in enumerate(phases, 1):
        status = phase.get('status', 'pending')  # complete, active, pending
        name = phase.get('name', 'Unknown Phase')
        description = phase.get('description', '')
        phase_type = phase.get('type', 'strategy')
        icon = phase_icons.get(phase_type, "⚙️")
        
        # Status styling
        if status == 'complete':
            status_icon = "✓"
            border_color = "#43A047"
            bg_color = "rgba(67, 160, 71, 0.05)"
        elif status == 'active':
            status_icon = "⚡"
            border_color = "#1E88E5"
            bg_color = "rgba(30, 136, 229, 0.08)"
        else:
            status_icon = " "
            border_color = "#E0E0E0"
            bg_color = "#FAFAFA"
        
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border-left: 4px solid {border_color};
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            position: relative;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="
                    font-size: 1.5rem;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: white;
                    border-radius: 50%;
                    border: 2px solid {border_color};
                    font-weight: bold;
                    color: {border_color};
                ">{status_icon}</span>
                <span style="font-size: 1.2rem;">{icon}</span>
                <strong style="color: #212121;">{name}</strong>
            </div>
            {f'<p style="margin: 0.5rem 0 0 3.5rem; color: #757575; font-size: 0.9rem;">{description}</p>' if description else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Connection line to next phase
        if idx < len(phases):
            st.markdown("""
            <div style="
                margin-left: 1.5rem;
                width: 2px;
                height: 15px;
                background: #E0E0E0;
            "></div>
            """, unsafe_allow_html=True)


def analysis_accordion_section(title: str, icon: str, preview: str, content: str, expanded: bool = False):
    """Accordion-style section for strategic analysis with preview"""
    with st.expander(f"{icon} **{title}**", expanded=expanded):
        if preview and not expanded:
            st.markdown(f"*{preview}*")
            st.markdown("---")
        
        st.markdown(content)


def enhanced_prediction_display(predictions: List[Dict[str, Any]]):
    """Enhanced prediction cards with timeline and confidence"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(124, 77, 255, 0.05), rgba(30, 136, 229, 0.05));
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
    ">
        <h3 style="margin: 0 0 1.5rem 0; color: #7C4DFF; text-align: center;">🔮 STRATEGIC PREDICTIONS</h3>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(predictions) if predictions else 3)
    
    for idx, pred in enumerate(predictions):
        with cols[idx]:
            timeframe = pred.get('timeframe', '30 Days')
            prediction_text = pred.get('prediction', '')
            confidence = pred.get('confidence', 'medium')
            evidence = pred.get('evidence', [])
            
            # Confidence color
            conf_colors = {
                'high': ('#43A047', '🟢'),
                'medium': ('#1E88E5', '🔵'),
                'low': ('#FB8C00', '🟡')
            }
            color, emoji = conf_colors.get(confidence.lower(), ('#1E88E5', '🔵'))
            
            st.markdown(f"""
            <div style="
                background: white;
                border: 2px solid {color};
                border-radius: 12px;
                padding: 1.5rem;
                min-height: 250px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            ">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 0.85rem; color: #757575; text-transform: uppercase; letter-spacing: 1px;">{timeframe}</div>
                    <div style="margin: 0.5rem 0;">
                        <span style="
                            background: {color};
                            color: white;
                            padding: 0.4rem 1rem;
                            border-radius: 20px;
                            font-size: 0.8rem;
                            font-weight: 600;
                        ">{emoji} {confidence.upper()}</span>
                    </div>
                </div>
                <div style="color: #212121; font-size: 0.95rem; line-height: 1.6;">
                    {prediction_text[:150]}{'...' if len(prediction_text) > 150 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Evidence in expander
            if evidence:
                with st.expander("📊 View Evidence"):
                    for ev in evidence:
                        st.markdown(f"- {ev}")


def key_takeaways_card(takeaways: List[str]):
    """Display key takeaways in a prominent card"""
    if not takeaways:
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 152, 0, 0.1));
        border-left: 5px solid #FFA726;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    ">
        <h4 style="margin: 0 0 1rem 0; color: #F57C00;">💡 Key Takeaways</h4>
    </div>
    """, unsafe_allow_html=True)
    
    for takeaway in takeaways:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: start;
            margin: 0.75rem 0;
            padding: 0.75rem;
            background: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        ">
            <span style="color: #FFA726; font-size: 1.2rem; margin-right: 0.75rem;">▸</span>
            <span style="color: #424242; line-height: 1.5;">{takeaway}</span>
        </div>
        """, unsafe_allow_html=True)
