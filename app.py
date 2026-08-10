import streamlit as st

# Page Configuration MUST be the first Streamlit command called
st.set_page_config(
    page_title="Kinetic Pulse",
    page_icon="⚡",
    layout="centered"
)


def render_safety_gate():
    """
    Renders a legally fortified safety gate. 
    Halts app execution until all waivers are explicitly checked.
    """
    if st.session_state.get("disclaimer_accepted", False):
        return True

    st.title("⚡ Kinetic Pulse")
    st.warning("⚠️ SAFETY, MEDICAL & LEGAL NOTICE")

    st.markdown("""
    ### 1. Medical Contraindications
    * **Avoid use** if you have active hernias, recent surgical procedures, cardiovascular issues, acute joint injuries, or are pregnant.
    * Consult a licensed physician or physical therapist prior to starting any physical routine.

    ### 2. Software & AI Output Disclaimer
    * **Kinetic Pulse** was developed with AI assistance and is designed purely for general informational and tracking purposes.
    * This software does **not** provide medical advice, diagnosis, physical therapy, or individualized clinical recommendations.

    ### 3. Assumption of Risk & Release of Liability
    * Physical exercise carries inherent risks of serious injury. By proceeding, you **voluntarily assume all risk** of physical harm, illness, or injury resulting from your use of this application.
    * You hereby release, waive, and hold harmless the developer(s) and owners from any liabilities, claims, or financial losses arising out of application usage or exercise execution.
    """)

    st.markdown("---")
    st.subheader("Required Confirmations")

    # Gating Checkboxes
    cb1 = st.checkbox(
        "I confirm I have no active contraindications (hernias, recent surgery, pregnancy, acute injuries)."
    )
    cb2 = st.checkbox(
        "I acknowledge this app is AI-assisted and agree to consult a medical specialist before acting on suggestions."
    )
    cb3 = st.checkbox(
        "I confirm I am 18 years of age or older."
    )
    cb4 = st.checkbox(
        "I agree to the Release of Liability and voluntarily assume all physical and technical risks associated with app use."
    )

    all_accepted = cb1 and cb2 and cb3 and cb4

    st.write("")
    if st.button("Enter Kinetic Pulse", disabled=not all_accepted, type="primary", use_container_width=True):
        st.session_state["disclaimer_accepted"] = True
        st.rerun()

    return False


# --- HARD UI EXECUTION GATE ---
if not render_safety_gate():
    st.stop()  # Completely halts execution of main app logic until gate passes


# --- SIDEBAR LEGAL REFERENCE ---
with st.sidebar:
    st.markdown("### ⚡ Kinetic Pulse")
    st.caption("Legal & Safety Status: **Verified**")
    if st.button("Review Safety & Legal Terms", use_container_width=True):
        st.session_state["disclaimer_accepted"] = False
        st.rerun()
    st.markdown("---")


# ==============================================================================
# YOUR KINETIC PULSE APP CODE STARTS BELOW
# ==============================================================================

st.title("⚡ Kinetic Pulse")

# --- Support Section ---
with st.container():
    st.markdown("### Support KineticPulse ☕")
    st.caption("If you found this App useful, consider supporting its continued development.")
    st.link_button("☕ Buy Me a Coffee / Support on Ko-fi", "https://ko-fi.com")

st.markdown("---")

# --- PASTE YOUR REMAINING KINETIC PULSE LOGIC / PROTOCOLS / TIMERS HERE ---
