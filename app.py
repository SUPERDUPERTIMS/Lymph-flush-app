from datetime import datetime
import os
import time
from PIL import Image, ImageDraw
import streamlit as st
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="KineticPulse: Multi-Protocol Tissue & Performance Suite",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Professional Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        border: none;
        color: white;
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    .protocol-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .metric-container {
        background: #f1f5f9;
        padding: 12px 16px;
        border-radius: 10px;
        border-left: 4px solid #2563eb;
        margin: 10px 0;
    }
    .breath-box {
        background: #e0f2fe;
        border: 2px solid #0284c7;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        color: #0369a1;
        margin: 15px 0;
    }
    .pressure-warning {
        background: #fef3c7;
        border: 2px solid #f59e0b;
        padding: 12px;
        border-radius: 10px;
        color: #92400e;
        font-weight: 600;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


# Helper function to force window scroll to top
def scroll_to_top():
    components.html(
        """
        <script>
            window.parent.scrollTo({ top: 0, behavior: 'instant' });
        </script>
        """,
        height=0,
        width=0
    )


# Helper function to log user metrics locally to a CSV file
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


# App Title & Professional Header
st.title("⚡ KineticPulse: Tissue & Performance Suite")
st.markdown("##### *Advanced Myofascial Maintenance & Mechanical Alignment Protocols*")
st.markdown("---")

# Session State Initialization for Safety Gate
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "safety_cleared" not in st.session_state:
    st.session_state.safety_cleared = False
if "selected_protocol" not in st.session_state:
    st.session_state.selected_protocol = "Advanced Lower Pelvic & Abdominal Flush Protocol"
if "current_step_index" not in st.session_state:
    st.session_state.current_step_index = 0

# --- SAFETY VERIFICATION GATE ---
if not st.session_state.user_name or not st.session_state.safety_cleared:
    st.markdown("""
        <div class="protocol-card">
            <h3>Clinical Protocol Access & Safety Verification</h3>
            <p>Please enter your profile name and complete all required safety verifications below to begin your training session.</p>
        </div>
    """, unsafe_allow_html=True)
    
    entered_name = st.text_input("Your Name:")
    
    st.warning(
        "⚠️ **MEDICAL DISCLAIMER & SAFETY NOTICE:**\n\n"
        "1. **Contraindications Check:** Do NOT perform these protocols if you have an active abdominal or inguinal hernia, "
        "severe acute digestive issues, recent surgery, or if you are pregnant.\n\n"
        "2. **Professional Guidance:** We strongly recommend consulting your physician, physical therapist, or a medical "
        "practitioner specializing in the lymphatic system or sports rehabilitation prior to starting this program.\n\n"
        "3. **Age Requirement:** You must be 18 years of age or older to use this protocol."
    )
    
    agree_contraindications = st.checkbox("I confirm I have no active contraindications or medical restrictions listed above.")
    agree_medical_consult = st.checkbox("I acknowledge the recommendation to consult a qualified physician, physical therapist, or lymphatic specialist before starting.")
    agree_age = st.checkbox("I confirm that I am 18 years of age or older.")
    
    if st.button("Initialize Clinical Session", type="primary"):
        if entered_name.strip() and agree_contraindications and agree_medical_consult and agree_age:
            st.session_state.user_name = entered_name.strip()
            st.session_state.safety_cleared = True
            scroll_to_top()
            st.rerun()
        else:
            st.error("Please enter your name and check all three confirmation boxes above to proceed.")
    st.stop()
else:
    st.success(f"Session Active | Practitioner: **{st.session_state.user_name}**")

# --- PROTOCOL SELECTOR SCREEN ---
st.markdown("### 📋 Select Training Protocol")
protocol_choice = st.selectbox(
    "Choose your session protocol:",
    [
        "Advanced Lower Pelvic & Abdominal Flush Protocol",
        "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)"
    ]
)

# Reset step index if protocol changes
if st.session_state.selected_protocol != protocol_choice:
    st.session_state.selected_protocol = protocol_choice
    st.session_state.current_step_index = 0
    scroll_to_top()
    st.rerun()

st.markdown("---")

# --- DEFINE PROTOCOLS ---

# 1. Lymph Flush Protocol Steps
lymph_steps = [
    {
        "step": "Step 1: Open Primary Drainage Gates",
        "duration": 90,
        "image_file": "step1.png",
        "distance": "12 cm - 15 cm below navel",
        "where": "Groin creases where legs meet torso, 1 cm to 2 cm inward toward pubic crease.",
        "action": "Hold the device stationary with a light touch for 45 to 60 seconds on the left side, then 45 to 60 seconds on the right side.",
        "goal": "Unlocks primary superficial inguinal lymph nodes so mobilized fluid has an unobstructed exit clearance route.",
        "benefit_text": "💡 Benefit Note: Primary drainage gates are unlocking to allow unobstructed exit clearance.",
    },
    {
        "step": "Step 2: Sub-Umbilical Mid-Release",
        "duration": 45,
        "image_file": "step2.png",
        "distance": "3 cm - 10 cm below navel",
        "where": "Sub-umbilical zone directly below your navel across a 10 cm wide band (5 cm left/right of center).",
        "action": "Angle the device 45° downward toward feet. Perform steady downward glides (2 cm/sec) from 3 cm down to 10 cm.",
        "goal": "Pre-clears mid-level abdominal fascial tightness and breaks up stagnant water retention to prevent bottlenecking.",
        "benefit_text": "💡 Benefit Note: Mid-level fascial tension is releasing and stagnant water retention is breaking up.",
    },
    {
        "step": "Step 3: Extended Low-Pelvic Release",
        "duration": 120,
        "image_file": "step3.png",
        "distance": "14 cm - 15 cm below navel",
        "where": "Low-pelvic zone directly over the central pubic border / lower anchor area.",
        "action": "Execute slow movement over the 120 seconds and try and hold for 5 seconds 14 to 15 cm below belly button.",
        "goal": "Mobilizes fluid pooled at the lowest base of the belly through slow, controlled tissue contact.",
        "benefit_text": "💡 Benefit Note: Slow movement over the 120 seconds is actively mobilizing fluid pooled at the base.",
    },
    {
        "step": "Step 4: The Deep Downward V-Sweep",
        "duration": 90,
        "image_file": "step4.png",
        "distance": "14 cm - 15 cm below navel → Outer Fold",
        "where": "Start from vertical centerline, extending 8 cm to 12 cm diagonally outward into deep groin fold creases.",
        "action": "Focus on slow movement. Work downwards and hold for 5 seconds then sideways along fold.",
        "goal": "Mechanically directs and flushes all accumulated fluid straight into the cleared drainage pathways with perfect directional form.",
        "benefit_text": "💡 Benefit Note: Fluid is being precisely channeled and swept straight into open drainage nodes for final clearance.",
    },
]

# 2. Hip Flexor Protocol Steps (Mapped to Master Guide Image)
hip_steps = [
    {
        "step": "Step 1: The Outer Hip (TFL)",
        "duration": 180, # 3 minutes total (1.5 mins per side)
        "image_file": "hip_master_guide.png",
        "distance": "Outer hip flare (Panel 1)",
        "where": "Just below the hard bony flare of your outer hip.",
        "action": "Set device to high speed. Position at a 45-degree angle. Maintain steady, continuous contact for 90 seconds straight per side.",
        "goal": "Unloads Tensor Fasciae Latae tension to clear lateral hip restrictions.",
        "benefit_text": "💡 Benefit Note: Continuous 90-second sensory pressure is dropping protective muscle guarding.",
    },
    {
        "step": "Step 2: Rear Hip, Glutes & Deep Lateral Rotators",
        "duration": 360, # 6 minutes total (3 mins per side: 90s Global Flush + 90s Option E)
        "image_file": "hip_master_guide.png",
        "distance": "Gluteal upper outer quadrant & mid-rotator pocket (Panels 2 & 3)",
        "where": "Part A: Upper outer quadrant of buttock (Panel 2). Part B (Option E): Midway between outer hip bone and tailbone in 'Figure 4' cross-leg position (Panel 3).",
        "action": "Part A (90s/side): Medium-high speed global flush (stay off sacrum/spine). Part B (90s/side): Medium speed with slow, oscillating circles in Figure 4 shape.",
        "goal": "Unlocks true end-range rotational tracking required for fluid, powerful hip-clearing mechanics during rapid turning kicks (mawashi-geri).",
        "benefit_text": "💡 Benefit Note: Unlocking deep rotational mobility behind the hip joint capsule for clean kicking rotation.",
    },
    {
        "step": "Step 3: Inner Thigh & Advanced Leverage Zone",
        "duration": 360, # 6 minutes total (3 mins per side: 90s Adductor Flush + 90s Option A)
        "image_file": "hip_master_guide.png",
        "distance": "Inner thigh to lower pubic ramus (Panels 4 & 5)",
        "where": "Part A: Inner thigh from 10 cm above knee to groin (Panel 4). Part B (Option A): Inner border seam 5-10 cm down from underwear line in half-butterfly position (Panel 5).",
        "action": "Part A (90s/side): High speed with light sweeping pressure. Part B (90s/side): Highest speed tracing a tight 5 cm path upward, stopping right at the pelvic bone boundary.",
        "goal": "Removes the neurological 'brakes' that restrict sudden vertical hip chambering, immediately freeing up range for maximum kick height.",
        "benefit_text": "💡 Benefit Note: Clearing the boundary between high adductor and lower pubic ramus to eliminate kicking brakes.",
    },
    {
        "step": "Step 4: The Structural Integration Lunge",
        "duration": 60, # 1 minute total (30 secs per side)
        "image_file": "hip_master_guide.png",
        "distance": "Front pocket line / Hip flexor stretch (Panel 6)",
        "where": "Low kneeling lunge position on a soft mat.",
        "action": "Actively tuck tailbone completely under to square pelvis. Shift weight forward a fraction of a centimeter until clean stretch is felt in front pocket line (30s per side).",
        "goal": "Locks in mechanical alignment and length following percussion tissue release.",
        "benefit_text": "💡 Benefit Note: Reinforcing structural integration and optimal pelvic tilt.",
    },
]

# Assign active protocol configuration based on selection
if st.session_state.selected_protocol == "Advanced Lower Pelvic & Abdominal Flush Protocol":
    protocol_steps = lymph_steps
else:
    protocol_steps = hip_steps

# Sidebar for Professional Tracking & Setup Guide
st.sidebar.header("📊 Clinical Setup & Log")
if st.session_state.selected_protocol == "Advanced Lower Pelvic & Abdominal Flush Protocol":
    st.sidebar.markdown("""
    * **Positioning:** Lie flat, knees bent at 90°.
    * **Device Setup:** Flat-head attachment on **medium-low vibration setting**.
    * **Pressure Rule:** **Do NOT press hard**; use a light touch to optimize tissue resonance.
    * **Breathing:** Maintain slow, deep belly breaths (4s inhale, 6s exhale).
    """)
else:
    st.sidebar.markdown("""
    * **Positioning:** Mat work, sitting, or kneeling lunge.
    * **Device Setup:** High or medium-high speed per step instructions.
    * **The 90-Second Rule:** Maintain uninterrupted sensory contact for full duration.
    * **Continuous Breathing:** Inhale deeply into low belly, exhale immediately as a soft sigh (no breath-holding).
    """)

daily_rating = st.sidebar.slider("Rate session tension relief (1-10):", 1, 10, 8)
daily_notes = st.sidebar.text_area("Practitioner Notes:")

if st.sidebar.button("Save Session Metrics"):
    log_session_to_csv(st.session_state.user_name, st.session_state.selected_protocol, daily_rating, daily_notes)
    st.sidebar.success(f"Saved log for {st.session_state.user_name} (Rating: {daily_rating}/10)")

# --- MAIN EXECUTION FLOW ---
st.subheader(f"Execution: {st.session_state.selected_protocol}")

if st.session_state.selected_protocol == "Advanced Lower Pelvic & Abdominal Flush Protocol":
    st.info("⚠️ **Protocol Rules Reminder:** Keep total execution time between 5 and 7 minutes. Drink 300 to 500 mL of water upon completion.")
else:
    st.info("⚠️ **Performance Rules Reminder:** Maintain continuous breathing throughout. Never hold your breath. Stay strictly off bone flares.")

current_idx = st.session_state.current_step_index

if current_idx < len(protocol_steps):
    step_info = protocol_steps[current_idx]

    st.markdown(f"### {step_info['step']}")

    if st.session_state.selected_protocol == "Advanced Lower Pelvic & Abdominal Flush Protocol":
        st.markdown(
            '<div class="pressure-warning">⚠️ TECHNIQUE REMINDER: Use a <b>medium-low vibration setting</b> and <b>do NOT press hard</b>. Allow device weight to handle tissue resonance.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="pressure-warning">⚠️ 90-SECOND RULE & BREATHING: Maintain uninterrupted contact. Inhale into low belly, exhale as a soft sigh without pausing.</div>',
            unsafe_allow_html=True
        )

    img_path = step_info["image_file"]
    if os.path.exists(img_path):
        img = Image.open(img_path)
        st.image(img, use_container_width=True, caption=f"Visual Guide: {step_info['step']}")
    else:
        st.warning(f"⚠️ Image file `{img_path}` pending upload in repository root.")

    st.markdown(f"""
        <div class="metric-container">
            <b>📍 Target Depth / Zone:</b> {step_info['distance']}<br>
            <b>🗺️ Precise Location:</b> {step_info['where']}<br>
            <b>⚡ Execution Action:</b> {step_info['action']}<br>
            <b>🎯 Physiological Goal:</b> {step_info['goal']}
        </div>
    """, unsafe_allow_html=True)

    total_duration_secs = step_info['duration']
    st.markdown(f"**Target Duration:** {total_duration_secs} seconds ({total_duration_secs // 60} minutes)")

    if st.button("Start Step Timer & Monitor", type="primary"):
        placeholder = st.empty()
        progress_bar = st.progress(0)
        breath_placeholder = st.empty()
        benefit_placeholder = st.empty()

        total_time = step_info["duration"]
        half_time = total_time // 2

        for remaining in range(total_time, -1, -1):
            mins, secs = divmod(remaining, 60)
            time_display = f"{mins:02d}:{secs:02d}"
            placeholder.markdown(f"### ⏱️ Time Remaining: **{time_display}**")
            progress_bar.progress(1.0 - (remaining / total_time))

            elapsed = total_time - remaining

            if st.session_state.selected_protocol == "Advanced Lower Pelvic & Abdominal Flush Protocol":
                breath_cycle = elapsed % 10
                if breath_cycle < 4:
                    breath_placeholder.markdown('<div class="breath-box">🌬️ Inhale Deeply (Into Lower Pelvis)... (4s)</div>', unsafe_allow_html=True)
                else:
                    breath_placeholder.markdown('<div class="breath-box">😌 Exhale Slowly & Release Tension... (6s)</div>', unsafe_allow_html=True)
            else:
                breath_cycle = elapsed % 8
                if breath_cycle < 4:
                    breath_placeholder.markdown('<div class="breath-box">🌬️ Deep belly inhale...</div>', unsafe_allow_html=True)
                else:
                    breath_placeholder.markdown('<div class="breath-box">😌 Soft relaxed sigh exhale...</div>', unsafe_allow_html=True)

            if "benefit_text" in step_info:
                benefit_placeholder.info(step_info["benefit_text"])

            if total_time > 60 and elapsed == half_time:
                st.toast("🔄 Switch sides! Move device to the opposite limb/side.", icon="👉")

            time.sleep(1)

        placeholder.markdown("### ✅ Step Complete!")
        breath_placeholder.empty()
        st.balloons()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Previous Step"):
                st.session_state.current_step_index -= 1
                scroll_to_top()
                st.rerun()
    with col2:
        if current_idx < len(protocol_steps) - 1:
            if st.button("Next Step ➡️", type="primary"):
                st.session_state.current_step_index += 1
                scroll_to_top()
                st.rerun()
        else:
            if st.button("🏁 Complete Protocol", type="primary"):
                st.session_state.current_step_index += 1
                scroll_to_top()
                st.rerun()
else:
    st.markdown("---")
    st.success(f"🏆 **Protocol Completed Successfully!** Great work completing the {st.session_state.selected_protocol}.")
    
    if st.button("Restart Session"):
        st.session_state.current_step_index = 0
        scroll_to_top()
        st.rerun()
