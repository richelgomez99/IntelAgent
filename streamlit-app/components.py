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
