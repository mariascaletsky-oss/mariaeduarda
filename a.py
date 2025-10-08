import streamlit as st

st.sidebar.title("📚 Aulas")
case_option = st.sidebar.selectbox(
    "Escolha uma disciplina:",
    ("AED", "DI", "OEDF", "PMA", "PROG", "SJ", "TGDC")
)

autor = st.sidebar.checkbox("Mostrar nome do autor", value=True)
ano de publicação = st.sidebar.checkbox("Mostrar ano de publicação", value=True)
show_emoji = st.sidebar.checkbox("Mostrar emoji com base no humor")

st.title("📝 Formatação de Nome")

aula = st.text_input("Digite número da aula:")

if nome:
    if case_option == "AED":
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
