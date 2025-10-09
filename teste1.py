import streamlit as st
import time

# ---------- FUNÇÃO ----------
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

nomes_cores = {
    "Áries ♈": "Laranja Vermelho",
    "Touro ♉": "Verde Floresta",
    "Gêmeos ♊": "Amarelo Ouro",
    "Câncer ♋": "Azul Dodger",
    "Leão ♌": "Laranja",
    "Virgem ♍": "Verde Limão",
    "Libra ♎": "Rosa Forte",
    "Escorpião ♏": "Vermelho Escuro",
    "Sagitário ♐": "Laranja Escuro",
    "Capricórnio ♑": "Cinza Escuro",
    "Aquário ♒": "Turquesa",
    "Peixes ♓": "Roxo Médio"
}

# ---------- SESSION STATE ----------
if "pagina" not in st.session_state:
    st.session_state.pagina = "perguntas"
if "nome" not in st.session_state:
    st.session_state.nome = ""
if "dia" not in st.session_state:
    st.session_state.dia = 0
if "mes" not in st.session_state:
    st.session_state.mes = 0

# ---------- PAGINA 1: PERGUNTAS ----------
if st.session_state.pagina == "perguntas":
    st.title("✨ Descubra seu Signo ✨")
    st.session_state.nome = st.text_input("Digite seu nome:", st.session_state.nome)
    st.session_state.dia = st.number_input("Dia do nascimento:", min_value=1, max_value=31, step=1, value=st.session_state.dia)
    st.session_state.mes = st.number_input("Mês do nascimento:", min_value=1, max_value=12, step=1, value=st.session_state.mes)
    
    if st.button("Calcular meu signo") and st.session_state.nome and st.session_state.dia and st.session_state.mes:
        st.session_state.pagina = "carregando"

# ---------- PAGINA 2: CARREGANDO ----------
elif st.session_state.pagina == "carregando":
    st.title("🔮 Calculando seu signo...")
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)
    st.session_state.pagina = "resultado"

# ---------- PAGINA 3: RESULTADO ----------
elif st.session_state.pagina == "resultado":
    nome = st.session_state.nome.title()
    dia = st.session_state.dia
    mes = st.session_state.mes
    mes_nome = meses.get(mes, "mês desconhecido")
    
    signo, frase = calcula_signo(dia, mes)
    cor_texto = cores_signo.get(signo, "#800080")
    nome_cor = nomes_cores.get(signo, "Cor Desconhecida")
    
    st.markdown(
        f"<h3 style='color:{cor_texto}'>Olá <b>{nome}</b>, seu aniversário é no dia <b>{dia} de {mes_nome}</b>, então você é de <b>{signo}</b>.</h3>",
        unsafe_allow_html=True
    )
    st.write(f"A cor associada ao seu signo é: **{nome_cor}** ({cor_texto})")
    
    conselho = st.radio("Gostaria de um conselho?", ("Não", "Sim"))
    if conselho == "Sim":
        st.success(frase)

    famoso = st.radio("Gostaria de saber um famoso do seu signo?", ("Não", "Sim"))
    if famoso == "Sim":
        nome_famoso = famosos.get(signo, "Desconhecido")
        st.info(f"Um famoso de {signo} é **{nome_famoso}** 🌟")
    
    if st.button("Voltar para perguntas"):
        st.session_state.pagina = "perguntas"
