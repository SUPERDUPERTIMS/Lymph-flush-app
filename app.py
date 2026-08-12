import csv
import html
import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Kinetic Pulse: Mobile Performance Suite",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Named page constants instead of magic integers
PAGE_PROFILE = 1
PAGE_SELECT = 2
PAGE_SESSION = 3
PAGE_ADMIN_LOGIN = 4
PAGE_ADMIN_VIEW = 5

PAYMENT_URL = "https://ko-fi.com/kineticpulseapp"
LOG_FILE_PATH = "kinetic_session_logs.csv"

# ==========================================
# 2. SECRETS / ADMIN AUTH
# ==========================================
# Password now comes from st.secrets, never hardcoded in source.
# Locally: create .streamlit/secrets.toml with:
#   admin_password = "your-password-here"
# On Streamlit Community Cloud: set it in the app's Secrets settings.
ADMIN_PASSWORD = st.secrets.get("admin_password")

# Basic brute-force throttling for the admin login page.
ADMIN_MAX_ATTEMPTS = 5
ADMIN_LOCKOUT_SECONDS = 60


def sanitize_text(value: str, max_len: int = 200) -> str:
    """Escape HTML and cap length before any user-supplied text is
    interpolated into unsafe_allow_html markdown or written to CSV.
    Prevents self-XSS via the name/notes fields."""
    if value is None:
        return ""
    value = str(value)[:max_len]
    return html.escape(value, quote=True)


def csv_safe(value: str) -> str:
    """Neutralize CSV/formula injection (e.g. values starting with
    =, +, -, @) for anyone who opens the log in Excel/Sheets."""
    value = str(value)
    if value and value[0] in ("=", "+", "-", "@"):
        return "'" + value
    return value


# ==========================================
# 3. HARD SAFETY & MEDICAL GATE
# ==========================================
def render_safety_gate() -> bool:
    if st.session_state.get("disclaimer_accepted", False):
        return True

    st.title("⚡ Kinetic Pulse")
    st.warning("⚠️ SAFETY, MEDICAL & LEGAL NOTICE")

    st.markdown(
        """
    ### 1. Medical Contraindications
    * **Avoid use** if you have active hernias, recent surgical procedures, cardiovascular issues, acute joint injuries, or are pregnant.
    * Consult a licensed physician or physical therapist prior to starting any physical routine.

    ### 2. Software & AI Output Disclaimer
    * **Kinetic Pulse** was developed with AI assistance and is designed purely for general informational and tracking purposes.
    * This software does **not** provide medical advice, diagnosis, physical therapy, or individualized clinical recommendations.

    ### 3. Assumption of Risk & Release of Liability
    * Physical exercise carries inherent risks of serious injury. By proceeding, you **voluntarily assume all risk** of physical harm, illness, or injury resulting from your use of this application.
    * You hereby release, waive, and hold harmless the developer(s) and owners from any liabilities, claims, or financial losses arising out of application usage or exercise execution.
    """
    )

    st.markdown("---")
    st.subheader("Required Confirmations")

    cb1 = st.checkbox(
        "I confirm I have no active contraindications (hernias, recent surgery,"
        " pregnancy, acute injuries)."
    )
    cb2 = st.checkbox(
        "I acknowledge this app is AI-assisted and agree to consult a medical"
        " specialist before acting on suggestions."
    )
    cb3 = st.checkbox("I confirm I am 18 years of age or older.")
    cb4 = st.checkbox(
        "I agree to the Release of Liability and voluntarily assume all physical"
        " and technical risks associated with app use."
    )

    all_accepted = cb1 and cb2 and cb3 and cb4

    st.write("")
    if st.button(
        "Enter Kinetic Pulse",
        disabled=not all_accepted,
        type="primary",
        use_container_width=True,
    ):
        st.session_state["disclaimer_accepted"] = True
        st.rerun()

    return False


if not render_safety_gate():
    st.stop()

with st.sidebar:
    st.markdown("### ⚡ Kinetic Pulse")
    st.caption("Legal & Safety Status: **Verified**")
    if st.button("Review Safety & Legal Terms", use_container_width=True):
        st.session_state["disclaimer_accepted"] = False
        st.rerun()
    st.markdown("---")

# ==========================================
# 4. GLOBAL CSS
# ==========================================
st.markdown(
    """
<style>
/* Aggressively hide Streamlit Cloud headers, toolbars, and share buttons */
header,
[data-testid="stHeader"],
[data-testid="stAppHeader"],
[data-testid="stHeaderToolbar"],
.stAppToolbar,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
[data-testid="stActionButton"],
[data-testid="baseButton-headerNoPadding"],
.stDeployButton,
#MainMenu,
footer,
[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

.stAppViewContainer, [data-testid="stAppViewContainer"], .main {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

.stApp {
    background-color: #f7f7f8 !important;
    padding: 0px 4px;
}

p, span, label, div, h1, h2, h3, h4, h5, h6 {
    color: #1a1a1a;
}

.stMarkdown, .stText, div[data-testid="stMarkdownContainer"] > p {
    color: #1a1a1a !important;
}

div[data-baseweb="input"], div[data-baseweb="textarea"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
}

div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
    color: #1a1a1a !important;
    background-color: #ffffff !important;
}

div[role="radiogroup"] label p, div[data-baseweb="checkbox"] label p {
    color: #1a1a1a !important;
    font-weight: 600 !important;
}

.stButton>button {
    width: 100%;
    border-radius: 50px !important;
    font-weight: 700;
    font-size: 1.1rem;
    padding: 14px 20px;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
}

.stButton>button[kind="primary"] {
    background-color: #0c38ff !important;
    border: none;
    color: #ffffff !important;
    box-shadow: 0 8px 16px rgba(12, 56, 255, 0.2);
}

.stButton>button[kind="primary"]:active {
    transform: scale(0.97);
}

.stButton>button[kind="secondary"] {
    background-color: #ffffff !important;
    border: 2px solid #eaeaea;
    color: #333333 !important;
}

.stButton>button[disabled] {
    opacity: 0.45 !important;
    cursor: not-allowed !important;
    background-color: #e2e8f0 !important;
    border: 1px solid #cbd5e1 !important;
    color: #64748b !important;
    box-shadow: none !important;
}

.st-key-admin_btn_container {
    position: fixed !important;
    bottom: 2px !important;
    right: 2px !important;
    z-index: 999999 !important;
    width: auto !important;
    margin: 0 !important;
    padding: 0 !important;
}

.st-key-admin_btn_container button {
    font-size: 0.65rem !important;
    padding: 3px 8px !important;
    border-radius: 8px !important;
    background-color: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid #ccc !important;
    color: #333 !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2) !important;
    width: auto !important;
}

.curved-header {
    background-color: #ff9800 !important;
    margin: -4rem -2rem 2rem -2rem;
    padding: 4rem 2rem 3rem 2rem;
    border-bottom-left-radius: 50% 15%;
    border-bottom-right-radius: 50% 15%;
    text-align: center;
    box-shadow: 0 4px 12px rgba(255, 152, 0, 0.15);
}

.curved-header h1 {
    color: #ffffff !important;
    margin-bottom: 0px;
    font-size: 2.2rem;
    font-weight: bold;
}

.curved-header p {
    color: rgba(255, 255, 255, 0.95) !important;
    font-size: 1.1rem;
    margin-top: 5px;
}

.protocol-card {
    background: #ffffff !important;
    padding: 24px;
    border-radius: 24px;
    border: 1px solid #f0f0f0;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    margin-bottom: 16px;
}

.selection-box {
    background: #ffffff !important;
    padding: 20px;
    border-radius: 24px;
    border: 1px solid #f0f0f0;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    margin-bottom: 14px;
}

.metric-container {
    background: #ffffff !important;
    padding: 18px;
    border-radius: 20px;
    border-left: 5px solid #ff9800;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    margin: 14px 0;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #4a4a4a !important;
}

.breath-box {
    background: #ffffff !important;
    border: 2px solid #0c38ff;
    padding: 18px;
    border-radius: 50px;
    text-align: center;
    font-size: 1.1rem;
    font-weight: bold;
    color: #0c38ff !important;
    margin: 15px 0;
    box-shadow: inset 0 2px 4px rgba(12, 56, 255, 0.05);
}

.contract-box {
    background: #e8f4fd !important;
    border: 2px solid #2196f3;
    padding: 14px;
    border-radius: 16px;
    text-align: center;
    font-size: 1rem;
    font-weight: bold;
    color: #0d47a1 !important;
    margin: 12px 0;
}

.pressure-warning {
    background: #fff8f0 !important;
    border: 1px solid #ffe0b2;
    padding: 14px;
    border-radius: 16px;
    color: #d84315 !important;
    font-weight: 600;
    font-size: 0.95rem;
    margin: 12px 0;
}

.support-box {
    text-align: center;
    margin-top: 25px;
    margin-bottom: 25px;
    padding: 20px;
    background: #ffffff;
    border-radius: 24px;
    border: 1px solid #f0f0f0;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
}

.support-box a.kofi-btn {
    display: inline-block;
    background-color: #29abe0;
    color: white !important;
    padding: 12px 20px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 4px 10px rgba(41, 171, 224, 0.2);
    transition: all 0.2s ease;
}

.side-visual-left {
    background:#e3f2fd; border:2px solid #2196f3; border-radius:15px;
    padding:15px; text-align:center; margin-bottom: 15px;
}
.side-visual-right {
    background:#e8f5e9; border:2px solid #4caf50; border-radius:15px;
    padding:15px; text-align:center; margin-bottom: 15px;
}
.side-visual-center {
    background:#fff3e0; border:2px solid #ff9800; border-radius:15px;
    padding:15px; text-align:center; margin-bottom: 15px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 5. SHARED UI HELPERS (dedupe repeated markup)
# ==========================================
def scroll_to_top():
    """Forces both JS window scroll and container scroll to the absolute top,
    plus removes Streamlit header/toolbar bars. Retries a handful of times
    because the DOM for the new page/step is still being painted when this
    first fires on rerun — a single fire-and-forget attempt can land before
    the new content (and its height) exists, leaving the scroll a no-op."""
    components.html(
        """
        <script>
            function doScroll() {
                var doc = window.parent.document;
                var headers = doc.querySelectorAll(
                    'header, [data-testid="stHeader"], [data-testid="stAppHeader"], .stAppToolbar, [data-testid="stToolbar"]'
                );
                headers.forEach(function(el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.height = '0px';
                });
                var container = doc.querySelector('.main') || doc.querySelector('[data-testid="stAppViewContainer"]');
                if (containers) { container.scrollTop = 0; }
                window.parent.scrollTo({ top: 0, behavior: 'instant' });
            }
            var tries = 0;
            var iv = setInterval(function() {
                doScroll();
                tries += 1;
                if (tries > 6) { clearInterval(iv); }
            }, 80);
        </script>
        """,
        height=0,
        width=0,
    )


def render_header(title: str, subtitle: str = ""):
    """Single source of truth for the curved page header (was duplicated
    ~8 times with copy-pasted HTML)."""
    subtitle_html = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"""<div class="curved-header"><h1>{html.escape(title)}</h1>{subtitle_html}</div>""",
        unsafe_allow_html=True,
    )


def render_support_box():
    """Single source of truth for the Ko-fi support box (was duplicated
    verbatim in two places)."""
    st.markdown(
        f"""
    <div class="support-box">
        <h4 style="margin-top: 0; color: #333;">Support KineticPulse ☕</h4>
        <p style="color: #666; font-size: 0.95rem; margin-bottom: 15px;">
            If you found this App useful, please support further development
            with a tip or donation on Ko-fi!
        </p>
        <a href="{PAYMENT_URL}" target="_blank" class="kofi-btn">☕ Support on Ko-fi</a>
    </div>
    """,
        unsafe_allow_html=True,
    )


def resolve_image_path(base_filename: str):
    if not base_filename:
        return None
    if os.path.exists(base_filename):
        return base_filename
    stem, _ = os.path.splitext(base_filename)
    for alt_ext in (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"):
        candidate = stem + alt_ext
        if os.path.exists(candidate):
            return candidate
    return None


def log_session_to_csv(name: str, protocol_name: str, rating, notes: str):
    """Append-only CSV log. Values are CSV-injection-escaped. Note: on
    ephemeral hosting (e.g. Streamlit Community Cloud) this file will not
    survive a redeploy/restart — swap in a real datastore (SQLite hosted
    volume, Google Sheets, Supabase, etc.) if long-term logs matter."""
    try:
        file_exists = os.path.isfile(LOG_FILE_PATH)
        with open(LOG_FILE_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(
                    ["Timestamp", "Practitioner Name", "Protocol", "Tension Rating", "Notes"]
                )
            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    csv_safe(name),
                    csv_safe(protocol_name),
                    rating,
                    csv_safe(notes),
                ]
            )
    except OSError as e:
        st.warning(f"⚠️ Could not save session log: {e}")


# ==========================================
# 6. SESSION STATE INIT
# ==========================================
DEFAULT_PROTOCOL = "Kinetic Synergy: The Core, Hip & Pelvic Release Protocol"

_defaults = {
    "app_page": PAGE_PROFILE,
    "user_name": "",
    "session_notes": "",
    "selected_protocol": DEFAULT_PROTOCOL,
    "current_step_index": 0,
    "admin_authenticated": False,
    "admin_attempts": 0,
    "admin_locked_until": 0.0,
    "timer_running": False,
    "timer_start": None,
}
for key, default_val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

with st.container(key="admin_btn_container"):
    if st.button("Admin", key="floating_admin_btn"):
        st.session_state.app_page = PAGE_ADMIN_LOGIN
        scroll_to_top()
        st.rerun()

# ==========================================
# 7. PROTOCOL DATA — single source of truth
# ==========================================
manual_lymph_steps = [
    {
        "step": "Step 1: Manual Lymphatic Priming (Opening Nodes)",
        "duration": 30,
        "image_file": "",
        "positioning": "Lie flat in a butterfly pose (soles of feet together, knees open).",
        "distance": "Superficial inguinal area in the groin crease.",
        "where": "Central lower abdomen and inner groin fold.",
        "action": (
            "Device OFF. Use warm hands. Perform 1 pelvic floor contract-relax"
            " cycle (squeeze 4s, release 6s). Follow with featherlight outward"
            " manual sweeps along the inner groin crease for 30 seconds."
        ),
        "goal": "Activates primary lower body lymphatic hubs using targeted manual stimulation and breathwork.",
        "benefit_text": "💡 Primary drainage routes are safely opened manually.",
        "switch_sides": False,
    },
    {
        "step": "Step 2: Outer Hip & Tensor Fasciae Latae (TFL) Release",
        "duration": 60,
        "image_file": "",
        "positioning": "Maintain butterfly posture to keep hip flexors elongated.",
        "distance": "Thick muscle belly of outer hip and upper thigh.",
        "where": "Outer hip and upper thigh muscle belly.",
        "action": (
            "Use a featherlight touch with the heel of your hand or knuckles."
            " Apply steady pressure into the TFL. Hold or make small circles"
            " (30 seconds per side)."
        ),
        "goal": "Releases restrictions in the lateral hip chain to restore fluid gait and neutral pelvic alignment.",
        "benefit_text": "💡 Lateral hip tension is safely pre-released.",
        "switch_sides": True,
    },
    {
        "step": "Step 3: Sub-Umbilical Gentle Glide",
        "duration": 45,
        "image_file": "",
        "positioning": "Transition to hook-lying position (knees bent at 90 degrees, feet flat).",
        "distance": "Sub-umbilical zone spanning 10 cm band directly below navel.",
        "where": "Sub-umbilical abdominal zone.",
        "action": (
            "Using flat pads of fingers, angle hands downward at 45 degrees."
            " Apply a smooth downward glide toward the lower pelvis. Never"
            " press hard."
        ),
        "goal": "Mobilizes mid-level abdominal fascia to release lower core rigidity and improve circulatory flow.",
        "benefit_text": "💡 Mid-level fascial mobility is safely encouraged.",
        "switch_sides": False,
    },
    {
        "step": "Step 4: Low-Pelvic Glide & Hold",
        "duration": 120,
        "image_file": "",
        "positioning": (
            "Sustained pelvic tilt (exhale, draw navel down, flatten lower back"
            " flush against floor)."
        ),
        "distance": "Lower pelvic region positioned over upper pubic mound.",
        "where": "Lower pelvic boundary where soft tissue meets pubic bone.",
        "action": (
            "Place fingertips just above pubic bone. Execute a slow downward"
            " stroke with a stationary pause. Perform 2 pelvic floor"
            " contract-relax cycles during pause, and repeat."
        ),
        "goal": "Integrates deep pelvic floor activation against a stable skeletal base to reset core stability patterns.",
        "benefit_text": "💡 Lower core tissue is mobilized against a safe skeletal barrier.",
        "switch_sides": False,
    },
    {
        "step": "Step 5: Outer Hip V-Sweep (The Flush)",
        "duration": 90,
        "image_file": "",
        "positioning": "Return to butterfly leg positioning to fully open pelvic outlet.",
        "distance": "Spanning from lower center base, sweeping outward toward hip bones.",
        "where": "Vertical centerline out toward hips.",
        "action": (
            "Glide downward with flat palms, pause 5–10s with pelvic floor"
            " relaxation, then curve outward and upward over the iliac crest"
            " in a V-shape."
        ),
        "goal": "Encourages complete fluid drainage from the pelvic core toward primary lateral elimination pathways.",
        "benefit_text": "💡 Interstitial fluid is safely flushed toward lateral pathways.",
        "switch_sides": False,
    },
]

lymph_steps = [
    {
        "step": "Step 1A: Manual Lymphatic Priming & Adductor Opening",
        "duration": 30,
        "image_file": "step1A.png",
        "extra_image_file": "step1A_extra.png",
        "positioning": (
            "Lie flat in a butterfly pose (soles of feet together, knees"
            " relaxed open to the sides) to open the groin crease and expose"
            " primary lymphatic nodes."
        ),
        "distance": "Superficial inguinal area in the groin crease.",
        "where": "Inner groin crease & primary lymphatic nodes.",
        "action": (
            "Perform 1 pelvic floor contract-relax cycle (squeeze inward for 4"
            " seconds, fully release for 6 seconds) to generate a localized"
            " fluid flush. Follow with featherlight, outward manual sweeps"
            " along the inner groin crease for 30 seconds."
        ),
        "goal": "Clears proximal lymphatic blockages and restores inner thigh flexibility by combining manual priming and active muscular pumping.",
        "benefit_text": "💡 Opens primary lymphatic hubs, reduces pelvic fluid accumulation, and improves inner thigh flexibility.",
        "switch_sides": False,
    },
    {
        "step": "Step 1B: Outer Hip & TFL Decompression",
        "duration": 60,
        "image_file": "step1B.jpg",
        "extra_image_file": "",
        "positioning": "Maintain the butterfly posture to keep hip flexors elongated.",
        "distance": "Outer hip belly (Tensor Fasciae Latae).",
        "where": "The thick muscle belly of the outer hip (TFL).",
        "action": (
            "Place the soft attachment at low speed over the TFL. Perform 1"
            " contract-relax cycle, then hold stationary with a featherlight"
            " touch for 30 seconds per side."
        ),
        "goal": "Decompresses deep lateral hip tissue to unblock primary circulation routes and restore neutral pelvic rotational balance.",
        "benefit_text": "💡 Releases outer hip tightness, reduces lateral pelvic pulling, and improves hip rotation.",
        "switch_sides": True,
    },
    {
        "step": "Step 2: Sub-Umbilical Mid-Release",
        "duration": 45,
        "image_file": "step2.jpg",
        "extra_image_file": "step2_extra.png",
        "positioning": (
            "Transition to a hook-lying position (knees bent at 90 degrees,"
            " feet flat on the floor). Avoid butterfly pose here to keep the"
            " lower belly soft rather than stretched taut."
        ),
        "distance": "Sub-umbilical band (10 cm band directly below the navel).",
        "where": "Directly below the navel across a 10 cm band.",
        "action": (
            "Using a featherlight touch, angle the device at 45 degrees"
            " downward. Perform slow, steady downward glides across the 10"
            " cm band directly below the navel for 45 seconds."
        ),
        "goal": "Softens sub-umbilical rigidity and breaks localized water retention to promote better circulatory flow in the lower core.",
        "benefit_text": "💡 Clears mid-level fascial tightness, breaks up water retention, and flattens lower stomach contour.",
        "switch_sides": False,
    },
    {
        "step": "Step 3: Low-Pelvic Frame Release & Core Stabilization",
        "duration": 120,
        "image_file": "step3.png",
        "extra_image_file": "",
        "positioning": (
            "Execute a single sustained pelvic tilt. Exhale, draw the navel"
            " down, and flatten the lower back completely flush against the"
            " floor without lifting the glutes. Hold this flat-back posture"
            " throughout."
        ),
        "distance": "Pubic bone frame & lower abdominal wall.",
        "where": "Lower pelvic boundary where soft tissue transitions into the pubic bone frame.",
        "action": (
            "Execute a slow downward glide to the pubic bone frame, followed"
            " by a stationary pause. Perform 2 pelvic floor contract-relax"
            " cycles during the pause phase, and repeat (total duration: 120"
            " seconds)."
        ),
        "goal": "Targets deep fascial restrictions against a stable bone frame to strengthen core integration and dramatically improve deep circulatory pumping.",
        "benefit_text": "💡 Targets dense pelvic fascia against a skeletal barrier, strengthens deep core activation, and accelerates drainage.",
        "switch_sides": False,
    },
    {
        "step": "Step 4: Outer Hip V-Sweep & Final Drainage",
        "duration": 90,
        "image_file": "step4.png",
        "extra_image_file": "",
        "positioning": "Return to butterfly leg positioning to fully open the pelvic outlet.",
        "distance": "Vertical centerline out to the iliac crest (hip bone).",
        "where": "Lower center base sweeping outward and upward over the hip bone.",
        "action": (
            "Glide downward toward the lower center base, pause for 5–10"
            " seconds while completing a final pelvic floor relaxation, then"
            " curve outward and upward over the iliac crest (hip bone) in a"
            " V-shaped path for 90 seconds."
        ),
        "goal": "Seals the session by ensuring complete circulatory and fluid drainage from the pelvic base toward primary lateral elimination pathways.",
        "benefit_text": "💡 Flushes all mobilized fluid toward peripheral routes, leaving lower abdomen light, uncompressed, and visibly toned.",
        "switch_sides": False,
    },
]

hip_steps = [
    {
        "step": "Step 1: Tensor Fasciae Latae (TFL) & Upper Outer Hip",
        "duration": 120,
        "image_file": "hip_step1.png",
        "distance": "Outer hip flare (TFL insertion)",
        "where": "Just below the hard bony iliac crest of the outer hip.",
        "action": "High speed at a 45-degree angle. Maintain steady contact for 60 seconds per side.",
        "goal": "Disarms lateral muscular guarding at the TFL insertion to restore unrestricted hip rotational velocity.",
        "benefit_text": "💡 Continuous pressure drops protective lateral muscle guarding.",
        "switch_sides": True,
    },
    {
        "step": "Step 2: Gluteus Medius & Minimus Stabilizers",
        "duration": 120,
        "image_file": "hip_step2.png",
        "distance": "Upper-outer gluteal region",
        "where": "Posterior to the TFL across the upper glute shelf.",
        "action": "Medium speed. Smooth circular sweeps and stationary holds for 60 seconds per side.",
        "goal": "Optimizes lateral pelvic stabilization patterns to maximize peak ground force production during single-leg drive.",
        "benefit_text": "💡 Stabilizing glute fibers enhances single-leg balance during chambering.",
        "switch_sides": True,
    },
    {
        "step": "Step 3: Deep External Rotators (Piriformis & Gemelli)",
        "duration": 120,
        "image_file": "hip_step3.png",
        "distance": "Deep posterior hip pocket",
        "where": "Center of the glute tracking toward the greater trochanter.",
        "action": "Medium-high speed. Targeted stationary holds on tender trigger points for 60 seconds per side.",
        "goal": "Unlocks fluid end-range hip rotation by releasing deep rotational restrictions, improving turning kick fluidity.",
        "benefit_text": "💡 Releasing deep rotators restores full internal/external rotational mobility.",
        "switch_sides": True,
    },
    {
        "step": "Step 4: Anterior Hip Flexors (Rectus Femoris)",
        "duration": 120,
        "image_file": "hip_step4.png",
        "distance": "Upper front thigh",
        "where": "Just below the front hip bone (ASIS), tracking down the quad.",
        "action": "Medium speed. Slow longitudinal sweeps for 60 seconds per side.",
        "goal": "Disrupts neural flexor guarding on the anterior chain to allow for cleaner, faster, vertical chamber acceleration.",
        "benefit_text": "💡 Disrupted guarding allows for cleaner vertical leg chamber acceleration.",
        "switch_sides": True,
    },
    {
        "step": "Step 5: Iliopsoas Deep Pocket Release",
        "duration": 120,
        "image_file": "hip_step5.png",
        "distance": "Deep inner hip crease",
        "where": "Internal to the ASIS bone in the soft pocket of the hip crease.",
        "action": "Low speed, featherlight touch. Gentle stationary holds for 60 seconds per side.",
        "goal": "Decompresses deep psoas hypertonicity using safe mechanical resonance to achieve deep, high knee-drive capabilities.",
        "benefit_text": "💡 Softening the deep psoas unlocks high knee-drive capabilities.",
        "switch_sides": True,
    },
    {
        "step": "Step 6: Dynamic Low-Lunge & Hip Flexor Integration",
        "duration": 120,
        "image_file": "hip_step6.png",
        "distance": "Anterior Hip Flexor & Adductor Chain",
        "where": "Half-kneeling low-lunge position (rear knee grounded, front knee over ankle).",
        "action": (
            "Adopt a stable low lunge. Tuck your pelvis underneath (posterior"
            " tilt), engage the glute on the trailing leg, and gently shift"
            " hips forward. Hold or lightly pulse for 60 seconds per side."
        ),
        "goal": "Converts passive tissue mobility gains into stable, dynamic end-range performance required for kicking and jumping.",
        "benefit_text": "💡 Active lunge stretching converts passive tissue release into usable athletic mobility.",
        "switch_sides": True,
    },
]

forearm_steps = [
    {
        "step": "Step 1: Lateral Epicondyle & Extensor Mass",
        "duration": 180,
        "image_file": "step5.png",
        "distance": "Outer Forearm",
        "where": "Lateral Epicondyle & Extensor Mass",
        "action": "Med-High Speed. Sweeping motion. (90s per side)",
        "goal": "Decompresses the Tennis/Padel Elbow Zone and extensor mass tension.",
        "benefit_text": "💡 Sweeping motions relax the extensor mass.",
        "switch_sides": True,
    },
    {
        "step": "Step 2: Medial Epicondyle & Flexor Belly",
        "duration": 180,
        "image_file": "step5.png",
        "distance": "Inner Forearm",
        "where": "Medial Epicondyle & Flexor Belly",
        "action": "Med Speed. Deep pulses. (90s per side)",
        "goal": "Targets the Golfer Elbow Zone to release flexor chain hypertonicity.",
        "benefit_text": "💡 Deep pulses release inner forearm flexors.",
        "switch_sides": True,
    },
    {
        "step": "Step 3: Posterior Capsule & Infraspinatus",
        "duration": 240,
        "image_file": "step5.png",
        "distance": "Back of Shoulder",
        "where": "Posterior Capsule & Infraspinatus",
        "action": "High Speed. Circular motions. (120s per side)",
        "goal": "Unlocks fluid posterior shoulder rotational mobility.",
        "benefit_text": "💡 Circular motions free up the shoulder capsule.",
        "switch_sides": True,
    },
    {
        "step": "Step 4: Bicep Tendon & Pec Minor Sweep",
        "duration": 240,
        "image_file": "step5.png",
        "distance": "Front of Shoulder/Chest",
        "where": "Bicep Tendon & Pec Minor",
        "action": "High Speed. Fast, light sweeps. (120s per side)",
        "goal": "Relieves anterior shoulder pulling and pec minor guarding.",
        "benefit_text": "💡 Fast sweeps relieve anterior pulling.",
        "switch_sides": True,
    },
]

ankle_steps = [
    {
        "step": "Step 1: Soleus & Gastrocnemius Flush",
        "duration": 240,
        "image_file": "step5.png",
        "distance": "Calves & Lower Leg",
        "where": "Soleus & Gastrocnemius",
        "action": "High Speed. Sweeping glides. (120s per side)",
        "goal": "Optimizes ankle dorsiflexion and calf decompression.",
        "benefit_text": "💡 Sweeping glides flush the posterior chain.",
        "switch_sides": True,
    },
    {
        "step": "Step 2: Peroneal & Anterior Tibialis Balance",
        "duration": 180,
        "image_file": "step5.png",
        "distance": "Outer and Front Lower Leg",
        "where": "Peroneal & Anterior Tibialis",
        "action": "Med-High Speed. Longitudinal sweeps. (90s per side)",
        "goal": "Targets the Lateral Stability Zone to optimize ankle stability.",
        "benefit_text": "💡 Longitudinal sweeps restore lower leg balance.",
        "switch_sides": True,
    },
    {
        "step": "Step 3: Tibialis Posterior & Deep Ankle Pocket",
        "duration": 180,
        "image_file": "step5.png",
        "distance": "Inner Ankle/Lower Leg",
        "where": "Tibialis Posterior & Deep Ankle Pocket",
        "action": "Med Speed. Targeted pulses. (90s per side)",
        "goal": "Releases deep rotators to restore medial support structure integrity.",
        "benefit_text": "💡 Targeted pulses release deep ankle pockets.",
        "switch_sides": True,
    },
    {
        "step": "Step 4: Plantar Fascia & Dynamic Calf Stretch",
        "duration": 120,
        "image_file": "step5.png",
        "distance": "Sole of foot and calf",
        "where": "Plantar Fascia & Calf",
        "action": "High Speed (sole). Roll 30s per foot, followed by Active stretch for 30s per leg.",
        "goal": "Integrates ground-force transmission mechanics through the entire chain.",
        "benefit_text": "💡 Rolling and stretching completes ground force integration.",
        "switch_sides": True,
    },
]

synergy_steps = [
    {
        "step": "Step 1: Sub-Umbilical Abdominal & Pelvic Framing",
        "duration": 45,
        "image_file": "step1_priming.png", # Fallback image used
        "positioning": "Hook-lying position (knees bent, feet flat) with lower back pressed gently flat.",
        "distance": "Sub-umbilical band (below navel) down to the pubic bone.",
        "where": "Soft sub-umbilical abdominal area.",
        "action": "Use low-speed vibration or flat-fingered downward glides (45 degrees) across the lower stomach. Slow belly inhales and exhales.",
        "goal": "Mobilizes mid-level fascial mobility to soften abdominal rigidity, flatten core contour, and initiate circulation.",
        "benefit_text": "💡 Softens core rigidity, flattens contours, and initiates local circulation.",
        "switch_sides": False,
    },
    {
        "step": "Step 2: Tensor Fasciae Latae (TFL) & Lateral Hip Release",
        "duration": 60,
        "image_file": "step2_tfl_corrected.png", # NEW CORRECTED IMAGE (Side-lying, Outer Hip)
        "positioning": "Side-lying pose (lie on left side to work right hip).",
        "distance": "Thick muscle belly on outer hip flare (just below iliac crest).",
        "where": "Tensor Fasciae Latae (TFL).",
        "action": "Steady, stationary compression or small circular pulses at low speed (30s per side).",
        "goal": "Disarms protective lateral guarding in the TFL insertion to instantly unblock pelvic rotational mobility.",
        "benefit_text": "💡 Disarms lateral muscle guarding, instantly unlocking pelvic rotational mobility.",
        "switch_sides": True,
    },
    {
        "step": "Step 3: Deep External Rotators & Gluteal Release",
        "duration": 60,
        "image_file": "step3_glute_corrected.png", # NEW CORRECTED IMAGE (Supine, Upper/Outer Glute)
        "positioning": "Supine (on back) in 'figure-four' stretch (crossed ankle over knee).",
        "distance": "Upper-outer quadrant of the gluteal muscle belly.",
        "where": "Posterior hip pocket (targeting Piriformis/deep rotators).",
        "action": "Medium speed pulses or stationary compression (30s per side).",
        "goal": "Targets deep gluteal restrictions to unblock sacral nerve signaling (S2-S4) and unleashed circulatory flow to the pelvic floor.",
        "benefit_text": "💡 Releases deep rotators to unblock sacral nerve pathways and pelvic blood flow.",
        "switch_sides": True,
    },
    {
        "step": "Step 4: The Vascular Sponge (Pelvic Floor Pumping & Breath-Hold)",
        "duration": 90,
        "image_file": "step4_pumping.png", # No-device image used
        "positioning": "Reclined hook-lying position (feet flat) or relaxed butterfly posture.",
        "distance": "Deep pelvic floor musculature (Pubococcygeus).",
        "where": "Internal core floor structures.",
        "action": "Device OFF. Inhale deeply, contract pelvic floor and lower abs inward/upward; HOLD breath and tension (4s); Exhale, RELEASE completely and heavily (6s). Repeat rhythmically.",
        "goal": "Trains neuromuscular response and acts as a dynamic vascular pump—squeezing old fluid out and flooding tissues with fresh, warm arterial blood.",
        "benefit_text": "💡 Trains reflex arcs, boosts local blood engorgement, and spikes local sensory responsiveness.",
        "switch_sides": False,
    },
    {
        "step": "Step 5: Pubic Arch Resonance & Stationary Vibration Hold",
        "duration": 120,
        "image_file": "step5_pubic_corrected.png", # NEW CORRECTED IMAGE (Stationary, Against Arch)
        "positioning": "Stable hook-lying position with a sustained posterior pelvic tilt (lower back flat against floor).",
        "distance": "Soft tissue immediately overlying the bony pubic arch (symphysis).",
        "where": "Lower center base where soft tissue meets the pubic frame.",
        "action": "Place soft head or air-cushion attachment directly against the upper pubic bone frame. Low-to-medium speed; COMPLETELY STATIONARY hold (no movement) (30s blocks). Breathe slowly.",
        "goal": "Uses skeletal resonance to transmit mechanical energy deep into the sacral plexus and suspensory ligaments, causing intense localized warming and engorgement.",
        "benefit_text": "💡 Uses skeletal resonance to target deep nerve endings, driving intense localized warmth and blood pooling.",
        "switch_sides": False,
    },
    {
        "step": "Step 6: The Plateau Reset (Sensory Integration Pause)",
        "duration": 45,
        "image_file": "step6_reset.png", # No-device, passive pose image used
        "positioning": "Open knees into fully relaxed butterfly position (soles of feet together).",
        "distance": "Entire pelvic core basin.",
        "where": "Passive reclined posture.",
        "action": "HANDS-OFF: Turn device off and remove all mechanical contact. Lie in total stillness, focusing on internal warmth and throbbing.",
        "goal": "Mandatory stillness phase to prevent sensory adaptation fatigue, allowing the nervous system to process the intense buildup.",
        "benefit_text": "💡 Prevents sensory fatigue, letting neural receptors process the buildup to maximize impact.",
        "switch_sides": False,
    },
    {
        "step": "Step 7: Inward Crescent V-Sweep (The Engorgement Seal)",
        "duration": 60,
        "image_file": "step7_inward_corrected.png", # NEW CORRECTED IMAGE (Butterfly, INWARD arc)
        "positioning": "Maintained relaxed butterfly leg positioning.",
        "distance": "From outer hip creases inward and downward along the inguinal ligament.",
        "where": "Lower center base sweeping outward towards the hip bones.",
        "action": "Execute slow downward toward center base, pause 5s with final pelvic relaxation, then light outward curve over hip bone, then sweep inward and downward towards pubic arch in a crescent path.",
        "goal": "Traps and seals the warm blood within the deep pelvic core, leaving the region fully engorged, highly sensitive, and fully revitalized.",
        "benefit_text": "💡 Seals the circulation increase and locks in deep tissue warmth and responsiveness.",
        "switch_sides": False,
    },
]

MASSAGE_GUN_INFO_HTML = """
<div class="metric-container">
<h3 style="color:#ff9800; margin-top:0;">Massage Gun Speeds and Techniques Guide</h3>
<p><b>1. Speed Settings and Operational Mechanics</b><br>
• <b>Low Speed (1,200 – 1,800 RPM):</b> Best for sensitive zones, delicate abdominal/pelvic fascia, and manual drainage priming.<br>
• <b>Medium Speed (1,900 – 2,400 RPM):</b> Perfect for medium muscle groups, forearm extensor work, calves, and relaxing general tension.<br>
• <b>High Speed (2,500 – 3,200+ RPM):</b> Designed for dense muscular structures like glutes, quads, and deep TFL release.</p>
<p><b>2. Recommended Attachment Heads</b><br>
• <b>Soft Air-Cushion Head:</b> Essential for abdominal and pelvic protocols.<br>
• <b>Large/Small Round Ball:</b> General full-body attachment for large muscle groups.<br>
• <b>Flat Head:</b> Great for broad, dense muscle zones.<br>
• <b>Bullet / Cone Head:</b> Highly targeted pinpoint pressure for deep trigger points.</p>
<p><b>3. Application Techniques</b><br>
• <b>Featherlight Touch:</b> Let the weight of the device work across the surface.<br>
• <b>Slow Sweeps:</b> Glide at approximately 2 cm per second along muscular pathways.<br>
• <b>Stationary Holds:</b> For dense muscular trigger points, hold continuously for 30 to 90 seconds while practicing deep belly breathing.</p>
</div>
"""

# Single source of truth: every protocol's metadata + description + steps
# live together, keyed by name, instead of being scattered across four
# separate parallel structures that had to be kept in sync by hand.
PROTOCOLS = {
    "Kinetic Synergy: The Core, Hip & Pelvic Release Protocol": {
        "enabled": True,
        "badge": "Active (Synergy)",
        "preview_img": "step1A_synergy.png",  # Fallback image used
        "description_html": """
<div class="metric-container">
<b>🎯 Why it must be done:</b><br>
This routine integrates lower abdominal shaping, hip flexor release, and deep pelvic vasocongestion (blood pooling). It is specifically engineered to target increased tissue engorgement, pudendal nerve pathway responsiveness, and peak physiological conditioning through structured breath-tension cycles and targeted vibration.<br><br>
<b>⏱️ How often:</b><br>
2 to 3 times per week. Use a quiet, relaxed environment to fully process the sensory feedback.<br><br>
<b>✨ Key Benefits:</b><br>
• <b>Unlock Deep core mobility:</b> Breaks up localized fascial rigidity in the lower stomach.<br>
• <b>Maximize localized circulation:</b> Uses rhythmic muscle pumping to boost deep arterial inflow.<br>
• <b>Targeted Nerve Activation:</b> Stimulates deep nerve ending resonance near the pubic frame.
</div>
""",
        "steps": synergy_steps,
    },
    "Advanced Lower Pelvic & Abdominal Flush Protocol": {
        "enabled": True,
        "badge": "Active",
        "preview_img": "step1A.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Why it must be done:</b><br>
Decompresses deep pelvic and fascial tension to reset proper core-to-extremity performance patterns and restore unrestricted circulatory flow to the pelvic base.<br><br>
<b>⏱️ How often:</b><br>
2 to 3 times per week, keeping total execution time between 5 and 7 minutes per session. Best performed after exercise or a warm shower to optimize circulation and tissue elasticity.
</div>
""",
        "steps": lymph_steps,
    },
    "Advanced Lower Pelvic & Abdominal Flush Protocol (No Massage Gun)": {
        "enabled": True,
        "badge": "Active (Manual)",
        "preview_img": "",
        "description_html": """
<div class="metric-container">
<b>🎯 Why it must be done:</b><br>
A safe, manual alternative using targeted compression and effleurage techniques to reset pelvic tissue integrity and encourage deep circulatory drainage.<br><br>
<b>⏱️ Frequency & Best Time:</b><br>
2 to 3 times per week, 5 to 7 minutes total. Best done after a warm shower or light exercise when circulation is naturally elevated. Use a small amount of massage oil or lotion to reduce friction.
</div>
""",
        "steps": manual_lymph_steps,
    },
    "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)": {
        "enabled": True,
        "badge": "Active",
        "preview_img": "hip_master_guide.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
 ballistic movements trigger defensive guarding. This protocol targets rapid decompression of the deep hip rotators and adductor chain to unleash unrestricted rotational velocity.<br><br>
<b>✨ Key Benefits:</b><br>
• <b>Free Vertical Chambering:</b> Disrupts neural guarding at the anterior/adductor interface.<
• <b>Max Peak Rotational Power:</b> Unlocks deep external rotators for explosive turning and spinning kicks.<
• <b>Active Integration:</b> concludes with dynamic mobility to convert passive tissue gains into active performance.
</div>
""",
        "steps": hip_steps,
    },
    "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)": {
        "enabled": False,
        "badge": "Locked",
        "preview_img": "step5.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
overhead snaps and racquet impacts overload the lateral epicondyle and posterior capsule. Relieves elbow tension while restoring posterior shoulder rotational mobility.
</div>
""",
        "steps": forearm_steps,
    },
    "Advanced Posterior Chain & Ankle Mobility Protocol (Ground-Force)": {
        "enabled": False,
        "badge": "Locked",
        "preview_img": "step5.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
 ankle dorsiflexion forces the knees and lower back to absorb excess rotational forces. Unlocking the soleus and peroneal complex restores proper ground-force transmission.
</div>
""",
        "steps": ankle_steps,
    },
    "Massage Gun General Information & Usage Tips": {
        "enabled": False,
        "badge": "Locked",
        "preview_img": "step1.jpg",
        "description_html": MASSAGE_GUN_INFO_HTML,
        "steps": [],
    },
}

PROTOCOL_FALLBACK_IMG = {
    "Kinetic Synergy: The Core, Hip & Pelvic Release Protocol": "step1A_synergy.png",
    "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)": "hip_master_guide.png",
    "Advanced Lower Pelvic & Abdominal Flush Protocol": "step1A.png",
    "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)": "step5.png",
    "Advanced Posterior Chain & Ankle Mobility Protocol (Ground-Force)": "step5.png",
}

# ==========================================
# 8. APPLICATION PAGES
# ==========================================

# --- PAGE 1: USER PROFILE ---
if st.session_state.app_page == PAGE_PROFILE:
    scroll_to_top()
    render_header("KineticPulse", "Configure your guided routine")

    st.markdown(
        """
<div class="protocol-card">
    <h3 style="margin-top:0; color:#1a1a1a;">Welcome</h3>
    <p style="color: #4a5568;">Enter your profile details to configure your specialized kinetic wellness session.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    entered_name = st.text_input("Practitioner Name:", value=st.session_state.user_name, max_chars=80)
    entered_notes = st.text_area(
        "Current Session Focus / Tension Areas:", value=st.session_state.session_notes, max_chars=500
    )

    render_support_box()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Configure Protocols", type="primary"):
        if entered_name.strip():
            # Sanitize before storing — this value later gets interpolated
            # into unsafe_allow_html markdown and into the CSV log.
            st.session_state.user_name = sanitize_text(entered_name.strip(), max_len=80)
            st.session_state.session_notes = sanitize_text(entered_notes.strip(), max_len=500)
            st.session_state.app_page = PAGE_SELECT
            scroll_to_top()
            st.rerun()
        else:
            st.error("Please fill in your name to proceed.")


# --- PAGE 2: PROTOCOL SELECTOR ---
elif st.session_state.app_page == PAGE_SELECT:
    scroll_to_top()
    render_header("Protocol Selector", f"Configure routine, {st.session_state.user_name}")

    st.markdown(
        "<h3 style='text-align: center; color: #333; margin-bottom: 20px;'>Select"
        " session focus:</h3>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="selection-box">', unsafe_allow_html=True)
    st.caption("Select an active performance protocol:")

    for p_name, p_info in PROTOCOLS.items():
        is_selected = st.session_state.selected_protocol == p_name
        if p_info["enabled"]:
            label = f"▶ {p_name} ({p_info['badge']})" if is_selected else f"⚡ {p_name}"
            if st.button(
                label,
                key=f"proto_btn_{p_name}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.selected_protocol = p_name
                scroll_to_top()
                st.rerun()
        else:
            st.button(
                f"🔒 {p_name} ({p_info['badge']})",
                key=f"proto_btn_{p_name}",
                disabled=True,
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    chosen_option = st.session_state.selected_protocol
    chosen_info = PROTOCOLS[chosen_option]
    selected_img_path = resolve_image_path(chosen_info["preview_img"])

    st.markdown('<div class="protocol-card">', unsafe_allow_html=True)
    if chosen_option == "Advanced Lower Pelvic & Abdominal Flush Protocol (No Massage Gun)":
        st.markdown(
            "<h4 style='color:#0c38ff; margin-top:0;'>🌟 Specialized Manual Protocol</h4>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**Selected Selection:**\n\n{chosen_option}")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            if chosen_option != "Massage Gun General Information & Usage Tips" and selected_img_path:
                st.image(selected_img_path, width=110)
            else:
                st.markdown("📘 **[Guide]**")
        with col2:
            st.markdown(f"**Selected Selection:**\n\n{chosen_option}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(chosen_info["description_html"], unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("Profile Back", type="secondary"):
            st.session_state.app_page = PAGE_PROFILE
            scroll_to_top()
            st.rerun()
    with col_next:
        is_info_only = chosen_option == "Massage Gun General Information & Usage Tips"
        button_label = "Info Complete" if is_info_only else "Begin Session"
        if st.button(button_label, type="primary"):
            st.session_state.selected_protocol = chosen_option
            st.session_state.current_step_index = 0
            st.session_state.app_page = PAGE_SELECT if is_info_only else PAGE_SESSION
            scroll_to_top()
            st.rerun()


# --- PAGE 3: INTERACTIVE GUIDED TIMER & ROUTINE ---
elif st.session_state.app_page == PAGE_SESSION:
    scroll_to_top()

    protocol_steps = PROTOCOLS[st.session_state.selected_protocol]["steps"]

    render_header("Interactive Guide")

    if st.button("Configure Protocol Back", type="secondary"):
        st.session_state.app_page = PAGE_SELECT
        scroll_to_top()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    current_idx = st.session_state.current_step_index

    if current_idx < len(protocol_steps):
        step_info = protocol_steps[current_idx]

        st.markdown(
            f"<h3 style='text-align: center; color: #333;'>{html.escape(step_info['step'])}</h3>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="pressure-warning">⚠️ TECHNIQUE: Maintain strict postural symmetry, calmbell breathing, and avoid excessive mechanical pressure.</div>',
            unsafe_allow_html=True,
        )

        if "pelvic" in step_info["step"].lower() or "lymphatic" in step_info["step"].lower():
            st.markdown(
                """
            <div class="contract-box" style="text-align: left; padding: 14px 18px; margin-bottom: 15px;">
                💡 <b>Performing Pelvic Floor Contract & Release:</b><br>
                • <b>Contract (Squeeze):</b> engage your pelvic floor muscles as if stopping flow or drawing lower belly inward and upward. Hold firmly for 4 seconds.<br>
                • <b>Release (Relax):</b> let go and relax the muscles completely for 6 seconds to optimize fluid drainage and neural reset.
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Non-device steps and specific manual protocols use other fallbacks
        is_pumping_step = step_info.get("image_file", "") == "step4_pumping.png"
        is_synergy_first = step_info.get("image_file", "") == "step1_priming.png"
        
        img_path = resolve_image_path(step_info.get("image_file", ""))
        
        # Determine fallback if not found
        if not img_path:
            if not is_pumping_step and st.session_state.selected_protocol != (
                "Advanced Lower Pelvic & Abdominal Flush Protocol (No Massage Gun)"
            ):
                fallback_file = PROTOCOL_FALLBACK_IMG.get(
                    st.session_state.selected_protocol, "step1.jpg"
                )
                img_path = resolve_image_path(fallback_file)

        extra_img_path = resolve_image_path(step_info.get("extra_image_file", ""))

        if img_path:
            st.image(img_path, use_container_width=True, caption=f"Placement Guide: {step_info['step']}")
        if extra_img_path:
            st.image(extra_img_path, use_container_width=True, caption="Positioning Reference (Extra Guide)")
        elif (
            not img_path
            and not extra_img_path
            and is_pumping_step
        ):
             st.info(
                "ℹ️ Active Muscular Pumping: Device OFF. Use hands gently on lower belly as a breath reminder."
            )
        elif (
            not img_path
            and not extra_img_path
            and st.session_state.selected_protocol
            == "Advanced Lower Pelvic & Abdominal Flush Protocol (No Massage Gun)"
        ):
            st.info(
                "ℹ️ Manual Protocol: Uses hands, palms, and body positioning as instructed (no hardware required)."
            )

        pos_info = f"<b>🧘 Positioning:</b> {step_info['positioning']}<br>" if "positioning" in step_info else ""
        st.markdown(
            f"""<div class="metric-container">
{pos_info}<b>📍 Targeted Chain:</b> {step_info['distance']}<br>
<b>🗺️ Location:</b> {step_info['where']}<br>
<b>⚡ Action:</b> {step_info['action']}<br>
<b>🎯 Performance Goal:</b> {step_info['goal']}
</div>""",
            unsafe_allow_html=True,
        )

        total_duration_secs = step_info["duration"]
        st.markdown(f"**Step Duration:** {total_duration_secs} seconds")

        # --- Non-blocking timer -------------------------------------------------
        if not st.session_state.timer_running:
            if st.button("Start Step Timer", type="primary"):
                st.session_state.timer_running = True
                st.session_state.timer_start = time.time()
                st.rerun()
        else:
            if st.button("Pause / Reset Timer", type="secondary"):
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                st.rerun()

            @st.fragment(run_every=1)
            def render_timer(step_info=step_info, total_time=total_duration_secs):
                if not st.session_state.timer_running or st.session_state.timer_start is None:
                    return

                elapsed = int(time.time() - st.session_state.timer_start)
                remaining = max(total_time - elapsed, 0)
                needs_switching = step_info.get("switch_sides", False)
                half_time = total_time // 2
                
                # Check for "Low-Pelvic" or "Synergy Step 5" or "Synergy Step 3"
                is_manual_squeezer = "Low-Pelvic Glide" in step_info["step"]
                is_pumping_active = "The Vascular Sponge" in step_info["step"] or is_manual_squeezer
                
                mins, secs = divmod(remaining, 60)

                if needs_switching:
                    if elapsed < half_time:
                        st.markdown(
                            '<div class="side-visual-left"><h1 style="font-size:3.5rem; margin:0;">🧍\u200d♂️ ⬅️</h1>'
                            '<h3 style="color:#0d47a1; margin:0; font-weight: bold;">WORKING: LEFT CHAIN</h3></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="side-visual-right"><h1 style="font-size:3.5rem; margin:0;">➡️ 🧍\u200d♂️</h1>'
                            '<h3 style="color:#1b5e20; font-weight: bold;">WORKING: RIGHT CHAIN</h3></div>',
                            unsafe_allow_html=True,
                        )
                        if elapsed == half_time:
                            st.toast("🔄 Switch sides to opposite limb.", icon="👉")
                else:
                    st.markdown(
                        '<div class="side-visual-center"><h1 style="font-size:3.5rem; margin:0;">🧍\u200d♂️🏆 **Step Complete!🏆** Prepare for the next phase.</h3>",
                        unsafe_allow_html=True,
                    )
                    st.balloons()

            render_timer()

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if current_idx > 0:
                if st.button("Previous Step", type="secondary"):
                    st.session_state.current_step_index -= 1
                    st.session_state.timer_running = False
                    st.session_state.timer_start = None
                    scroll_to_top()
                    st.rerun()
        with col2:
            next_label = "Next Step" if current_idx < len(protocol_steps) - 1 else "Complete Routine"
            if st.button(next_label, type="primary"):
                st.session_state.current_step_index += 1
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                scroll_to_top()
                st.rerun()
    else:
        st.markdown("---")
        st.success("🥇 **Performance Routine Completed!🏆** Great work on optimizing your chain.")
        render_support_box()

        log_session_to_csv(
            st.session_state.user_name,
            st.session_state.selected_protocol,
            10,
            st.session_state.session_notes,
        )

        if st.button("Begin New Session", type="primary"):
            st.session_state.app_page = PAGE_PROFILE
            st.session_state.current_step_index = 0
            scroll_to_top()
            st.rerun()


# --- PAGE 4: SECURE ADMIN LOGIN ---
elif st.session_state.app_page == PAGE_ADMIN_LOGIN:
    scroll_to_top()
    render_header("Admin Portal", "System Data Access")

    st.markdown(
        """
<div class="protocol-card">
    <p style="color:#1a1a1a;">enter the administrator credential to access practitioner logs.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if ADMIN_PASSWORD is None:
        st.error(
            "⚠️ Admin authentication is not configured. Configure `admin_password` inside"
            " `.streamlit/secrets.toml` locally or in the app's Community Cloud Secrets settings."
        )
    else:
        now = time.time()
        locked_out = now < st.session_state.admin_locked_until

        if locked_out:
            wait_secs = int(st.session_state.admin_locked_until - now)
            st.error(f"🔒 System locked due to access failures. Retry available in {wait_secs}s.")
        else:
            admin_password = st.text_input("Administrator Credential:", type="password")
            if st.button("Authenticate", type="primary"):
                if admin_password == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_attempts = 0
                    st.session_state.app_page = PAGE_ADMIN_VIEW
                    scroll_to_top()
                    st.rerun()
                else:
                    st.session_state.admin_attempts += 1
                    if st.session_state.admin_attempts >= ADMIN_MAX_ATTEMPTS:
                        st.session_state.admin_locked_until = now + ADMIN_LOCKOUT_SECONDS
                        st.session_state.admin_attempts = 0
                        st.error("🔒 Maximum authentication failures. System locked for 60 seconds.")
                    else:
                        remaining_tries = ADMIN_MAX_ATTEMPTS - st.session_state.admin_attempts
                        st.error(f"❌ Incorrect credential. {remaining_tries} authentication attempt(s) remaining.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Profile Back", type="secondary"):
        st.session_state.app_page = PAGE_PROFILE
        scroll_to_top()
        st.rerun()


# --- PAGE 5: ADMIN DATA VIEWER ---
elif st.session_state.app_page == PAGE_ADMIN_VIEW:
    scroll_to_top()
    if not st.session_state.admin_authenticated:
        st.warning("🔒 This portal requires authentication.")
        st.session_state.app_page = PAGE_ADMIN_LOGIN
        scroll_to_top()
        st.rerun()
    else:
        render_header("Practitioner Logs", "Session Activity Data")

        if not os.path.exists(LOG_FILE_PATH):
            st.warning(
                f"⚠️ The log file `{LOG_FILE_PATH}` does not exist yet. No sessions"
                " have been recorded by the system."
            )
        else:
            df = pd.read_csv(LOG_FILE_PATH)
            if df.empty:
                st.info("ℹ️ The log file is empty. No sessions have been completed yet.")
            else:
                df = df.sort_values(by="Timestamp", ascending=False)
                st.dataframe(df, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout / Profile Back", type="secondary"):
            st.session_state.admin_authenticated = False
            st.session_state.app_page = PAGE_PROFILE
            scroll_to_top()
            st.rerun()
