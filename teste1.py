import streamlit as st

# Função para calcular o signo
def calcula_signo(dia, mes):
    if (mes == 3 and dia >= 21) or (mes == 4 and dia <= 20):
        return "Áries ♈", "A coragem é meu sobrenome."
    elif (mes == 4 and dia >= 21) or (mes == 5 and dia <= 20):
        return "Touro ♉", "Aprecie as pequenas coisas."
    elif (mes == 5 and dia >= 21) or (mes == 6 and dia <= 20):
        return "Gêmeos ♊", "Comunicativo e adaptável."
    elif (mes == 6 and dia >= 21) or (mes == 7 and dia <= 22):
        return "Câncer ♋", "Lar, doce lar."
    elif (mes == 7 and dia >= 23) or (mes == 8 and dia <= 22):
        return "Leão ♌", "Brilho e confiança."
    elif (mes == 8 and dia >= 23) or (mes == 9 and dia <= 22):
        return "Virgem ♍", "Organização e eficiência."
    elif (mes == 9 and dia >= 23) or (mes == 10 and dia <= 22):
        return "Libra ♎", "Busca por harmonia."
    elif (mes == 10 and dia >= 23) or (mes == 11 and dia <= 21):
        return "Escorpião ♏", "Intensidade e paixão."
    elif (mes == 11 and dia >= 22) or (mes == 12 and dia <= 21):
        return "Sagitário ♐", "Aventura e liberdade."
    elif (mes == 12 and dia >= 22) or (mes == 1 and dia <= 19):
        return "Capricórnio ♑", "Disciplina e responsabilidade."
    elif (mes == 1 and dia >= 20) or (mes == 2 and dia <= 18):
        return "Aquário ♒", "Inovação e originalidade."
    elif (mes == 2 and dia >= 19) or (mes == 3 and dia <= 20):
        return "Peixes ♓", "Sensibilidade e empatia."
    else:
        return "Data inválida", ""

# Interface
st.title("Descubra seu Signo 🌟")

# Entradas do usuário
nome = st.text_input("Digite seu nome:")
dia = int(st.number_input("Dia do nascimento:", min_value=1, max_value=31, step=1))
mes = int(st.number_input("Mês do nascimento:", min_value=1, max_value=12, step=1))

# Exibição principal
if nome and dia > 0 and mes > 0:
    signo, frase = calcula_signo(dia, mes)
    nome_title = nome.title()  # 🔹 Primeiras letras maiúsculas
    if signo != "Data inválida":
        st.write(f"Olá **{nome_title}**, seu aniversário é no dia **{dia} do {mes}**, então você é de **{signo}**.")
        conselho = st.radio("Gostaria de um conselho?", ("Não", "Sim"))
        if conselho == "Sim":
            st.success(frase)
    else:
        st.error("Data inválida. Verifique o dia e o mês informados.")
