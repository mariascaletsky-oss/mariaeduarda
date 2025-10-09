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

# Famosos americanos com imagens (links diretos Imgur)
famosos = {
    "Áries ♈": ("Lady Gaga", "https://imgur.com/a/AsMAk0H"),
    "Touro ♉": ("Dwayne 'The Rock' Johnson", "https://i.imgur.com/UC0QGxB.jpg"),
    "Gêmeos ♊": ("Kanye West", "https://i.imgur.com/xK2xE2s.jpg"),
    "Câncer ♋": ("Selena Gomez", "https://i.imgur.com/Y5dL6Ww.jpg"),
    "Leão ♌": ("Jennifer Lopez", "https://i.imgur.com/8r9N8dB.jpg"),
    "Virgem ♍": ("Beyoncé", "https://i.imgur.com/yHNmqjC.jpg"),
    "Libra ♎": ("Kim Kardashian", "https://i.imgur.com/s8Ykt5Z.jpg"),
    "Escorpião ♏": ("Leonardo DiCaprio", "https://i.imgur.com/1yXoSxW.jpg"),
    "Sagitário ♐": ("Taylor Swift", "https://i.imgur.com/WxeK0Oa.jpg"),
    "Capricórnio ♑": ("Michelle Obama", "https://i.imgur.com/fpDqhnx.jpg"),
    "Aquário ♒": ("Oprah Winfrey", "https://i.imgur.com/YVhO0bC.jpg"),
    "Peixes ♓": ("Rihanna", "https://i.imgur.com/1O8PQXk.jpg")
}

# Interface principal
st.title("✨ Descubra seu Signo ✨")

# Entradas do usuário
nome = st.text_input("Digite seu nome:")
dia = int(st.number_input("Dia do nascimento:", min_value=1, max_value=31, step=1))
mes = int(st.number_input("Mês do nascimento:", min_value=1, max_value=12, step=1))

# Exibição principal
if nome and dia > 0 and mes > 0:
    signo, frase = calcula_signo(dia, mes)
    nome_title = nome.title()  # Primeira letra maiúscula
    
    if signo != "Data inválida":
        st.write(f"Olá **{nome_title}**, seu aniversário é no dia **{dia} do {mes}**, então você é de **{signo}**.")
        
        conselho = st.radio("Gostaria de um conselho?", ("Não", "Sim"))
        if conselho == "Sim":
            st.success(frase)

        famoso = st.radio("Gostaria de saber um famoso do seu signo?", ("Não", "Sim"))
        if famoso == "Sim":
            nome_famoso, img_url = famosos.get(signo, ("Desconhecido", ""))
            st.info(f"Um famoso de {signo} é **{nome_famoso}** 🌟")
            if img_url:
                st.image(img_url, width=300, caption=nome_famoso)
    else:
        st.error("Data inválida. Verifique o dia e o mês informados.")
