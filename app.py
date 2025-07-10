import streamlit as st
from auth import login, logout
from dashboard import show_dashboard

def main():
    st.set_page_config(page_title="EMS Supabase", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
    else:
        logout_button = st.sidebar.button("🚪 Logout", on_click=logout)
        show_dashboard()

if __name__ == "__main__":
    main()
