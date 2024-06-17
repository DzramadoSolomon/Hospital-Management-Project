import streamlit as st


def show_home_page():
    st.markdown("# Welcome to Providence Hospital")
    st.image("hospital_logo.png", use_column_width=True)
    st.markdown("<h2 style='text-align: center;'>\"Their fruit will be for food, and their leaves for healing\" - Ezekiel 47:12c</h2>", unsafe_allow_html=True)
    
    # About Section
    st.header("About Providence Hospital")
    st.write("""
    Providence Hospital is a leading healthcare institution dedicated to providing exceptional patient care, 
    advancing medical research, and educating the next generation of healthcare professionals. 
    With state-of-the-art facilities and a team of highly skilled medical experts, 
    we strive to deliver comprehensive and compassionate healthcare services to our patients.
    """)

    st.subheader("Our Mission")
    st.write("""
    Our mission is to improve the health and well-being of our community by providing high-quality, 
    patient-centered care in a compassionate and respectful environment. 
    We are committed to excellence in healthcare delivery, 
    medical education, and research, and we continuously seek ways to enhance the services we provide.
    """)

    st.subheader("Our Vision")
    st.write("""
    Our vision is to be the premier healthcare institution in the region, 
    known for our commitment to excellence, innovation, and patient satisfaction. 
    We aspire to be a leader in medical education and research, 
    shaping the future of healthcare and making a positive impact on the lives of our patients and their families.
    """)
