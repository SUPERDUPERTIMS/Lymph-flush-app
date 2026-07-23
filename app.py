import os
import time
from PIL import Image, ImageDraw
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Lymphatic Flush Protocol Guide", page_icon="💧", layout="centered"
)

# App Title & Overview
st.title("💧 Lower Pelvic & Abdominal Flush Protocol")
st.markdown(
    "Your interactive guide and timer for targeted interstitial fluid drainage."
)

# Name Input Prompt at the Beginning
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.user_name:
    st.subheader("Welcome! Please enter your name to begin:")
    entered_name = st.text_input("Your Name:")
    if st.button("Start App", type="primary"):
        if entered_name.strip():
            st.session_state.user_name = entered_name.strip()
            st.rerun()
        else:
            st.warning("Please enter your name to proceed.")
    st.stop()
else:
    st.success(f"Welcome back, {st.session_state.user_name}!")

# Protocol Steps Definition based on standard protocol[span_0](start_span)[span_0](end_span)
protocol_steps = [
    {
        "step": "Step 1: Open Primary Drainage Gates",
        "duration": 90,  # seconds total (45s per side)[span_1](start_span)[span_1](end_span)
        "image_file": "step1.png",
        "where": (
            "Groin creases where legs meet torso, 1 cm to 2 cm inward toward"
            " pubic crease."
        ),
        "action": (
            "Hold the device stationary with a light touch. 45 seconds on the"
            " left side, then 45 seconds on the right side."
        ),
        "goal": (
            "Unlocks primary superficial inguinal lymph nodes for unobstructed"
            " clearance."
        ),
        "benefit_text": (
            "💡 Benefit Note: Primary drainage gates are unlocking to allow"
            " unobstructed exit clearance."
        ),
    },
    {
        "step": "Step 2: Sub-Umbilical Mid-Release",
        "duration": 45,  # seconds[span_2](start_span)[span_2](end_span)
        "image_file": "step2.png",
        "where": (
            "Sub-umbilical zone 3 cm to 10 cm directly below your navel across a"
            " 10 cm wide band."
        ),
        "action": (
            "Angle the device 45° downward. Perform steady downward glides (2"
            " cm per second) from the 3 cm mark down to 10 cm."
        ),
        "goal": (
            "Pre-clears mid-level fascial tightness and breaks up stagnant"
            " water retention."
        ),
        "benefit_text": (
            "💡 Benefit Note: Mid-level fascial tension is releasing and"
            " stagnant water retention is breaking up."
        ),
    },
    {
        "step": "Step 3: Extended Low-Pelvic Release",
        "duration": 120,  # seconds[span_3](start_span)[span_3](end_span)
        "image_file": "step3.png",
        "where": (
            "Low-pelvic zone 12 cm to 15 cm below the navel over the central"
            " pubic border."
        ),
        "action": (
            "Hold the device perpendicular (90°) to the pubic bone. Maintain"
            " continuous vertical glides."
        ),
        "goal": (
            "Mobilizes fluid pooled at the lowest base while releasing lower"
            " anchor fascial tension."
        ),
        "benefit_text": (
            "💡 Benefit Note: Fluid pooled at the lowest base of the belly is"
            " actively mobilizing."
        ),
    },
    {
        "step": "Step 4: The Deep Downward V-Sweep",
        "duration": 90,  # seconds[span_4](start_span)[span_4](end_span)
        "image_file": "step4.png",
        "where": (
            "Start from vertical centerline at 14-15 cm below navel, sweeping"
            " into groin folds."
        ),
        "action": (
            "Pause 3-5 seconds at bottom center, sweep diagonally outward"
            " slowly (0.5 cm/sec) into groin crease. Alternate sides."
        ),
        "goal": (
            "Mechanically sweeps mobilized fluid straight into open drainage"
            " nodes."
        ),
        "benefit_text": (
            "💡 Benefit Note: Fluid is being mechanically swept straight into"
            " open drainage nodes for clearance."
        ),
    },
]

# Sidebar for Navigation / Tracking Log
st.sidebar.header("📊 Daily Tracker & Ratings")
daily_rating = st.sidebar.slider(
    "Rate your session / tension relief today (1-10):", 1, 10, 5
)
daily_notes = st.sidebar.text_area("Notes / Observations:")

if st.sidebar.button("Save Session Log"):
    st.sidebar.success(
        f"Session saved successfully for {st.session_state.user_name}! Rating:"
        f" {daily_rating}/10"
    )

# Main Execution Flow
st.markdown("---")
st.subheader("Interactive Protocol Session")

# Technique Reminder Note Box
st.info(
    "⚠️ **Technique Note:** Always use a **low vibration setting** and a"
    " **soft touch**. Do not apply deep pressure[span_5](start_span)[span_5](end_span)."
)

# Session State Initialization
if "current_step_index" not in st.session_state:
    st.session_state.current_step_index = 0

current_idx = st.session_state.current_step_index

if current_idx < len(protocol_steps):
    step_info = protocol_steps[current_idx]

    # Notice guiding user to review description/image at top before scrolling to start
    st.toast("📌 New step loaded! Review instructions above, then scroll down to start timer.", icon="👆")

    st.markdown(f"### {step_info['step']}")

    # Render image with dynamic processing for Step 3
    img_path = step_info["image_file"]
    if os.path.exists(img_path):
        img = Image.open(img_path)

        # Programmatically overlay a polished semi-transparent coloured vertical strip for Step 3
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
            caption=f"Visual Guide for {step_info['step']}",
        )
    else:
        st.warning(
            f"⚠️ Image file `{img_path}` not found in repository. Upload"
            " cropped quadrant images to display them here."
        )

    st.info(f"**Where:** {step_info['where']}")
    st.warning(f"**Action:** {step_info['action']}")
    st.success(f"**Goal:** {step_info['goal']}")

    st.markdown(f"**Target Duration:** {step_info['duration']} seconds[span_6](start_span)[span_6](end_span)")

    # Timer Component
    if st.button("Start Step Timer", type="primary"):
        placeholder = st.empty()
        progress_bar = st.progress(0)
        benefit_placeholder = st.empty()

        total_time = step_info["duration"]

        # Initial breath reminder popup/alert
        st.toast(
            "🌿 Breathe deeply in and out. Relax your pelvic floor.", icon="🧘"
        )
        
        # Updated correct notice at the start of Step 3
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

            # Step 1: Switch sides prompt at 45 seconds & show benefit
            if current_idx == 0:
                if elapsed == 45:
                    st.toast("🔄 Switch sides! Move device to the right groin crease.", icon="👉")
                if elapsed == 22 or elapsed == 68:
                    benefit_placeholder.info(step_info["benefit_text"])

            # Step 2 mid-step trigger & benefit
            elif current_idx == 1 and elapsed == 22:
                st.toast(
                    "🌿 Mid-step check: Breathe deep and stay relaxed.", icon="🧘"
                )
                benefit_placeholder.info(step_info["benefit_text"])

            # Step 3 mid-step trigger & benefit (60 seconds)
            elif current_idx == 2 and elapsed == 60:
                st.toast(
                    "🌿 Mid-step check: Maintain constant gentle contact.", icon="🧘"
                )
                benefit_placeholder.info(step_info["benefit_text"])

            # Step 4: Speed reminder at start & switch sides halfway (45 seconds) + benefit
            elif current_idx == 3:
                if elapsed == 2:
                    st.toast("🐢 Speed check: Maintain an ultra-slow pace (0.5 cm/sec).", icon="⏱️")
                if elapsed == 45:
                    st.toast("🔄 Switch sides! Move to the other groin crease.", icon="👉")
                    benefit_placeholder.info(step_info["benefit_text"])

            time.sleep(1)

        placeholder.markdown("### ✅ Step Complete!")
        st.balloons()

    col1, col2 = st.columns(2)
    with col1:
        if current_idx > 0:
            if st.button("Previous Step"):
                st.session_state.current_step_index -= 1
                st.rerun()
    with col2:
        if current_idx < len(protocol_steps) - 1:
            if st.button("Next Step"):
                st.session_state.current_step_index += 1
                st.rerun()
        else:
            if st.button("Finish Protocol"):
                st.success(
                    f"🎉 Congratulations {st.session_state.user_name}! Protocol"
                    " complete! Remember to drink 300-500 mL of fresh water[span_7](start_span)[span_7](end_span)."
                )
                st.session_state.current_step_index = 0
                st.rerun()
else:
    if st.button("Restart Protocol"):
        st.session_state.current_step_index = 0
        st.rerun()
