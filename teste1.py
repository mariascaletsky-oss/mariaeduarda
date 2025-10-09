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

cores_signo = {
    "Áries ♈": "#FF4500",
    "Touro ♉": "#228B22",
    "Gêmeos ♊": "#FFD700",
    "Câncer ♋": "#1E90FF",
    "Leão ♌": "#FFA500",
    "Virgem ♍": "#32CD32",
    "Libra ♎": "#FF69B4",
    "Escorpião ♏": "#8B0000",
    "Sagitário ♐": "#FF8C00",
    "Capricórnio ♑": "#2F4F4F",
    "Aquário ♒": "#00CED1",
    "Peixes ♓": "#9370DB"
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
else:
    st.markdown("""
        <style>
        .stApp {background-color: #fff0f5;}
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
        cor_texto = cores_signo.get(signo, "#800080") if tema == "Colorido ✨" else "#000000"
        
        st.markdown(
            f"<h3 style='color:{cor_texto}'>Olá <b>{nome_title}</b>, seu aniversário é no dia <b>{dia} de {mes_nome}</b>, então você é de <b>{signo}</b>.</h3>",
            unsafe_allow_html=True
        )
        if tema == "Colorido ✨":
            st.write(f"A cor associada ao seu signo é: **{cor_texto}**")
        
        conselho = st.radio("Gostaria de um conselho?", ("Não", "Sim"))
        if conselho == "Sim":
            st.success(frase)

        famoso = st.radio("Gostaria de saber um famoso do seu signo?", ("Não", "Sim"))
        if famoso == "Sim":
            nome_famoso = famosos.get(signo, "Desconhecido")
            st.info(f"Um famoso de {signo} é **{nome_famoso}** 🌟")
    else:
        st.error("Data inválida. Verifique o dia e o mês informados.")
