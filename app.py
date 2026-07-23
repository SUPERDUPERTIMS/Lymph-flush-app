import os
import time
from PIL import Image, ImageDraw
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Advanced Lower Pelvic & Abdominal Flush Protocol",
    page_icon="💧",
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
    </style>
""", unsafe_allow_html=True)

# App Title & Professional Header
st.title("💧 Advanced Lower Pelvic & Abdominal Flush Protocol")
st.markdown("##### *Targeted Interstitial Fluid Drainage & Deep Pelvic Wall Release*")
st.markdown("---")

# Name Input & Safety Gate Initialization
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "safety_cleared" not in st.session_state:
    st.session_state.safety_cleared = False

if not st.session_state.user_name or not st.session_state.safety_cleared:
    st.markdown("""
        <div class="protocol-card">
            <h3>Welcome to Clinical Protocol Access</h3>
            <p>Please enter your profile name and confirm your clinical clearance status to begin.</p>
        </div>
    """, unsafe_allow_html=True)
    
    entered_name = st.text_input("Your Name:")
    
    st.warning(
        "⚠️ **CONTRAINDICATIONS CHECK:** Do NOT perform if you have an active "
        "abdominal or inguinal hernia, severe acute digestive issues (e.g., acute IBD, appendicitis), "
        "recent abdominal surgery, or if you are pregnant[span_2](start_span)[span_2](end_span)."
    )
    
    agreed = st.checkbox("I confirm I have no active contraindications listed above.")
    
    if st.button("Initialize Clinical Session", type="primary"):
        if entered_name.strip() and agreed:
            st.session_state.user_name = entered_name.strip()
            st.session_state.safety_cleared = True
            st.rerun()
        else:
            st.error("Please enter your name and check the confirmation box to proceed.")
    st.stop()
else:
    st.success(f"Session Active | Practitioner: **{st.session_state.user_name}**")

# Protocol Steps Definition strictly mapped to official documentation[span_3](start_span)[span_3](end_span)
protocol_steps = [
    {
        "step": "Step 1: Open Primary Drainage Gates",
        "duration": 90,  # Total seconds (45s per side)[span_4](start_span)[span_4](end_span)
        "image_file": "step1.png",
        "distance": "12 cm - 15 cm below navel[span_5](start_span)[span_5](end_span)",
        "where": "Groin creases where legs meet torso, 1 cm to 2 cm inward toward pubic crease[span_6](start_span)[span_6](end_span).",
        "action": "Hold the device stationary with a light touch for 45 to 60 seconds on the left side, then 45 to 60 seconds on the right side[span_7](start_span)[span_7](end_span).",
        "goal": "Unlocks primary superficial inguinal lymph nodes so mobilized fluid has an unobstructed exit clearance route[span_8](start_span)[span_8](end_span).",
        "benefit_text": "💡 Benefit Note: Primary drainage gates are unlocking to allow unobstructed exit clearance[span_9](start_span)[span_9](end_span).",
    },
    {
        "step": "Step 2: Sub-Umbilical Mid-Release",
        "duration": 45,  # Seconds[span_10](start_span)[span_10](end_span)
        "image_file": "step2.png",
        "distance": "3 cm - 10 cm below navel[span_11](start_span)[span_11](end_span)",
        "where": "Sub-umbilical zone directly below your navel across a 10 cm wide band (5 cm left/right of center)[span_12](start_span)[span_12](end_span).",
        "action": "Angle the device 45° downward toward feet. Perform steady downward glides (2 cm/sec) from 3 cm down to 10 cm[span_13](start_span)[span_13](end_span).",
        "goal": "Pre-clears mid-level abdominal fascial tightness and breaks up stagnant water retention to prevent bottlenecking[span_14](start_span)[span_14](end_span).",
        "benefit_text": "💡 Benefit Note: Mid-level fascial tension is releasing and stagnant water retention is breaking up[span_15](start_span)[span_15](end_span).",
    },
    {
        "step": "Step 3: Extended Low-Pelvic Release",
        "duration": 120,  # Seconds[span_16](start_span)[span_16](end_span)
        "image_file": "step3.png",
        "distance": "12 cm - 15 cm below navel[span_17](start_span)[span_17](end_span)",
        "where": "Low-pelvic zone directly over the central pubic border / lower anchor area[span_18](start_span)[span_18](end_span).",
        "action": "Hold the device perpendicular (90°) to the pubic bone. Maintain continuous vertical glides across this central zone[span_19](start_span)[span_19](end_span).",
        "goal": "Mobilizes fluid pooled at the lowest base of the belly while completely releasing lower anchor fascial tension[span_20](start_span)[span_20](end_span).",
        "benefit_text": "💡 Benefit Note: Fluid pooled at the lowest base of mật/belly is actively mobilizing[span_21](start_span)[span_21](end_span).",
    },
    {
        "step": "Step 4: The Deep Downward V-Sweep",
        "duration": 90,  # Seconds[span_22](start_span)[span_22](end_span)
        "image_file": "step4.png",
        "distance": "14 cm - 15 cm below navel → Outer[span_23](start_span)[span_23](end_span)",
        "where": "Start from vertical centerline, extending 8 cm to 12 cm diagonally outward into deep groin fold creases[span_24](start_span)[span_24](end_span).",
        "action": "Pause at bottom centerline for 3-5 seconds. Sweep diagonally outward into left crease (0.5 cm/sec). Repeat right side[span_25](start_span)[span_25](end_span).",
        "goal": "Mechanically sweeps all mobilized fluid from the lowest central pocket straight into open drainage nodes[span_26](start_span)[span_26](end_span).",
        "benefit_text": "💡 Benefit Note: Fluid is being mechanically swept straight into open drainage nodes for clearance[span_27](start_span)[span_27](end_span).",
    },
]

# Sidebar for Professional Tracking & Setup Guide
st.sidebar.header("📊 Clinical Setup & Log")
st.sidebar.markdown("""
* **Positioning:** Lie flat, knees bent at 90°[span_28](start_span)[span_28](end_span).
* **Device Setup:** Flat-head attachment on medium-low vibration setting[span_29](start_span)[span_29](end_span).
* **Breathing:** Maintain slow, deep belly breaths into the lower pelvis[span_30](start_span)[span_30](end_span).
""")

daily_rating = st.sidebar.slider("Rate session tension relief (1-10):", 1, 10, 7)
daily_notes = st.sidebar.text_area("Practitioner Notes:")

if st.sidebar.button("Save Session Metrics"):
    st.sidebar.success(f"Saved log for {st.session_state.user_name} (Rating: {daily_rating}/10)")

# Main Execution Flow
st.subheader("Clinical Protocol Session Execution")

# Technique Reminder Note Box
st.info(
    "⚠️ **Protocol Rules Reminder:** Keep total execution time between 5 and 7 minutes[span_31](start_span)[span_31](end_span). "
    "Drink 300 to 500 mL of fresh water immediately upon completion[span_32](start_span)[span_32](end_span)."
)

# Session State Initialization
if "current_step_index" not in st.session_state:
    st.session_state.current_step_index = 0

current_idx = st.session_state.current_step_index

if current_idx < len(protocol_steps):
    step_info = protocol_steps[current_idx]

    # Persistent prominent notice guiding user to review instructions at top before starting timer
    st.toast("📌 Step loaded! Review specifications and layout below, then scroll down to execute.", icon="👆")

    st.markdown(f"### {step_info['step']}")

    # Render image with dynamic processing for Step 3
    img_path = step_info["image_file"]
    if os.path.exists(img_path):
        img = Image.open(img_path)

        # Programmatically overlay a polished semi-transparent colored vertical strip for Step 3
        if current_idx == 2:
            width, height = img.size
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            strip_left = int(width * 0.42)
            strip_right = int(width * 0.58)
            strip_top = int(height * 0.20)
            strip_bottom = int(height * 0.85)
            draw.rectangle(
                [strip_left, strip_top, strip_right, strip_bottom],
                fill=(46, 139, 87, 160),
            )
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert(
                "RGB"
            )

        st.image(
            img,
            use_container_width=True,
            caption=f"Visual Guide: {step_info['step']}",
        )
    else:
        st.warning(f"⚠️ Image file `{img_path}` pending upload in repository root.")

    # Structured Protocol Metadata Card Display
    st.markdown(f"""
        <div class="metric-container">
            <b>📍 Target Depth / Zone:</b> {step_info['distance']}<br>
            <b>🗺️ Precise Location:</b> {step_info['where']}<br>
            <b>⚡ Execution Action:</b> {step_info['action']}<br>
            <b>🎯 Physiological Goal:</b> {step_info['goal']}
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Target Duration:** {step_info['duration']} seconds[span_33](start_span)[span_33](end_span)")

    # Timer Component with Expanded Visibility Pop-ups
    if st.button("Start Step Timer & Monitor", type="primary"):
        placeholder = st.empty()
        progress_bar = st.progress(0)
        benefit_placeholder = st.empty()

        total_time = step_info["duration"]

        # Initial breath reminder popup/alert
        st.toast("🌿 Breathe deeply in and out. Relax your pelvic floor[span_34](start_span)[span_34](end_span).", icon="🧘")
        
        # Step 3 Specific Instruction Prompt
        if current_idx == 2:
            st.toast("⚠️ Do not lift, maintain massage gun contact for full duration to ensure drainage.", icon="✊")

        for remaining in range(total_time, -1, -1):
            mins, secs = divmod(remaining, 60)
            time_display = f"{mins:02d}:{secs:02d}"
            placeholder.markdown(
                f"### ⏱️ Time Remaining: **{time_display}**"
            )
            progress_bar.progress(1.0 - (remaining / total_time))

            elapsed = total_time - remaining

            # Timing triggers & benefit popups
            if current_idx == 0:
                if elapsed == 45:
                    st.toast("🔄 Switch sides! Move device to the right groin crease.", icon="👉")
                if elapsed == 22 or elapsed == 68:
                    benefit_placeholder.info(step_info["benefit_text"])

            elif current_idx == 1:
                if elapsed == 22:
                    st.toast("🌿 Mid-step check: Breathe deep and stay relaxed.", icon="🧘")
                    benefit_placeholder.info(step_info["benefit_text"])

            elif current_idx == 2:
                if elapsed == 60:
                    st.toast("🌿 Mid-step check: Maintain constant gentle contact.", icon="🧘")
                    benefit_placeholder.info(step_info["benefit_text"])

            elif current_idx == 3:
                if elapsed == 2:
                    st.toast("🐢 Speed check: Maintain an ultra-slow pace (0.5 cm/sec)[span_35](start_span)[span_35](end_span).", icon="⏱️")
                if elapsed == 45:
                    st.toast("🔄 Switch sides! Move to the other groin crease[span_36](start_span)[span_36](end_span).", icon="👉")
                    benefit_placeholder.info(step_info["benefit_text"])

            time.sleep(1)

        placeholder.markdown("### ✅ Step Complete!")
        st.balloons()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Previous Step"):
                st.session_state.current_step_index -= 1
                st.rerun()
    with col2:
        if current_idx < len(protocol_steps) - 1:
            if st.button("Next Step ➡️", type="primary"):
                st.session_state.current_step_index += 1
                st.rerun()
        else:
            if st.button("🏁 Complete Protocol", type="primary"):
                st.success(
                    f"🎉 Congratulations {st.session_state.user_name}! Protocol complete! "
                    "Remember to drink 300-500 mL of fresh water[span_37](start_span)[span_37](end_span)."
                )
                st.session_state.current_step_index = 0
                st.rerun()
else:
    if st.button("Restart Protocol"):
        st.session_state.current_step_index = 0
        st.rerun()
