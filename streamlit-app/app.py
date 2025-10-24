"""
Patent Tracker - Competitive Intelligence Dashboard
Ported from AWS IntelAgent Streamlit dashboard
"""
import streamlit as st
from gemini_agent import run_agent
import json
import os

st.set_page_config(
    page_title="Patent Tracker - Competitive Intelligence",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Header
st.title("🔍 Patent Tracker")
st.caption("AI-Powered Competitive Intelligence using Fivetran + Google Cloud")

# Sidebar
with st.sidebar:
    st.header("Monitored Companies")
    st.write("- 🟣 Anthropic")
    st.write("- 🟢 OpenAI")
    st.write("- 🔵 Google DeepMind")
    
    st.divider()
    
    st.header("Quick Queries")
    if st.button("📊 Anthropic Deep Dive"):
        st.session_state.quick_query = "Analyze Anthropic's strategic direction. What are they building? Who are they targeting? How fast are they moving?"
    
    if st.button("🔍 OpenAI Analysis"):
        st.session_state.quick_query = "Analyze OpenAI's current strategy. What products are they developing? What's their go-to-market approach?"
    
    if st.button("⚔️ Compare All Three"):
        st.session_state.quick_query = "Compare Anthropic, OpenAI, and Google DeepMind. Who's moving fastest? What are their different strategic focuses?"
    
    if st.button("🔮 30-Day Predictions"):
        st.session_state.quick_query = "Based on all available data, what products or announcements should we expect from these companies in the next 30 days?"
    
    if st.button("🎯 Patent Analysis"):
        st.session_state.quick_query = "What are the most strategic patents filed by Anthropic in the last 6 months? What do they reveal about their product roadmap?"
    
    st.divider()
    
    st.header("About")
    st.markdown("""
    **Tech Stack:**
    - Fivetran connector (USPTO patents)
    - BigQuery (patent data)
    - Cloud Functions (jobs, news, GitHub)
    - Firestore (multi-source data)
    - Gemini 1.5 Pro (agent orchestration)
    
    **Data Sources:**
    - USPTO Patents (via Google Patents API)
    - Greenhouse Job Boards
    - Google News RSS
    - GitHub Public Repos
    
    **Ported from AWS IntelAgent**
    """)
    
    st.divider()
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()

# Main chat interface
st.header("💬 Ask the Intelligence Agent")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
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
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get agent response
    with st.chat_message("assistant"):
        # Create expandable section for tool calls
        tool_calls_container = st.container()
        response_container = st.container()
        
        with st.spinner("🔍 Agent analyzing multiple data sources..."):
            try:
                result = run_agent(user_input, st.session_state.conversation_history)
                response = result["response"]
                st.session_state.conversation_history = result["conversation_history"]
                tool_calls = result.get("tool_calls", [])
                
                # Display tool calls in expander
                if tool_calls:
                    with tool_calls_container:
                        with st.expander("🛠️ **Tool Calls & Data Sources** (click to expand)", expanded=False):
                            for i, call in enumerate(tool_calls, 1):
                                st.markdown(f"**Call {i}: `{call['name']}`**")
                                st.json(call['args'], expanded=False)
                                
                                if 'result' in call:
                                    st.markdown(f"**Result:**")
                                    # Show preview of result
                                    result_str = json.dumps(call['result'], default=str)
                                    if len(result_str) > 500:
                                        st.code(result_str[:500] + "...", language="json")
                                        st.caption(f"(Truncated - {len(result_str)} total characters)")
                                    else:
                                        st.json(call['result'], expanded=False)
                                
                                if i < len(tool_calls):
                                    st.divider()
                
                # Display main response
                with response_container:
                    st.markdown(response)
                    
            except Exception as e:
                response = f"⚠️ Error: {str(e)}\n\nPlease ensure Google Cloud credentials are configured and all services are deployed."
                st.error(response)
    
    # Add assistant message to chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update display
    st.rerun()

# Example queries
if not st.session_state.messages:
    st.info("**💡 Try asking:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("- What's Anthropic building based on their recent patents?")
        st.write("- Compare OpenAI and Anthropic's hiring strategies")
        st.write("- Predict what Google DeepMind will announce next month")
    
    with col2:
        st.write("- Which company is moving fastest right now?")
        st.write("- What do Anthropic's GitHub repos reveal about their strategy?")
        st.write("- Analyze news coverage patterns for all three companies")

# Footer
st.divider()
st.caption("Patent Tracker | Powered by Fivetran, Google Cloud, and Gemini | Ported from AWS IntelAgent")
