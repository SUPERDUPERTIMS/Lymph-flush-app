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

PAGE_PROFILE = 1
PAGE_SELECT = 2
PAGE_SESSION = 3
PAGE_ADMIN_LOGIN = 4
PAGE_ADMIN_VIEW = 5

PAYMENT_URL = "https://ko-fi.com/kineticpulseapp"
LOG_FILE_PATH = "kinetic_session_logs.csv"

# ==========================================
# 2. SECRETS & SECURITY HELPERS
# ==========================================
ADMIN_PASSWORD = st.secrets.get("admin_password")
ADMIN_MAX_ATTEMPTS = 5
ADMIN_LOCKOUT_SECONDS = 60


def sanitize_text(value: str, max_len: int = 200) -> str:
    """Escape HTML and cap length before text is processed or saved."""
    if value is None:
        return ""
    value = str(value)[:max_len]
    return html.escape(value, quote=True)


def csv_safe(value: str) -> str:
    """Neutralize formula injection for CSV export."""
    value = str(value)
    if value and value[0] in ("=", "+", "-", "@"):
        return "'" + value
    return value


# ==========================================
# 3. SAFETY & MEDICAL NOTICE GATE
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
# 4. GLOBAL STYLING (CSS)
# ==========================================
st.markdown(
    """
<style>
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
# 5. UI COMPONENTS & LOGGING UTILITIES
# ==========================================
def scroll_to_top():
    """Forces page viewport back to the top on transition."""
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
                if (container) { container.scrollTop = 0; }
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
    subtitle_html = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"""<div class="curved-header"><h1>{html.escape(title)}</h1>{subtitle_html}</div>""",
        unsafe_allow_html=True,
    )


def render_support_box():
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
# 6. SESSION STATE INITIALIZATION
# ==========================================
DEFAULT_PROTOCOL = "Advanced Lower Pelvic & Abdominal Protocol"

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
# 7. ROUTINE & PROTOCOL DATA
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
        "goal": "Safely stimulates primary drainage routes using tactile control without mechanical percussion.",
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
        "goal": "Pre-releases lateral hip and thigh tension safely without percussion.",
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
        "goal": "Encourages mid-level fascial mobility and flattens upper-to-lower stomach contour.",
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
        "goal": "Rhythmically mobilizes lower core tissue against a stable skeletal barrier using body weight and hand pressure.",
        "benefit_text": "💡 Lower core tissue is mobilized against a safe skeletal barrier.",
        "switch_sides": False,
    },
    {
        "step": "Step 5: Outer Hip V-Sweep",
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
        "goal": "Flushes all mobilized fluid out toward major peripheral drainage routes.",
        "benefit_text": "💡 Interstitial fluid is safely directed toward lateral pathways.",
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
            " fluid movement. Follow with featherlight, outward manual sweeps"
            " along the inner groin crease for 30 seconds."
        ),
        "goal": "Opens primary lymphatic hubs, reduces fluid accumulation in the lower pelvis, and increases inner thigh flexibility.",
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
        "goal": "Releases outer hip tightness, reduces lateral pelvic pulling, and improves hip rotation.",
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
        "goal": "Clears mid-level fascial tightness, breaks up localized water retention, and flattens the upper-to-lower stomach contour.",
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
        "goal": "Targets dense pelvic fascia against a stable skeletal barrier, strengthens deep core activation for a flatter belly profile, and accelerates tissue drainage.",
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
        "goal": "Directs all mobilized fluid out toward major peripheral drainage routes, leaving the lower abdomen feeling uncompressed, light, and visibly toned.",
        "benefit_text": "💡 Directs all mobilized fluid toward peripheral routes, leaving lower abdomen light, uncompressed, and visibly toned.",
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
        "goal": "Unloads TFL tension to clear lateral restrictions before high-velocity kicks.",
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
        "goal": "Restores lateral pelvic stability and hip abduction range.",
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
        "goal": "Releases deep rotators to unlock fluid end-range rotation for turning and spinning kicks.",
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
        "goal": "Disarms neural brakes on the anterior chain to prevent hip locking during extension.",
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
        "goal": "Relieves deep psoas hypertonicity without excessive pressure on vascular structures.",
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
        "goal": "Integrates tissue release into active end-range hip extension to lock in kick chambering gains.",
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
        "goal": "Relieve tension in the Tennis/Padel Elbow Zone.",
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
        "goal": "Release the Golfer Elbow Zone.",
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
        "goal": "Improve posterior shoulder mobility.",
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
        "goal": "Provide anterior shoulder release.",
        "benefit_text": "💡 Fast sweeps relieve anterior pulling.",
        "switch_sides": True,
    },
]

ankle_steps = [
    {
        "step": "Step 1: Soleus & Gastrocnemius Cleanse",
        "duration": 240,
        "image_file": "step5.png",
        "distance": "Calves & Lower Leg",
        "where": "Soleus & Gastrocnemius",
        "action": "High Speed. Sweeping glides. (120s per side)",
        "goal": "Calf & Achilles Decompression.",
        "benefit_text": "💡 Sweeping glides restore movement across the posterior chain.",
        "switch_sides": True,
    },
    {
        "step": "Step 2: Peroneal & Anterior Tibialis Balance",
        "duration": 180,
        "image_file": "step5.png",
        "distance": "Outer and Front Lower Leg",
        "where": "Peroneal & Anterior Tibialis",
        "action": "Med-High Speed. Longitudinal sweeps. (90s per side)",
        "goal": "Target the Lateral Stability Zone.",
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
        "goal": "Provide Medial Support.",
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
        "goal": "Ground Force Integration.",
        "benefit_text": "💡 Rolling and stretching completes ground force integration.",
        "switch_sides": True,
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

PROTOCOLS = {
    "Advanced Lower Pelvic & Abdominal Protocol": {
        "enabled": True,
        "badge": "Active",
        "preview_img": "step1A.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Why it should be done:</b><br>
Optimizes posture, leg positioning, and core engagement during this routine to maximize fluid clearance, release deep fascial tension, and help flatten the lower abdominal wall.<br><br>
<b>⏱️ How often:</b><br>
2 to 3 times per week, keeping total execution time between 5 and 7 minutes per session. Best performed after exercise or a warm shower to optimize circulation and tissue elasticity.
</div>
""",
        "steps": lymph_steps,
    },
    "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)": {
        "enabled": True,
        "badge": "Active",
        "preview_img": "hip_master_guide.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
High-velocity, ballistic movements trigger defensive muscle guarding. This 6-step protocol disarms neural "brakes" and prevents the hip flexors and rotators from locking up under mechanical strain.<br><br>
<b>✨ Key Benefits:</b><br>
• <b>Free Vertical Chambering:</b> Removes neurological restrictions at the adductor/pubic interface.<br>
• <b>Full Rotational Mobility:</b> Releases deep hip rotators to unlock fluid end-range rotation.<br>
• <b>Active Integration:</b> Concludes with dynamic low lunges to lock in athletic mobility gains.
</div>
""",
        "steps": hip_steps,
    },
    "Advanced Lower Pelvic & Abdominal Protocol (No Massage Gun)": {
        "enabled": False,
        "badge": "Locked",
        "preview_img": "",
        "description_html": """
<div class="metric-container">
<b>🎯 Why it should be done:</b><br>
A safe, 100% manual alternative that eliminates percussion risks entirely. Uses gentle manual effleurage (sweeping strokes), flat-palm pressure, and self-myofascial release to protect soft tissues while safely encouraging fluid mobilization.<br><br>
<b>⏱️ Frequency & Best Time:</b><br>
2 to 3 times per week, 5 to 7 minutes total. Best done after a warm shower or light exercise when circulation is naturally elevated. Use a small amount of massage oil or lotion to reduce friction.
</div>
""",
        "steps": manual_lymph_steps,
    },
    "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)": {
        "enabled": False,
        "badge": "Locked",
        "preview_img": "step5.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
Repetitive overhead snaps and racquet impacts overload the lateral epicondyle and posterior shoulder capsule. Relieves muscle tension at the elbow to eliminate strain while restoring posterior shoulder mobility.
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
Restricted ankle dorsiflexion forces the knees and lower back to absorb excess rotational and impact shear forces during directional changes. Unlocking the soleus and peroneal complex restores proper ground-force transmission.
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
    "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)": "hip_master_guide.png",
    "Advanced Lower Pelvic & Abdominal Protocol": "step1A.png",
    "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)": "step5.png",
    "Advanced Posterior Chain & Ankle Mobility Protocol (Ground-Force)": "step5.png",
}

# ==========================================
# 8. VIEW & ROUTING ENGINE
# ==========================================

# --- PAGE 1: USER PROFILE ---
if st.session_state.app_page == PAGE_PROFILE:
    scroll_to_top()
    render_header("KineticPulse", "Start your session")

    st.markdown(
        """
<div class="protocol-card">
    <h3 style="margin-top:0; color:#1a1a1a;">Welcome</h3>
    <p style="color: #4a5568;">Please enter your profile details to configure your guided routine.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    entered_name = st.text_input("Your Name:", value=st.session_state.user_name, max_chars=80)
    entered_notes = st.text_area(
        "Session Notes / Focus Areas:", value=st.session_state.session_notes, max_chars=500
    )

    render_support_box()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Continue to Protocols", type="primary"):
        if entered_name.strip():
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
    render_header("Choose Focus / Info", f"Welcome back, {st.session_state.user_name}")

    st.markdown(
        "<h3 style='text-align: center; color: #333; margin-bottom: 20px;'>Select"
        " training focus:</h3>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="selection-box">', unsafe_allow_html=True)
    st.caption("Tap an active protocol to select:")

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
        if st.button("Back", type="secondary"):
            st.session_state.app_page = PAGE_PROFILE
            scroll_to_top()
            st.rerun()
    with col_next:
        is_info_only = chosen_option == "Massage Gun General Information & Usage Tips"
        button_label = "Review Complete" if is_info_only else "Continue to Protocol"
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

    render_header("Routine Session")

    if st.button("Change Protocol / View Info", type="secondary"):
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
            '<div class="pressure-warning">⚠️ TECHNIQUE: Maintain steady contact,'
            " strict pelvic positioning, and calm breathing.</div>",
            unsafe_allow_html=True,
        )

        if "pelvic" in step_info["step"].lower() or "lymphatic" in step_info["step"].lower():
            st.markdown(
                """
            <div class="contract-box" style="text-align: left; padding: 14px 18px; margin-bottom: 15px;">
                💡 <b>How to perform Pelvic Floor Contract & Release:</b><br>
                • <b>Contract (Squeeze):</b> Engage your pelvic floor muscles as if trying to stop the flow of urine or drawing your lower belly inward and upward. Hold firmly for 4 seconds.<br>
                • <b>Release (Relax):</b> Fully let go and relax the muscles completely for 6 seconds, allowing interstitial fluids to move naturally.
            </div>
            """,
                unsafe_allow_html=True,
            )

        img_path = resolve_image_path(step_info.get("image_file", ""))
        if not img_path:
            fallback_file = PROTOCOL_FALLBACK_IMG.get(
                st.session_state.selected_protocol, "step1.jpg"
            )
            img_path = resolve_image_path(fallback_file)

        extra_img_path = resolve_image_path(step_info.get("extra_image_file", ""))

        if img_path:
            st.image(img_path, use_container_width=True, caption=f"Guide: {step_info['step']}")
        if extra_img_path:
            st.image(extra_img_path, use_container_width=True, caption="Positioning Reference (Extra Guide)")

        pos_info = f"<b>🧘 Positioning:</b> {step_info['positioning']}<br>" if "positioning" in step_info else ""
        st.markdown(
            f"""<div class="metric-container">
{pos_info}<b>📍 Target Zone:</b> {step_info['distance']}<br>
<b>🗺️ Location:</b> {step_info['where']}<br>
<b>⚡ Action:</b> {step_info['action']}<br>
<b>🎯 Goal:</b> {step_info['goal']}
</div>""",
            unsafe_allow_html=True,
        )

        total_duration_secs = step_info["duration"]
        st.markdown(f"**Target Duration:** {total_duration_secs} seconds")

        if not st.session_state.timer_running:
            if st.button("Start Step Timer", type="primary"):
                st.session_state.timer_running = True
                st.session_state.timer_start = time.time()
                st.rerun()
        else:
            if st.button("Stop / Reset Timer", type="secondary"):
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                st.rerun()

            @st.fragment(run_every=1)
            def render_timer(step_info=step_info, total_time=total_duration_secs):
                if not st.session_state.get("timer_running", False) or st.session_state.get("timer_start") is None:
                    return

                elapsed = int(time.time() - st.session_state.timer_start)
                remaining = max(total_time - elapsed, 0)
                needs_switching = step_info.get("switch_sides", False)
                half_time = total_time // 2

                # Strictly target Low-Pelvic step for 24s loop
                is_low_pelvic_step = "Low-Pelvic" in step_info.get("step", "")

                mins, secs = divmod(remaining, 60)

                # Lateral / Side Indicator Setup
                if needs_switching:
                    if elapsed < half_time:
                        st.markdown(
                            '<div class="side-visual-left"><h1 style="font-size:3.5rem; margin:0;">🧍‍♂️ ⬅️</h1>'
                            '<h3 style="color:#0d47a1; margin:0; font-weight: bold;">WORKING: LEFT SIDE</h3></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="side-visual-right"><h1 style="font-size:3.5rem; margin:0;">➡️ 🧍‍♂️</h1>'
                            '<h3 style="color:#1b5e20; font-weight: bold;">WORKING: RIGHT SIDE</h3></div>',
                            unsafe_allow_html=True,
                        )
                        if elapsed == half_time:
                            st.toast("🔄 Switch sides! Move to opposite limb.", icon="👉")
                else:
                    st.markdown(
                        '<div class="side-visual-center"><h1 style="font-size:3.5rem; margin:0;">🧍‍♂️</h1>'
                        '<h3 style="color:#e65100; font-weight: bold;">WORKING: CENTER ZONE / BILATERAL</h3></div>',
                        unsafe_allow_html=True,
                    )

                # Main Countdown Timer & Progress
                st.markdown(
                    f"<h3 style='text-align: center;'>⏱️ {mins:02d}:{secs:02d}</h3>",
                    unsafe_allow_html=True,
                )
                st.progress(1.0 - (remaining / total_time) if total_time else 1.0)

                # 24-Second Lower Abdominal / Low-Pelvic Protocol Timing Loop
                if is_low_pelvic_step:
                    cycle_time = elapsed % 24

                    if cycle_time < 10:
                        st.markdown(
                            '<div class="contract-box" style="background:#e8f5e9 !important; border-color:#4caf50; color:#1b5e20 !important;">'
                            '🖐️ Perform Downward Low-Pelvic Glide (10s)</div>',
                            unsafe_allow_html=True,
                        )
                    elif cycle_time < 14:
                        st.markdown(
                            '<div class="contract-box" style="background:#ffebee !important; border-color:#f44336; color:#b71c1c !important;">'
                            '⚡ Squeeze Pelvic Floor Inward & Upward (4s)</div>',
                            unsafe_allow_html=True,
                        )
                    elif cycle_time < 18:
                        st.markdown(
                            '<div class="contract-box" style="background:#e3f2fd !important; border-color:#2196f3; color:#0d47a1 !important;">'
                            '🛑 Hold Position (4s)</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="contract-box" style="background:#fff3e0 !important; border-color:#ff9800; color:#e65100 !important;">'
                            '💨 Slow Exhale & Fully Release Pelvic Floor (6s)</div>',
                            unsafe_allow_html=True,
                        )

                if "benefit_text" in step_info:
                    st.info(step_info["benefit_text"])

                # Completion Handler
                if remaining <= 0:
                    st.session_state.timer_running = False
                    st.session_state.timer_start = None
                    st.markdown(
                        "<h3 style='text-align: center; color: #0c38ff;'>✅ Step Complete!</h3>",
                        unsafe_allow_html=True,
                    )
                    st.balloons()

            render_timer()

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if current_idx > 0:
                if st.button("Back", type="secondary"):
                    st.session_state.current_step_index -= 1
                    st.session_state.timer_running = False
                    st.session_state.timer_start = None
                    scroll_to_top()
                    st.rerun()
        with col2:
            next_label = "Next" if current_idx < len(protocol_steps) - 1 else "Finish"
            if st.button(next_label, type="primary"):
                st.session_state.current_step_index += 1
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                scroll_to_top()
                st.rerun()
    else:
        st.markdown("---")
        st.success("🏆 **Protocol Completed Successfully!** Great work.")
        render_support_box()

        log_session_to_csv(
            st.session_state.user_name,
            st.session_state.selected_protocol,
            10,
            st.session_state.session_notes,
        )

        if st.button("Start New Session", type="primary"):
            st.session_state.app_page = PAGE_PROFILE
            st.session_state.current_step_index = 0
            scroll_to_top()
            st.rerun()


# --- PAGE 4: SECURE ADMIN LOGIN ---
elif st.session_state.app_page == PAGE_ADMIN_LOGIN:
    scroll_to_top()
    render_header("Admin Login", "Data Access")

    st.markdown(
        """
<div class="protocol-card">
    <p style="color:#1a1a1a;">Please enter the administrator password to view session logs.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if ADMIN_PASSWORD is None:
        st.error(
            "⚠️ Admin password is not configured. Add `admin_password` to"
            " `.streamlit/secrets.toml` (locally) or the app's Secrets"
            " settings (Streamlit Community Cloud)."
        )
    else:
        now = time.time()
        locked_out = now < st.session_state.admin_locked_until

        if locked_out:
            wait_secs = int(st.session_state.admin_locked_until - now)
            st.error(f"🔒 Too many failed attempts. Try again in {wait_secs}s.")
        else:
            admin_password = st.text_input("Password:", type="password")
            if st.button("Login", type="primary"):
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
                        st.error("🔒 Too many failed attempts. Locked out for 60 seconds.")
                    else:
                        remaining_tries = ADMIN_MAX_ATTEMPTS - st.session_state.admin_attempts
                        st.error(f"❌ Incorrect password. {remaining_tries} attempt(s) remaining.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to App", type="secondary"):
        st.session_state.app_page = PAGE_PROFILE
        scroll_to_top()
        st.rerun()


# --- PAGE 5: ADMIN DATA VIEWER ---
elif st.session_state.app_page == PAGE_ADMIN_VIEW:
    scroll_to_top()
    if not st.session_state.admin_authenticated:
        st.warning("🔒 You must be logged in to access this page.")
        st.session_state.app_page = PAGE_ADMIN_LOGIN
        scroll_to_top()
        st.rerun()
    else:
        render_header("Session Logs", "All User Activity Data")

        if not os.path.exists(LOG_FILE_PATH):
            st.warning(
                f"⚠️ The log file `{LOG_FILE_PATH}` does not exist yet. No sessions"
                " have been recorded."
            )
        else:
            df = pd.read_csv(LOG_FILE_PATH)
            if df.empty:
                st.info("ℹ️ The log file is empty. No sessions have been completed yet.")
            else:
                df = df.sort_values(by="Timestamp", ascending=False)
                st.dataframe(df, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout / Back to App", type="secondary"):
            st.session_state.admin_authenticated = False
            st.session_state.app_page = PAGE_PROFILE
            scroll_to_top()
            st.rerun()
