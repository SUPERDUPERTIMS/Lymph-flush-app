from datetime import datetime
import os
import time
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

# Page configuration with mobile viewport optimization
st.set_page_config(
    page_title="KineticPulse: Mobile Performance Suite",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Professional Mobile-First Custom Styling (Based on 1000173890_2.jpg)
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
        border-radius: 50px !important; /* Pill shape */
        font-weight: 700;
        font-size: 1.1rem;
        padding: 14px 20px;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"] {
        background-color: #0c38ff !important; /* Bright Royal Blue */
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

    /* Curved Orange Header Simulation */
    .curved-header {
        background-color: #ff9800; /* Warm Orange */
        margin: -4rem -2rem 2rem -2rem; /* Pulling header to the edges */
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

    /* Clean White Cards (Pill style lists) */
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


# Initialize Session State Flow Control
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

# --- PAGE 1: NAME, NOTES & SAFETY CHECKS ---
if st.session_state.app_page == 1:
    # Custom Curved Header
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
    # Custom Curved Header
    st.markdown(f"""
        <div class="curved-header">
            <h1>Choose Protocol</h1>
            <p>Welcome back, {st.session_state.user_name}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center; color: #333; margin-bottom: 20px;'>What's on your mind?</h3>", unsafe_allow_html=True)

    # Lymph Flush 1st, Hip Flexor 2nd
    protocol_options = [
        "Advanced Lower Pelvic & Abdominal Flush Protocol",
        "Advanced Hip & Pelvic Performance Protocol (Karate & Kicking)"
    ]
    
    preview_images = {
        protocol_options[0]: "step1.png",
        protocol_options[1]: "hip_master_guide.png"
    }

    st.markdown('<div class="selection-box">', unsafe_allow_html=True)
    chosen_option = st.radio(
        "Select training focus:",
        protocol_options,
        index=0 if st.session_state.selected_protocol == protocol_options[0] else 1,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    selected_img_path = preview_images[chosen_option]
    
    # Display preview card
    st.markdown('<div class="protocol-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        if os.path.exists(selected_img_path):
            st.image(selected_img_path, width=110)
        else:
            st.markdown("🍊 **[Preview]**")
    with col2:
        st.markdown(f"**Selected Focus:**\n\n{chosen_option}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Conditionally show details based on selection
    if chosen_option == "Advanced Lower Pelvic & Abdominal Flush Protocol":
        st.markdown("""
            <div class="metric-container">
                <b>🎯 Why it should be done:</b><br>
                To target interstitial fluid drainage, break up stagnant water retention and lower-belly puffiness, and release deep pelvic and abdominal fascial tension.<br><br>
                <b>⏱️ How often:</b><br>
                2 to 3 times per week, keeping total execution time between 5 and 7 minutes per session.<br><br>
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

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("Back", type="secondary"):
            st.session_state.app_page = 1
            scroll_to_top()
            st.rerun()
    with col_next:
        if st.button("Continue", type="primary"):
            st.session_state.selected_protocol = chosen_option
            st.session_state.current_step_index = 0
            st.session_state.app_page = 3
            scroll_to_top()
            st.rerun()

# --- PAGE 3: STEP-BY-STEP INTERACTIVE GUIDE ---
elif st.session_state.app_page == 3:
    lymph_steps = [
        {
            "step": "Step 1: Open Primary Drainage Gates",
            "duration": 90,
            "image_file": "step1.png",
            "distance": "12 cm - 15 cm below navel",
            "where": "Groin creases where legs meet torso, 1 cm to 2 cm inward toward pubic crease.",
            "action": "Hold device stationary with a light touch for 45-60s on left side, then 45-60s on right side.",
            "goal": "Unlocks primary superficial inguinal lymph nodes for fluid exit clearance.",
            "benefit_text": "💡 Primary drainage gates are unlocking for unobstructed clearance.",
        },
        {
            "step": "Step 2: Sub-Umbilical Mid-Release",
            "duration": 45,
            "image_file": "step2.png",
            "distance": "3 cm - 10 cm below navel",
            "where": "Sub-umbilical zone directly below navel across a 10 cm wide band.",
            "action": "Angle device 45° downward. Perform steady downward glides (2 cm/sec) from 3 cm down to 10 cm.",
            "goal": "Pre-clears mid-level fascial tightness and breaks up water retention.",
            "benefit_text": "💡 Mid-level fascial tension is releasing.",
        },
        {
            "step": "Step 3: Extended Low-Pelvic Release",
            "duration": 120,
            "image_file": "step3.png",
            "distance": "14 cm - 15 cm below navel",
            "where": "Low-pelvic zone directly over central pubic border.",
            "action": "Execute slow movement over 120 seconds, holding for 5 seconds at the lowest point.",
            "goal": "Mobilizes fluid pooled at the lowest base of the belly.",
            "benefit_text": "💡 Actively mobilizing fluid pooled at the base.",
        },
        {
            "step": "Step 4: The Deep Downward V-Sweep",
            "duration": 90,
            "image_file": "step4.png",
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

    if st.session_state.selected_protocol == "Advanced Lower Pelvic & Abdominal Flush Protocol":
        protocol_steps = lymph_steps
    else:
        protocol_steps = hip_steps

    st.markdown(f"""
        <div class="curved-header">
            <h1>Routine Session</h1>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Change Protocol", type="secondary"):
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
            st.warning(f"⚠️ Image file `{img_path}` not found in folder.")

        st.markdown(f"""
            <div class="metric-container">
                <b>📍 Target Depth:</b> {step_info['distance']}<br>
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
