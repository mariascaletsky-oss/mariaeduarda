import streamlit as st

st.title("Transformador de Nome e Signo")

# Campo para nome
nome = st.text_input("Digite seu nome:")

# Campo para aniversário (dia e mês)
dia = st.number_input("Dia do nascimento:", min_value=1, max_value=31, step=1)
mes = st.number_input("Mês do nascimento:", min_value=1, max_value=12, step=1)

# Função para calcular signo
def calcula_signo(dia, mes):
    if (mes == 3 and dia >= 21) or (mes == 4 and dia <= 20):
        return "Áries ♈"
    elif (mes == 4 and dia >= 21) or (mes == 5 and dia <= 20):
        return "Touro ♉"
    elif (mes == 5 and dia >= 21) or (mes == 6 and dia <= 20):
        return "Gêmeos ♊"
    elif (mes == 6 and dia >= 21) or (mes == 7 and dia <= 22):
        return "Câncer ♋"
    elif (mes == 7 and dia >= 23) or (mes == 8 and dia <= 22):
        return "Leão ♌"
    elif (mes == 8 and dia >= 23) or (mes == 9 and dia <= 22):
        return "Virgem ♍"
    elif (mes == 9 and dia >= 23) or (mes == 10 and dia <= 22):
        return "Libra ♎"
    elif (mes == 10 and dia >= 23) or (mes == 11 and dia <= 21):
        return "Escorpião ♏"
    elif (mes == 11 and dia >= 22) or (mes == 12 and dia <= 21):
        return "Sagitário ♐"
    elif (mes == 12 and dia >= 22) or (mes == 1 and dia <= 19):
        return "Capricórnio ♑"
    elif (mes == 1 and dia >= 20) or (mes == 2 and dia <= 18):
        return "Aquário ♒"
    elif (mes == 2 and dia >= 19) or (mes == 3 and dia <= 20):
        return "Peixes ♓"
    else:
        return "Data inválida"

if nome:
    st.write("Minúsculas:", nome.lower())
    st.write("Maiúsculas:", nome.upper())
    st.write("Capitalizado:", nome.capitalize())
    st.write(f"Número de letras: {len(nome)}")

if dia and mes:
    signo = calcula_signo(dia, mes)
    st.write(f"Seu signo é: {signo}")
