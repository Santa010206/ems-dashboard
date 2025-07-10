import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ Use fallback default for testing if not found
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials are missing. Please check your .env or set the variables.")
    st.stop()

# ✅ Create Supabase client safely
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Failed to create Supabase client: {e}")
    st.stop()


def login():
    st.title("🔐 EMS Login ")

    tab1, tab2 = st.tabs(["🔑 Login", "🆕 Register"])

    # --- Login tab ---
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user"] = res.user
                st.session_state["logged_in"] = True
                st.success(f"✅ Logged in as {res.user.email}")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Login failed: {e}")

    # --- Register tab ---
    with tab2:
        new_email = st.text_input("New Email", key="reg_email")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")

        if st.button("Register"):
            if new_pass != confirm_pass:
                st.error("Passwords do not match.")
            elif not new_email or not new_pass:
                st.error("Please fill in all fields.")
            else:
                try:
                    supabase.auth.sign_up({"email": new_email, "password": new_pass})
                    st.success("✅ Registration successful! Please check your email and log in.")
                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")


def logout():
    st.session_state.clear()
    st.success("✅ Logged out.")
    st.experimental_rerun()
