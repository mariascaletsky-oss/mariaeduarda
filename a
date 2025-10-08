import streamlit as st

# Sidebar for options
st.sidebar.title("🔧 Configurações")
case_option = st.sidebar.selectbox(
    "Escolha o formato do nome:",
    ("Minúsculas", "Maiúsculas", "Título")
)

show_greeting = st.sidebar.checkbox("Mostrar saudação personalizada", value=True)
show_length = st.sidebar.checkbox("Mostrar número de caracteres", value=True)
show_emoji = st.sidebar.checkbox("Mostrar emoji com base no humor")

# Main interface
st.title("📝 Formatação de Nome")

nome = st.text_input("Digite seu nome:")

if nome:
    # Formata o nome de acordo com a escolha do usuário
    if case_option == "Minúsculas":
        nome_formatado = nome.lower()
    elif case_option == "Maiúsculas":
        nome_formatado = nome.upper()
    else:
        nome_formatado = nome.title()

    st.write(f"**Nome formatado:** {nome_formatado}")

    if show_greeting:
        st.success(f"Olá, {nome_formatado}! 👋 Seja bem-vindo(a).")

    if show_length:
        st.info(f"O nome digitado tem **{len(nome)}** caracteres.")

    if show_emoji:
        humor = st.radio("Como você está se sentindo hoje?", ("😀 Feliz", "😐 Normal", "😢 Triste"))
        st.write(f"Você escolheu: {humor}")
