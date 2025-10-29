# app_busca_deputado.py
# -*- coding: utf-8 -*-
"""
App simples em Streamlit:
- Usuário digita o NOME do(a) deputado(a)
- App busca na API da Câmara (/deputados) e lista correspondências
- Usuário escolhe um resultado e o app mostra partido, UF, situação e outros dados relevantes

Como rodar:
  pip install streamlit requests
  streamlit run app_busca_deputado.py
"""

import requests
import streamlit as st

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"User-Agent": "Streamlit Busca Deputado/1.0", "Accept": "application/json"}

st.set_page_config(page_title="Buscar Deputado por Nome", page_icon="🔎", layout="centered")
st.title("🔎 Buscar deputado(a) por nome – Câmara dos Deputados")
st.caption("Fonte: API de Dados Abertos da Câmara dos Deputados")

@st.cache_data(ttl=1200)
def search_deputados_by_name(nome: str):
    params = {"nome": nome, "ordem": "ASC", "ordenarPor": "nome", "itens": 100}
    try:
        r = requests.get(f"{API_BASE}/deputados", params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json().get("dados", [])
        return data
    except requests.RequestException as e:
        st.error(f"Erro ao buscar deputados: {e}")
        return []

@st.cache_data(ttl=1800)
def get_deputado_details(dep_id: int):
    try:
        r = requests.get(f"{API_BASE}/deputados/{dep_id}", headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json().get("dados", {})
    except requests.RequestException as e:
        st.error(f"Erro ao buscar detalhes do deputado: {e}")
        return {}

with st.form("form_busca"):
    nome_query = st.text_input("Digite o nome (completo ou parte)", placeholder="ex.: Maria, Silva, João…")
    submitted = st.form_submit_button("Buscar")

if submitted and nome_query.strip():
    resultados = search_deputados_by_name(nome_query.strip())
    if not resultados:
        st.warning("Nenhum resultado encontrado. Tente variar maiúsculas/minúsculas ou parte do nome.")
    else:
        st.success(f"{len(resultados)} resultado(s) encontrado(s)")
        # Para nomes muito comuns, oferecemos uma seleção
        opcoes = {f"{d['nome']} — {d.get('siglaPartido','?')}/{d.get('siglaUf','?')} (ID {d['id']})": d['id'] for d in resultados}
        escolha_rotulo = st.selectbox("Selecione o(a) deputado(a)", options=list(opcoes.keys()))
        dep_id = opcoes.get(escolha_rotulo)

        if dep_id:
            detalhes = get_deputado_details(dep_id)
            ultimo = detalhes.get("ultimoStatus", {})
            gabinete = ultimo.get("gabinete", {})

            # Campos principais
            nome_eleitoral = ultimo.get("nomeEleitoral")
            nome_civil = detalhes.get("nomeCivil")
            sigla_partido = ultimo.get("siglaPartido")
            sigla_uf = ultimo.get("siglaUf")
            situacao = ultimo.get("situacao")
            condicao = ultimo.get("condicaoEleitoral")
            url_foto = ultimo.get("urlFoto")
            email = gabinete.get("email") or detalhes.get("email")
            telefone = gabinete.get("telefone")
            predio = gabinete.get("predio")
            sala = gabinete.get("sala")
            andar = gabinete.get("andar")
            nome_gab = gabinete.get("nome")

            st.markdown("---")
            col1, col2 = st.columns([1,2])
            with col1:
                if url_foto:
                    st.image(url_foto, caption=nome_eleitoral or nome_civil, use_container_width=True)
                else:
                    st.write("Sem foto disponível")
            with col2:
                st.subheader(nome_eleitoral or nome_civil or "Deputado(a)")
                st.write(f"**Partido/UF:** {sigla_partido or '—'}/{sigla_uf or '—'}")
                st.write(f"**Situação no cargo:** {situacao or '—'}")
                st.write(f"**Condição eleitoral:** {condicao or '—'}")
                st.write(f"**E-mail do gabinete:** {email or '—'}")
                st.write(
                    f"**Gabinete:** {nome_gab or '—'} • Prédio {predio or '—'}, sala {sala or '—'}, andar {andar or '—'}"
                )
                st.write(f"**Telefone:** {telefone or '—'}")

            # Extras úteis do objeto principal
            st.markdown("#### Outras informações")
            info_tabela = {
                "ID": dep_id,
                "Nome civil": nome_civil,
                "Nome eleitoral": nome_eleitoral,
                "Partido": sigla_partido,
                "UF": sigla_uf,
                "Situação": situacao,
                "Condição eleitoral": condicao,
            }
            st.table({"Campo": list(info_tabela.keys()), "Valor": list(info_tabela.values())})

            # Link para dados na API (útil para inspeção)
            st.markdown(
                f"Ver na API: [deputados/{dep_id}]({API_BASE}/deputados/{dep_id})"
            )
else:
    st.info("Digite um nome e clique em **Buscar** para começar.")

st.markdown("\n—\n*App didático. Confira detalhes e metadados na API oficial.*")
