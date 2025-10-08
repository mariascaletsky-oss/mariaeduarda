import streamlit as st

def main():
    st.title("Transformador de Nome")
    st.write("Digite seu nome para ver diferentes transformações do texto.")

    nome = st.text_input("Digite seu nome:")

    if nome:
        st.write("Nome em minúsculas:", nome.lower())
        st.write("Nome em maiúsculas:", nome.upper())
        st.write("Nome capitalizado:", nome.capitalize())
        st.write(f"Tamanho do nome: {len(nome)} caracteres")

        if len(nome) < 3:
            st.warning("Nome muito curto! Por favor, digite pelo menos 3 caracteres.")

    if st.button("Limpar"):
        # Para limpar o input, usamos a função experimental set_value
        st.experimental_rerun()

if __name__ == "__main__":
    main()
