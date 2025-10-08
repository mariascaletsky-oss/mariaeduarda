import streamlit as st

nome = st.input_box("digite seu nome:")
if nome:
    st.write(nome.upper())
