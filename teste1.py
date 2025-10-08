import streamlit as st
import random

st.title("Transformador de Nome com Emoji")

nome = st.text_input("Digite seu nome:")

emojis = ["😀", "😎", "🤖", "🐱", "🌟", "🔥", "🎉", "🍕", "🚀", "💡"]

if nome:
    emoji = random.choice(emojis)
    st.write(f"{emoji} Minúsculas:", nome.lower())
    st.write(f"{emoji} Maiúsculas:", nome.upper())
    st.write(f"{emoji} Capitalizado:", nome.capitalize())
    st.write(f"{emoji} Número de letras: {len(nome)}")
