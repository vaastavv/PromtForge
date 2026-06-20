import streamlit as st
import json
from datetime import datetime
from core.preprocessor import preprocess_prompt
from core.parser import parse_sections

# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="PromptForge",
    page_icon="⚒️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# Session State Initialization (MUST be at the top)
# ==============================================================================
if "raw_prompt_input" not in st.session_state:
    st.session_state.raw_prompt_input = ""

# ==============================================================================
# Callback Functions
# ==============================================================================
def load_sample_prompt():
    """Safely updates the session state before the widget renders."""
    st.session_state.raw_prompt_input = SAMPLE_PROMPT

# ==============================================================================
# Sidebar: Pipeline Explanation
# ==============================================================================
with st.sidebar:
    st.header("⚒️ PromptForge Pipeline")
    st.markdown("""
    1. **Raw Prompt Input**
    2. **Prompt Preprocessor** *(Day 2 - ACTIVE)*
    3. **Section Parser** *(Day 3 - ACTIVE)*
    4. **Prompt IR Generator** *(Day 4)*
    5. **Constraint Locker** *(Day 5)*
    6. **Compression Planner & Engine** *(Day 5)*
    7. **Prompt Reconstructor** *(Day 5)*
    8. **Multi-Metric Evaluator** *(Day 6)*
    9. **Adaptive Repair** *(Day 6)*
    10. **Final Output + Report** *(Day 7)*
    """)
    st.divider()
    st.caption("v0.3.0 (Day 3 Section Parser)\nLocal-first, 8GB RAM friendly, No paid APIs.")

# ==============================================================================
# Main UI: Header & Description
# ==============================================================================
st.title("⚒️ PromptForge")
st.markdown("""
**Offline Constraint-Preserving Prompt Compiler**  
Transform messy prompts into short, safe, and optimized prompts while strictly preserving intent, constraints, and output formats.
""")

# ==============================================================================
# Sample Prompt Data
# ==============================================================================
SAMPLE_PROMPT = """You are an expert Python developer. I need you to write a script that scrapes data from a website. 
Important constraints: 
- Do not use any paid APIs. 
- The script must run offline after initial download, or use only free libraries. 
- It must run on a machine with only 8GB of RAM, so do not load the whole page into memory at once.
- You must return the output strictly in JSON format.
- Do not miss any of the features mentioned.


Features required:
- Prompt IR generation
- Multi-metric evaluation
- Local LLM support via Ollama

Please provide the code and a brief explanation. Make sure to use Python and no cloud dependency."""

# ==============================================================================
# Input Section
# ==============================================================================
st.subheader("1. Input Prompt")

col1, col2 = st.columns([3, 1])
with col1:
    # Bind value to session state, and use the key
    raw_prompt = st.text_area(
        "Paste your raw, messy prompt here:",
        value=st.session_state.raw_prompt_input,
        height=200,
        placeholder="Enter your prompt...",
        key="raw_prompt_input"
    )
with col2:
    st.write("") # Spacer
    st.write("") # Spacer
    # Use on_click callback to safely update session state
    st.button(
        "📋 Load Sample Prompt", 
        use_container_width=True, 
        on_click=load_sample_prompt
    )

compression_mode = st.selectbox(
    "2. Select Compression Mode",
    options=["Safe", "Balanced", "Aggressive", "Research"],
    help="Safe: Minimal changes, max preservation. Balanced: Good reduction, strict constraint lock. Aggressive: Max token reduction, high compression on context/examples. Research: Optimized for technical/academic prompts."
)

# ==============================================================================
# Action Button
# ==============================================================================
st.divider()
optimize_clicked = st.button("🚀 Optimize Prompt", type="primary", use_container_width=True)

# ==============================================================================
# Output Section
# ==============================================================================
if optimize_clicked:
    if not raw_prompt.strip():
        st.warning("️ Please enter a prompt or load the sample prompt first.")
    else:
        # --- DAY 2: PREPROCESSING ---
        with st.spinner("Running Prompt Preprocessor..."):
            preprocessed_data = preprocess_prompt(raw_prompt)
        
        # --- DAY 3: SECTION PARSING ---
        with st.spinner("Running Section Parser..."):
            parsed_data = parse_sections(preprocessed_data)
        
        st.success("✅ Preprocessing and Parsing complete!")
        
        # --- DAY 2 UI: PREPROCESSING RESULTS ---
        st.divider()
        st.subheader("3. Preprocessing Results")
        stats = preprocessed_data["stats"]
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Chars Before", stats["char_count_before"])
        col2.metric("Chars After", stats["char_count_after"])
        col3.metric("Lines", stats["line_count"])
        col4.metric("Chunks", stats["chunk_count"])
        col5.metric("Approx Words", stats["approx_word_count"])
        
        st.divider()
        st.markdown("### 🧹 Cleaned Prompt")
        st.text_area("Cleaned Text (Read-only)", value=preprocessed_data["clean_text"], height=100, disabled=True)
        
        # --- DAY 3 UI: PARSING RESULTS ---
        st.divider()
        st.subheader("4. Section Parsing Results")
        
        # Create tabs for organized viewing of parsed sections
        tab_constraints, tab_features, tab_output, tab_all = st.tabs([
            " Detected Constraints", 
            "✨ Detected Features", 
            "📄 Output Requirements", 
            "️ All Sections"
        ])
        
        # Helper function to display a list of parsed items
        def display_parsed_list(items):
            if not items:
                st.info("No items detected in this category.")
            else:
                for item in items:
                    text = item["text"]
                    kws = item["matched_keywords"]
                    kw_str = f" *(Matched: {', '.join(kws)})*" if kws else ""
                    st.markdown(f"- {text}{kw_str}")

        with tab_constraints:
            st.markdown("#### Hard Constraints (Locked for Compression)")
            display_parsed_list(parsed_data["constraints"])
            
        with tab_features:
            st.markdown("#### Required Features")
            display_parsed_list(parsed_data["features"])
            
        with tab_output:
            st.markdown("#### Output Format Requirements")
            display_parsed_list(parsed_data["output_format"])
            
        with tab_all:
            st.markdown("#### Full Breakdown")
            for category, items in parsed_data.items():
                if items:
                    with st.expander(f"{category.upper()} ({len(items)} items)"):
                        display_parsed_list(items)

        # --- PLACEHOLDERS FOR DAYS 4-7 ---
        st.divider()
        st.subheader("5. Optimization Results (Coming Soon)")
        st.info("🚧 *Prompt IR, Compression, and Evaluation will appear here in Days 4-7.*")