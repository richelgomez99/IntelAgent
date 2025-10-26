"""
Data Visualization Helpers
Simple chart generation for tool results
"""
import streamlit as st
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px


def create_job_breakdown_chart(job_data: List[Dict[str, Any]]) -> go.Figure:
    """Create a pie chart showing job department breakdown"""
    if not job_data:
        return None
    
    # Extract departments from job titles (simplified logic)
    departments = {}
    for job in job_data:
        title = job.get('title', '').lower()
        
        # Simple keyword matching for departments
        if any(word in title for word in ['engineer', 'developer', 'technical', 'software']):
            dept = 'Engineering'
        elif any(word in title for word in ['sales', 'account', 'business development']):
            dept = 'Sales'
        elif any(word in title for word in ['research', 'scientist', 'ml', 'ai']):
            dept = 'Research'
        elif any(word in title for word in ['operations', 'ops', 'program manager']):
            dept = 'Operations'
        elif any(word in title for word in ['finance', 'accounting', 'controller']):
            dept = 'Finance'
        elif any(word in title for word in ['hr', 'recruiter', 'people']):
            dept = 'HR'
        elif any(word in title for word in ['marketing', 'content', 'social']):
            dept = 'Marketing'
        else:
            dept = 'Other'
        
        departments[dept] = departments.get(dept, 0) + 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(departments.keys()),
        values=list(departments.values()),
        hole=0.3,
        marker=dict(colors=['#1E88E5', '#7C4DFF', '#43A047', '#FB8C00', '#E53935', '#00ACC1', '#8E24AA', '#757575'])
    )])
    
    fig.update_layout(
        title="Job Distribution by Department",
        showlegend=True,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_patent_timeline(patent_data: List[Dict[str, Any]]) -> go.Figure:
    """Create a timeline visualization of patent filings"""
    if not patent_data:
        return None
    
    # Extract dates and titles
    dates = []
    titles = []
    
    for patent in patent_data:
        pub_date = patent.get('publication_date', '')
        if pub_date and len(str(pub_date)) == 8:  # Format: YYYYMMDD
            try:
                year = str(pub_date)[:4]
                month = str(pub_date)[4:6]
                day = str(pub_date)[6:8]
                date_str = f"{year}-{month}-{day}"
                dates.append(date_str)
                titles.append(patent.get('title', 'Untitled')[:60] + '...')
            except:
                continue
    
    if not dates:
        return None
    
    fig = go.Figure(data=go.Scatter(
        x=dates,
        y=[1] * len(dates),
        mode='markers',
        marker=dict(size=12, color='#1E88E5'),
        text=titles,
        hovertemplate='<b>%{text}</b><br>Date: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Patent Filing Timeline",
        xaxis_title="Publication Date",
        yaxis=dict(visible=False),
        height=300,
        margin=dict(l=20, r=20, t=40, b=40),
        hovermode='closest'
    )
    
    return fig


def create_source_comparison_chart(tool_calls: List[Dict[str, Any]]) -> go.Figure:
    """Create a bar chart comparing data sources"""
    if not tool_calls:
        return None
    
    sources = []
    counts = []
    colors = []
    
    color_map = {
        'Patents': '#1E88E5',
        'Jobs': '#7C4DFF',
        'News': '#43A047',
        'GitHub': '#FB8C00'
    }
    
    for call in tool_calls:
        name = call.get('name', '').replace('get_', '').title()
        count = call.get('result', {}).get('count', 0)
        sources.append(name)
        counts.append(count)
        colors.append(color_map.get(name, '#757575'))
    
    fig = go.Figure(data=[go.Bar(
        x=sources,
        y=counts,
        marker=dict(color=colors),
        text=counts,
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Data Sources Overview",
        xaxis_title="Source",
        yaxis_title="Items Collected",
        height=350,
        margin=dict(l=20, r=20, t=40, b=40),
        showlegend=False
    )
    
    return fig


def create_metrics_sparkline(values: List[int], color: str = "#1E88E5") -> go.Figure:
    """Create a simple sparkline for trending metrics"""
    if not values or len(values) < 2:
        return None
    
    fig = go.Figure(data=go.Scatter(
        y=values,
        mode='lines',
        fill='tozeroy',
        line=dict(color=color, width=2),
        fillcolor=f'rgba(30, 136, 229, 0.1)'
    ))
    
    fig.update_layout(
        showlegend=False,
        height=60,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def display_enhanced_metrics_with_charts(metrics: Dict[str, int], tool_calls: List[Dict[str, Any]] = None):
    """Display metrics dashboard with optional charts"""
    st.markdown("### 📊 Data Collection Overview")
    
    # Show metrics
    cols = st.columns(len(metrics))
    
    icons = {
        "Patents": "📜",
        "Jobs": "👥",
        "News": "📰",
        "GitHub": "💻"
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
    
    # Optional: Show comparison chart
    if tool_calls and len(tool_calls) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            chart = create_source_comparison_chart(tool_calls)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        except Exception as e:
            pass  # Silently fail if chart generation fails
