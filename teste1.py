import streamlit as st
import random

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

# Interface do usuário
st.title("Transformador de Nome e Signo")

# Inputs principais
nome = st.text_input("Digite seu nome:")
dia = st.number_input("Dia do nascimento:", min_value=1, max_value=31, step=1)
mes = st.number_input("Mês do nascimento:", min_value=1, max_value=12, step=1)

# Opções na barra lateral
opcao = st.sidebar.selectbox(
    "O que você gostaria de ver?",
    ("Transformações do nome", "Número de letras", "Signo", "Perguntas Verdadeiro ou Falso")
)

# Exibição com base na seleção
if opcao == "Transformações do nome" and nome:
    st.write("Minúsculas:", nome.lower())
    st.write("Maiúsculas:", nome.upper())
    st.write("Capitalizado:", nome.capitalize())

if opcao == "Número de letras" and nome:
    st.write(f"Número de letras: {len(nome)}")

if opcao == "Signo" and dia and mes:
    signo, frase = calcula_signo(dia, mes)
    st.write(f"Seu signo é: {signo}")
    st.write(f"Frase do signo: {frase}")

if opcao == "Perguntas Verdadeiro ou Falso":
    perguntas = [
        ("Seu nome contém a letra 'a'.", 'a' in nome.lower()),
        ("Seu signo é Áries.", calcula_signo(dia, mes)[0] == "Áries ♈")
    ]
