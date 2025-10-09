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

# Famosos americanos (sem imagem)
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

# Tradução dos meses
meses = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

# ---------- SIDEBAR INTERATIVA ----------
st.sidebar.title("🔮 Menu Zodiacal")
st.sidebar.markdown("Escolha uma opção divertida para explorar seu signo:")

# Tema do app
tema = st.sidebar.selectbox("Escolha o tema do app:", ["🌞 Claro", "🌙 Escuro", "✨ Colorido"])
if tema == "🌞 Claro":
    st.sidebar.success("Você escolheu o tema claro! ☀️")
elif tema == "🌙 Escuro":
    st.sidebar.info("Você escolheu o tema escuro! 🌙")
else:
    st.sidebar.warning("Você escolheu o tema colorido! 🌈")

# Curiosidades rápidas
curiosidade = st.sidebar.checkbox("Mostrar curiosidade do signo")
if curiosidade:
    st.sidebar.write("💫 Dica: Cada signo tem características únicas! Explore para descobrir mais.")

# Atalhos
st.sidebar.markdown("---")
st.sidebar.markdown("Atalhos rápidos:")
st.sidebar.button("Transformações do nome")
st.sidebar.button("Número de letras")

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
        st.write(f"Olá **{nome_title}**, seu aniversário é no dia **{dia} de {mes_nome}**, então você é de **{signo}**.")
        
        conselho = st.radio("Gostaria de um conselho?", ("Não", "Sim"))
        if conselho == "Sim":
            st.success(frase)

        famoso = st.radio("Gostaria de saber um famoso do seu signo?", ("Não", "Sim"))
        if famoso == "Sim":
            nome_famoso = famosos.get(signo, "Desconhecido")
            st.info(f"Um famoso de {signo} é **{nome_famoso}** 🌟")

        # Nova pergunta
        nova_pergunta = st.radio("Quer responder uma última pergunta divertida?", ("Não", "Sim"))
        if nova_pergunta == "Sim":
            st.write("👉 Aqui você pode adicionar o que quiser depois!")
    else:
        st.error("Data inválida. Verifique o dia e o mês informados.")
