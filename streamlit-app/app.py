"""
Patent Tracker - Competitive Intelligence Dashboard
Built for Google Cloud AI Hackathon 2025
"""
import streamlit as st
from gemini_agent import run_agent, run_agent_streaming
from format_response import format_strategic_response
from export import generate_markdown_report, generate_html_report, generate_json_export
from components import metrics_dashboard, follow_up_button, section_header, tool_call_summary_card
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="Patent Tracker - Competitive Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open(os.path.join(os.path.dirname(__file__), "styles.css")) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except FileNotFoundError:
    pass  # CSS file optional for development

# Helper functions
def extract_company_name(query: str) -> str:
    """Extract company name from user query"""
    companies = ["Anthropic", "OpenAI", "Google", "DeepMind"]
    for company in companies:
        if company.lower() in query.lower():
            return company
    return "Company"

def generate_follow_up_questions(response: str, company: str) -> list:
    """Generate intelligent follow-up questions based on the analysis"""
    questions = []
    
    # Default questions
    base_questions = [
        f"Compare {company} with their closest competitor",
        f"Deep dive into {company}'s patent strategy",
        f"Analyze {company}'s hiring velocity by department",
        f"Track sentiment trends in {company}'s news coverage"
    ]
    
    # Context-aware questions based on response content
    if "patent" in response.lower():
        questions.append(f"What technology domains are {company}'s patents targeting?")
    
    if "hiring" in response.lower() or "job" in response.lower():
        questions.append(f"Which departments is {company} expanding fastest?")
    
    if "github" in response.lower() or "open source" in response.lower():
        questions.append(f"Analyze {company}'s developer community engagement")
    
    if "news" in response.lower() or "announcement" in response.lower():
        questions.append(f"What are the recent strategic moves by {company}?")
    
    if "prediction" in response.lower() or "forecast" in response.lower():
        questions.append(f"Generate a 6-month roadmap prediction for {company}")
    
    # Combine and limit to 6 questions
    all_questions = questions + base_questions
    return all_questions[:6]

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "tool_calls_history" not in st.session_state:
    st.session_state.tool_calls_history = {}
if "last_company" not in st.session_state:
    st.session_state.last_company = None
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# Professional Header
st.markdown("""
<div style="
    padding: 2rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid #E0E0E0;
">
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
        <div style="
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #1E88E5, #7C4DFF);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        ">🔍</div>
        <div>
            <h1 style="margin: 0; color: #212121; font-size: 2rem; font-weight: 700;">Competitive Intelligence Platform</h1>
            <p style="margin: 0.3rem 0 0 0; color: #757575; font-size: 1rem;">
                Real-time strategic analysis powered by AI
            </p>
        </div>
    </div>
    <div style="
        display: flex;
        gap: 1.5rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #F0F0F0;
    ">
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #546E7A; font-size: 0.9rem;">
            <span>📜</span> Patents
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #546E7A; font-size: 0.9rem;">
            <span>👥</span> Hiring Data
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #546E7A; font-size: 0.9rem;">
            <span>📰</span> News
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #546E7A; font-size: 0.9rem;">
            <span>💻</span> Open Source
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar - enhanced design
with st.sidebar:
    # Companies section
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(30, 136, 229, 0.1), rgba(124, 77, 255, 0.1));
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(30, 136, 229, 0.2);
    ">
        <h3 style="margin: 0 0 1rem 0; color: #1E88E5; font-size: 1.1rem;">📊 Monitored Companies</h3>
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <div style="color: #212121;">🟣 Anthropic</div>
            <div style="color: #212121;">🟢 OpenAI</div>
            <div style="color: #212121;">🔵 Google DeepMind</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Data sources section
    st.markdown("""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <h3 style="margin: 0 0 1rem 0; color: #7C4DFF; font-size: 1.1rem;">🔍 Data Sources</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;">
            <div style="text-align: center; padding: 0.8rem; background: #F5F5F5; border-radius: 8px;">
                <div style="font-size: 1.8rem;">📜</div>
                <div style="font-size: 0.8rem; color: #757575; margin-top: 0.3rem;">Patents</div>
            </div>
            <div style="text-align: center; padding: 0.8rem; background: #F5F5F5; border-radius: 8px;">
                <div style="font-size: 1.8rem;">👥</div>
                <div style="font-size: 0.8rem; color: #757575; margin-top: 0.3rem;">Jobs</div>
            </div>
            <div style="text-align: center; padding: 0.8rem; background: #F5F5F5; border-radius: 8px;">
                <div style="font-size: 1.8rem;">📰</div>
                <div style="font-size: 0.8rem; color: #757575; margin-top: 0.3rem;">News</div>
            </div>
            <div style="text-align: center; padding: 0.8rem; background: #F5F5F5; border-radius: 8px;">
                <div style="font-size: 1.8rem;">💻</div>
                <div style="font-size: 0.8rem; color: #757575; margin-top: 0.3rem;">GitHub</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tech stack
    st.markdown("""
    <div style="
        background: linear-gradient(to bottom, #F5F5F5, white);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #E0E0E0;
    ">
        <h3 style="margin: 0 0 0.8rem 0; color: #212121; font-size: 1rem;">⚡ Powered By</h3>
        <div style="font-size: 0.85rem; color: #546E7A; line-height: 1.6;">
            <div>🔵 Google Cloud Platform</div>
            <div>🤖 Gemini 2.5 Pro</div>
            <div>🔥 Firestore Database</div>
            <div>☁️ Cloud Functions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Clear button
    if st.button("🗑️ Clear Conversation", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.tool_calls_history = {}
        st.rerun()
    
    st.caption("🏆 Google Cloud AI Hackathon 2025")

# Main chat interface
st.markdown("""
<div style="margin: 2rem 0 1rem 0;">
    <h2 style="color: #212121; margin: 0;">💬 Ask the Intelligence Agent</h2>
    <p style="color: #757575; margin: 0.3rem 0 0 0; font-size: 0.95rem;">
        Get strategic insights by analyzing patents, jobs, news, and open source activity
    </p>
</div>
""", unsafe_allow_html=True)

# Quick question buttons - only show if no messages
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="
        background: linear-gradient(to right, rgba(30, 136, 229, 0.05), rgba(124, 77, 255, 0.05));
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 2rem;
    ">
        <h3 style="margin: 0 0 0.5rem 0; color: #1E88E5;">💡 Quick Start Questions</h3>
        <p style="color: #757575; margin: 0;">Click a question to begin your analysis:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    questions = [
        "Analyze Anthropic's strategic direction and market positioning",
        "What is OpenAI building based on hiring and patents?",
        "Compare Anthropic and OpenAI's competitive strategies",
        "What are Google DeepMind's recent R&D focus areas?",
        "Which AI company is moving fastest right now?",
        "Predict what Anthropic will announce in the next 90 days"
    ]
    
    for idx, question in enumerate(questions):
        with col1 if idx % 2 == 0 else col2:
            # Custom styled button using markdown
            button_html = f"""
            <div style="margin-bottom: 0.8rem;">
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    border: 2px solid #E0E0E0;
                    cursor: pointer;
                    transition: all 0.2s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <div style="color: #1E88E5; font-weight: 600; font-size: 0.9rem;">
                        💬 {question}
                    </div>
                </div>
            </div>
            """
            if st.button(question, key=f"quick_{idx}", use_container_width=True):
                st.session_state.quick_query = question
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

# Display chat history
if len(st.session_state.messages) == 0:
    # Empty state message
    st.markdown("""
    <div style="
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(to bottom, rgba(30, 136, 229, 0.03), rgba(124, 77, 255, 0.03));
        border-radius: 16px;
        border: 2px dashed #E0E0E0;
        margin: 2rem 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
        <h3 style="color: #212121; margin-bottom: 0.5rem;">Ready to Analyze</h3>
        <p style="color: #757575; font-size: 1rem;">
            Ask a question about AI companies or select a quick start option above
        </p>
    </div>
    """, unsafe_allow_html=True)

# Display chat history (for past messages only - don't duplicate live display)
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        # Just show the formatted response for past messages
        # (Tool calls/metrics/exports only shown during live analysis)
        if message["role"] == "assistant":
            format_strategic_response(message["content"])
        else:
            st.markdown(message["content"])

# Handle quick query button clicks
if "quick_query" in st.session_state:
    user_input = st.session_state.quick_query
    del st.session_state.quick_query
else:
    user_input = st.chat_input("Ask about competitors... (e.g., 'What's Anthropic building?')")

if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display the user message immediately in chat
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get agent response with REAL-TIME updates in chat message context
    with st.chat_message("assistant"):
        # Create status within the assistant's message area
        with st.status("🧠 Agent analyzing...", expanded=True) as status:
            try:
                # Create live update containers
                progress_container = st.container()
                tool_data_container = st.container()
                
                # Call agent with streaming callback
                result = run_agent_streaming(
                    user_input, 
                    st.session_state.conversation_history,
                    progress_container,
                    tool_data_container
                )
                
                response = result["response"]
                st.session_state.conversation_history = result["conversation_history"]
                tool_calls = result.get("tool_calls", [])
                
                status.update(label="✅ Analysis Complete!", state="complete")
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Store tool calls for this message
                message_index = len(st.session_state.messages) - 1
                st.session_state.tool_calls_history[message_index] = tool_calls
                
            except Exception as e:
                status.update(label="❌ Error occurred", state="error")
                response = f"⚠️ Error: {str(e)}\n\nPlease ensure Google Cloud credentials are configured and all services are deployed."
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.error(response)
                tool_calls = []
        
        # Display tool calls summary OUTSIDE the status component to avoid nesting
        if 'tool_calls' in locals() and tool_calls:
            with st.expander(f"🛠️ **Tool Calls & Data Sources** ({len(tool_calls)} calls made)", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Data Sources Used", len(tool_calls))
                with col2:
                    total_items = sum(call.get('result', {}).get('count', 0) for call in tool_calls)
                    st.metric("Total Data Points", total_items)
                with col3:
                    sources = set(call['name'].replace('get_', '').title() for call in tool_calls)
                    st.metric("Types", ", ".join(sources))
                
                st.divider()
                
                for j, call in enumerate(tool_calls, 1):
                    st.markdown(f"### 📊 Call {j}: `{call['name'].replace('_', ' ').title()}`")
                    st.markdown("**Parameters:**")
                    st.json(call['args'], expanded=False)
                    
                    if 'result' in call:
                        result_data = call['result']
                        if 'summary' in result_data:
                            st.success(f"**Summary:** {result_data['summary']}")
                        if 'count' in result_data:
                            st.caption(f"📈 Found {result_data['count']} items")
                    
                    if j < len(tool_calls):
                        st.divider()
            
            # Store for export
            st.session_state.last_response = response
            st.session_state.last_company = extract_company_name(user_input)
            
            # Display metrics dashboard
            metrics = {}
            for call in tool_calls:
                source = call['name'].replace('get_', '').title()
                count = call.get('result', {}).get('count', 0)
                metrics[source] = count
            
            if metrics:
                metrics_dashboard(metrics)
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Display formatted response
            format_strategic_response(response)
            
            # Add export buttons
            st.markdown("<br><br>", unsafe_allow_html=True)
            section_header("Export Report", "📥")
            
            col1, col2, col3 = st.columns(3)
            
            company_name = st.session_state.last_company or "Analysis"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with col1:
                md_report = generate_markdown_report(company_name, response, tool_calls)
                st.download_button(
                    label="📝 Download Markdown",
                    data=md_report,
                    file_name=f"{company_name}_report_{timestamp}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col2:
                html_report = generate_html_report(company_name, response, tool_calls)
                st.download_button(
                    label="🌐 Download HTML",
                    data=html_report,
                    file_name=f"{company_name}_report_{timestamp}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col3:
                json_export = generate_json_export(company_name, response, tool_calls)
                st.download_button(
                    label="📊 Download JSON",
                    data=json_export,
                    file_name=f"{company_name}_data_{timestamp}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Generate follow-up questions
            st.markdown("<br>", unsafe_allow_html=True)
            section_header("Suggested Follow-Up Questions", "💡")
            
            follow_ups = generate_follow_up_questions(response, company_name)
            
            col1, col2 = st.columns(2)
            for idx, question in enumerate(follow_ups):
                with col1 if idx % 2 == 0 else col2:
                    if st.button(f"💬 {question}", key=f"followup_{idx}", use_container_width=True):
                        st.session_state.quick_query = question
                        st.rerun()
        
        # Set flag to prevent auto-scroll on rerun
        st.session_state.just_completed = True
    
    # Rerun to ensure state is saved, but scroll will be handled
    st.rerun()

# Example queries - only show if no conversation (removed to clean up UI)

# Footer
st.divider()
st.caption("Patent Tracker | Powered by Google Cloud, Vertex AI & Gemini 2.5 Pro | Built for Google Cloud AI Hackathon 2025")
