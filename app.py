from datetime import datetime
import os
import time
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# Page configuration with mobile viewport optimization
st.set_page_config(
    page_title="KineticPulse: Mobile Performance Suite",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Professional Mobile-First Custom Styling
st.markdown("""
<style>
/* Force full light gray background to make white cards pop */
.stApp {
    background-color: #f7f7f8 !important;
}
.main {
    background-color: #f7f7f8 !important;
    padding: 0px 4px;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Vibrant Blue Pill-Shaped Primary Buttons */
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
    color: white;
    box-shadow: 0 8px 16px rgba(12, 56, 255, 0.2);
}
.stButton>button[kind="primary"]:active {
    transform: scale(0.97);
}
.stButton>button[kind="secondary"] {
    background-color: #ffffff !important;
    border: 2px solid #eaeaea;
    color: #333333;
}

/* ABSOLUTE BOTTOM RIGHT CORNER FLOATING ADMIN BUTTON */
div[data-testid="stElementContainer"]:has(button[aria-label="Admin"]),
div.element-container:has(button[aria-label="Admin"]) {
    position: fixed !important;
    bottom: 2px !important;
    right: 2px !important;
    z-index: 999999 !important;
    width: auto !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stElementContainer"]:has(button[aria-label="Admin"]) button,
div.element-container:has(button[aria-label="Admin"]) button {
    font-size: 0.65rem !important;
    padding: 3px 8px !important;
    border-radius: 8px !important;
    background-color: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid #ccc !important;
    color: #333 !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2) !important;
}

/* Curved Orange Header Simulation */
.curved-header {
    background-color: #ff9800;
    margin: -4rem -2rem 2rem -2rem;
    padding: 4rem 2rem 3rem 2rem;
    border-bottom-left-radius: 50% 15%;
    border-bottom-right-radius: 50% 15%;
    text-align: center;
    color: white;
    box-shadow: 0 4px 12px rgba(255, 152, 0, 0.15);
}
.curved-header h1 {
    color: white !important;
    margin-bottom: 0px;
    font-size: 2.2rem;
    font-weight: bold;
}
.curved-header p {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.1rem;
    margin-top: 5px;
}

/* Clean White Cards */
.protocol-card {
    background: #ffffff;
    padding: 24px;
    border-radius: 24px;
    border: 1px solid #f0f0f0;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    margin-bottom: 16px;
}

/* Selection Block Styling */
.selection-box {
    background: #ffffff;
    padding: 20px;
    border-radius: 24px;
    border: 1px solid #f0f0f0;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    margin-bottom: 14px;
}

/* Info Containers */
.metric-container {
    background: #ffffff;
    padding: 18px;
    border-radius: 20px;
    border-left: 5px solid #ff9800;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    margin: 14px 0;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #4a4a4a;
}

.breath-box {
    background: #ffffff;
    border: 2px solid #0c38ff;
    padding: 18px;
    border-radius: 50px;
    text-align: center;
    font-size: 1.2rem;
    font-weight: bold;
    color: #0c38ff;
    margin: 15px 0;
    box-shadow: inset 0 2px 4px rgba(12, 56, 255, 0.05);
}

.pressure-warning {
    background: #fff8f0;
    border: 1px solid #ffe0b2;
    padding: 14px;
    border-radius: 16px;
    color: #d84315;
    font-weight: 600;
    font-size: 0.95rem;
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
def scroll_to_top():
    components.html(
        """
        <script>
            window.parent.scrollTo({ top: 0, behavior: 'smooth' });
        </script>
        """,
        height=0,
        width=0
    )

def log_session_to_csv(name, protocol_name, rating, notes):
    import csv
    file_exists = os.path.isfile('kinetic_session_logs.csv')
    with open('kinetic_session_logs.csv', mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Practitioner Name", "Protocol", "Tension Rating", "Notes"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            protocol_name,
            rating,
            notes
        ])

# PLAIN TEXT PASSWORD
ADMIN_PASSWORD = "Ralph1234"


# --- INITIALIZE SESSION STATE ---
if "app_page" not in st.session_state:
    st.session_state.app_page = 1
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "session_notes" not in st.session_state:
    st.session_state.session_notes = ""
if "selected_protocol" not in st.session_state:
    st.session_state.selected_protocol = "Advanced Lower Pelvic & Abdominal Flush Protocol"
if "current_step_index" not in st.session_state:
    st.session_state.current_step_index = 0
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False


# --- GLOBAL FLOATING ADMIN BUTTON ---
if st.button("Admin", key="floating_admin_btn"):
    st.session_state.app_page = 4
    scroll_to_top()
    st.rerun()


# --- PAGE 1: NAME, NOTES & SAFETY CHECKS ---
if st.session_state.app_page == 1:
    st.markdown("""
<div class="curved-header">
    <h1>KineticPulse</h1>
    <p>Start your session</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="protocol-card">
    <h3 style="margin-top:0;">Welcome</h3>
    <p style="color: #666;">Please enter your profile details and complete safety verifications to begin.</p>
</div>
""", unsafe_allow_html=True)

    entered_name = st.text_input("Your Name:", value=st.session_state.user_name)
    entered_notes = st.text_area("Session Notes / Focus Areas:", value=st.session_state.session_notes)

    st.warning(
        "⚠️ **SAFETY & MEDICAL NOTICE:**\n\n"
        "1. Avoid if you have active hernias, recent surgery, or pregnancy.\n"
        "2. Consult your physician or physical therapist prior to starting.\n"
        "3. You must be 18 years of age or older."
    )

    agree_contraindications = st.checkbox("I confirm no active contraindications listed above.")
    agree_medical_consult = st.checkbox("I acknowledge the recommendation to consult a specialist.")
    agree_age = st.checkbox("I confirm I am 18 years of age or older.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Continue", type="primary"):
        if entered_name.strip() and agree_contraindications and agree_medical_consult and agree_age:
            st.session_state.user_name = entered_name.strip()
            st.session_state.session_notes = entered_notes.strip()
            st.session_state.app_page = 2
            scroll_to_top()
            st.rerun()
        else:
            st.error("Please fill in your name and check all safety confirmation boxes to proceed.")


# --- PAGE 2: PROTOCOL SELECTOR WITH CARDS & PREVIEW LOGOS ---
elif st.session_state.app_page == 2:
    st.markdown(f"""
<div class="curved-header">
    <h1>Choose Focus / Info</h1>
    <p>Welcome back, {st.session_state.user_name}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center; color: #333; margin-bottom: 20px;'>What's on your mind?</h3>", unsafe_allow_html=True)

    protocol_options = [
        "Advanced Lower Pelvic & Abdominal Flush Protocol",
        "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)",
        "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)",
        "Advanced Posterior Chain & Ankle Mobility Protocol (Ground-Force)",
        "Massage Gun General Information & Usage Tips"
    ]
    
    # Preview Images Dictionary
    preview_images = {
        protocol_options[0]: "1000174663.png",
        protocol_options[1]: "hip_master_guide.png",
        protocol_options[2]: "step5.png",
        protocol_options[3]: "step5.png",
        protocol_options[4]: "step1.jpg"
    }

    st.markdown('<div class="selection-box">', unsafe_allow_html=True)
    
    current_selected = st.session_state.selected_protocol
    if current_selected in protocol_options:
        default_idx = protocol_options.index(current_selected)
    else:
        default_idx = 0

    chosen_option = st.radio(
        "Select training focus:",
        protocol_options,
        index=default_idx,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    selected_img_path = preview_images[chosen_option]
    
    st.markdown('<div class="protocol-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        if chosen_option != "Massage Gun General Information & Usage Tips" and os.path.exists(selected_img_path):
            st.image(selected_img_path, width=110)
        else:
            st.markdown("📘 **[Guide]**")
    with col2:
        st.markdown(f"**Selected Selection:**\n\n{chosen_option}")
    st.markdown('</div>', unsafe_allow_html=True)

    if chosen_option == "Advanced Lower Pelvic & Abdominal Flush Protocol":
        st.markdown("""
<div class="metric-container">
<b>🎯 Why it should be done:</b><br>
To target interstitial fluid drainage, break up stagnant water retention and lower-belly puffiness, and release deep pelvic and abdominal fascial tension safely.<br><br>
<b>⏱️ How often:</b><br>
2 to 3 times per week, keeping total execution time between 5 and 7 minutes per session. After exercise is ideal, as increased blood flow and body temperature help mobilize fluids and enhance tissue responsiveness.
</div>
""", unsafe_allow_html=True)
        
        if os.path.exists("1000174663.png"):
            st.image("1000174663.png", use_container_width=True, caption="Protocol Overview")
        else:
            st.info("🖼️ **Image Placeholder:** Please ensure your screenshot '1000174663.png' is placed in the app folder to display it here.")
        
    elif chosen_option == "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)":
        st.markdown("""
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
High-velocity, ballistic movements trigger defensive muscle guarding. This 6-step protocol uses unbroken sensory pressure and continuous breathing to disarm neural "brakes" and prevent the hip flexors and rotators from locking up under mechanical strain.<br><br>
<b>✨ Key Benefits:</b><br>
• <b>Free Vertical Chambering:</b> Removes neurological restrictions at the adductor/pubic interface, freeing up range for maximum vertical kick height and clean acceleration.<br>
• <b>Full Rotational Mobility:</b> Releases deep hip rotators to unlock fluid end-range rotation required for turning kicks without losing joint stability.<br>
• <b>Comprehensive Decompression:</b> Systematic progression from lateral stabilizers down to deep hip flexors to override the body's natural guarding reflex.
</div>
""", unsafe_allow_html=True)

    elif chosen_option == "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)":
        st.markdown("""
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
Repetitive overhead snaps and racquet impacts overload the lateral epicondyle and posterior shoulder capsule. Relieves muscle tension at the elbow to eliminate strain while restoring posterior shoulder mobility.
</div>
""", unsafe_allow_html=True)

    elif chosen_option == "Advanced Posterior Chain & Ankle Mobility Protocol (Ground-Force)":
        st.markdown("""
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
Restricted ankle dorsiflexion forces the knees and lower back to absorb excess rotational and impact shear forces during directional changes. Unlocking the soleus and peroneal complex restores proper ground-force transmission.
</div>
""", unsafe_allow_html=True)

    elif chosen_option == "Massage Gun General Information & Usage Tips":
        st.markdown("""
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
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("Back", type="secondary"):
            st.session_state.app_page = 1
            scroll_to_top()
            st.rerun()
    with col_next:
        button_label = "Continue to Protocol" if chosen_option != "Massage Gun General Information & Usage Tips" else "Review Complete"
        if st.button(button_label, type="primary"):
            st.session_state.selected_protocol = chosen_option
            st.session_state.current_step_index = 0
            if chosen_option == "Massage Gun General Information & Usage Tips":
                st.session_state.app_page = 2
            else:
                st.session_state.app_page = 3
            scroll_to_top()
            st.rerun()


# --- PAGE 3: STEP-BY-STEP INTERACTIVE GUIDE ---
elif st.session_state.app_page == 3:
    
    # --- UPDATED LYMPHATIC FLUSH PROTOCOL STEPS ---
    lymph_steps = [
        {
            "step": "Step 1A: Manual Lymphatic Priming",
            "duration": 30,
            "image_file": "1000176422.png",
            "distance": "12 cm to 15 cm below the navel.",
            "where": "The superficial inguinal area in the groin crease, 1 cm to 2 cm inward from the outer fold.",
            "action": "Device OFF. Use warm hands and a featherlight, manual sweeping motion (effleurage) toward the inner nodes.",
            "goal": "Safely opens primary drainage routes using tactile control without mechanical percussion.",
            "benefit_text": "💡 Primary drainage routes are safely opening manually.",
            "switch_sides": False
        },
        {
            "step": "Step 1B: Outer Hip & Tensor Fasciae Latae Activation",
            "duration": 60,
            "image_file": "1000176423.jpg",
            "distance": "10 cm to 15 cm below the navel, shifted 10 cm to 12 cm outward from the centerline.",
            "where": "The thick, meaty muscle belly of the outer hip and upper thigh (tensor fasciae latae).",
            "action": "Using a soft attachment at low speed, hold the device stationary with a strict featherlight touch for 30 seconds on the left side, then repeat for 30 seconds on the right side.",
            "goal": "Safely targets lateral hip and thigh muscle tissue to pre-release tension.",
            "benefit_text": "💡 Tension is safely pre-releasing from lateral hip tissue.",
            "switch_sides": True
        },
        {
            "step": "Step 2: Sub-Umbilical Mid-Release",
            "duration": 45,
            "image_file": "step2.jpg",
            "distance": "3 cm to 10 cm below the navel across a 10 cm wide band.",
            "where": "The sub-umbilical zone directly below the navel.",
            "action": "Angle the device at 45 degrees downward. Using a soft attachment at low speed, perform steady, slow downward glides.",
            "goal": "Pre-clears mid-level fascial tightness and breaks up localized water retention.",
            "benefit_text": "💡 Mid-level fascial tightness is safely releasing.",
            "switch_sides": False
        },
        {
            "step": "Step 3: Low-Pelvic Glide and Pause Cycle",
            "duration": 120,
            "image_file": "step3.png",
            "distance": "12 cm to 15 cm below the navel, positioned directly over the upper pubic mound.",
            "where": "The lower pelvic boundary right where soft tissue transitions into the pubic bone.",
            "action": "Using a soft attachment at medium speed, execute a slow downward glide followed by a 30-second stationary pause against the pubic bone frame. Repeat for 120 seconds.",
            "goal": "Rhythmically mobilizes lower core tissue against a stable skeletal barrier.",
            "benefit_text": "💡 Actively mobilizing lower core tissue against a safe skeletal barrier.",
            "switch_sides": False
        },
        {
            "step": "Step 4: Outer Hip V-Sweep",
            "duration": 90,
            "image_file": "step4.png",
            "distance": "8 cm to 15 cm below the navel, sweeping outward toward the hip bone.",
            "where": "Start from the vertical centerline.",
            "action": "Using a soft attachment at low speed, glide downwards to 15 cm, hold stationary for 5-10 seconds, then curve outward and upward over the iliac crest.",
            "goal": "Directs and flushes accumulated fluid safely away from sensitive areas.",
            "benefit_text": "💡 Flushing accumulated fluid safely up and over hip tissue.",
            "switch_sides": False
        },
    ]

    # --- 6-STEP HIP & PELVIC PERFORMANCE PROTOCOL ---
    hip_steps = [
        {
            "step": "Step 1: Tensor Fasciae Latae (TFL) & Upper Outer Hip",
            "duration": 120,
            "image_file": "hip_master_guide.png",
            "distance": "Outer hip flare (TFL insertion)",
            "where": "Just below the hard bony iliac crest of the outer hip.",
            "action": "High speed at a 45-degree angle. Maintain steady contact for 60 seconds per side.",
            "goal": "Unloads TFL tension to clear lateral restrictions before high-velocity kicks.",
            "benefit_text": "💡 Continuous pressure drops protective lateral muscle guarding.",
            "switch_sides": True
        },
        {
            "step": "Step 2: Gluteus Medius & Minimus Stabilizers",
            "duration": 120,
            "image_file": "hip_master_guide.png",
            "distance": "Upper-outer gluteal region",
            "where": "Posterior to the TFL across the upper glute shelf.",
            "action": "Medium speed. Smooth circular sweeps and stationary holds for 60 seconds per side.",
            "goal": "Restores lateral pelvic stability and hip abduction range.",
            "benefit_text": "💡 Stabilizing glute fibers enhances single-leg balance during chambering.",
            "switch_sides": True
        },
        {
            "step": "Step 3: Deep External Rotators (Piriformis & Gemelli)",
            "duration": 120,
            "image_file": "hip_master_guide.png",
            "distance": "Deep posterior hip pocket",
            "where": "Center of the glute tracking toward the greater trochanter.",
            "action": "Medium-high speed. Targeted stationary holds on tender trigger points for 60 seconds per side.",
            "goal": "Releases deep rotators to unlock fluid end-range rotation for turning and spinning kicks.",
            "benefit_text": "💡 Releasing deep rotators restores full internal/external rotational mobility.",
            "switch_sides": True
        },
        {
            "step": "Step 4: Anterior Hip Flexors (Rectus Femoris)",
            "duration": 120,
            "image_file": "hip_master_guide.png",
            "distance": "Upper front thigh",
            "where": "Just below the front hip bone (ASIS), tracking down the quad.",
            "action": "Medium speed. Slow longitudinal sweeps for 60 seconds per side.",
            "goal": "Disarms neural brakes on the anterior chain to prevent hip locking during extension.",
            "benefit_text": "💡 Disrupted guarding allows for cleaner vertical leg chamber acceleration.",
            "switch_sides": True
        },
        {
            "step": "Step 5: Iliopsoas Deep Pocket Release",
            "duration": 120,
            "image_file": "hip_master_guide.png",
            "distance": "Deep inner hip crease",
            "where": "Internal to the ASIS bone in the soft pocket of the hip crease.",
            "action": "Low speed, featherlight touch. Gentle stationary holds for 60 seconds per side.",
            "goal": "Relieves deep psoas hypertonicity without excessive pressure on vascular structures.",
            "benefit_text": "💡 Softening the deep psoas unlocks high knee-drive capabilities.",
            "switch_sides": True
        },
        {
            "step": "Step 6: Adductor/Pubic Interface (Inner Thigh Tie-In)",
            "duration": 120,
            "image_file": "hip_master_guide.png",
            "distance": "Upper inner thigh / pubic bone boundary",
            "where": "High on the inner thigh, safely below the groin crease against the pubic bone.",
            "action": "Low speed. Featherlight downward sweeps and gentle static contact for 60 seconds per side.",
            "goal": "Removes neurological restrictions at the adductor tie-in for unrestricted splits and high chambers.",
            "benefit_text": "💡 Unlocking the adductor interface frees up vertical chambering and flexibility.",
            "switch_sides": True
        }
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
            "switch_sides": True
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
            "switch_sides": True
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
            "switch_sides": True
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
            "switch_sides": True
        }
    ]

    ankle_steps = [
        {
            "step": "Step 1: Soleus & Gastrocnemius Flush",
            "duration": 240, 
            "image_file": "step5.png",
            "distance": "Calves & Lower Leg",
            "where": "Soleus & Gastrocnemius",
            "action": "High Speed. Sweeping glides. (120s per side)",
            "goal": "Calf & Achilles Decompression.",
            "benefit_text": "💡 Sweeping glides flush the posterior chain.",
            "switch_sides": True
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
            "switch_sides": True
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
            "switch_sides": True
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
            "switch_sides": True
        }
    ]

    if st.session_state.selected_protocol == "Advanced Lower Pelvic & Abdominal Flush Protocol":
        protocol_steps = lymph_steps
    elif st.session_state.selected_protocol == "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)":
        protocol_steps = hip_steps
    elif st.session_state.selected_protocol == "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)":
        protocol_steps = forearm_steps
    else:
        protocol_steps = ankle_steps

    st.markdown(f"""
<div class="curved-header">
    <h1>Routine Session</h1>
</div>
""", unsafe_allow_html=True)

    if st.button("Change Protocol / View Info", type="secondary"):
        st.session_state.app_page = 2
        scroll_to_top()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    current_idx = st.session_state.current_step_index

    if current_idx < len(protocol_steps):
        step_info = protocol_steps[current_idx]

        st.markdown(f"<h3 style='text-align: center; color: #333;'>{step_info['step']}</h3>", unsafe_allow_html=True)

        st.markdown(
            '<div class="pressure-warning">⚠️ TECHNIQUE: Maintain steady contact and calm, controlled breathing throughout.</div>',
            unsafe_allow_html=True
        )

        img_path = step_info["image_file"]
        if os.path.exists(img_path):
            img = Image.open(img_path)
            st.image(img, use_container_width=True, caption=f"Guide: {step_info['step']}")
        else:
            st.warning(f"⚠️ Image file `{img_path}` not found in folder. Make sure your image files match exactly.")

        st.markdown(f"""
<div class="metric-container">
    <b>📍 Target Zone:</b> {step_info['distance']}<br>
    <b>🗺️ Location:</b> {step_info['where']}<br>
    <b>⚡ Action:</b> {step_info['action']}<br>
    <b>🎯 Goal:</b> {step_info['goal']}
</div>
""", unsafe_allow_html=True)

        total_duration_secs = step_info['duration']
        st.markdown(f"**Target Duration:** {total_duration_secs} seconds")

        if st.button("Start Step Timer", type="primary"):
            
            side_visual_placeholder = st.empty()
            placeholder = st.empty()
            progress_bar = st.progress(0)
            breath_placeholder = st.empty()
            benefit_placeholder = st.empty()

            total_time = step_info["duration"]
            half_time = total_time // 2
            needs_switching = step_info.get("switch_sides", False)

            for remaining in range(total_time, -1, -1):
                mins, secs = divmod(remaining, 60)
                elapsed = total_time - remaining
                
                if needs_switching:
                    if elapsed < half_time:
                        if os.path.exists("man_left.png"):
                            side_visual_placeholder.image("man_left.png", use_container_width=True)
                        else:
                            side_visual_placeholder.markdown("""
                            <div style="background:#e3f2fd; border:2px solid #2196f3; border-radius:15px; padding:15px; text-align:center; margin-bottom: 15px;">
                                <h1 style="font-size:3.5rem; margin:0;">🧍‍♂️ ⬅️</h1>
                                <h3 style="color:#0d47a1; margin:0; font-weight: bold;">WORKING: LEFT SIDE</h3>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        if os.path.exists("man_right.png"):
                            side_visual_placeholder.image("man_right.png", use_container_width=True)
                        else:
                            side_visual_placeholder.markdown("""
                            <div style="background:#e8f5e9; border:2px solid #4caf50; border-radius:15px; padding:15px; text-align:center; margin-bottom: 15px;">
                                <h1 style="font-size:3.5rem; margin:0;">➡️ 🧍‍♂️</h1>
                                <h3 style="color:#1b5e20; margin:0; font-weight: bold;">WORKING: RIGHT SIDE</h3>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    if os.path.exists("man_center.png"):
                        side_visual_placeholder.image("man_center.png", use_container_width=True)
                    else:
                        side_visual_placeholder.markdown("""
                        <div style="background:#fff3e0; border:2px solid #ff9800; border-radius:15px; padding:15px; text-align:center; margin-bottom: 15px;">
                            <h1 style="font-size:3.5rem; margin:0;">🧍‍♂️</h1>
                            <h3 style="color:#e65100; margin:0; font-weight: bold;">WORKING: CENTER ZONE / BILATERAL</h3>
                        </div>
                        """, unsafe_allow_html=True)

                placeholder.markdown(f"<h3 style='text-align: center;'>⏱️ {mins:02d}:{secs:02d}</h3>", unsafe_allow_html=True)
                progress_bar.progress(1.0 - (remaining / total_time))

                if (elapsed % 10) < 5:
                    breath_placeholder.markdown('<div class="breath-box">🌬️ Deep Belly Inhale...</div>', unsafe_allow_html=True)
                else:
                    breath_placeholder.markdown('<div class="breath-box">😌 Slow Relaxed Exhale...</div>', unsafe_allow_html=True)

                if "benefit_text" in step_info:
                    benefit_placeholder.info(step_info["benefit_text"])

                if needs_switching and total_time > 30 and elapsed == half_time:
                    st.toast("🔄 Switch sides! Move to opposite limb.", icon="👉")

                time.sleep(1)

            side_visual_placeholder.empty()
            placeholder.markdown("<h3 style='text-align: center; color: #0c38ff;'>✅ Step Complete!</h3>", unsafe_allow_html=True)
            breath_placeholder.empty()
            st.balloons()

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if current_idx > 0:
                if st.button("Back", type="secondary"):
                    st.session_state.current_step_index -= 1
                    scroll_to_top()
                    st.rerun()
        with col2:
            if current_idx < len(protocol_steps) - 1:
                if st.button("Next", type="primary"):
                    st.session_state.current_step_index += 1
                    scroll_to_top()
                    st.rerun()
            else:
                if st.button("Finish", type="primary"):
                    st.session_state.current_step_index += 1
                    scroll_to_top()
                    st.rerun()
    else:
        st.markdown("---")
        st.success("🏆 **Protocol Completed Successfully!** Great work.")
        
        log_session_to_csv(st.session_state.user_name, st.session_state.selected_protocol, 10, st.session_state.session_notes)
        
        if st.button("Start New Session", type="primary"):
            st.session_state.app_page = 1
            st.session_state.current_step_index = 0
            scroll_to_top()
            st.rerun()

# --- PAGE 4: SECURE ADMIN LOGIN ---
elif st.session_state.app_page == 4:
    st.markdown("""
<div class="curved-header">
    <h1>Admin Login</h1>
    <p>Data Access</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="protocol-card">
    <p>Please enter the administrator password to view session logs.</p>
</div>
""", unsafe_allow_html=True)

    admin_password = st.text_input("Password:", type="password")

    if st.button("Login", type="primary"):
        if admin_password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.session_state.app_page = 5
            scroll_to_top()
            st.rerun()
        else:
            st.error("❌ Incorrect Password. Please try again.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to App", type="secondary"):
        st.session_state.app_page = 1
        scroll_to_top()
        st.rerun()

# --- PAGE 5: ADMIN DATA VIEWER ---
elif st.session_state.app_page == 5:
    if not st.session_state.admin_authenticated:
        st.warning("🔒 You must be logged in to access this page.")
        st.session_state.app_page = 4
        scroll_to_top()
        st.rerun()

    st.markdown("""
<div class="curved-header">
    <h1>Session Logs</h1>
    <p>All User Activity Data</p>
</div>
""", unsafe_allow_html=True)

    log_file_path = 'kinetic_session_logs.csv'
    if not os.path.exists(log_file_path):
        st.warning(f"⚠️ The log file `{log_file_path}` does not exist yet. No sessions have been recorded.")
    else:
        df = pd.read_csv(log_file_path)
        if df.empty:
            st.info("ℹ️ The log file is empty. No sessions have been completed yet.")
        else:
            df = df.sort_values(by="Timestamp", ascending=False)
            st.dataframe(df, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout / Back to App", type="secondary"):
        st.session_state.admin_authenticated = False
        st.session_state.app_page = 1
        scroll_to_top()
        st.rerun()
