import streamlit as st
import json
from datetime import datetime

# Core imports
from core.preprocessor import preprocess_prompt
from core.parser import parse_sections
from core.ir_generator import generate_prompt_ir
from core.constraint_locker import lock_constraints
from core.compression_planner import plan_compression
from core.compressor import compress_prompt
from core.reconstructor import reconstruct_prompt

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
# Session State Initialization
# ==============================================================================
if "raw_prompt_input" not in st.session_state:
    st.session_state.raw_prompt_input = ""

# ==============================================================================
# Callback Functions
# ==============================================================================
def load_sample_prompt():
    st.session_state.raw_prompt_input = SAMPLE_PROMPT

# ==============================================================================
# Sidebar: Pipeline Explanation
# ==============================================================================
with st.sidebar:
    st.header("⚒️ PromptForge Pipeline")
    st.markdown("""
    1. **Raw Prompt Input**
    2. **Prompt Preprocessor** *(Day 2)*
    3. **Section Parser** *(Day 3)*
    4. **Prompt IR Generator** *(Day 4)*
    5. **Constraint Locker & Compressor** *(Day 5 - ACTIVE)*
    6. **Prompt Reconstructor** *(Day 5 - ACTIVE)*
    7. **Multi-Metric Evaluator** *(Day 6)*
    8. **Adaptive Repair** *(Day 6)*
    9. **Final Output + Report** *(Day 7)*
    """)
    st.divider()
    st.caption("v0.5.0 (Day 5 Compressor)\nLocal-first, 8GB RAM friendly, No paid APIs.")

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
SAMPLE_PROMPT = """You are an expert Python developer. I want you to write a script that scrapes data from a website. 
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

Please provide the code and a brief explanation. Make sure to use Python and no cloud dependency. Make sure that the code is clean. Make sure that the code is clean."""

# ==============================================================================
# Input Section
# ==============================================================================
st.subheader("1. Input Prompt")

col1, col2 = st.columns([3, 1])
with col1:
    raw_prompt = st.text_area(
        "Paste your raw, messy prompt here:",
        value=st.session_state.raw_prompt_input,
        height=200,
        placeholder="Enter your prompt...",
        key="raw_prompt_input"
    )
with col2:
    st.write("") 
    st.write("") 
    st.button("📋 Load Sample Prompt", use_container_width=True, on_click=load_sample_prompt)

compression_mode = st.selectbox(
    "2. Select Compression Mode",
    options=["Safe", "Balanced", "Aggressive", "Research"],
    help="Safe: Minimal changes. Balanced: Good reduction. Aggressive: Max reduction. Research: Optimized for technical prompts."
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
        st.warning("⚠️ Please enter a prompt or load the sample prompt first.")
    else:
        # --- PIPELINE EXECUTION ---
        with st.spinner("Running Prompt Preprocessor..."):
            preprocessed_data = preprocess_prompt(raw_prompt)
        
        with st.spinner("Running Section Parser..."):
            parsed_data = parse_sections(preprocessed_data)
            
        with st.spinner("Generating Prompt IR..."):
            prompt_ir = generate_prompt_ir(preprocessed_data, parsed_data, compression_mode)
            
        with st.spinner("Locking constraints and planning compression..."):
            prompt_ir = lock_constraints(prompt_ir)
            prompt_ir = plan_compression(prompt_ir)
            
        with st.spinner("Compressing and reconstructing prompt..."):
            compressed_sections, prompt_ir = compress_prompt(prompt_ir)
            optimized_prompt = reconstruct_prompt(compressed_sections)
            
        # Save to session state for future days
        st.session_state.prompt_ir = prompt_ir
        st.session_state.optimized_prompt = optimized_prompt
        
        st.success("✅ Full compilation pipeline complete!")
        
        # --- DAY 2 & 3 & 4 UI (Condensed into expanders to save space) ---
        st.divider()
        with st.expander("🔍 View Preprocessing & Parsing Details (Days 2-4)"):
            stats = preprocessed_data["stats"]
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Chars Before", stats["char_count_before"])
            c2.metric("Chars After", stats["char_count_after"])
            c3.metric("Lines", stats["line_count"])
            c4.metric("Chunks", stats["chunk_count"])
            c5.metric("Approx Words", stats["approx_word_count"])
            
            st.markdown("##### Prompt IR Summary")
            col_ir1, col_ir2, col_ir3, col_ir4 = st.columns(4)
            col_ir1.metric("Constraints Locked", len(prompt_ir["constraints"]))
            col_ir2.metric("Features Detected", len(prompt_ir["features"]))
            col_ir3.metric("IR Sections", len(prompt_ir["sections"]))
            col_ir4.metric("Target Reduction", f"{prompt_ir['compression_policy']['target_reduction']*100:.0f}%")
            
            with st.expander("View Full Prompt IR (JSON)"):
                st.json(prompt_ir)

        # --- DAY 5 UI: FINAL OPTIMIZED PROMPT ---
        st.divider()
        st.subheader("6. Final Optimized Prompt")
        
        # Display warnings if any
        if prompt_ir["traceability"]["warnings"]:
            for warning in prompt_ir["traceability"]["warnings"]:
                st.warning(warning)
        
        st.text_area("Optimized Prompt (Ready to Copy)", value=optimized_prompt, height=300)
        
        with st.expander("🔍 View Compression Steps & Preserved Constraints"):
            st.markdown("#### Compression Steps Applied")
            if prompt_ir["traceability"]["compression_steps"]:
                for step in prompt_ir["traceability"]["compression_steps"]:
                    st.markdown(f"- `{step}`")
            else:
                st.info("No compression steps were applied (Safe mode or no duplicates/fillers found).")
                
            st.markdown("#### Preserved Constraints")
            if prompt_ir["constraints"]:
                for c in prompt_ir["constraints"]:
                    st.markdown(f"- **[{c['type']}]** {c['text']}")
            else:
                st.info("No constraints were detected.")