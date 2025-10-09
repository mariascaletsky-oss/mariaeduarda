import streamlit as st

# ---------- FUNÇÕES ----------
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

# ---------- DADOS ----------
famosos = {
    "Áries ♈": "Lady Gaga",
    "Touro ♉": "Dwayne 'The Rock' Johnson",
    "Gêmeos ♊": "Kanye West",
    "Câncer ♋": "Selena Gomez",
    "Leão ♌": "Jennifer Lopez",
    "Virgem ♍": "Beyoncé",
    "Libra ♎": "Kim Kardashian",
    "Escorpião ♏": "Leonardo DiCaprio",
    "Sagitário ♐": "Taylor Swift",
    "Capricórnio ♑": "Michelle Obama",
    "Aquário ♒": "Oprah Winfrey",
    "Peixes ♓": "Rihanna"
}

meses = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

# Cores por signo
cores_signo = {
    "Áries ♈": "#FF4500",       # laranja vermelho
    "Touro ♉": "#228B22",       # verde floresta
    "Gêmeos ♊": "#FFD700",      # amarelo ouro
    "Câncer ♋": "#1E90FF",      # azul dodger
    "Leão ♌": "#FFA500",        # laranja
    "Virgem ♍": "#32CD32",      # verde limão
    "Libra ♎": "#FF69B4",       # rosa forte
    "Escorpião ♏": "#8B0000",   # vermelho escuro
    "Sagitário ♐": "#FF8C00",   # laranja escuro
    "Capricórnio ♑": "#2F4F4F", # cinza escuro
    "Aquário ♒": "#00CED1",     # azul turquesa
    "Peixes ♓": "#9370DB"       # roxo médio
}

# ---------- SIDEBAR ----------
st.sidebar.title("🎨 Tema do App")
tema = st.sidebar.selectbox("Escolha o tema:", ["Claro 🌞", "Colorido ✨"])

# ---------- CSS POR TEMA ----------
if tema == "Claro 🌞":
    st.markdown("""
        <style>
        .stApp {background-color: #ffffff; color: #000000;}
        .stApp * {color: #000000 !important; font-family: 'Arial', sans-serif !important;}
        </style>
    """, unsafe_allow_html=True)

else:  # Colorido
    # Para o tema colorido, a cor será definida depois do cálculo do signo
    st.markdown("""
        <style>
        .stApp {background-color: #fff0f5;}
        .stApp * {font-family: 'Comic Sans MS', cursive, sans-serif !important;}
        </style>
    """, unsafe_allow_html=True)

# ---------- INTERFACE PRINCIPAL ----------
st.title("✨ Descubra seu Signo ✨")

nome = st.text_input("Digite seu nome:")
dia = int(st.number_input("Dia do nascimento:", min_value=1, max_value=31, step=1))
mes = int(st.number_input("Mês do nascimento:", min_value=1, max_value=12, step=1))

if nome and dia > 0 and mes > 0:
    signo, frase = calcula_signo(dia, mes)
    nome_title = nome.title()
    
    if signo != "Data inválida":
        mes_nome = meses.get(mes, "mês desconhecido")
        
        # Se tema colorido, aplica cor do signo
        if tema == "Colorido ✨":
            cor_texto = cores_signo.get(signo, "#80008
