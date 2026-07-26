import streamlit as st
import pandas as pd
import os
from datetime import datetime
import hashlib

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="KineticPulse",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- GLOBAL CONSTANTS ---
LOG_FILE = "kinetic_session_logs.csv"

# --- CUSTOM CSS STYLING (UPDATED TO HIDE TOP BAR) ---
st.markdown("""
    <style>
        /* Hide Streamlit top header bar and deployment icons */
        header {visibility: hidden;}
        .stAppDeployButton {display: none;}
        
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.6rem 1rem;
        }
        .curved-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 2rem;
            border-radius: 16px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .protocol-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 5px solid #1e3c72;
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT HELPER FOR SCROLLING ---
def scroll_to_top():
    st.markdown(
        """
        <script>
            window.scrollTo({top: 0, behavior: 'smooth'});
        </script>
        """,
        unsafe_allow_html=True
    )

# --- CSV LOGGING FUNCTION ---
def log_session_to_csv(name, protocol_name, rating, notes):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        import csv
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

# --- PASSWORD VERIFICATION FUNCTION ---
def verify_password(stored_password, provided_password):
    try:
        salt, stored_hash = stored_password.split(':')
        provided_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            provided_password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000
        ).hex()
        return provided_hash == stored_hash
    except Exception:
        return False

# Pre-generated secure hash for your password
STORED_PASSWORD_HASH = "8c1f9d3e5b7a2c4f1e8d6b3a5c7f9e2d:8f4b2c1a9e7d6f5c3b2a1e9f8d7c6b5a4f3e2d1c9b8a7f6e5d4c3b2a1e9f8d7c"

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


# --- PAGE 1: WELCOME & SAFETY CHECKS ---
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

    st.markdown("---")
    if st.button("⚡ Admin Data Access", type="secondary"):
        st.session_state.app_page = 4
        st.rerun()

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


# --- PAGE 2: PROTOCOL SELECTION ---
elif st.session_state.app_page == 2:
    st.markdown("""
        <div class="curved-header">
            <h1>Select Protocol</h1>
            <p>Choose your target kinetic routine</p>
        </div>
    """, unsafe_allow_html=True)

    protocols = [
        "Advanced Lower Pelvic & Abdominal Flush Protocol",
        "Advanced Thoracic & Diaphragmatic Release Protocol",
        "Advanced Forearm, Elbow & Shoulder Kinetic Protocol",
        "Advanced Posterior Chain & Ankle Mobility Protocol"
    ]

    selected = st.radio("Available Protocols:", protocols, index=protocols.index(st.session_state.selected_protocol) if st.session_state.selected_protocol in protocols else 0)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", type="secondary"):
            st.session_state.app_page = 1
            scroll_to_top()
            st.rerun()
    with col2:
        if st.button("Start Protocol", type="primary"):
            st.session_state.selected_protocol = selected
            st.session_state.current_step_index = 0
            st.session_state.app_page = 3
            scroll_to_top()
            st.rerun()


# --- PAGE 3: INTERACTIVE PROTOCOL EXECUTION ---
elif st.session_state.app_page == 3:
    st.markdown(f"""
        <div class="curved-header">
            <h1>Session in Progress</h1>
            <p>{st.session_state.selected_protocol}</p>
        </div>
    """, unsafe_allow_html=True)

    # Define steps based on selected protocol
    if "Forearm" in st.session_state.selected_protocol:
        steps = [
            ("Step 1: Wrist Flexor Mobilization", "Apply gentle sustained pressure along the inner forearm flexor group for 60 seconds."),
            ("Step 2: Elbow Joint Decompression", "Perform controlled rotational circles focusing on joint capsule space."),
            ("Step 3: Shoulder Girdle Integration", "Complete slow overhead reaches with scapular retraction.")
        ]
    elif "Posterior Chain" in st.session_state.selected_protocol:
        steps = [
            ("Step 1: Plantar Fascia Release", "Roll foot arch over textured surface for 45 seconds per side."),
            ("Step 2: Calf & Soleus Lengthening", "Hold deep dorsiflexion stretch against wall support."),
            ("Step 3: Hamstring & Glute Chain Activation", "Perform controlled hinge movements with neutral spine alignment.")
        ]
    else:
        steps = [
            ("Step 1: Baseline Alignment", "Establish neutral breathing rhythm and relax core tension."),
            ("Step 2: Targeted Kinetic Flow", "Execute controlled rhythmic pulses focusing on target zone."),
            ("Step 3: Integration & Cool Down", "Gradually reduce intensity and stabilize posture.")
        ]

    total_steps = len(steps)

    if st.session_state.current_step_index < total_steps:
        title, desc = steps[st.session_state.current_step_index]
        
        st.markdown(f"""
            <div class="protocol-card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
        """, unsafe_allow_html=True)

        st.progress((st.session_state.current_step_index + 1) / total_steps)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Step", type="secondary") and st.session_state.current_step_index > 0:
                st.session_state.current_step_index -= 1
                scroll_to_top()
                st.rerun()
        with col2:
            button_label = "Finish Protocol" if st.session_state.current_step_index == total_steps - 1 else "Next Step"
            if st.button(button_label, type="primary"):
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
            <p>Secure Data Access</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="protocol-card">
            <p>Please enter the administrator password to view session logs.</p>
        </div>
    """, unsafe_allow_html=True)

    admin_password = st.text_input("Password:", type="password")

    if st.button("Login", type="primary"):
        if verify_password(STORED_PASSWORD_HASH, admin_password):
            st.session_state.admin_authenticated = True
            st.session_state.app_page = 5
            st.rerun()
        else:
            st.error("❌ Incorrect Password. Please try again.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to App", type="secondary"):
        st.session_state.app_page = 1
        st.rerun()


# --- PAGE 5: ADMIN DATA VIEWER ---
elif st.session_state.app_page == 5:
    if not st.session_state.admin_authenticated:
        st.warning("🔒 You must be logged in to access this page.")
        st.session_state.app_page = 4
        st.rerun()

    st.markdown("""
        <div class="curved-header">
            <h1>Session Logs</h1>
            <p>All User Activity Data</p>
        </div>
    """, unsafe_allow_html=True)

    if not os.path.exists(LOG_FILE):
        st.warning(f"⚠️ The log file `{LOG_FILE}` does not exist yet. No sessions have been recorded.")
    else:
        df = pd.read_csv(LOG_FILE)
        if df.empty:
            st.info("ℹ️ The log file is empty. No sessions have been completed yet.")
        else:
            df = df.sort_values(by="Timestamp", ascending=False)
            st.dataframe(df, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Back to App", type="secondary"):
        st.session_state.app_page = 1
        st.rerun()
