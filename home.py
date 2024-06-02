import streamlit as st

def show_home_page():
    st.markdown("# Welcome to Providence Hospital")
    st.image("hospital_logo.png", use_column_width=True)
    st.markdown("<h2 style='text-align: center;'>\"Their fruit will be for food, and their leaves for healing\" - Ezekiel 47:12c</h2>", unsafe_allow_html=True)
