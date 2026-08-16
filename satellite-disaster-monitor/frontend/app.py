import os
import time
import streamlit as st
from PIL import Image

from utils.api_client import (
    analyze_image,
    check_backend_health,
    fetch_history,
    clear_backend_history,
    DEFAULT_BACKEND_URL
)
from utils.charts import create_band_stats_chart, create_confidence_chart

# 1. Streamlit Page Configuration
st.set_page_config(
    page_title="Satellite Disaster Monitor",
    page_icon="🛰️",
    layout="wide"
)

# Custom CSS styling for cards, shadows, and badges
st.markdown("""
<style>
    .stAppViewContainer {
        background-color: #0b0e14;
    }
    .explanation-card {
        background: linear-gradient(135deg, #131b26 0%, #1a2433 100%);
        border-left: 4px solid #00d2ff;
        border-radius: 8px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    }
    .history-card {
        background-color: #131b26;
        border: 1px solid #1e2c3d;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    
    /* Severity Badges */
    .severity-badge-low {
        background-color: #1b5e20;
        color: #81c784;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #2e7d32;
    }
    .severity-badge-moderate {
        background-color: #f57f17;
        color: #fff9c4;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #fbc02d;
    }
    .severity-badge-high {
        background-color: #e65100;
        color: #ffe0b2;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #f57c00;
    }
    .severity-badge-critical {
        background-color: #b71c1c;
        color: #ffcdd2;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        display: inline-block;
        border: 1px solid #c62828;
    }
</style>
""", unsafe_allow_html=True)

# 2. Sidebar Configuration
with st.sidebar:
    st.title("🛰️ Disaster Monitor")
    st.markdown("Automated satellite imagery classification and situational assessment tool for response teams.")
    st.divider()
    
    backend_url = st.text_input(
        "Backend API Base URL",
        value=os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL)
    )
    
    is_online = check_backend_health(backend_url)
    if is_online:
        st.success("🟢 Backend API: Online")
    else:
        st.error(f"🔴 Backend unreachable at `{backend_url}`")
        
    st.divider()
    st.caption("Satellite Disaster Assessment System v0.1.0")

# Session state initialization
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = None
if "analyzed_filename" not in st.session_state:
    st.session_state["analyzed_filename"] = None
if "processing_time" not in st.session_state:
    st.session_state["processing_time"] = None

def reset_analysis():
    st.session_state["analysis_results"] = None
    st.session_state["analyzed_filename"] = None
    st.session_state["processing_time"] = None

# 3. Main Header & Navigation Tabs
st.title("🛰️ Satellite Disaster Monitoring Dashboard")

tab_analyze, tab_history = st.tabs(["🔍 Real-Time Analysis", "📜 Analysis History"])

# ----------------- TAB 1: REAL-TIME ANALYSIS -----------------
with tab_analyze:
    st.write("Upload satellite imagery (RGB, Thermal, IR, or SAR) for real-time disaster detection and AI-generated assessment.")
    
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("1. Image Input")
        uploaded_file = st.file_uploader(
            "Select Satellite Image File",
            type=["jpg", "jpeg", "png", "tif", "tiff"],
            help="Upload JPEG, PNG, or TIFF satellite image files"
        )
        
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
            except Exception:
                st.error("Failed to render preview. File may not be a valid image format.")
                image = None

            btn_col1, btn_col2 = st.columns([2, 1])
            with btn_col1:
                analyze_clicked = st.button("🔍 Analyze Satellite Image", use_container_width=True, type="primary")
            with btn_col2:
                st.button("🔄 Reset", use_container_width=True, on_click=reset_analysis)
            
            if analyze_clicked and image is not None:
                reset_analysis()
                st.session_state["analyzed_filename"] = uploaded_file.name
                
                start_time = time.time()
                with st.spinner("Processing satellite imagery & querying LLM analysis..."):
                    mime_type = uploaded_file.type or "image/jpeg"
                    success, response_data = analyze_image(
                        file_bytes=file_bytes,
                        filename=uploaded_file.name,
                        mime_type=mime_type,
                        backend_url=backend_url
                    )
                    elapsed = time.time() - start_time
                    st.session_state["processing_time"] = round(elapsed, 2)
                    
                    if success:
                        st.session_state["analysis_results"] = response_data
                        st.toast("✅ Image analyzed & saved to history!", icon="🛰️")
                    else:
                        st.error(response_data.get("error", "An unknown error occurred."))

    with col_right:
        st.subheader("2. Assessment & Intelligence")
        
        results = st.session_state.get("analysis_results")
        if results and st.session_state.get("analyzed_filename") == (uploaded_file.name if uploaded_file else None):
            prediction = results.get("prediction", {})
            explanation = results.get("explanation", "")
            processing_time = st.session_state.get("processing_time")
            
            disaster_type = prediction.get("disaster_type", "N/A").upper()
            severity = prediction.get("severity", "low").lower()
            confidence = prediction.get("confidence", 0.0)
            image_type = prediction.get("image_type_detected", "RGB")
            band_stats = prediction.get("band_stats", {})
            
            badge_class = f"severity-badge-{severity}"
            badge_icon = "🟢" if severity == "low" else "🟡" if severity == "moderate" else "🟠" if severity == "high" else "🔴"
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                <div>
                    <span class="{badge_class}">{badge_icon} SEVERITY: {severity.upper()}</span>
                    <span style="font-size: 0.9em; color: #aaaaaa; margin-left: 10px;">Type: <b>{disaster_type}</b> ({image_type})</span>
                </div>
                {f'<div style="font-size: 0.85em; color: #00d2ff; background-color: #131b26; padding: 4px 10px; border-radius: 12px; border: 1px solid #1e2c3d;">⚡ Processed in {processing_time}s</div>' if processing_time else ''}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="explanation-card">
                <h4 style="margin-top: 0; color: #00d2ff; font-size: 1.05em;">🤖 AI Assessment Brief (Groq LLM)</h4>
                <p style="margin-bottom: 0; color: #DDDDDD; font-size: 0.95em; line-height: 1.5;">{explanation}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### Model Metrics & Band Statistics")
            c1, c2 = st.columns([1, 1])
            with c1:
                fig_conf = create_confidence_chart(confidence)
                st.pyplot(fig_conf, use_container_width=True)
            with c2:
                fig_bands = create_band_stats_chart(band_stats)
                st.pyplot(fig_bands, use_container_width=True)
                
            st.caption(f"Intensity Mean: {band_stats.get('mean_intensity', 0.0):.1f}")
            
        else:
            st.info("👈 Upload a satellite image on the left and click **Analyze Satellite Image** to view model assessment results.")

# ----------------- TAB 2: ANALYSIS HISTORY -----------------
with tab_history:
    st.subheader("📜 Historical Analysis Reports")
    st.write("Browse and review all satellite images analyzed during this session.")
    
    h_col1, h_col2 = st.columns([4, 1])
    with h_col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if clear_backend_history(backend_url):
                st.toast("History cleared!", icon="🧹")
                st.rerun()
                
    success, history_items = fetch_history(backend_url)
    
    if not success or not history_items:
        st.info("No past analysis reports found. Analyze an image in the **Real-Time Analysis** tab to record history.")
    else:
        st.write(f"Total Saved Reports: **{len(history_items)}**")
        
        for item in history_items:
            pred = item.get("prediction", {})
            sev = pred.get("severity", "low").lower()
            badge_class = f"severity-badge-{sev}"
            badge_icon = "🟢" if sev == "low" else "🟡" if sev == "moderate" else "🟠" if sev == "high" else "🔴"
            
            with st.expander(f"📷 {item.get('filename')} — {pred.get('disaster_type', '').upper()} ({item.get('timestamp')})"):
                st.markdown(f"""
                <div class="history-card">
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 8px;">
                        <span class="{badge_class}">{badge_icon} SEVERITY: {sev.upper()}</span>
                        <span>Confidence: <b>{pred.get('confidence', 0.0):.1%}</b></span>
                        <span>Image Sensor: <b>{pred.get('image_type_detected', 'RGB')}</b></span>
                    </div>
                    <div style="color: #00d2ff; font-weight: bold; margin-top: 8px;">🤖 Groq LLM Explanation:</div>
                    <p style="color: #dddddd; margin-top: 4px;">{item.get('explanation')}</p>
                </div>
                """, unsafe_allow_html=True)
