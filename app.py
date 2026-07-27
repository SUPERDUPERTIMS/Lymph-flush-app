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
    
    preview_images = {
        protocol_options[0]: "step1.jpg",
        protocol_options[1]: "hip_master_guide.png",
        protocol_options[2]: "forearm_guide.png",
        protocol_options[3]: "ankle_guide.png",
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
To target interstitial fluid drainage, break up stagnant water retention and lower-belly puffiness, and release deep pelvic and abdominal fascial tension.<br><br>
<b>⏱️ How often:</b><br>
2 to 3 times per week, keeping total execution time between 5 and 7 minutes per session. After exercise is ideal, as increased blood flow and body temperature help mobilize fluids and enhance tissue responsiveness.<br><br>
<b>✨ Benefits you will notice:</b><br>
• Flatter, more defined look<br>
• Physically feeling better<br>
• Complete fluid clearance
</div>
""", unsafe_allow_html=True)
        
    elif chosen_option == "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)":
        st.markdown("""
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
High-velocity, ballistic movements trigger defensive muscle guarding. This protocol uses 90-second unbroken sensory pressure and continuous breathing to disarm neural "brakes" and prevent the hip flexors from locking up under mechanical strain.<br><br>
<b>✨ Key Benefits:</b><br>
• <b>Free Vertical Chambering:</b> Removes neurological restrictions at the adductor/pubic interface, freeing up range for maximum vertical kick height and clean acceleration.<br>
• <b>Full Rotational Mobility:</b> Releases deep hip rotators to unlock fluid end-range rotation required for turning kicks without losing joint stability.<br>
• <b>Disrupted Guarding:</b> Lowers muscle guarding, improves local circulation, and overrides the body's natural tendency to brace during high-stress movements.<br><br>
<b>⏱️ Recommended Frequency:</b><br>
• <b>Schedule:</b> 3 times per week (e.g., Monday, Wednesday, Friday) with at least 24 hours between sessions.<br>
• <b>Timing:</b> Ideal as a dedicated mobility pre-session or on non-consecutive recovery days.<br>
• <b>Limit:</b> Avoid running this specific deep 16-minute mechanical routine daily, as tissues need time to adjust and recover from the intense sensory input.
</div>
""", unsafe_allow_html=True)

    elif chosen_option == "Advanced Forearm, Elbow & Shoulder Kinetic Protocol (Racquet & Overhead)":
        st.markdown("""
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
Repetitive overhead snaps and racquet impacts overload the lateral epicondyle and posterior shoulder capsule. Relieves muscle tension at the elbow to eliminate "tennis/padel elbow" strain while restoring posterior shoulder mobility for fluid internal/external rotation under load.<br><br>
<b>✨ Key Benefits:</b><br>
• <b>Elbow Relief:</b> Decompresses the brachioradialis and wrist extensor mass to reduce lateral joint strain.<br>
• <b>Restored Shoulder Rotation:</b> Clears posterior capsule and infraspinatus restrictions for unimpeded overhead reach.<br>
• <b>Fluid Wrist Snaps:</b> Restores elastic recoil and power transfer through racquet strikes.<br><br>
<b>⏱️ Recommended Frequency:</b><br>
• <b>Schedule:</b> 2 to 3 times per week, specifically after matches or heavy hitting sessions.<br>
• <b>Duration:</b> 12 minutes total execution time across 4 targeted steps.
</div>
""", unsafe_allow_html=True)

    elif chosen_option == "Advanced Posterior Chain & Ankle Mobility Protocol (Ground-Force)":
        st.markdown("""
<div class="metric-container">
<b>🎯 Why It Must Be Done:</b><br>
Restricted ankle dorsiflexion forces the knees and lower back to absorb excess rotational and impact shear forces during directional changes. Unlocking the soleus and peroneal complex restores proper ground-force transmission.<br><br>
<b>✨ Key Benefits:</b><br>
• <b>Deeper Mobility:</b> Increases ankle dorsiflexion, enabling deeper squatting, lunging, and lower stance capacity.<br>
• <b>Lateral Stability:</b> Frees the peroneal complex to stabilize sudden cuts on court surfaces.<br>
• <b>Knee & Back Protection:</b> Reduces compensatory stress transferred upward along the posterior kinetic chain.<br><br>
<b>⏱️ Recommended Frequency:</b><br>
• <b>Schedule:</b> 2 to 3 times per week as part of a pre-workout mobility warm-up or recovery session.<br>
• <b>Duration:</b> 14 minutes total execution time across 4 targeted steps.
</div>
""", unsafe_allow_html=True)

    elif chosen_option == "Massage Gun General Information & Usage Tips":
        st.markdown("""
<div class="metric-container">
<h4 style="color:#ff9800; margin-top:0;">Massage Gun Speeds and Techniques for First-Time Users</h4>

<p><b>1. Speed Settings and Operational Mechanics</b><br>
Different speed settings serve distinct neurological and mechanical purposes, allowing first-time users to transition from light tissue relaxation to deep myofascial release:</p>
<p style="margin-left: 15px;">
• <b>Low to Medium-Low Speed:</b> Ideal for sensitive areas, delicate fascia work, and lymphatic drainage, as it optimizes tissue resonance without triggering a defensive muscular contraction.<br><br>
• <b>Medium to High Speed:</b> Used for global muscle flushes, releasing broader superficial tensions, and targeting major muscle bellies like the glutes.<br><br>
• <b>High Speed:</b> Deployed to break up deep-seated muscle stiffness, address dense fascial boundaries, and bypass neurological "brakes" in localized athletic zones.
</p>

<p><b>2. Fittings and Attachment Selection</b><br>
Different attachment heads alter how percussive therapy interacts with soft tissue during a session:</p>
<p style="margin-left: 15px;">
• <b>Flat-Head Attachment:</b> Typically paired with medium-low settings to optimize tissue resonance, distribute pressure broadly, and perform fluid drainage or sub-umbilical releases safely.<br><br>
• <b>Targeted Standard Heads (Spherical/Bullet variants):</b> Used for pinpointing specific fascial boundaries, deep lateral rotators, and tight structural interfaces without slipping off tissue zones.
</p>

<p><b>3. General Massage Gun Techniques & Rules</b><br>
First-time users should adhere to strict foundational mechanics to prevent tissue irritation and maximize effectiveness:</p>
<p style="margin-left: 15px;">
• <b>The 90-Second Rule:</b> Muscles require uninterrupted sensory pressure to drop their protective defenses, so users must maintain steady, unbroken contact on each localized spot for the full 90 seconds straight without skipping or skimming across areas.<br><br>
• <b>Avoid Bone:</b> Keep the vibrating attachment strictly on soft muscle tissue, staying completely clear of kneecaps, spines, and pelvic or hip bone flares.<br><br>
• <b>Mandatory Respiratory Continuity:</b> Users must maintain continuous, non-stop inhales and exhales throughout execution; holding the breath or bracing instantly triggers an adrenaline response that locks down the muscles.
</p>
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
    lymph_steps = [
        {
            "step": "Step 1: Open Primary Drainage Gates",
            "duration": 90,
            "image_file": "step1.jpg",
            "distance": "12 cm - 15 cm below navel",
            "where": "Groin creases where legs meet torso, 1 cm to 2 cm inward toward pubic crease.",
            "action": "Hold device stationary with a light touch for 45-60s on left side, then 45-60s on right side.",
            "goal": "Unlocks primary superficial inguinal lymph nodes for fluid exit clearance.",
            "benefit_text": "💡 Primary drainage gates are unlocking for unobstructed clearance.",
        },
        {
            "step": "Step 2: Sub-Umbilical Mid-Release",
            "duration": 45,
            "image_file": "step2.jpg",
            "distance": "3 cm - 10 cm below navel",
            "where": "Sub-umbilical zone directly below navel across a 10 cm wide band.",
            "action": "Angle device 45° downward. Perform steady downward glides (2 cm/sec) from 3 cm down to 10 cm.",
            "goal": "Pre-clears mid-level fascial tightness and breaks up water retention.",
            "benefit_text": "💡 Mid-level fascial tension is releasing.",
        },
        {
            "step": "Step 3: Extended Low-Pelvic Release",
            "duration": 120,
            "image_file": "step3.jpg",
            "distance": "14 cm - 15 cm below navel",
            "where": "Low-pelvic zone directly over central pubic border.",
            "action": "Execute slow movement over 120 seconds, holding for 5 seconds at the lowest point.",
            "goal": "Mobilizes fluid pooled at the lowest base of the belly.",
            "benefit_text": "💡 Actively mobilizing fluid pooled at the base.",
        },
        {
            "step": "Step 4: The Deep Downward V-Sweep",
            "duration": 90,
            "image_file": "step4.jpg",
            "distance": "14 cm - 15 cm below navel → Outer Fold",
            "where": "Start from vertical centerline, extending 8-12 cm diagonally into deep groin folds.",
            "action": "Focus on slow movement. Work downwards, hold for 5 seconds, then sweep sideways.",
            "goal": "Directs and flushes accumulated fluid straight into cleared drainage pathways.",
            "benefit_text": "💡 Fluid is being channeled straight into open drainage nodes.",
        },
    ]

    hip_steps = [
        {
            "step": "Step 1: The Outer Hip (TFL)",
            "duration": 180,
            "image_file": "hip_master_guide.png",
            "distance": "Outer hip flare (Panel 1)",
            "where": "Just below hard bony flare of outer hip.",
            "action": "High speed at 45-degree angle. Maintain steady contact for 90 seconds per side.",
            "goal": "Unloads Tensor Fasciae Latae tension to clear lateral restrictions.",
            "benefit_text": "💡 Continuous pressure drops protective muscle guarding.",
        },
        {
            "step": "Step 2: Rear Hip & Rotators",
            "duration": 360,
            "image_file": "hip_master_guide.png",
            "distance": "Gluteal quadrant & mid-rotator pocket (Panels 2 & 3)",
            "where": "Part A: Upper outer buttock (Panel 2). Part B: Figure 4 cross-leg position (Panel 3).",
            "action": "Part A (90s/side): Medium-high global flush. Part B (90s/side): Medium speed with slow oscillating circles.",
            "goal": "Unlocks end-range rotational tracking for rapid turning kicks.",
            "benefit_text": "💡 Unlocking deep rotational mobility behind hip capsule.",
        },
        {
            "step": "Step 3: Inner Thigh & Adductor Zone",
            "duration": 360,
            "image_file": "hip_master_guide.png",
            "distance": "Inner thigh to lower pubic ramus (Panels 4 & 5)",
            "where": "Part A: Inner thigh to groin (Panel 4). Part B: Half-butterfly position (Panel 5).",
            "action": "Part A (90s/side): High speed light sweep. Part B (90s/side): Tight 5 cm path upward stopping at pelvic bone.",
            "goal": "Removes neurological brakes restricting vertical hip chambering.",
            "benefit_text": "💡 Clearing boundary to eliminate kicking brakes.",
        },
        {
            "step": "Step 4: Structural Integration Lunge",
            "duration": 60,
            "image_file": "hip_master_guide.png",
            "distance": "Front pocket line / Hip flexor stretch (Panel 6)",
            "where": "Low kneeling lunge position on mat.",
            "action": "Tuck tailbone under, shift weight slightly forward until stretch is felt (30s per side).",
            "goal": "Locks in mechanical alignment and length.",
            "benefit_text": "💡 Reinforcing structural integration and optimal pelvic tilt.",
        },
    ]

    forearm_steps = [
        {
            "step": "Step 1: Lateral Extensor Mass & Brachioradialis",
            "duration": 180,
            "image_file": "forearm_guide.png",
            "video_file": "elbow_intro.mp4",
            "distance": "Outer Forearm Mass",
            "where": "Position 3 cm below outer elbow crease over fleshy forearm mass.",
            "action": "Medium Speed (Flat/Cushion attachment). Palm facing down. Glide slowly down toward wrist (1 cm/sec) and back up (90s per arm).",
            "goal": "Relieves tension at the lateral epicondyle to eliminate tennis/padel elbow strain.",
            "benefit_text": "💡 Decompressing wrist extensors to restore fluid wrist snaps.",
        },
        {
            "step": "Step 2: Medial Flexor & Pronator Teres Release",
            "duration": 180,
            "image_file": "forearm_guide.png",
            "distance": "Inner Forearm Belly",
            "where": "Start 3 cm below inner elbow joint (avoid inner elbow groove nerve channel).",
            "action": "Low-to-Medium Speed. Palm facing up. Trace narrow path along inner forearm belly down toward mid-forearm (90s per arm).",
            "goal": "Releases tight flexor group from repetitive gripping and rotational strikes.",
            "benefit_text": "💡 Releasing forearm flexors to prevent medial joint strain.",
        },
        {
            "step": "Step 3: Posterior Capsule & Infraspinatus",
            "duration": 240,
            "image_file": "forearm_guide.png",
            "distance": "Posterior Scapular Pocket",
            "where": "Fleshy muscular pocket behind shoulder blade below the spine of the scapula.",
            "action": "Medium-High Speed (Bullet/Ball attachment). Reach arm across chest. Use slow, deep circular sweeps (120s per shoulder).",
            "goal": "Clears posterior capsule restriction to restore full shoulder rotation.",
            "benefit_text": "💡 Unlocking deep posterior shoulder rotation for overhead power.",
        },
        {
            "step": "Step 4: Pec Minor & Anterior Wall Clearance",
            "duration": 120,
            "image_file": "forearm_guide.png",
            "distance": "Sub-Clavicular Chest Wall",
            "where": "Just below collarbone, moving diagonally toward front shoulder joint.",
            "action": "Low Speed (Flat attachment). Opposite hand behind lower back. Angle device at 45° on soft muscle tissue (60s per side).",
            "goal": "Opens the chest wall and prevents forward shoulder protraction.",
            "benefit_text": "💡 Opening front shoulder wall to optimize scapular posture.",
        },
    ]

    ankle_steps = [
        {
            "step": "Step 1: Gastrocnemius & Deep Soleus Flush",
            "duration": 240,
            "image_file": "ankle_guide.png",
            "video_file": "calves_intro.mp4",
            "distance": "Calf Muscle Belly to Achilles Transition",
            "where": "Upper calf down to lower third where muscle transitions into Achilles tendon.",
            "action": "High Speed (Large Ball/Flat head). Part A (60s): Sweep calf bellies. Part B (60s): Hold pressure on outer/inner lower calf borders (120s per leg).",
            "goal": "Frees deep calf stiffness to immediately increase ankle dorsiflexion.",
            "benefit_text": "💡 Increasing ankle dorsiflexion for deeper squatting and lunging.",
        },
        {
            "step": "Step 2: Peroneal Complex (Lateral Lower Leg)",
            "duration": 180,
            "image_file": "ankle_guide.png",
            "distance": "Lateral Lower Leg Channel",
            "where": "Outer side of shin between shin bone and calf.",
            "action": "Medium Speed. Turn leg slightly inward. Glide slowly along outer muscle channel from 5 cm below knee to 5 cm above ankle (90s per leg).",
            "goal": "Improves ankle stability during sudden lateral cuts and changes of direction.",
            "benefit_text": "💡 Stabilizing outer lower leg for rapid lateral court cuts.",
        },
        {
            "step": "Step 3: Posterior Hamstring Insertion & Biceps Femoris",
            "duration": 300,
            "image_file": "ankle_guide.png",
            "distance": "Mid-Hamstring to Outer Knee Pocket",
            "where": "Part A: Mid-to-outer hamstring belly. Part B: Outer hamstring pocket 5-10 cm above back of knee.",
            "action": "Medium-High Speed. Sit on chair edge. Part A (90s): Longitudinal glides up to gluteal fold. Part B (60s): Hold outer pocket (150s per leg).",
            "goal": "Clears lateral knee pulling and unloads posterior kinetic chain tension.",
            "benefit_text": "💡 Relieving posterior kinetic strain and outer knee tension.",
        },
        {
            "step": "Step 4: Loaded Soleus Mobilization Stretch",
            "duration": 120,
            "image_file": "ankle_guide.png",
            "distance": "Ankle Dorsiflexion End-Range",
            "where": "Standing lunge facing wall with back heel flat on ground.",
            "action": "Bend knees, driving front and back knees forward over toes without lifting heel. Hold end-range position with deep belly breaths (60s per leg).",
            "goal": "Reinforces neurological lengthening and locks in ankle dorsiflexion range.",
            "benefit_text": "💡 Locking in ankle end-range dorsiflexion with active mobilization.",
        },
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

        # --- NEW LOGIC: RENDER VIDEO IF IT EXISTS ---
        if "video_file" in step_info:
            vid_path = step_info["video_file"]
            if os.path.exists(vid_path):
                st.video(vid_path)
            else:
                st.info(f"🎥 **Video Placeholder:** To view the intro video here, please add your video file named `{vid_path}` into the app's folder.")

        # --- IMAGE RENDERING ---
        img_path = step_info["image_file"]
        if os.path.exists(img_path):
            img = Image.open(img_path)
            st.image(img, use_container_width=True, caption=f"Guide: {step_info['step']}")
        else:
            st.warning(f"⚠️ Image file `{img_path}` not found in folder.")

        st.markdown(f"""
<div class="metric-container">
    <b>📍 Target Zone:</b> {step_info['distance']}<br>
    <b>🗺️ Location:</b> {step_info['where']}<br>
    <b>⚡ Action:</b> {step_info['action']}<br>
    <b>🎯 Goal:</b> {step_info['goal']}
</div>
""", unsafe_allow_html=True)

        total_duration_secs = step_info['duration']
        st.markdown(f"**Target Duration:** {total_duration_secs} seconds ({total_duration_secs // 60} mins)")

        if st.button("Start Step Timer", type="primary"):
            placeholder = st.empty()
            progress_bar = st.progress(0)
            breath_placeholder = st.empty()
            benefit_placeholder = st.empty()

            total_time = step_info["duration"]
            half_time = total_time // 2

            for remaining in range(total_time, -1, -1):
                mins, secs = divmod(remaining, 60)
                placeholder.markdown(f"<h3 style='text-align: center;'>⏱️ {mins:02d}:{secs:02d}</h3>", unsafe_allow_html=True)
                progress_bar.progress(1.0 - (remaining / total_time))

                elapsed = total_time - remaining
                if (elapsed % 10) < 5:
                    breath_placeholder.markdown('<div class="breath-box">🌬️ Deep Belly Inhale...</div>', unsafe_allow_html=True)
                else:
                    breath_placeholder.markdown('<div class="breath-box">😌 Slow Relaxed Exhale...</div>', unsafe_allow_html=True)

                if "benefit_text" in step_info:
                    benefit_placeholder.info(step_info["benefit_text"])

                if total_time > 60 and elapsed == half_time:
                    st.toast("🔄 Switch sides! Move to opposite limb.", icon="👉")

                time.sleep(1)

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
