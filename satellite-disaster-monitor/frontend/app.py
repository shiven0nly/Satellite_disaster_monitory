import io
import os
import time
import streamlit as st
from PIL import Image

from utils.api_client import (
    analyze_image,
    check_backend_health,
    fetch_history,
    clear_backend_history,
    DEFAULT_BACKEND_URL,
)
from utils.charts import create_band_stats_chart, create_confidence_chart

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Satellite Disaster Monitor",
    page_icon="🛰️",
    layout="wide",
)

st.markdown("""
<style>
    .stAppViewContainer { background-color: #0b0e14; }

    .explanation-card {
        background: linear-gradient(135deg, #131b26 0%, #1a2433 100%);
        border-left: 4px solid #00d2ff;
        border-radius: 8px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }
    .history-card {
        background-color: #131b26;
        border: 1px solid #1e2c3d;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .sensor-label {
        font-size: 0.78em;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #00d2ff;
        margin-bottom: 4px;
    }
    .landslide-label {
        font-size: 0.78em;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #ff9800;
        margin-bottom: 4px;
    }

    /* Severity badges */
    .severity-badge-low      { background:#1b5e20; color:#81c784; padding:4px 12px; border-radius:16px; font-weight:700; display:inline-block; border:1px solid #2e7d32; }
    .severity-badge-medium   { background:#f57f17; color:#fff9c4; padding:4px 12px; border-radius:16px; font-weight:700; display:inline-block; border:1px solid #fbc02d; }
    .severity-badge-moderate { background:#f57f17; color:#fff9c4; padding:4px 12px; border-radius:16px; font-weight:700; display:inline-block; border:1px solid #fbc02d; }
    .severity-badge-high     { background:#e65100; color:#ffe0b2; padding:4px 12px; border-radius:16px; font-weight:700; display:inline-block; border:1px solid #f57c00; }
    .severity-badge-critical { background:#b71c1c; color:#ffcdd2; padding:4px 12px; border-radius:16px; font-weight:700; display:inline-block; border:1px solid #c62828; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛰️ Disaster Monitor")
    st.markdown("Automated multi-sensor satellite imagery classification and situational assessment for response teams.")
    st.divider()

    backend_url = st.text_input(
        "Backend API Base URL",
        value=os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL),
    )

    is_online = check_backend_health(backend_url)
    if is_online:
        st.success("🟢 Backend API: Online")
    else:
        st.error(f"🔴 Backend unreachable at `{backend_url}`")

    st.divider()
    st.markdown("**Active ML Models**")
    st.caption("🌊 Flood: HistGradientBoosting + SAR RF")
    st.caption("⛰️ Landslide: PyTorch ResNet34 UNet")
    st.divider()
    st.caption("Satellite Disaster Assessment System v0.3.0")

# ─── Session state ────────────────────────────────────────────────────────────
for key in ("analysis_results", "analyzed_key", "processing_time"):
    if key not in st.session_state:
        st.session_state[key] = None

def reset_analysis():
    st.session_state["analysis_results"] = None
    st.session_state["analyzed_key"] = None
    st.session_state["processing_time"] = None

# ─── Header & Tabs ────────────────────────────────────────────────────────────
st.title("🛰️ Satellite Disaster Monitoring Dashboard")
tab_analyze, tab_history = st.tabs(["🔍 Real-Time Analysis", "📜 Analysis History"])

# ═══════════════════════ TAB 1 : REAL-TIME ANALYSIS ══════════════════════════
with tab_analyze:
    st.write("Select the target disaster model pipeline and upload satellite imagery for AI assessment.")

    # ── Model Mode Selector ──────────────────────────────────────────────────
    selected_mode = st.radio(
        "Choose Target Disaster AI Model:",
        ["🌊 Flood Detection Model", "⛰️ Landslide Detection Model"],
        horizontal=True
    )

    is_landslide_mode = "Landslide" in selected_mode

    if not is_landslide_mode:
        # ── FLOOD MODEL UPLOAD BLOCKS ─────────────────────────────────────────
        st.subheader("🌊 Flood Detection Pipeline (Multi-Modal / Single Image)")
        st.caption("Processes Optical NDWI, SAR radar backscatter, and Thermal IR for inundated area detection.")

        up_col1, up_col2, up_col3 = st.columns(3, gap="medium")

        with up_col1:
            st.markdown('<div class="sensor-label">🔵 Optical Image</div>', unsafe_allow_html=True)
            optical_file = st.file_uploader(
                "Optical (RGB visual)",
                type=["jpg", "jpeg", "png", "tif", "tiff"],
                key="flood_optical",
                label_visibility="collapsed",
            )
            if optical_file:
                st.image(Image.open(io.BytesIO(optical_file.getvalue())), use_container_width=True, caption="Flood Optical")

        with up_col2:
            st.markdown('<div class="sensor-label">🟣 SAR Image</div>', unsafe_allow_html=True)
            sar_file = st.file_uploader(
                "SAR (radar / cloud-penetration)",
                type=["jpg", "jpeg", "png", "tif", "tiff"],
                key="flood_sar",
                label_visibility="collapsed",
            )
            if sar_file:
                st.image(Image.open(io.BytesIO(sar_file.getvalue())), use_container_width=True, caption="Flood SAR")

        with up_col3:
            st.markdown('<div class="sensor-label">🔴 Thermal IR Image</div>', unsafe_allow_html=True)
            thermal_file = st.file_uploader(
                "Thermal IR (heat / hotspot)",
                type=["jpg", "jpeg", "png", "tif", "tiff"],
                key="flood_thermal",
                label_visibility="collapsed",
            )
            if thermal_file:
                st.image(Image.open(io.BytesIO(thermal_file.getvalue())), use_container_width=True, caption="Thermal IR")

        any_uploaded = bool(optical_file or sar_file or thermal_file)
        st.write("")

        btn_a, btn_b = st.columns([3, 1])
        with btn_a:
            analyze_clicked = st.button(
                "🔍 Analyze Flood Disaster Imagery",
                use_container_width=True,
                type="primary",
                disabled=not any_uploaded,
            )
        with btn_b:
            st.button("🔄 Reset", use_container_width=True, on_click=reset_analysis)

        if not any_uploaded:
            st.info("📂 Please upload at least one satellite image above for Flood detection.")

        current_key = f"flood|{optical_file.name if optical_file else ''}|{sar_file.name if sar_file else ''}|{thermal_file.name if thermal_file else ''}"

        if analyze_clicked and any_uploaded:
            reset_analysis()
            st.session_state["analyzed_key"] = current_key

            start = time.time()
            with st.spinner("Running trained ML Flood Detection Model + Groq LLM assessment..."):
                ok, data = analyze_image(
                    model_type="flood",
                    optical_bytes=optical_file.getvalue() if optical_file else None,
                    optical_name=optical_file.name if optical_file else None,
                    optical_mime=optical_file.type if optical_file else None,
                    sar_bytes=sar_file.getvalue() if sar_file else None,
                    sar_name=sar_file.name if sar_file else None,
                    sar_mime=sar_file.type if sar_file else None,
                    thermal_bytes=thermal_file.getvalue() if thermal_file else None,
                    thermal_name=thermal_file.name if thermal_file else None,
                    thermal_mime=thermal_file.type if thermal_file else None,
                    backend_url=backend_url,
                )
            st.session_state["processing_time"] = round(time.time() - start, 2)

            if ok:
                st.session_state["analysis_results"] = data
                st.toast("✅ Flood disaster analysis complete!", icon="🌊")
            else:
                st.error(data.get("error", "An unknown error occurred."))

    else:
        # ── LANDSLIDE MODEL UPLOAD BLOCKS ─────────────────────────────────────
        st.subheader("⛰️ Landslide Detection Pipeline (PyTorch ResNet34 UNet)")
        st.caption("Activates the trained 14-Channel PyTorch Landslide Segmentation Model to detect slope movement, debris scars, and soil displacement.")

        ls_col1, ls_col2, ls_col3 = st.columns(3, gap="medium")

        with ls_col1:
            st.markdown('<div class="landslide-label">🟢 Landslide Optical / Scarring</div>', unsafe_allow_html=True)
            ls_optical_file = st.file_uploader(
                "Landslide Optical (RGB / Scarring)",
                type=["jpg", "jpeg", "png", "tif", "tiff"],
                key="landslide_optical",
                label_visibility="collapsed",
            )
            if ls_optical_file:
                st.image(Image.open(io.BytesIO(ls_optical_file.getvalue())), use_container_width=True, caption="Landslide Optical")

        with ls_col2:
            st.markdown('<div class="landslide-label">⛰️ DEM Elevation / Slope</div>', unsafe_allow_html=True)
            ls_dem_file = st.file_uploader(
                "DEM Elevation / Slope Gradient Map",
                type=["jpg", "jpeg", "png", "tif", "tiff"],
                key="landslide_dem",
                label_visibility="collapsed",
            )
            if ls_dem_file:
                st.image(Image.open(io.BytesIO(ls_dem_file.getvalue())), use_container_width=True, caption="DEM Slope Elevation")

        with ls_col3:
            st.markdown('<div class="landslide-label">🟣 SAR Texture / Radar</div>', unsafe_allow_html=True)
            ls_sar_file = st.file_uploader(
                "SAR Radar Surface Texture",
                type=["jpg", "jpeg", "png", "tif", "tiff"],
                key="landslide_sar",
                label_visibility="collapsed",
            )
            if ls_sar_file:
                st.image(Image.open(io.BytesIO(ls_sar_file.getvalue())), use_container_width=True, caption="Landslide SAR Radar")

        any_ls_uploaded = bool(ls_optical_file or ls_dem_file or ls_sar_file)
        st.write("")

        btn_a, btn_b = st.columns([3, 1])
        with btn_a:
            analyze_ls_clicked = st.button(
                "⛰️ Run Landslide PyTorch ML Model Analysis",
                use_container_width=True,
                type="primary",
                disabled=not any_ls_uploaded,
            )
        with btn_b:
            st.button("🔄 Reset", use_container_width=True, on_click=reset_analysis)

        if not any_ls_uploaded:
            st.info("📂 Please upload at least one imagery file in the Landslide blocks above.")

        current_key = f"landslide|{ls_optical_file.name if ls_optical_file else ''}|{ls_dem_file.name if ls_dem_file else ''}|{ls_sar_file.name if ls_sar_file else ''}"

        if analyze_ls_clicked and any_ls_uploaded:
            reset_analysis()
            st.session_state["analyzed_key"] = current_key

            start = time.time()
            with st.spinner("Running trained PyTorch ResNet34-UNet Landslide Model + Groq LLM assessment..."):
                ok, data = analyze_image(
                    model_type="landslide",
                    landslide_optical_bytes=ls_optical_file.getvalue() if ls_optical_file else None,
                    landslide_optical_name=ls_optical_file.name if ls_optical_file else None,
                    landslide_optical_mime=ls_optical_file.type if ls_optical_file else None,
                    landslide_dem_bytes=ls_dem_file.getvalue() if ls_dem_file else None,
                    landslide_dem_name=ls_dem_file.name if ls_dem_file else None,
                    landslide_dem_mime=ls_dem_file.type if ls_dem_file else None,
                    landslide_sar_bytes=ls_sar_file.getvalue() if ls_sar_file else None,
                    landslide_sar_name=ls_sar_file.name if ls_sar_file else None,
                    landslide_sar_mime=ls_sar_file.type if ls_sar_file else None,
                    backend_url=backend_url,
                )
            st.session_state["processing_time"] = round(time.time() - start, 2)

            if ok:
                st.session_state["analysis_results"] = data
                st.toast("✅ Landslide model analysis complete & saved to history!", icon="⛰️")
            else:
                st.error(data.get("error", "An unknown error occurred."))

    # ── Results panel ────────────────────────────────────────────────────────
    results = st.session_state.get("analysis_results")

    if results and st.session_state.get("analyzed_key") == current_key:
        st.divider()
        st.subheader("📊 Assessment & Intelligence Report")

        prediction = results.get("prediction", {})
        explanation = results.get("explanation", "")
        proc_time   = st.session_state.get("processing_time")

        disaster_type = prediction.get("disaster_type", "N/A").upper()
        severity      = prediction.get("severity", "low").lower()
        confidence    = prediction.get("confidence", 0.0)
        image_type    = prediction.get("image_type_detected", "Multi-Modal")
        band_stats    = prediction.get("band_stats", {})

        badge_class = f"severity-badge-{severity}"
        badge_icon  = {"low": "🟢", "medium": "🟡", "moderate": "🟡", "high": "🟠", "critical": "🔴"}.get(severity, "🔴")

        st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
            <div>
                <span class="{badge_class}">{badge_icon} SEVERITY: {severity.upper()}</span>
                <span style="font-size:0.9em; color:#aaaaaa; margin-left:10px;">
                    Type: <b>{disaster_type}</b> &nbsp;|&nbsp; Model: {image_type}
                </span>
            </div>
            {f'<div style="font-size:0.85em; color:#00d2ff; background:#131b26; padding:4px 10px; border-radius:12px; border:1px solid #1e2c3d;">⚡ {proc_time}s</div>' if proc_time else ''}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="explanation-card">
            <h4 style="margin-top:0; color:#00d2ff; font-size:1.05em;">🤖 Groq LLM — Senior Analyst Brief</h4>
            <p style="margin-bottom:0; color:#DDDDDD; font-size:0.95em; line-height:1.6;">{explanation}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### Spectral & Model Risk Telemetry")
        mc1, mc2 = st.columns(2)
        with mc1:
            st.pyplot(create_confidence_chart(confidence), use_container_width=True)
        with mc2:
            st.pyplot(create_band_stats_chart(band_stats), use_container_width=True)
        st.caption(f"Debris / Water Pixel Ratio: {band_stats.get('water_pixel_ratio', 0.0):.1%}")

# ═══════════════════════ TAB 2 : ANALYSIS HISTORY ════════════════════════════
with tab_history:
    st.subheader("📜 Historical Analysis Reports")
    st.write("Browse all satellite disaster model analyses saved this session.")

    h1, h2 = st.columns([5, 1])
    with h2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if clear_backend_history(backend_url):
                st.toast("History cleared!", icon="🧹")
                st.rerun()

    ok_hist, history_items = fetch_history(backend_url)

    if not ok_hist or not history_items:
        st.info("No past reports. Run Flood or Landslide disaster analysis in the **Real-Time Analysis** tab to start logging.")
    else:
        st.write(f"Total saved reports: **{len(history_items)}**")
        for item in history_items:
            pred = item.get("prediction", {})
            sev  = pred.get("severity", "low").lower()
            badge_class = f"severity-badge-{sev}"
            badge_icon  = {"low": "🟢", "medium": "🟡", "moderate": "🟡", "high": "🟠", "critical": "🔴"}.get(sev, "🔴")

            with st.expander(
                f"📷  {item.get('filename')}  —  {pred.get('disaster_type', '').upper()}  ({item.get('timestamp')})"
            ):
                images_meta = pred.get("images_analyzed", {})

                st.markdown(f"""
                <div class="history-card">
                    <div style="display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin-bottom:10px;">
                        <span class="{badge_class}">{badge_icon} {sev.upper()}</span>
                        <span>Confidence: <b>{pred.get('confidence', 0.0):.1%}</b></span>
                        <span>Model: <b>{pred.get('image_type_detected', 'Disaster Model')}</b></span>
                    </div>
                    <div style="font-size:0.85em; color:#888; margin-bottom:8px;">
                        <b>Optical / Scarring:</b> {images_meta.get('optical', '—')}<br>
                        <b>SAR / Elevation:</b> {images_meta.get('sar', '—')}<br>
                        <b>Thermal / Texture:</b> {images_meta.get('thermal_ir', '—')}
                    </div>
                    <div style="color:#00d2ff; font-weight:bold; margin-top:6px;">🤖 Groq LLM Assessment:</div>
                    <p style="color:#dddddd; margin-top:4px; line-height:1.55;">{item.get('explanation')}</p>
                </div>
                """, unsafe_allow_html=True)
