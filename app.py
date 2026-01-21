# app.py
"""
Clinical Trial Matching Agent - Streamlit Interface with Real-Time Updates
"""

import streamlit as st
import os
from datetime import datetime
from agent.orchestrator import ClinicalTrialAgent
import json
import time

# Page config
st.set_page_config(
    page_title="Clinical Trial Matching Agent",
    page_icon="🔬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-thinking {
        background-color: #f0f8ff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .tool-call {
        background-color: #fff5e6;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .iteration-badge {
        background-color: #9c27b0;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .agentic-badge {
        background-color: #1f77b4;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'agent_activities' not in st.session_state:
        st.session_state.agent_activities = []


def activity_callback(activity: dict):
    """
    Callback function to receive real-time updates from the agent
    This gets called each time the agent does something
    """
    st.session_state.agent_activities.append(activity)


def display_activity_log(activities):
    """Display the agent's activity log in real-time"""
    for activity in activities:
        activity_type = activity.get('type')
        content = activity.get('content')

        if activity_type == 'start':
            st.markdown("""
            <div class="success-box">
                <strong>🚀 Agent Started</strong><br/>
                Autonomous search initiated...
            </div>
            """, unsafe_allow_html=True)

        elif activity_type == 'iteration':
            iteration = activity.get('iteration', 0)
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <span class="iteration-badge">ITERATION {iteration}</span>
            </div>
            """, unsafe_allow_html=True)

        elif activity_type == 'thinking':
            iteration = activity.get('iteration', 0)
            st.markdown(f"""
            <div class="agent-thinking">
                <strong>💭 Agent Reasoning</strong><br/>
                {content}
            </div>
            """, unsafe_allow_html=True)

        elif activity_type == 'tool_call':
            tool_name = activity.get('tool_name', 'unknown')
            tool_input = activity.get('tool_input', {})
            st.markdown(f"""
            <div class="tool-call">
                <strong>🔧 Tool Call: {tool_name}</strong>
                <span class="agentic-badge">AUTONOMOUS</span><br/>
                <details>
                    <summary>View parameters</summary>
                    <pre>{json.dumps(tool_input, indent=2)}</pre>
                </details>
            </div>
            """, unsafe_allow_html=True)

        elif activity_type == 'tool_result':
            tool_name = activity.get('tool_name', 'unknown')
            st.markdown(f"""
            <div style="padding: 0.5rem; margin-left: 2rem; color: #666; font-size: 0.9rem;">
                ✓ {tool_name} completed
            </div>
            """, unsafe_allow_html=True)

        elif activity_type == 'complete':
            iterations = activity.get('iterations', 0)
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ Search Complete!</strong><br/>
                Completed in {iterations} autonomous iterations
            </div>
            """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">🔬 Clinical Trial Matching Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Autonomous AI-powered trial discovery and matching</div>',
                unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Sidebar
    with st.sidebar:
        st.markdown("### 🤖 About This Agent")
        st.markdown("""
        This demonstrates **Agentic AI** behavior:

        ✅ **Autonomous Planning**  
        Agent decides which tools to use and when

        ✅ **Multi-Step Execution**  
        Search → Filter → Rank → Save

        ✅ **Adaptive Reasoning**  
        Adjusts strategy based on results

        ✅ **Tool Orchestration**  
        Uses multiple APIs autonomously
        """)

        st.markdown("---")
        st.markdown("### ⚙️ Technical Stack")
        st.markdown("""
        - **AI**: Claude Sonnet 4
        - **Backend**: Python, Anthropic API
        - **Database**: MongoDB (planned)
        - **APIs**: ClinicalTrials.gov
        """)

        st.markdown("---")
        st.markdown("### 📊 Current Status")
        st.info("**DEMO MODE** - Using mock data\n\nReal API integration in progress")

        if st.button("🗑️ Clear History"):
            st.session_state.search_history = []
            st.session_state.agent_activities = []
            st.rerun()

    # Main tabs
    tab1, tab2 = st.tabs(["🔍 New Search", "📊 Search History"])

    with tab1:
        st.markdown("### 👤 Patient Information")

        col1, col2 = st.columns(2)

        with col1:
            patient_id = st.text_input("Patient ID", value="PATIENT_001", placeholder="e.g., PATIENT_001")
            age = st.number_input("Age", min_value=0, max_value=120, value=57)
            gender = st.selectbox("Gender", ["male", "female", "all"])

        with col2:
            location = st.text_input("Location", value="Denver, CO", placeholder="City, State")
            conditions_input = st.text_area(
                "Medical Conditions (one per line)",
                value="severe fatty liver disease\nNAFLD\nCAP score 374",
                height=100
            )

        conditions = [c.strip() for c in conditions_input.split('\n') if c.strip()]

        # Search button
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            search_button = st.button("🚀 Run Agent Search", type="primary", use_container_width=True)

        if search_button:
            # Validate
            if not patient_id or not conditions:
                st.error("Please provide Patient ID and at least one condition")
                return

            # Get API key
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                st.error("❌ ANTHROPIC_API_KEY not found in environment")
                return

            # Clear previous activities
            st.session_state.agent_activities = []

            # Build criteria
            patient_criteria = {
                "age": age,
                "gender": gender,
                "conditions": conditions,
                "location": location,
                "patient_id": patient_id
            }

            # Create placeholder for real-time updates
            activity_container = st.container()

            # Create agent with callback
            agent = ClinicalTrialAgent(
                api_key=api_key,
                activity_callback=activity_callback
            )

            # Run search with real-time updates
            with st.spinner("🤖 Agent working autonomously..."):
                result = agent.run_autonomous_search(patient_criteria)

            # Display all activities
            with activity_container:
                st.markdown("---")
                st.markdown("### 🎬 Agent Activity Log")
                st.markdown("*Watch how the agent autonomously planned and executed the search*")
                display_activity_log(st.session_state.agent_activities)

            if result['success']:
                # Save to history
                search_record = {
                    'timestamp': datetime.now(),
                    'patient_criteria': patient_criteria,
                    'result': result,
                    'iterations': result['iterations'],
                    'activities': st.session_state.agent_activities.copy()
                }
                # Show log file location
                if 'log_file' in result and result['log_file']:
                    st.info(f"📝 Detailed log saved to: `{result['log_file']}`")

                st.success(f"✅ Search completed in {result['iterations']} iterations")
                st.balloons()
                st.session_state.search_history.insert(0, search_record)

                # Display final results
                st.markdown("---")
                st.markdown("### 📋 Final Results")
                st.markdown(result['final_response'])

                st.success(f"✅ Search completed in {result['iterations']} iterations and saved to history")
                st.balloons()
            else:
                st.error(f"❌ Search failed: {result.get('error')}")

    with tab2:
        st.markdown("### 📊 Previous Searches")

        if not st.session_state.search_history:
            st.info("No searches yet. Run your first search in the 'New Search' tab!")
        else:
            for idx, record in enumerate(st.session_state.search_history):
                with st.expander(
                        f"Search #{len(st.session_state.search_history) - idx} - "
                        f"{record['patient_criteria']['patient_id']} - "
                        f"{record['timestamp'].strftime('%Y-%m-%d %H:%M')}",
                        expanded=(idx == 0)
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Patient Criteria:**")
                        st.json(record['patient_criteria'])

                    with col2:
                        st.markdown("**Metrics:**")
                        st.metric("Iterations", record['iterations'])
                        st.metric("Timestamp", record['timestamp'].strftime('%H:%M:%S'))

                    # Show activity log for this search
                    if 'activities' in record:
                        with st.expander("View Agent Activity Log"):
                            display_activity_log(record['activities'])

                    st.markdown("**Results:**")
                    st.markdown(record['result']['final_response'])


if __name__ == "__main__":
    main()