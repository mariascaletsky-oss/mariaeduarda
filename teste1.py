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

# Dicionário com famosos e fotos
famosos = {
    "Áries ♈": ("Lady Gaga", "https://upload.wikimedia.org/wikipedia/commons/5/5f/Lady_Gaga_interview_2021.jpg"),
    "Touro ♉": ("Dwayne 'The Rock' Johnson", "https://upload.wikimedia.org/wikipedia/commons/f/f0/Dwayne_Johnson_2%2C_2013.jpg"),
    "Gêmeos ♊": ("Kanye West", "https://upload.wikimedia.org/wikipedia/commons/d/d2/Kanye_West_at_the_2009_Tribeca_Film_Festival_%28cropped%29.jpg"),
    "Câncer ♋": ("Selena Gomez", "https://upload.wikimedia.org/wikipedia/commons/3/34/Selena_Gomez_2021_2.jpg"),
    "Leão ♌": ("Jennifer Lopez", "https://upload.wikimedia.org/wikipedia/commons/4/4e/Jennifer_Lopez_2019_2.jpg"),
    "Virgem ♍": ("Beyoncé", "https://upload.wikimedia.org/wikipedia/commons/3/3e/Beyoncé_in_2023.jpg"),
    "Libra ♎": ("Kim Kardashian", "https://upload.wikimedia.org/wikipedia/commons/3/31/Kim_Kardashian_2019.jpg"),
    "Escorpião ♏": ("Leonardo DiCaprio", "https://upload.wikimedia.org/wikipedia/commons/2/2f/Leonardo_DiCaprio_2014.jpg"),
    "Sagitário ♐": ("Taylor Swift", "https://upload.wikimedia.org/wikipedia/commons/f/f2/Taylor_Swift_2_-_2019_by_Glenn_Francis.jpg"),
    "Capricórnio ♑": ("Michelle Obama", "https://upload.wikimedia.org/wikipedia/commons/3/32/Michelle_Obama_official_portrait_2013.jpg"),
    "Aquário ♒": ("Oprah Winfrey", "https://upload.wikimedia.org/wikipedia/commons/8/81/Oprah_in_2014.jpg"),
    "Peixes ♓": ("Rihanna", "https://upload.wikimedia.org/wikipedia/commons/9/9f/Rihanna_Fenty_2018.png")
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
