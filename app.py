import streamlit as st
import json
import os

# Core imports
from core.preprocessor import preprocess_prompt
from core.parser import parse_sections
from core.ir_generator import generate_prompt_ir
from core.constraint_locker import lock_constraints
from core.compression_planner import plan_compression
from core.compressor import compress_prompt
from core.reconstructor import reconstruct_prompt

# Evaluation imports
from evaluation.token_metrics import estimate_tokens, calculate_token_reduction
from evaluation.constraint_score import calculate_constraint_preservation
from evaluation.feature_score import calculate_feature_coverage
from evaluation.keyword_score import extract_keywords, calculate_keyword_preservation
from evaluation.output_format_score import calculate_output_format_score
from evaluation.risk_score import calculate_risk_score
from evaluation.final_score import calculate_final_score

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
# Sidebar
# ==============================================================================
with st.sidebar:
    st.header("⚒️ PromptForge")
    st.markdown("""
    1. Raw Prompt Input
    2. Preprocessor
    3. Section Parser
    4. Prompt IR Generator
    5. Constraint Locker
    6. Compression Planner
    7. Rule-Based Compressor
    8. Reconstructor
    9. **Multi-Metric Evaluator** *(Day 6 - ACTIVE)*
    10. Final Output
    """)
    st.divider()
    st.caption("v0.6.0 (Day 6 Evaluator)\nLocal-first | 8GB RAM | No paid APIs")

# ==============================================================================
# Sample Prompt
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
# Main UI
# ==============================================================================
st.title("⚒️ PromptForge — Prompt Optimizer")
st.markdown("Transform messy prompts into short, safe, optimized prompts while preserving intent, constraints, and output formats.")

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
    st.button("📋 Load Sample", use_container_width=True, on_click=load_sample_prompt)

compression_mode = st.selectbox(
    "2. Select Compression Mode",
    options=["Safe", "Balanced", "Aggressive", "Research"]
)

st.divider()
optimize_clicked = st.button("🚀 Optimize Prompt", type="primary", use_container_width=True)

# ==============================================================================
# Pipeline Execution & Output
# ==============================================================================
if optimize_clicked:
    if not raw_prompt.strip():
        st.warning("⚠️ Please enter a prompt first.")
    else:
        with st.spinner("Running full pipeline..."):
            preprocessed_data = preprocess_prompt(raw_prompt)
            parsed_data = parse_sections(preprocessed_data)
            prompt_ir = generate_prompt_ir(preprocessed_data, parsed_data, compression_mode)
            prompt_ir = lock_constraints(prompt_ir)
            prompt_ir = plan_compression(prompt_ir)
            compressed_sections, prompt_ir = compress_prompt(prompt_ir)
            optimized_prompt = reconstruct_prompt(compressed_sections)

        st.success("✅ Optimization complete!")

        # --- DAY 6: MULTI-METRIC EVALUATION ---
        st.divider()
        st.subheader("3. Multi-Metric Evaluation Dashboard")
        
        # Calculate all metrics
        token_red = calculate_token_reduction(raw_prompt, optimized_prompt)
        constraint_score = calculate_constraint_preservation(prompt_ir["constraints"], optimized_prompt)
        feature_score = calculate_feature_coverage(prompt_ir["features"], optimized_prompt)
        keyword_score = calculate_keyword_preservation(extract_keywords(prompt_ir), optimized_prompt)
        format_score = calculate_output_format_score(prompt_ir["output_requirements"], optimized_prompt)
        risk = calculate_risk_score(constraint_score, feature_score, format_score)
        final_score = calculate_final_score(token_red, constraint_score, feature_score, format_score, keyword_score)

        # Display Metric Cards Row 1
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Token Reduction", f"{token_red*100:.1f}%", f"Target: {prompt_ir['compression_policy']['target_reduction']*100:.0f}%")
        m2.metric("Constraint Score", f"{constraint_score*100:.0f}%", "Target: 100%")
        m3.metric("Feature Coverage", f"{feature_score*100:.0f}%", "Target: 90%")
        m4.metric("Format Score", f"{format_score*100:.0f}%", "Target: 90%")
        m5.metric("Keyword Score", f"{keyword_score*100:.0f}%")

        # Display Metric Cards Row 2
        m6, m7 = st.columns(2)
        m6.metric("Risk Level", risk)
        m7.metric("Final Quality Score", f"{final_score*100:.1f}%")

        # Risk Warning
        if risk == "High":
            st.error("⚠️ HIGH RISK: Critical constraints were lost during compression! Consider using 'Safe' or 'Balanced' mode.")
        elif risk == "Medium":
            st.warning("⚠️ MEDIUM RISK: Some features or formatting may be degraded. Review the output carefully.")
        else:
            st.success("✅ LOW RISK: The optimized prompt is safe and preserves all critical elements.")

        # --- FINAL OPTIMIZED PROMPT ---
        st.divider()
        st.subheader("4. Final Optimized Prompt")
        
        if prompt_ir["traceability"]["warnings"]:
            for w in prompt_ir["traceability"]["warnings"]:
                st.warning(w)

        st.text_area("Optimized Prompt", value=optimized_prompt, height=300)

        with st.expander("🔍 Compression Steps & Preserved Constraints"):
            st.markdown("#### Steps Applied")
            steps = prompt_ir["traceability"]["compression_steps"]
            if steps:
                for s in steps:
                    st.markdown(f"- `{s}`")
            else:
                st.info("No compression steps applied.")
            st.markdown("#### Preserved Constraints")
            for c in prompt_ir["constraints"]:
                st.markdown(f"- **[{c['type']}]** {c['text']}")