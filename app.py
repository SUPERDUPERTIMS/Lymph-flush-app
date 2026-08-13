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
    if not value:
        return ""
    return html.escape(str(value)[:max_len], quote=True)


def csv_safe(value: str) -> str:
    """Neutralize formula injection for CSV export."""
    val_str = str(value)
    if val_str and val_str[0] in ("=", "+", "-", "@"):
        return "'" + val_str
    return val_str


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

.st-key-floating_admin_btn {
    position: fixed !important;
    bottom: 2px !important;
    right: 2px !important;
    z-index: 999999 !important;
    width: auto !important;
    margin: 0 !important;
    padding: 0 !important;
}

.st-key-floating_admin_btn button {
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

.side-switch-flash {
    animation: flashAlert 0.8s ease-in-out;
}
@keyframes flashAlert {
    0% { opacity: 0.2; transform: scale(0.98); }
    50% { opacity: 1; transform: scale(1.02); }
    100% { opacity: 1; transform: scale(1); }
}
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 5. UI COMPONENTS, ANIMATION & AUDIO HELPERS
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


def play_switch_audio_cue(freq: float = 587.33, freq_end: float = 880.0):
    """Plays a Web Audio API synth sweep or soft chime across transitions."""
    components.html(
        f"""
        <script>
            try {{
                var AudioContext = window.AudioContext || window.webkitAudioContext;
                if (AudioContext) {{
                    var ctx = new AudioContext();
                    if (ctx.state === 'suspended') {{
                        ctx.resume();
                    }}
                    var osc = ctx.createOscillator();
                    var gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime({freq}, ctx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime({freq_end}, ctx.currentTime + 0.2);
                    gain.gain.setValueAtTime(0.12, ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.3);
                }}
            }} catch(e) {{}}
        </script>
        """,
        height=0,
        width=0,
    )


def render_animated_breathing_visualizer(cycle_seconds: int = 10, inhale_ratio: float = 0.4):
    """Renders a CSS pulsing breathing circle synced to a full inhale/exhale cycle."""
    inhale_duration = round(cycle_seconds * inhale_ratio, 1)
    exhale_duration = round(cycle_seconds * (1 - inhale_ratio), 1)

    components.html(
        f"""
        <style>
            .breath-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 180px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
            .breath-circle {{
                width: 70px;
                height: 70px;
                border-radius: 50%;
                background: radial-gradient(circle, #29abe0 0%, #0c38ff 100%);
                box-shadow: 0 0 20px rgba(12, 56, 255, 0.4);
                animation: breathe {cycle_seconds}s infinite ease-in-out;
            }}
            .breath-label {{
                margin-top: 15px;
                font-size: 0.95rem;
                font-weight: bold;
                color: #0c38ff;
                letter-spacing: 0.5px;
            }}
            @keyframes breathe {{
                0%, 100% {{
                    transform: scale(1.0);
                    opacity: 0.6;
                    box-shadow: 0 0 10px rgba(12, 56, 255, 0.2);
                }}
                {int(inhale_ratio * 100)}% {{
                    transform: scale(2.1);
                    opacity: 1.0;
                    box-shadow: 0 0 30px rgba(41, 171, 224, 0.7);
                }}
            }}
        </style>
        <div class="breath-container">
            <div class="breath-circle"></div>
            <div class="breath-label">Inhale ({inhale_duration}s) ➔ Exhale ({exhale_duration}s)</div>
        </div>
        """,
        height=190,
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


def log_session_to_csv(name: str, protocol_name: str, rating: int, notes: str):
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
    "side_switched_toast": False,
    "phase_chime_played": False,
    "session_logged": False,
}
for key, default_val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

# Floating Admin Access Button
if st.button("Admin", key="floating_admin_btn"):
    st.session_state.app_page = PAGE_ADMIN_LOGIN
    scroll_to_top()
    st.rerun()

# ==========================================
# 7. ROUTINE & PROTOCOL DATA
# ==========================================

somatic_breath_steps = [
    {
        "step": "Phase 1: Parasympathetic Priming & Gentle Squeezes",
        "duration": 210,
        "image_file": "",
        "positioning": "Lie on back in hook-lying pose (knees bent at 90°, feet flat on floor, lower back flat).",
        "distance": "Lower abdomen and pelvic diaphragm.",
        "where": "Deep pelvic floor & abdominal region.",
        "action": (
            "• <b>Breathing Cadence:</b> Inhale through nose for 4 seconds (belly rises); exhale slowly through mouth for 6 seconds (belly lowers).\n"
            "• <b>Gentle Squeeze Mechanics:</b> On each exhalation, gently draw the pelvic floor upward and inward (a 30% soft lift). Hold for 2 seconds.\n"
            "• <b>Complete Release:</b> On inhalation, release all engagement entirely for 8 seconds, letting the belly expand fully."
        ),
        "goal": "Triggers nervous system down-regulation, relaxes rigid core guarding, and establishes neuromuscular awareness.",
        "encouragement": "🔥 <b>You're doing great!</b> Focus on steady, effortless breathing. Notice how each exhalation washes away stored physical tension.",
        "benefit_text": "💡 Extended exhalations signal your central nervous system to shift into deep parasympathetic recovery.",
        "switch_sides": False,
    },
    {
        "step": "Phase 2: Somatic Engagement, Controlled Holds & Flutters",
        "duration": 300,
        "image_file": "",
        "positioning": "Hook-lying pose or knees gently rested together with feet wider than hip-width.",
        "distance": "Deep internal pelvic floor muscles.",
        "where": "Pelvic bowl & deep core structure.",
        "action": (
            "<b>Perform the following 15-second repeating sequence:</b>\n\n"
            "1. <b>Deep Hold (8 seconds):</b> Inhale deeply into lower belly, completely expanding and relaxing the pelvic floor for 8 full seconds.\n"
            "2. <b>Intentional Squeeze (2 seconds):</b> Exhale with a moderate (60%) upward pull/lift of the pelvic muscles. Hold firm for 2 seconds.\n"
            "3. <b>Rapid Flutters (5 seconds):</b> Immediately perform light, rapid, rhythmic micro-engagements (pulsing quickly on/off 4–5 times across 5 seconds)."
        ),
        "goal": "Sharpens mind-body connection, enhances tissue vascularity, and builds dynamic neuromuscular elasticity.",
        "encouragement": "⚡ <b>Keep up the momentum!</b> Rhythm and control are key. Feel the precise activation during every squeeze and flutter.",
        "benefit_text": "💡 Alternating between deep holds and quick flutters trains both postural and dynamic muscle fibers.",
        "switch_sides": False,
    },
    {
        "step": "Phase 3: Deep Autonomic Flow & Complete Tension Release",
        "duration": 300,
        "image_file": "",
        "positioning": "Supine position with legs fully extended or supported in butterfly pose.",
        "distance": "Whole-body autonomic system.",
        "where": "Pelvis, lower spine, and abdominal core.",
        "action": (
            "• <b>Effortless Flow:</b> Transition away from counting seconds. Inhale slowly and let your breath flow freely without pauses.\n"
            "• <b>Passive Synchronization:</b> Allow the pelvic floor to softly expand on inhale and gently settle on exhale naturally.\n"
            "• <b>Full Decompression:</b> Scan your lower body for residual tightness and release all effort into the floor."
        ),
        "goal": "Discharges residual stress, restores full natural circulation, and locks in deep physical clarity.",
        "encouragement": "🌟 <b>Outstanding job!</b> You've completed the active work. Let your body absorb the benefits and enjoy total decompression.",
        "benefit_text": "💡 Passive recovery allows the autonomic nervous system to consolidate new movement patterns and restore balance.",
        "switch_sides": False,
    },
]

female_somatic_steps = [
    {
        "step": "Phase 1: Diaphragmatic Unloading & Pelvic Basin Priming",
        "duration": 240,
        "image_file": "",
        "positioning": "Lie flat in butterfly pose (soles of feet together, knees open) or relaxed hook-lying posture.",
        "distance": "Lower pelvic bowl & sub-umbilical fascia.",
        "where": "Deep pelvic floor, perineal body, and pelvic diaphragm.",
        "action": (
            "• <b>Diaphragmatic Inhale (4s):</b> Inhale deeply into lower belly and pelvic basin. Feel the pelvic floor expand downward.\n"
            "• <b>Soft Exhale (6s):</b> Exhale slowly through slightly parted lips, letting the belly melt flat without forcing engagement.\n"
            "• <b>Tactile Anchor:</b> Place one hand on low belly and one on upper chest to ensure lower hand rises first."
        ),
        "goal": "Releases chronic abdominal bracing, optimizes thoracic diaphragm excursion, and warms tissue for vascular inflow.",
        "encouragement": "🌸 <b>Soften into the mat.</b> Let every exhalation drop stored tension in your jaw, neck, and hip flexors.",
        "benefit_text": "💡 Continuous 4s/6s diaphragmatic breathing down-regulates the central nervous system and prepares pelvic micro-vasculature.",
        "switch_sides": False,
    },
    {
        "step": "Phase 2: Neuromuscular Stacking & Variable Timing",
        "duration": 300,
        "image_file": "",
        "positioning": "Hook-lying position (knees bent, feet flat) with knees pressed together or squeezing a soft block for adductor co-activation.",
        "distance": "Deep pelvic bowl, adductor chain, and motor cortex pathways.",
        "where": "Urogenital triangle, adductor origins, and pelvic diaphragm.",
        "action": (
            "<b>Perform the repeating 16-second neuromuscular stacking sequence:</b><br><br>"
            "1. <b>3s Staircase Ramp:</b> On exhale, progressively increase pelvic contraction from 30% → 60% → 100% force over 3 full seconds to recruit high-threshold motor units.<br>"
            "2. <b>3s Peak Hold & Neural Anchor:</b> At 100% maximum tension, hold firm for 3 seconds while pressing the tip of your tongue to the roof of your mouth and casting eyes upward.<br>"
            "3. <b>5s Micro-Flutter Cascade:</b> Immediately perform 4 to 5 rapid micro-pulses in quick succession over 5 seconds.<br>"
            "4. <b>5s Complete Eccentric Release:</b> Deep inhale for 5 seconds, completely dropping all pelvic floor and adductor engagement."
        ),
        "goal": "Bypasses neural habituation, forces maximum arterial vasodilation, and optimizes dynamic tissue responsiveness.",
        "encouragement": "⚡ <b>Focus on the neural anchor!</b> Pressing the tongue and casting eyes upward disrupts mental spectatoring.",
        "benefit_text": "💡 Staircase Ramp + Neural Anchor + Flutter Cascade forces acute arterial inflow and prevents mechanical plateaus.",
        "switch_sides": False,
    },
    {
        "step": "Phase 3: Restorative Integration & Autonomic Reset",
        "duration": 240,
        "image_file": "",
        "positioning": "Supine with legs extended flat or resting over a bolster, arms relaxed by sides.",
        "distance": "Whole pelvic girdle, lower lumbar spine, and central nervous system.",
        "where": "Autonomic nervous system & lower abdominal core.",
        "action": (
            "• <b>Unpaced Autonomic Flow:</b> Discontinue all counting and active holds. Allow breath to move naturally through the nose.\n"
            "• <b>Somatic Scanning:</b> Direct awareness to the space below the navel, releasing any micro-tension in the hips or jaw.\n"
            "• <b>Full Decompression:</b> Rest quietly to allow hyper-oxygenated blood to fully bathe the pelvic tissues."
        ),
        "goal": "Consolidates parasympathetic adaptation, relieves deep muscle guarding, and locks in vascular integration.",
        "encouragement": "🌿 <b>Rest and absorb.</b> Let your body integrate the dynamic activation and settle into deep physical recovery.",
        "benefit_text": "💡 Passive integration stabilizes heart rate variability and reinforces long-term soft-tissue compliance.",
        "switch_sides": False,
    },
]

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
            "• <b>Squeeze-Hold Technique:</b> Exhale fully while gently squeezing and drawing the pelvic floor muscles upward (4 seconds hold).\n"
            "• <b>Full Release:</b> Inhale deeply and completely release all engagement (6 seconds full relaxation).\n"
            "• <b>Manual Sweep:</b> Use warm hands (device OFF) to apply featherlight outward sweeps along the inner groin crease for 30 seconds."
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
            "• <b>Device Placement:</b> Place soft attachment at low speed over outer hip/TFL.\n"
            "• <b>Squeeze-Hold-Release:</b> Perform 1 deliberate Squeeze-Hold (exhale, pull pelvic floor upward for 4s) followed by a 6s Complete Release.\n"
            "• <b>Percussion Glides:</b> Maintain featherlight device contact with slow glides for 30 seconds per side."
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
            "• <b>Device Angle:</b> Hold device at a 45-degree downward angle with featherlight contact.\n"
            "• <b>Breathing Sync:</b> Inhale to soften the belly; exhale as you perform slow downward glides across the 10 cm band below the navel for 45 seconds.\n"
            "• <b>Relaxation Control:</b> Keep the pelvic floor completely unengaged and open throughout this step."
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
            "• <b>Step A (Glide):</b> Execute a slow downward percussion glide to the pubic bone frame and pause the device stationary over the soft tissue just above the bone.\n"
            "• <b>Step B (Squeeze-Hold):</b> While holding stationary, exhale deeply and pull the pelvic floor upward and inward. Hold this active squeeze for 4 full seconds.\n"
            "• <b>Step C (Full Release):</b> Inhale slowly, letting the lower belly expand and fully relaxing the pelvic floor for 6 full seconds.\n"
            "• <b>Repeat Cycle:</b> Perform 2 full Squeeze-Hold-Release cycles per pause, then reposition slightly along the pubic frame across the 120 seconds."
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
            "• <b>Downward Glide:</b> Glide downward toward the lower center base and pause for 5–10 seconds.\n"
            "• <b>Squeeze-Release Sync:</b> Perform 1 Squeeze-Hold (4s) followed by a complete 6s Release, letting all lower abdominal tension drop.\n"
            "• <b>V-Sweep Finish:</b> Curve the device outward and upward over the iliac crest (hip bone) in a V-shaped path for 90 seconds to drain fluid outward."
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
        "positioning": "Side-lying or seated with hip relaxed at 45 degrees.",
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
        "positioning": "Prone or side-lying with target leg slightly bent.",
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
        "positioning": "Prone position with hips flat on mat.",
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
        "positioning": "Supine or half-kneeling position.",
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
        "positioning": "Supine hook-lying position (knees bent, feet flat).",
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
        "positioning": "Half-kneeling low-lunge position (rear knee grounded, front knee over ankle).",
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
        "step": "Step 1: Lateral Epicondyle & Wrist Extensor Release (Padel/Tennis Elbow)",
        "duration": 180,
        "image_file": "forearm_step1.png",
        "positioning": "Seated with forearm resting flat on table or thigh, palm facing down.",
        "distance": "Outer Forearm & Lateral Elbow",
        "where": "Extensor Carpi Radialis & Extensor Digitorum near lateral epicondyle.",
        "action": "Medium speed. Slow longitudinal glides from lateral elbow toward wrist for 90s per arm.",
        "goal": "Unloads extensor mass tension to relieve lateral epicondylitis and restore wrist extensor compliance.",
        "benefit_text": "💡 Decompressing wrist extensors reduces impact shock on lateral elbow tendon insertions.",
        "switch_sides": True,
    },
    {
        "step": "Step 2: Medial Epicondyle & Wrist Flexor Decompression (Golfer Elbow Zone)",
        "duration": 180,
        "image_file": "forearm_step2.png",
        "positioning": "Seated with forearm fully supported on thigh or table, palm facing upward.",
        "distance": "Inner Forearm & Medial Elbow",
        "where": "Flexor Carpi Radialis, Pronator Teres & Flexor Digitorum Superficialis.",
        "action": "Medium speed. Focused longitudinal glides and gentle stationary holds over dense belly for 90s per arm.",
        "goal": "Relieves high tension from repetitive racquet/paddle gripping and overhead pronation snaps.",
        "benefit_text": "💡 Targeted flexor release restores grip elasticity and reduces strain at the medial epicondyle.",
        "switch_sides": True,
    },
    {
        "step": "Step 3: Posterior Shoulder Capsule & Infraspinatus Decompression",
        "duration": 240,
        "image_file": "forearm_step3.png",
        "positioning": "Seated or standing, crossing target arm gently across chest to stretch posterior capsule.",
        "distance": "Posterior Shoulder & Scapular Infra-spinous Fossa",
        "where": "Infraspinatus, Teres Minor, and Posterior Deltoid belly.",
        "action": "Medium-High speed. Slow circular sweeps over posterior shoulder blade pocket for 120s per shoulder.",
        "goal": "Restores internal rotation and deceleration clearance necessary for overhead racquet swings.",
        "benefit_text": "💡 Releasing posterior capsule tightness prevents anterior shoulder impingement during follow-through.",
        "switch_sides": True,
    },
    {
        "step": "Step 4: Anterior Shoulder & Pectoralis Minor Kinetic Sweep",
        "duration": 240,
        "image_file": "forearm_step4.png",
        "positioning": "Standing tall with chest open, target shoulder externally rotated.",
        "distance": "Anterior Shoulder & Sub-Clavicular Chest Region",
        "where": "Pectoralis Minor, Biceps Long-Head Tendon groove, and Anterior Deltoid.",
        "action": "Low-Medium speed with soft attachment. Featherlight sweeps along chest-to-shoulder transition for 120s per side.",
        "goal": "Disarms forward shoulder rounding and anterior kinetic strain from overhead serving and smashing.",
        "benefit_text": "💡 Opening anterior chest tissue improves overhead reach and shoulder kinetic chain efficiency.",
        "switch_sides": True,
    },
]

ankle_steps = [
    {
        "step": "Step 1: Soleus & Gastrocnemius Cleanse",
        "duration": 240,
        "image_file": "step5.png",
        "positioning": "Seated on floor or chair with knee bent at 90 degrees.",
        "distance": "Calves & Lower Leg",
        "where": "Soleus & Gastrocnemius",
        "action": "High Speed. Sweeping glides for 120s per side.",
        "goal": "Calf & Achilles Decompression.",
        "benefit_text": "💡 Sweeping glides restore movement across the posterior chain.",
        "switch_sides": True,
    },
    {
        "step": "Step 2: Peroneal & Anterior Tibialis Balance",
        "duration": 180,
        "image_file": "step5.png",
        "positioning": "Seated cross-legged or with lower leg supported.",
        "distance": "Outer and Front Lower Leg",
        "where": "Peroneal & Anterior Tibialis",
        "action": "Med-High Speed. Longitudinal sweeps for 90s per side.",
        "goal": "Target the Lateral Stability Zone.",
        "benefit_text": "💡 Longitudinal sweeps restore lower leg balance.",
        "switch_sides": True,
    },
    {
        "step": "Step 3: Tibialis Posterior & Deep Ankle Pocket",
        "duration": 180,
        "image_file": "step5.png",
        "positioning": "Seated with ankle resting over opposite knee.",
        "distance": "Inner Ankle/Lower Leg",
        "where": "Tibialis Posterior & Deep Ankle Pocket",
        "action": "Med Speed. Targeted pulses for 90s per side.",
        "goal": "Provide Medial Support.",
        "benefit_text": "💡 Targeted pulses release deep ankle pockets.",
        "switch_sides": True,
    },
    {
        "step": "Step 4: Plantar Fascia & Dynamic Calf Stretch",
        "duration": 120,
        "image_file": "step5.png",
        "positioning": "Seated or standing against wall for stretch.",
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
    "Advanced Lower Pelvic & Abdominal Protocol (No Massage Gun)": {
        "enabled": False,
        "badge": "Locked",
        "preview_img": "step1A.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Status:</b> Temporarily locked for image updates.<br><br>
<b>🎯 Why it should be done:</b><br>
A safe, 100% manual alternative that eliminates percussion risks entirely. Uses gentle manual effleurage (sweeping strokes), flat-palm pressure, and self-myofascial release to protect soft tissues while safely encouraging fluid mobilization.
</div>
""",
        "steps": manual_lymph_steps,
    },
    "Somatic Breath & Pelvic Protocol": {
        "enabled": True,
        "badge": "Active Breathwork",
        "preview_img": "",
        "description_html": """
<div class="metric-container">
<b>🎯 Why You Should Set Aside Time for This Routine:</b><br><br>
• <b>🧠 Mental Clarity & Focus:</b> Extended parasympathetic breathing calms an overactive nervous system, lowers stress hormones, and clears brain fog.<br><br>
• <b>💪 Somatic Control & Grounded Strength:</b> Builds deep pelvic stability and releases stored physical tension from the lower body without any tools or gear.<br><br>
• <b>✨ Deep Neuromuscular Activation:</b> Structured cycles of holds, squeezes, and flutters heighten local vascular flow and muscle responsiveness.<br><br>
• <b>🌿 Total Autonomy:</b> A 100% equipment-free practice designed to re-establish mind-body connection and restore natural somatic balance.<br><br>
<b>⏱️ Total Duration:</b> ~13.5 Minutes (3 Structured Phases). Lie flat in a quiet space in hook-lying pose.
</div>
""",
        "steps": somatic_breath_steps,
    },
    "Female Pelvic Vascularization & Somatic Breathing Protocol": {
        "enabled": True,
        "badge": "Active Breathwork",
        "preview_img": "",
        "description_html": """
<div class="metric-container">
<b>🎯 Why This Protocol Belongs in Your Routine:</b><br>
Functions as a targeted neuro-vascular driver. Instead of training the body into a single static state, it dynamically alternates between deep vasodilation and high-frequency neuromuscular activation.<br><br>
<b>✨ Key Targeted Neuromuscular Techniques (Phase 2):</b><br>
• <b>Staircase Ramp (3s):</b> Progressive force increase (30% → 60% → 100%) to recruit higher-threshold motor units.<br>
• <b>Peak Hold & Neural Anchor (3s):</b> Hold 100% tension while pressing tongue to palate and looking upward to disrupt cognitive spectatoring.<br>
• <b>Micro-Flutter Cascade (5s):</b> 4 to 5 rapid micro-pulses before full release to force an acute surge in arterial circulation.<br>
• <b>Adductor Co-Activation:</b> Pressing knees together to stabilize the pelvic girdle during activation.<br><br>
<b>🔄 How & Frequency:</b><br>
Alternate between the Standard Tension Release Protocol (pure down-regulation) and this Female Vascularization Protocol (neuromuscular tone & vascular flow) 3 to 5 times weekly for optimal results without mechanical plateaus.
</div>
""",
        "steps": female_somatic_steps,
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
    "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)": {
        "enabled": False,
        "badge": "Locked",
        "preview_img": "forearm_master_guide.png",
        "description_html": """
<div class="metric-container">
<b>🎯 Status:</b> Temporarily locked for maintenance.<br><br>
<b>🎯 Why It Must Be Done:</b><br>
High-velocity racquet impacts, padel smashes, and overhead serves place severe mechanical strain on the forearm tendon insertions and posterior shoulder capsule. This 4-step kinetic protocol unloads tennis and golfer elbow zones while restoring full overhead mobility.
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
    "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)": "forearm_master_guide.png",
    "Advanced Lower Pelvic & Abdominal Protocol": "step1A.png",
    "Advanced Lower Pelvic & Abdominal Protocol (No Massage Gun)": "step1A.png",
    "Advanced Posterior Chain & Ankle Mobility Protocol (Ground-Force)": "step5.png",
}

DEFAULT_PLACEHOLDER_SVG = """
<svg width="100%" height="180" viewBox="0 0 400 180" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#e2e8f0" rx="16"/>
  <circle cx="200" cy="90" r="40" fill="#cbd5e1"/>
  <path d="M185 90 L215 90 M200 75 L200 105" stroke="#475569" stroke-width="6" stroke-linecap="round"/>
  <text x="50%" y="150" dominant-baseline="middle" text-anchor="middle" fill="#64748b" font-family="sans-serif" font-size="14" font-weight="bold">Kinetic Pulse Performance Guide</text>
</svg>
"""

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
                st.session_state.current_step_index = 0
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
        if "Breath" in chosen_option:
            st.markdown("🧘‍♀️ **[Breathwork]**")
        elif chosen_option != "Massage Gun General Information & Usage Tips" and selected_img_path:
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
            st.session_state.session_logged = False
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
        st.session_state.current_step_index = 0
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

        is_somatic = "Breath" in st.session_state.selected_protocol

        if is_somatic:
            st.markdown(
                '<div class="pressure-warning">🧘 SOMATIC GUIDANCE: Focus on controlled breathing,'
                " steady muscle activation, and complete physical relaxation. No tools needed.</div>",
                unsafe_allow_html=True,
            )
            render_animated_breathing_visualizer(cycle_seconds=10, inhale_ratio=0.4)
        else:
            st.markdown(
                '<div class="pressure-warning">⚠️ TECHNIQUE: Maintain steady contact,'
                " strict pelvic positioning, and calm breathing.</div>",
                unsafe_allow_html=True,
            )

        if not is_somatic:
            img_path = resolve_image_path(step_info.get("image_file", ""))
            if not img_path:
                fallback_file = PROTOCOL_FALLBACK_IMG.get(st.session_state.selected_protocol, "")
                img_path = resolve_image_path(fallback_file)

            extra_img_path = resolve_image_path(step_info.get("extra_image_file", ""))

            if img_path:
                st.image(img_path, use_container_width=True, caption=f"Guide: {step_info['step']}")
            else:
                st.markdown(DEFAULT_PLACEHOLDER_SVG, unsafe_allow_html=True)

            if extra_img_path:
                st.image(extra_img_path, use_container_width=True, caption="Positioning Reference (Extra Guide)")

        pos_info = f"<b>🧘 Positioning:</b> {step_info['positioning']}<br>" if "positioning" in step_info else ""
        encouragement_info = f"<br><b>💬 Motivation:</b> {step_info['encouragement']}" if "encouragement" in step_info else ""

        formatted_action = step_info['action'].replace('\n', '<br>')
        st.markdown(
            f"""<div class="metric-container">
{pos_info}<b>📍 Target Zone:</b> {step_info['distance']}<br>
<b>🗺️ Location:</b> {step_info['where']}<br><br>
<b>⚡ Action & Execution Steps:</b><br>{formatted_action}<br><br>
<b>🎯 Goal:</b> {step_info['goal']}{encouragement_info}
</div>""",
            unsafe_allow_html=True,
        )

        total_duration_secs = int(step_info["duration"])
        st.markdown(f"**Target Duration:** {total_duration_secs // 60}m {total_duration_secs % 60}s ({total_duration_secs} seconds)")

        if not st.session_state.timer_running:
            if st.button("Start Step Timer", type="primary"):
                st.session_state.timer_running = True
                st.session_state.timer_start = time.time()
                st.session_state.side_switched_toast = False
                st.session_state.phase_chime_played = False
                st.rerun()
        else:
            if st.button("Stop / Reset Timer", type="secondary"):
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                st.session_state.side_switched_toast = False
                st.session_state.phase_chime_played = False
                st.rerun()

            @st.fragment(run_every=1)
            def render_timer(s_info=step_info, total_time=total_duration_secs):
                if not st.session_state.get("timer_running", False) or st.session_state.get("timer_start") is None:
                    return

                elapsed = int(time.time() - st.session_state.timer_start)
                remaining = max(total_time - elapsed, 0)
                needs_switching = s_info.get("switch_sides", False)
                half_time = total_time // 2

                mins, secs = divmod(remaining, 60)

                if elapsed == 1 and not st.session_state.get("phase_chime_played", False):
                    st.session_state.phase_chime_played = True
                    play_switch_audio_cue(freq=440.0, freq_end=660.0)

                if needs_switching:
                    if elapsed < half_time:
                        st.markdown(
                            '<div class="side-visual-left"><h1 style="font-size:3.5rem; margin:0;">🧍‍♂️ ⬅️</h1>'
                            '<h3 style="color:#0d47a1; margin:0; font-weight: bold;">WORKING: LEFT SIDE</h3></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="side-visual-right side-switch-flash"><h1 style="font-size:3.5rem; margin:0;">➡️ 🧍‍♂️</h1>'
                            '<h3 style="color:#1b5e20; font-weight: bold;">WORKING: RIGHT SIDE</h3></div>',
                            unsafe_allow_html=True,
                        )
                        if elapsed >= half_time and not st.session_state.get("side_switched_toast", False):
                            st.session_state.side_switched_toast = True
                            play_switch_audio_cue(freq=587.33, freq_end=880.0)
                            st.toast("🔄 Switch sides! Move to opposite limb.", icon="👉")
                else:
                    st.markdown(
                        '<div class="side-visual-center"><h1 style="font-size:3.5rem; margin:0;">🧘‍♀️</h1>'
                        '<h3 style="color:#e65100; font-weight: bold;">CENTER ZONE / SOMATIC BREATH</h3></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"<h3 style='text-align: center;'>⏱️ {mins:02d}:{secs:02d}</h3>",
                    unsafe_allow_html=True,
                )
                st.progress(1.0 - (remaining / total_time) if total_time else 1.0)

                if "benefit_text" in s_info:
                    st.info(s_info["benefit_text"])

                if remaining <= 0:
                    st.session_state.timer_running = False
                    st.session_state.timer_start = None
                    st.markdown(
                        "<h3 style='text-align: center; color: #0c38ff;'>✅ Step Complete!</h3>",
                        unsafe_allow_html=True,
                    )
                    st.balloons()

            render_timer(s_info=step_info, total_time=total_duration_secs)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if current_idx > 0:
                if st.button("Back", type="secondary"):
                    st.session_state.current_step_index -= 1
                    st.session_state.timer_running = False
                    st.session_state.timer_start = None
                    st.session_state.side_switched_toast = False
                    st.session_state.phase_chime_played = False
                    scroll_to_top()
                    st.rerun()
        with col2:
            next_label = "Next" if current_idx < len(protocol_steps) - 1 else "Finish"
            if st.button(next_label, type="primary"):
                st.session_state.current_step_index += 1
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                st.session_state.side_switched_toast = False
                st.session_state.phase_chime_played = False
                scroll_to_top()
                st.rerun()
    else:
        st.markdown("---")
        st.success("🏆 **Protocol Completed Successfully!** Great work.")

        st.markdown('<div class="protocol-card">', unsafe_allow_html=True)
        st.markdown("### Rate Your Post-Session Tension Level")
        rating_val = st.slider(
            "Tension / Freedom of Movement Rating (1 = Tense/Restricted, 10 = Fully Released):",
            min_value=1,
            max_value=10,
            value=8,
        )

        if not st.session_state.get("session_logged", False):
            if st.button("Save & Log Session Rating", type="primary"):
                log_session_to_csv(
                    st.session_state.user_name,
                    st.session_state.selected_protocol,
                    rating_val,
                    st.session_state.session_notes,
                )
                st.session_state.session_logged = True
                st.success("Session rating logged successfully!")
                st.rerun()
        else:
            st.info("✅ Your session feedback has been saved to the log.")

        st.markdown("</div>", unsafe_allow_html=True)

        render_support_box()

        if st.button("Start New Session", type="primary"):
            st.session_state.app_page = PAGE_PROFILE
            st.session_state.current_step_index = 0
            st.session_state.session_logged = False
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
