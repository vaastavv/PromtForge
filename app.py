import streamlit as st
import json
import os
from datetime import datetime

# Core imports
from core.preprocessor import preprocess_prompt
from core.parser import parse_sections
from core.ir_generator import generate_prompt_ir
from core.constraint_locker import lock_constraints
from core.compression_planner import plan_compression
from core.compressor import compress_prompt
from core.reconstructor import reconstruct_prompt, adaptive_repair

# Evaluation imports
from evaluation.token_metrics import estimate_tokens, calculate_token_reduction
from evaluation.constraint_score import calculate_constraint_preservation
from evaluation.feature_score import calculate_feature_coverage
from evaluation.keyword_score import extract_keywords, calculate_keyword_preservation
from evaluation.output_format_score import calculate_output_format_score
from evaluation.risk_score import calculate_risk_score
from evaluation.final_score import calculate_final_score
from evaluation.semantic_similarity import calculate_semantic_similarity

# Visualization imports
from visualization.diff_viewer import compute_line_diff, calculate_diff_stats

# Phase 2: Semantic Engine imports
from models.embedding_model import load_embedding_model, is_embedding_available, get_load_error

# ==============================================================================
# Page Configuration & Session State
# ==============================================================================
st.set_page_config(page_title="PromptForge", page_icon="⚒️", layout="wide", initial_sidebar_state="expanded")

if "raw_prompt_input" not in st.session_state:
    st.session_state.raw_prompt_input = ""
if "optimization_complete" not in st.session_state:
    st.session_state.optimization_complete = False

# ==============================================================================
# Callback Functions
# ==============================================================================
def load_sample_prompt():
    st.session_state.raw_prompt_input = SAMPLE_PROMPT

def run_optimization():
    raw_prompt = st.session_state.raw_prompt_input
    if not raw_prompt.strip():
        st.warning("⚠️ Please enter a prompt first.")
        return
    
    with st.spinner("Running full pipeline..."):
        preprocessed_data = preprocess_prompt(raw_prompt)
        parsed_data = parse_sections(preprocessed_data)
        prompt_ir = generate_prompt_ir(preprocessed_data, parsed_data, st.session_state.compression_mode)
        prompt_ir = lock_constraints(prompt_ir)
        prompt_ir = plan_compression(prompt_ir)
        compressed_sections, prompt_ir = compress_prompt(prompt_ir)
        optimized_prompt = reconstruct_prompt(compressed_sections)
        repaired_prompt, repair_log, repair_warnings = adaptive_repair(optimized_prompt, prompt_ir)
        
        # --- PHASE 2: SEMANTIC SIMILARITY ---
        semantic_result = calculate_semantic_similarity(raw_prompt, repaired_prompt)
        semantic_score = semantic_result["score"] if semantic_result["available"] else None

        # Standard Metrics
        token_red = calculate_token_reduction(raw_prompt, repaired_prompt)
        constraint_score = calculate_constraint_preservation(prompt_ir["constraints"], repaired_prompt)
        feature_score = calculate_feature_coverage(prompt_ir["features"], repaired_prompt)
        keyword_score = calculate_keyword_preservation(extract_keywords(prompt_ir), repaired_prompt)
        format_score = calculate_output_format_score(prompt_ir["output_requirements"], repaired_prompt)
        risk = calculate_risk_score(constraint_score, feature_score, format_score)
        
        # Final Score (Passes semantic_score, handles fallback automatically)
        final_score = calculate_final_score(token_red, constraint_score, feature_score, format_score, keyword_score, semantic_score)
        
        diff_result = compute_line_diff(raw_prompt, repaired_prompt)
        diff_stats = calculate_diff_stats(diff_result)
        
        # Store in session state
        st.session_state.optimization_complete = True
        st.session_state.prompt_ir = prompt_ir
        st.session_state.optimized_prompt = repaired_prompt
        st.session_state.repair_log = repair_log
        st.session_state.metrics = {
            "token_reduction": token_red, "constraint_score": constraint_score,
            "feature_score": feature_score, "keyword_score": keyword_score,
            "format_score": format_score, "risk": risk, "final_score": final_score,
            "semantic_result": semantic_result
        }
        st.session_state.diff_result = diff_result
        st.session_state.diff_stats = diff_stats

# ==============================================================================
# Sidebar & Sample Prompt
# ==============================================================================
with st.sidebar:
    st.header("️ PromptForge")
    st.markdown("**Phase 2: Semantic Integration**")
    st.divider()
    
    enable_semantic = st.checkbox("Enable semantic evaluation", value=False, 
                                  help="Loads local embedding model for semantic scoring.")
    
    if enable_semantic:
        load_embedding_model()
        if is_embedding_available():
            st.success("✅ Semantic Engine Ready")
        else:
            st.warning("⚠️ Semantic Engine Unavailable")
    else:
        st.info("ℹ️ Semantic evaluation disabled.")

    st.divider()
    st.markdown("### Pipeline")
    st.markdown("""
    1. Raw Prompt Input
    2. Preprocessor
    3. Section Parser
    4. Prompt IR Generator
    5. Constraint Locker
    6. Compression Planner
    7. Rule-Based Compressor
    8. Reconstructor
    9. Adaptive Repair
    10. Multi-Metric Evaluator
    """)

SAMPLE_PROMPT = """You are an expert Python developer. I want you to write a script that scrapes data from a website. 
Important constraints: 
- Do not use any paid APIs. 
- The script must run offline after initial download, or use only free libraries. 
- It must run on a machine with only 8GB of RAM, so do not load the whole page into memory at once.
- You must return the output strictly in JSON format.

Features required:
- Prompt IR generation
- Multi-metric evaluation
- Local LLM support via Ollama

Please provide the code and a brief explanation. Make sure to use Python and no cloud dependency. Make sure that the code is clean. Make sure that the code is clean."""

# ==============================================================================
# Main UI
# ==============================================================================
st.title("⚒️ PromptForge")
st.markdown("Transform messy prompts into short, safe, optimized prompts while preserving intent, constraints, and output formats.")

st.subheader("1. Input Prompt")
col1, col2 = st.columns([3, 1])
with col1:
    raw_prompt = st.text_area("Paste your raw, messy prompt here:", value=st.session_state.raw_prompt_input, height=200, placeholder="Enter your prompt...", key="raw_prompt_input")
with col2:
    st.write(""); st.write("")
    st.button("📋 Load Sample", use_container_width=True, on_click=load_sample_prompt)

st.session_state.compression_mode = st.selectbox("2. Select Compression Mode", options=["Safe", "Balanced", "Aggressive", "Research"])

st.divider()
st.button("🚀 Optimize Prompt", type="primary", use_container_width=True, on_click=run_optimization)

# ==============================================================================
# Results Tabs
# ==============================================================================
if st.session_state.optimization_complete:
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Optimized Prompt", "📊 Evaluation", " Prompt IR", "🔍 Diff Viewer"])
    
    with tab1:
        st.subheader("Final Optimized Prompt")
        st.text_area("Optimized Prompt", value=st.session_state.optimized_prompt, height=400)
        
    with tab2:
        st.subheader("Multi-Metric Evaluation Dashboard")
        m = st.session_state.metrics
        sem = m["semantic_result"]
        
        # Semantic Status Message
        if not sem["available"]:
            st.info("ℹ️ Semantic similarity is unavailable. Final score is calculated using rule-based weights only.")
        elif sem["warning"]:
            st.warning(f"⚠️ Semantic Warning: {sem['warning']}")
        
        # Row 1: Standard Metrics
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Token Reduction", f"{m['token_reduction']*100:.1f}%")
        m2.metric("Constraint Score", f"{m['constraint_score']*100:.0f}%")
        m3.metric("Feature Coverage", f"{m['feature_score']*100:.0f}%")
        m4.metric("Format Score", f"{m['format_score']*100:.0f}%")
        m5.metric("Keyword Score", f"{m['keyword_score']*100:.0f}%")
        
        # Row 2: Semantic & Final Score
        m6, m7, m8 = st.columns(3)
        
        # Color-coded Semantic Metric
        if sem["available"]:
            score_pct = f"{sem['score']*100:.1f}%"
            if sem["label"] == "High":
                m6.metric("Semantic Similarity", score_pct, delta="High Preservation")
            elif sem["label"] == "Medium":
                m6.metric("Semantic Similarity", score_pct, delta="Medium Preservation", delta_color="normal")
            else:
                m6.metric("Semantic Similarity", score_pct, delta="Low Preservation", delta_color="inverse")
        else:
            m6.metric("Semantic Similarity", "N/A", delta="Disabled")
            
        m7.metric("Risk Level", m['risk'])
        m8.metric("Final Quality Score", f"{m['final_score']*100:.1f}%")
        
    with tab3:
        st.subheader("Prompt Intermediate Representation")
        ir = st.session_state.prompt_ir
        st.json(ir)
        
    with tab4:
        st.subheader("Before/After Diff Viewer")
        diff_result = st.session_state.diff_result
        diff_stats = st.session_state.diff_stats
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Original Lines", diff_stats["original_lines"])
        c2.metric("Optimized Lines", diff_stats["optimized_lines"])
        c3.metric("Preserved Lines", diff_stats["preserved_lines"])
        c4.metric("Removed Lines", diff_stats["removed_lines"])
        st.markdown("### ❌ Removed Lines")
        for line in diff_result["removed"]:
            st.markdown(f"- 🔴 {line}")