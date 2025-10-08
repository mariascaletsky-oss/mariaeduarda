import streamlit as st

nome = st.text_input("digite seu nome:")
if nome:
    st.write(nome.lower())
