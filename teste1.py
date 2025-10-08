import streamlit as st

st.title("Transformador de Nome")

nome = st.text_input("Digite seu nome:")

if nome:
    st.write("Minúsculas:", nome.lower())
    st.write("Maiúsculas:", nome.upper())
    st.write("Capitalizado:", nome.capitalize())
    st.write(f"Número de letras: {len(nome)}")
