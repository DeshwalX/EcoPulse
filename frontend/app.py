import requests
import streamlit as st

st.set_page_config(
    page_title="EcoPulse Plant Curation System", page_icon="🌿", layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"

if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None

if st.session_state.user_id is None:
    st.markdown(
        "<h2 style='text-align: center;'>🌿 EcoPulse Enterprise Dashboard</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: gray;'>Multi-Role Inference & Data Curation Framework</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form", clear_on_submit=True):
            st.subheader("System Authentication")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Access System")

            if submit:
                if not username or not password:
                    st.error("Please enter both credentials.")
                else:
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/api/login",
                            data={"username": username, "password": password},
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.user_id = data["user_id"]
                            st.session_state.username = data["username"]
                            st.session_state.role = data["role"]
                            st.success(f"Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error(
                                "Invalid credentials. Try client_demo / password123"
                            )
                    except requests.exceptions.ConnectionError:
                        st.error(
                            "Backend server offline. Ensure FastAPI is running on port 8000."
                        )

else:
    st.sidebar.markdown(f"### Welcome, **{st.session_state.username}**")
    st.sidebar.info(f"💼 Role Tier: **{st.session_state.role}**")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

    if st.session_state.role == "Client":
        from views.client import show_client_view

        show_client_view(BACKEND_URL, st.session_state.user_id)

    elif st.session_state.role == "Botanist":
        from views.botanist import show_botanist_view

        show_botanist_view(BACKEND_URL)

    elif st.session_state.role == "Admin":
        from views.admin import show_admin_view

        show_admin_view(BACKEND_URL)