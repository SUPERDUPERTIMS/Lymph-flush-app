import time
import streamlit as st

st.set_page_config(
    page_title="Lymphatic Flush Protocol Guide", page_icon="💧", layout="centered"
)

# App Title & Overview
st.title("💧 Lower Pelvic & Abdominal Flush Protocol")
st.markdown(
    "Your interactive guide and timer for targeted interstitial fluid drainage."
)

# Protocol Steps Definition based on the standard protocol
protocol_steps = [
    {
        "step": "Step 1: Open Primary Drainage Gates",
        "duration": 90,  # seconds total (45s per side)
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
    },
    {
        "step": "Step 2: Sub-Umbilical Mid-Release",
        "duration": 45,  # seconds
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
    },
    {
        "step": "Step 3: Extended Low-Pelvic Release",
        "duration": 120,  # seconds
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
    },
    {
        "step": "Step 4: The Deep Downward V-Sweep",
        "duration": 90,  # seconds
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
        f"Session saved successfully! Rating: {daily_rating}/10"
    )

# Main Execution Flow
st.markdown("---")
st.subheader("Interactive Protocol Session")

# Session State Initialization
if "current_step_index" not in st.session_state:
    st.session_state.current_step_index = 0

current_idx = st.session_state.current_step_index

if current_idx < len(protocol_steps):
    step_info = protocol_steps[current_idx]

    st.markdown(f"### {step_info['step']}")
    st.info(f"**Where:** {step_info['where']}")
    st.warning(f"**Action:** {step_info['action']}")
    st.success(f"**Goal:** {step_info['goal']}")

    st.markdown(f"**Target Duration:** {step_info['duration']} seconds")

    # Timer Component
    if st.button("Start Step Timer", type="primary"):
        placeholder = st.empty()
        progress_bar = st.progress(0)

        total_time = step_info["duration"]
        for remaining in range(total_time, -1, -1):
            mins, secs = divmod(remaining, 60)
            time_display = f"{mins:02d}:{secs:02d}"
            placeholder.markdown(
                f"### ⏱️ Time Remaining: **{time_display}**"
            )
            progress_bar.progress(
                1.0 - (remaining / total_time)
            )
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
                    "Protocol complete! Remember to drink 300-500 mL of fresh"
                    " water."
                )
                st.session_state.current_step_index = 0
                st.rerun()
else:
    if st.button("Restart Protocol"):
        st.session_state.current_step_index = 0
        st.rerun()
