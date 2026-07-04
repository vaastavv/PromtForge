import streamlit as st
import pandas as pd
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
from core.reconstructor import reconstruct_prompt
from core.section_relevance import score_all_sections
from core.adaptive_repair import repair_prompt

# Evaluation imports
from evaluation.token_metrics import calculate_token_reduction
from evaluation.constraint_score import calculate_constraint_preservation
from evaluation.feature_score import calculate_feature_coverage
from evaluation.keyword_score import extract_keywords, calculate_keyword_preservation
from evaluation.output_format_score import calculate_output_format_score
from evaluation.risk_score import calculate_risk_score
from evaluation.final_score import calculate_final_score
from evaluation.semantic_similarity import calculate_semantic_similarity

# Visualization imports
from visualization.diff_viewer import compute_line_diff, calculate_diff_stats

# Phase 2 & 3: Engine imports
from models.embedding_model import load_embedding_model, is_embedding_available
from models.ollama_client import is_ollama_available, get_available_models, rewrite_prompt_with_ollama

# ==============================================================================
# Page Configuration & Session State
# ==============================================================================
st.set_page_config(page_title="PromptForge", page_icon="⚒️", layout="wide", initial_sidebar_state="collapsed")

if "raw_prompt_input" not in st.session_state:
    st.session_state.raw_prompt_input = ""
if "optimization_complete" not in st.session_state:
    st.session_state.optimization_complete = False

# ==============================================================================
# Callback Functions
# ==============================================================================
def load_sample_prompt():
    st.session_state.raw_prompt_input = SAMPLE_PROMPT

def run_evaluation(raw_text, optimized_text, prompt_ir):
    """Helper to run all metrics and return a unified report."""
    semantic_result = calculate_semantic_similarity(raw_text, optimized_text)
    semantic_score = semantic_result["score"] if semantic_result["available"] else None

    token_red = calculate_token_reduction(raw_text, optimized_text)
    constraint_res = calculate_constraint_preservation(prompt_ir["constraints"], optimized_text)
    feature_res = calculate_feature_coverage(prompt_ir["features"], optimized_text)
    keyword_score = calculate_keyword_preservation(extract_keywords(prompt_ir), optimized_text)
    format_res = calculate_output_format_score(prompt_ir["output_requirements"], optimized_text)
    
    risk = calculate_risk_score(constraint_res["score"], feature_res["score"], format_res["score"])
    final_score = calculate_final_score(token_red, constraint_res["score"], feature_res["score"], format_res["score"], keyword_score, semantic_score)
    
    return {
        "token_reduction": token_red,
        "constraint_score": constraint_res,
        "feature_score": feature_res,
        "keyword_score": keyword_score,
        "format_score": format_res,
        "risk": risk,
        "final_score": final_score,
        "semantic_result": semantic_result
    }

def run_optimization():
    raw_prompt = st.session_state.raw_prompt_input
    if not raw_prompt.strip():
        st.warning("⚠️ Please enter a prompt first.")
        return
    
    with st.spinner("Running full pipeline..."):
        # 1. Rule-Based Pipeline
        preprocessed_data = preprocess_prompt(raw_prompt)
        parsed_data = parse_sections(preprocessed_data)
        prompt_ir = generate_prompt_ir(preprocessed_data, parsed_data, st.session_state.compression_mode)
        prompt_ir = lock_constraints(prompt_ir)
        prompt_ir = score_all_sections(prompt_ir)
        prompt_ir = plan_compression(prompt_ir)
        
        compressed_sections, prompt_ir = compress_prompt(prompt_ir)
        rule_based_prompt, prompt_ir = reconstruct_prompt(compressed_sections, prompt_ir)
        
        # 2. Optional Local LLM Rewrite
        llm_rewritten_prompt = None
        use_llm = st.session_state.get("use_ollama_rewrite", False)
        selected_model = st.session_state.get("ollama_model", "llama3.2:1b")
        
        if use_llm and is_ollama_available():
            prompt_ir["traceability"]["compression_steps"].append(f"Local LLM rewrite applied using {selected_model}")
            with st.spinner(f"🦙 Polishing with {selected_model}..."):
                rewrite_result = rewrite_prompt_with_ollama(rule_based_prompt, prompt_ir, selected_model)
                if rewrite_result["success"]:
                    llm_rewritten_prompt = rewrite_result["rewritten_prompt"]
                else:
                    prompt_ir["traceability"]["warnings"].append(f"LLM Rewrite failed: {rewrite_result['error']}")
                    
        # 3. Determine prompt to evaluate
        prompt_to_evaluate = llm_rewritten_prompt if llm_rewritten_prompt else rule_based_prompt
        
        # 4. Evaluation & Adaptive Repair
        pre_repair_report = run_evaluation(raw_prompt, prompt_to_evaluate, prompt_ir)
        
        final_prompt = prompt_to_evaluate
        repair_applied = False
        if pre_repair_report["risk"] in ["High", "Medium"]:
            final_prompt, prompt_ir = repair_prompt(prompt_ir, prompt_to_evaluate, pre_repair_report)
            if prompt_ir["traceability"].get("restored_items"):
                repair_applied = True
                
        post_repair_report = run_evaluation(raw_prompt, final_prompt, prompt_ir) if repair_applied else pre_repair_report
        
        # 5. Diff & Session State
        diff_result = compute_line_diff(raw_prompt, final_prompt)
        diff_stats = calculate_diff_stats(diff_result)
        
        st.session_state.optimization_complete = True
        st.session_state.prompt_ir = prompt_ir
        st.session_state.rule_based_prompt = rule_based_prompt
        st.session_state.llm_rewritten_prompt = llm_rewritten_prompt
        st.session_state.final_prompt = final_prompt
        st.session_state.pre_repair_report = pre_repair_report
        st.session_state.post_repair_report = post_repair_report
        st.session_state.repair_applied = repair_applied
        st.session_state.diff_result = diff_result
        st.session_state.diff_stats = diff_stats

# ==============================================================================
# Sidebar (Minimalist)
# ==============================================================================
with st.sidebar:
    st.header("⚒️ PromptForge")
    st.caption("v3.0.0 | Phase 3: Local LLM")
    st.divider()
    st.markdown("### System Status")
    if is_embedding_available(): st.success("✅ Semantic Engine Ready")
    else: st.warning("⚠️ Semantic Engine Offline")
    
    if is_ollama_available(): st.success("✅ Ollama Ready")
    else: st.error("❌ Ollama Offline")

# ==============================================================================
# Sample Prompt
# ==============================================================================
SAMPLE_PROMPT = """You are an expert Python developer. Write a script to scrape data from a website.
Important constraints:
- Do not use any paid APIs.
- The script must run offline.
- It must run on a machine with only 8GB of RAM.
- You must return the output strictly in JSON format.
- Do not miss any features.

Features required:
- Prompt IR generation
- Multi-metric evaluation
- Adaptive repair logic

Context:
This is a very long and unnecessary explanation of why we need this script. It was written by someone who talks too much. We need this script because the old one was bad.

Please provide the code. Make sure to use Python. Make sure the code is clean. Make sure the code is clean."""

# ==============================================================================
# Main UI: 7-Tab Layout
# ==============================================================================
st.title("⚒️ PromptForge")
st.markdown("Offline Constraint-Preserving Prompt Compiler with Semantic Intelligence & Local LLM Polish")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Input", "2. Optimized Prompt", "3. Prompt IR", 
    "4. Evaluation", "5. Diff", "6. Traceability", "7. Export"
])

# --- TAB 1: INPUT ---
with tab1:
    st.header("1. Input Configuration")
    
    raw_prompt = st.text_area("Paste your raw, messy prompt here:", value=st.session_state.raw_prompt_input, height=300, key="raw_prompt_input")
    
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        st.button("📋 Load Sample Prompt", use_container_width=True, on_click=load_sample_prompt)
    with col_btn2:
        st.session_state.compression_mode = st.selectbox("Compression Mode", options=["Safe", "Balanced", "Aggressive", "Research"])
        
    st.divider()
    st.subheader("Optional Enhancements")
    
    col_sem, col_llm = st.columns(2)
    with col_sem:
        st.markdown("**Semantic Evaluation**")
        enable_semantic = st.checkbox("Enable semantic evaluation", value=False, key="enable_semantic")
        if enable_semantic:
            load_embedding_model()
            if is_embedding_available(): st.success("✅ Engine Ready")
            else: st.warning("⚠️ Engine Unavailable")
            
    with col_llm:
        st.markdown("**Local LLM Polish**")
        ollama_avail = is_ollama_available()
        st.checkbox("Use local LLM rewrite", key="use_ollama_rewrite", disabled=not ollama_avail)
        if ollama_avail:
            models = get_available_models()
            if models:
                st.selectbox("Model", options=models, key="ollama_model", disabled=not st.session_state.get("use_ollama_rewrite", False))
            else:
                st.caption("No models found. Run `ollama pull llama3.2:1b`")
        else:
            st.caption("Ollama not running.")
            
    st.divider()
    st.button("🚀 Optimize Prompt", type="primary", use_container_width=True, on_click=run_optimization)
    
    if st.session_state.optimization_complete:
        st.success("✅ Optimization complete! Navigate to the tabs above to view results.")

# --- TAB 2: OPTIMIZED PROMPT ---
with tab2:
    st.header("2. Final Optimized Prompt")
    if not st.session_state.optimization_complete:
        st.info("ℹ️ Run the optimization pipeline in the Input tab to see results here.")
    else:
        if st.session_state.repair_applied:
            st.success("✅ Adaptive Repair Applied: Missing critical elements were automatically restored!")
        elif st.session_state.llm_rewritten_prompt:
            st.success("✅ Local LLM rewrite applied successfully.")
            
        st.text_area("Final Prompt", value=st.session_state.final_prompt, height=400)
        
        with st.expander("🔍 View Intermediate Versions"):
            st.markdown("**Rule-Based Version (Before LLM):**")
            st.text_area("Rule-Based", value=st.session_state.rule_based_prompt, height=200)
            if st.session_state.llm_rewritten_prompt:
                st.markdown("**LLM Rewritten Version (Before Repair):**")
                st.text_area("LLM Rewritten", value=st.session_state.llm_rewritten_prompt, height=200)

# --- TAB 3: PROMPT IR ---
with tab3:
    st.header("3. Prompt Intermediate Representation")
    if not st.session_state.optimization_complete:
        st.info("ℹ️ Run the optimization pipeline in the Input tab to see results here.")
    else:
        ir = st.session_state.prompt_ir
        st.subheader("Section Relevance & Strategy")
        plan_data = []
        for sec in ir.get("sections", []):
            plan_data.append({
                "Section": sec.get("name", "").capitalize(),
                "Action": sec.get("compression_action", "unknown").replace("_", " ").title(),
                "Relevance": f"{sec.get('relevance_score', 0)*100:.0f}%",
                "Label": sec.get("relevance_label", "low").capitalize(),
                "Locked": "🔒" if sec.get("locked", False) else ""
            })
        if plan_data:
            st.dataframe(pd.DataFrame(plan_data), use_container_width=True, hide_index=True)
            
        with st.expander("View Full Prompt IR (JSON)"):
            st.json(ir)

# --- TAB 4: EVALUATION ---
with tab4:
    st.header("4. Multi-Metric Evaluation Dashboard")
    if not st.session_state.optimization_complete:
        st.info("ℹ️ Run the optimization pipeline in the Input tab to see results here.")
    else:
        post = st.session_state.post_repair_report
        st.markdown("#### Final Quality Metrics")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Token Reduction", f"{post['token_reduction']*100:.1f}%")
        m2.metric("Constraint Score", f"{post['constraint_score']['score']*100:.0f}%")
        m3.metric("Feature Coverage", f"{post['feature_score']['score']*100:.0f}%")
        m4.metric("Format Score", f"{post['format_score']['score']*100:.0f}%")
        m5.metric("Keyword Score", f"{post['keyword_score']*100:.0f}%")
        
        m6, m7, m8 = st.columns(3)
        sem = post['semantic_result']
        m6.metric("Semantic Similarity", f"{sem['score']*100:.1f}%" if sem['available'] else "N/A")
        m7.metric("Risk Level", post['risk'])
        m8.metric("Final Quality Score", f"{post['final_score']*100:.1f}%")

# --- TAB 5: DIFF ---
with tab5:
    st.header("5. Before/After Diff Viewer")
    if not st.session_state.optimization_complete:
        st.info("ℹ️ Run the optimization pipeline in the Input tab to see results here.")
    else:
        diff_result = st.session_state.diff_result
        diff_stats = st.session_state.diff_stats
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Original Lines", diff_stats["original_lines"])
        c2.metric("Optimized Lines", diff_stats["optimized_lines"])
        c3.metric("Preserved Lines", diff_stats["preserved_lines"])
        c4.metric("Removed Lines", diff_stats["removed_lines"])
        
        st.subheader("❌ Removed Lines")
        if diff_result["removed"]:
            for line in diff_result["removed"]:
                st.markdown(f"- 🔴 {line}")

# --- TAB 6: TRACEABILITY ---
with tab6:
    st.header("6. Traceability & Audit Log")
    if not st.session_state.optimization_complete:
        st.info("ℹ️ Run the optimization pipeline in the Input tab to see results here.")
    else:
        trace = st.session_state.prompt_ir.get("traceability", {})
        
        st.subheader("🗜️ Compression & Rewrite Steps")
        steps = trace.get("compression_steps", [])
        if steps:
            for step in steps:
                st.markdown(f"- `{step}`")
                
        st.subheader("🔧 Restored Items")
        restored = trace.get("restored_items", [])
        if restored:
            for item in restored:
                st.markdown(f"- ✅ {item}")
        else:
            st.info("No items were restored.")
            
        st.subheader("⚠️ Warnings")
        warnings = trace.get("warnings", [])
        if warnings:
            for w in warnings:
                st.warning(w)
        else:
            st.success("No warnings generated.")

# --- TAB 7: EXPORT ---
with tab7:
    st.header("7. Export Results")
    if not st.session_state.optimization_complete:
        st.info("ℹ️ Run the optimization pipeline in the Input tab to see results here.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("📥 Download Prompt (.txt)", data=st.session_state.final_prompt, file_name="optimized_prompt.txt", mime="text/plain", use_container_width=True)
        with col2:
            ir_json = json.dumps(st.session_state.prompt_ir, indent=2)
            st.download_button("📥 Download IR (.json)", data=ir_json, file_name="prompt_ir.json", mime="application/json", use_container_width=True)
        with col3:
            report = {"timestamp": datetime.now().isoformat(), "metrics": st.session_state.post_repair_report}
            st.download_button("📥 Download Report (.json)", data=json.dumps(report, indent=2), file_name="report.json", mime="application/json", use_container_width=True)