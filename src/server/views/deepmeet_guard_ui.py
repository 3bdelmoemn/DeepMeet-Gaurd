import streamlit as st
import requests
import json
import time

# ============================================================
# Config
# ============================================================
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Deepmeet Guard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Custom CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:        #0a0c10;
    --surface:   #111318;
    --border:    #1e2330;
    --accent:    #00f5a0;
    --accent2:   #00c8ff;
    --danger:    #ff4757;
    --warning:   #ffa502;
    --text:      #e8eaf0;
    --muted:     #5a6070;
    --radius:    8px;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Header */
.dg-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 24px 0 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
}
.dg-logo {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}
.dg-title { font-size: 28px; font-weight: 800; letter-spacing: -0.5px; }
.dg-title span { color: var(--accent); }
.dg-subtitle { font-size: 13px; color: var(--muted); font-family: 'Space Mono', monospace; }

/* Cards */
.dg-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 16px;
}
.dg-card-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 16px;
    font-family: 'Space Mono', monospace;
}

/* Status badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-ok      { background: #00f5a015; color: var(--accent);  border: 1px solid var(--accent); }
.badge-err     { background: #ff475715; color: var(--danger);  border: 1px solid var(--danger); }
.badge-warn    { background: #ffa50215; color: var(--warning); border: 1px solid var(--warning); }
.badge-info    { background: #00c8ff15; color: var(--accent2); border: 1px solid var(--accent2); }

/* Response box */
.resp-box {
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: var(--accent);
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 300px;
    overflow-y: auto;
    margin-top: 12px;
}

/* Step indicator */
.step-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
}
.step-num {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #000;
    flex-shrink: 0;
}
.step-label { font-size: 14px; font-weight: 600; }
.step-desc  { font-size: 12px; color: var(--muted); }

/* Override streamlit buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #000 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 1px !important;
    padding: 10px 24px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Danger button */
.danger-btn > button {
    background: linear-gradient(135deg, var(--danger), #c0392b) !important;
    color: #fff !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #0d1117 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px #00f5a020 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #0d1117 !important;
    border: 1px dashed var(--border) !important;
    border-radius: var(--radius) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    border: none !important;
    padding: 12px 24px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* Metric */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 16px !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# Helpers
# ============================================================
def api(method: str, path: str, **kwargs):
    try:
        r = requests.request(method, f"{BASE_URL}{path}", timeout=30, **kwargs)
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return 0, {"error": "Cannot connect to server. Is it running?"}
    except Exception as e:
        return 0, {"error": str(e)}


def show_response(status: int, data: dict):
    if status == 0:
        st.markdown(f'<span class="badge badge-err">CONNECTION ERROR</span>', unsafe_allow_html=True)
    elif 200 <= status < 300:
        st.markdown(f'<span class="badge badge-ok">✓ {status} OK</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="badge badge-err">✗ {status}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="resp-box">{json.dumps(data, indent=2, ensure_ascii=False)}</div>', unsafe_allow_html=True)


def user_id_input(key: str):
    uid = st.session_state.get("last_user_id", "")
    return st.text_input("User ID", value=uid, key=key,
                         placeholder="Paste user_id from Step 1...")


# ============================================================
# Header
# ============================================================
st.markdown("""
<div class="dg-header">
    <div class="dg-logo">🛡️</div>
    <div>
        <div class="dg-title">Deepmeet <span>Guard</span></div>
        <div class="dg-subtitle">API TEST INTERFACE // v1.0.0</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Sidebar — Health + Server Config
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Server")
    base = st.text_input("Base URL", value=BASE_URL, key="base_url")
    BASE_URL = base

    st.markdown("---")
    st.markdown("### 🩺 Health Check")
    if st.button("Ping Server"):
        status, data = api("GET", "/deepmeet/health")
        if status == 200:
            st.markdown('<span class="badge badge-ok">● ONLINE</span>', unsafe_allow_html=True)
            st.json(data)
        else:
            st.markdown('<span class="badge badge-err">● OFFLINE</span>', unsafe_allow_html=True)
            st.json(data)

    st.markdown("---")
    st.markdown("### 📋 Flow Guide")
    steps = [
        ("1", "Upload Info",      "POST /simulator/data/upload/info"),
        ("2", "Upload References","POST /simulator/data/references/upload"),
        ("3", "Impersonate",      "POST /simulator/setup/impersonate"),
        ("4", "Clone Voice",      "POST /simulator/setup/clone"),
        ("5", "Start Session",    "POST /simulator/communication/start"),
        ("6", "End Session",      "POST /simulator/communication/end"),
        ("7", "Get Report",       "POST /simulator/communication/report"),
    ]
    for num, label, route in steps:
        st.markdown(f"""
        <div class="step-row">
            <div class="step-num">{num}</div>
            <div>
                <div class="step-label">{label}</div>
                <div class="step-desc">{route}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if "last_user_id" in st.session_state and st.session_state.last_user_id:
        st.markdown(f"""
        <div class="dg-card">
            <div class="dg-card-title">Active User ID</div>
            <code style="color: var(--accent); font-size: 11px; word-break: break-all;">
                {st.session_state.last_user_id}
            </code>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# Main Tabs
# ============================================================
tab_sim, tab_det = st.tabs(["🤖  SIMULATOR", "🔍  DETECTOR"])


# ============================================================
# SIMULATOR TAB
# ============================================================
with tab_sim:
    col1, col2 = st.columns([1, 1], gap="large")

    # ── LEFT COLUMN ──────────────────────────────────────────
    with col1:

        # Step 1 — Upload Info
        st.markdown('<div class="dg-card"><div class="dg-card-title">Step 1 — Upload User & Org Info</div>', unsafe_allow_html=True)

        with st.expander("👤 User Info", expanded=True):
            name       = st.text_input("Name",       value="Ahmed Youssef",     key="u_name")
            role       = st.text_input("Role",       value="Backend Developer", key="u_role")
            skills     = st.text_input("Skills (comma-separated)",
                                       value="Python, FastAPI, PostgreSQL",      key="u_skills")
            experience = st.text_area("Experience (one per line)",
                                      value="Backend Developer at TechCorp (2022–2024)",
                                      key="u_exp", height=80)
            education  = st.text_input("Education",  value="BSc CS — Cairo University 2021", key="u_edu")
            projects   = st.text_area("Projects (one per line)",
                                      value="E-commerce platform with FastAPI",
                                      key="u_proj", height=80)
            strengths  = st.text_input("Strengths (comma-separated)",
                                       value="Fast learner, problem solver",     key="u_str")
            weaknesses = st.text_input("Weaknesses (comma-separated)",
                                       value="Over-engineering solutions",       key="u_weak")

        with st.expander("🏢 Organization Info", expanded=True):
            company          = st.text_input("Company",      value="Paymob",          key="o_comp")
            industry         = st.text_input("Industry",     value="Fintech",          key="o_ind")
            tech_stack       = st.text_input("Tech Stack (comma-separated)",
                                             value="Python, Microservices, Kubernetes", key="o_tech")
            org_role         = st.text_input("Role",         value="Backend Engineer", key="o_role")
            responsibilities = st.text_area("Responsibilities (one per line)",
                                            value="Build payment processing APIs",
                                            key="o_resp", height=80)

        if st.button("📤 Upload Info", key="btn_upload_info"):
            payload = {
                "user_info": {
                    "name":       name,
                    "role":       role,
                    "skills":     [s.strip() for s in skills.split(",")],
                    "experience": [e.strip() for e in experience.splitlines() if e.strip()],
                    "education":  education,
                    "projects":   [p.strip() for p in projects.splitlines() if p.strip()],
                    "strengths":  [s.strip() for s in strengths.split(",")],
                    "weaknesses": [w.strip() for w in weaknesses.split(",")],
                },
                "organization_info": {
                    "company":          company,
                    "industry":         industry,
                    "tech_stack":       [t.strip() for t in tech_stack.split(",")],
                    "role":             org_role,
                    "responsibilities": [r.strip() for r in responsibilities.splitlines() if r.strip()],
                },
            }
            status, data = api("POST", "/deepmeet/simulator/data/upload/info", json=payload)
            show_response(status, data)
            if status == 200 and "user_id" in data:
                st.session_state.last_user_id = data["user_id"]
                st.success(f"✅ user_id saved: {data['user_id']}")

        st.markdown('</div>', unsafe_allow_html=True)

        # Step 2 — Upload References
        st.markdown('<div class="dg-card"><div class="dg-card-title">Step 2 — Upload References</div>', unsafe_allow_html=True)

        uid2       = user_id_input("uid_refs")
        audio_file = st.file_uploader("🎙️ Audio File", type=["wav", "mp3", "ogg", "m4a"], key="ref_audio")
        text_file  = st.file_uploader("📄 Reference Text", type=["txt"],                  key="ref_text")

        if st.button("📤 Upload References", key="btn_upload_refs"):
            if not uid2:
                st.warning("Please enter a User ID")
            elif not audio_file or not text_file:
                st.warning("Please upload both audio and text files")
            else:
                files  = {
                    "audio":          (audio_file.name,  audio_file,  audio_file.type),
                    "reference_text": (text_file.name,   text_file,   "text/plain"),
                }
                status, data = api("POST", "/deepmeet/simulator/data/upload/references",
                                   data={"user_id": uid2}, files=files)
                show_response(status, data)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT COLUMN ─────────────────────────────────────────
    with col2:

        # Step 3 — Impersonate
        st.markdown('<div class="dg-card"><div class="dg-card-title">Step 3 — Impersonate</div>', unsafe_allow_html=True)
        uid3 = user_id_input("uid_imp")
        if st.button("🎭 Impersonate", key="btn_imp"):
            if not uid3:
                st.warning("Please enter a User ID")
            else:
                status, data = api("POST", f"/deepmeet/simulator/setup/impersonate?user_id={uid3}")
                show_response(status, data)
        st.markdown('</div>', unsafe_allow_html=True)

        # Step 4 — Clone Voice
        st.markdown('<div class="dg-card"><div class="dg-card-title">Step 4 — Clone Voice</div>', unsafe_allow_html=True)
        uid4 = user_id_input("uid_clone")
        if st.button("🔊 Clone Voice", key="btn_clone"):
            if not uid4:
                st.warning("Please enter a User ID")
            else:
                status, data = api("POST", f"/deepmeet/simulator/setup/clone?user_id={uid4}")
                show_response(status, data)
        st.markdown('</div>', unsafe_allow_html=True)

        # Step 5 & 6 — Start / End Simulation
        st.markdown('<div class="dg-card"><div class="dg-card-title">Step 5 & 6 — Simulation Control</div>', unsafe_allow_html=True)
        uid5 = user_id_input("uid_sim")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶ Start", key="btn_start_sim"):
                if not uid5:
                    st.warning("Please enter a User ID")
                else:
                    status, data = api("POST", f"/deepmeet/simulator/communication/start?user_id={uid5}")
                    show_response(status, data)
                    if status == 200:
                        st.session_state.sim_running = True
        with c2:
            st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
            if st.button("■ End", key="btn_end_sim"):
                if not uid5:
                    st.warning("Please enter a User ID")
                else:
                    status, data = api("POST", f"/deepmeet/simulator/communication/end?user_id={uid5}")
                    show_response(status, data)
                    if status == 200:
                        st.session_state.sim_running = False
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Step 7 — Report
        st.markdown('<div class="dg-card"><div class="dg-card-title">Step 7 — Simulation Report</div>', unsafe_allow_html=True)
        uid7 = user_id_input("uid_report")
        if st.button("📊 Get Report", key="btn_sim_report"):
            if not uid7:
                st.warning("Please enter a User ID")
            else:
                status, data = api("POST", f"/deepmeet/simulator/communication/report?user_id={uid7}")
                show_response(status, data)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# DETECTOR TAB
# ============================================================
with tab_det:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # Start Detection
        st.markdown('<div class="dg-card"><div class="dg-card-title">Start Detection</div>', unsafe_allow_html=True)

        meeting_name = st.text_input(
            "Meeting Name",
            value="meeting_001",
            key="det_meeting",
            placeholder="e.g. interview_john_2024"
        )

        if st.button("▶ Start Detection", key="btn_start_det"):
            if not meeting_name:
                st.warning("Please enter a meeting name")
            else:
                status, data = api("POST", f"/deepmeet/detector/start?meeting_name={meeting_name}")
                show_response(status, data)
                if status == 200:
                    st.session_state.det_running     = True
                    st.session_state.det_meeting_name = meeting_name

        st.markdown('</div>', unsafe_allow_html=True)

        # End Detection
        st.markdown('<div class="dg-card"><div class="dg-card-title">End Detection</div>', unsafe_allow_html=True)

        # Status indicator
        if st.session_state.get("det_running"):
            st.markdown('<span class="badge badge-ok">● RUNNING</span>', unsafe_allow_html=True)
            st.markdown(f"<small style='color: var(--muted)'>Meeting: {st.session_state.get('det_meeting_name', '')}</small>", unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-warn">● IDLE</span>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("■ End Detection", key="btn_end_det"):
            status, data = api("POST", "/deepmeet/detector/end")
            show_response(status, data)
            if status == 200:
                st.session_state.det_running = False
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Detection Report
        st.markdown('<div class="dg-card"><div class="dg-card-title">Detection Report</div>', unsafe_allow_html=True)

        report_meeting = st.text_input(
            "Meeting Name",
            value=st.session_state.get("det_meeting_name", ""),
            key="det_report_meeting",
            placeholder="Enter meeting name to fetch report"
        )

        if st.button("📊 Get Detection Report", key="btn_det_report"):
            if not report_meeting:
                st.warning("Please enter a meeting name")
            else:
                status, data = api("GET", f"/deepmeet/detector/report?meeting_name={report_meeting}")
                show_response(status, data)

                # Summary cards if success
                if status == 200 and "report" in data:
                    r = data["report"]
                    st.markdown("<br>", unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Total Samples", r.get("total_samples", 0))
                    with m2:
                        st.metric("Fake", r.get("total_fake", 0))
                    with m3:
                        st.metric("Real", r.get("total_real", 0))

                    verdict = r.get("verdict", "Unknown")
                    badge   = "badge-err" if verdict == "Fake" else "badge-ok"
                    st.markdown(f"""
                    <div style="text-align:center; margin-top: 16px;">
                        <div style="font-size: 13px; color: var(--muted); margin-bottom: 8px; font-family: 'Space Mono', monospace;">VERDICT</div>
                        <span class="badge {badge}" style="font-size: 16px; padding: 8px 24px;">
                            {verdict.upper()}
                        </span>
                        <div style="font-size: 12px; color: var(--muted); margin-top: 8px;">
                            {r.get('fake_percentage', 0)}% fake across {len(r.get('periods', []))} period(s)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)