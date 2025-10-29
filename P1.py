# app_busca_deputado_paginas.py
# -*- coding: utf-8 -*-
"""
App Streamlit com **duas páginas** e **sidebar de opções**:
- Página 1: PESQUISA → usuário digita o nome e executa a busca
- Página 2: RESPOSTAS → lista resultados, gráficos/tabelas e exibe detalhes; possui botão "⬅ Voltar à Pesquisa"
- Sidebar (em ambas as páginas): opções de exibição (tabela compacta / link para API)

Gráficos e relatórios gerados
- Gráfico de barras por UF (nº de deputados em exercício por unidade federativa)
- Gráfico de setores (pizza) com a distribuição dos deputados por partido (usa matplotlib **se disponível**; caso contrário, mostra barras como fallback)
- Tabela interativa (nome, partido, UF, e e-mail) + download CSV
- Relatório detalhado de **despesas por deputado**, com **filtros por ano e tipo de gasto** e **exportação CSV**

Como rodar (com pizza usando matplotlib):
  pip install streamlit requests pandas matplotlib

Como rodar (sem matplotlib – o app funciona, mas a pizza vira barras):
  pip install streamlit requests pandas

  streamlit run app_busca_deputado_paginas.py
"""

import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional

# matplotlib é opcional — se não houver, fazemos fallback para barras
try:
    import matplotlib.pyplot as plt  # type: ignore
    HAS_MPL = True
except Exception:
    HAS_MPL = False

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"User-Agent": "Streamlit Busca Deputado/2.4", "Accept": "application/json"}

st.set_page_config(page_title="Buscar Deputado (2 páginas)", page_icon="🔎", layout="wide")
st.title("🔎 Busca de Deputado")
st.caption("Fonte: API de Dados Abertos da Câmara dos Deputados")

# ----------------------
# Funções de API
# ----------------------
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

@st.cache_data(ttl=600)
def get_despesas(dep_id: int, ano: Optional[int] = None) -> pd.DataFrame:
    """Busca despesas do deputado e retorna DataFrame."""
    url = f"{API_BASE}/deputados/{dep_id}/despesas"
    params = {"ordem": "DESC", "ordenarPor": "dataDocumento"}
    if ano is not None:
        params["ano"] = ano
    try:
        # paginação simples (até 50 páginas por segurança)
        dados_total: list[dict] = []
        pagina = 1
        for _ in range(50):
            params.update({"pagina": pagina, "itens": 100})
            r = requests.get(url, params=params, headers=HEADERS, timeout=30)
            r.raise_for_status()
            resp = r.json()
            dados = resp.get("dados", [])
            dados_total.extend(dados)
            links = resp.get("links", [])
            has_next = any(l.get("rel") == "next" for l in links)
            if not has_next:
                break
            pagina += 1
        return pd.DataFrame(dados_total)
    except requests.RequestException as e:
        st.error(f"Erro ao buscar despesas: {e}")
        return pd.DataFrame()

# ----------------------
# Estado global mínimo
# ----------------------
for key, default in {
    "pagina": "Pesquisa",
    "nome_query": "",
    "resultados": [],
    "dep_id": None,
    "tabela_compacta": True,
    "mostrar_link_api": True,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ----------------------
# SIDEBAR (opções persistentes)
# ----------------------
with st.sidebar:
    st.header("Opções de exibição")
    st.session_state.tabela_compacta = st.checkbox(
        "Mostrar tabela compacta", value=st.session_state.tabela_compacta
    )
    st.session_state.mostrar_link_api = st.checkbox(
        "Mostrar link para a API", value=st.session_state.mostrar_link_api
    )
    st.markdown("---")
    st.caption("Use o menu abaixo para alternar páginas.")
    pagina_sidebar = st.radio(
        "Navegação",
        options=["Pesquisa", "Respostas"],
        index=0 if st.session_state.pagina == "Pesquisa" else 1,
    )
    if pagina_sidebar != st.session_state.pagina:
        st.session_state.pagina = pagina_sidebar
        st.rerun()

# --------------------------------------------------
# PÁGINA 1 — PESQUISA
# --------------------------------------------------
if st.session_state.pagina == "Pesquisa":
    st.subheader("Pesquisa")
    with st.form("form_pesquisa"):
        nome_query = st.text_input(
            "Nome do(a) deputado(a)",
            placeholder="ex.: Maria, Silva, João…",
            help="Digite o nome completo ou parte do nome",
            value=st.session_state.nome_query,
        )
        col_btn = st.columns([1,1,6])
        with col_btn[0]:
            submitted = st.form_submit_button("Buscar")
        with col_btn[1]:
            limpar = st.form_submit_button("Limpar")

    # Ações
    if submitted and (nome_query or "").strip():
        st.session_state.nome_query = (nome_query or "").strip()
        st.session_state.resultados = search_deputados_by_name(st.session_state.nome_query)
        st.session_state.dep_id = None
        st.session_state.pagina = "Respostas"  # vai para página 2
        st.rerun()

    if 'limpar' in locals() and limpar:
        st.session_state.nome_query = ""
        st.session_state.resultados = []
        st.session_state.dep_id = None
        st.info("Campos limpos. Faça nova pesquisa.")

    st.markdown(
        "> Dica: após enviar a busca, você será levado(a) automaticamente à página **Respostas**."
    )

# --------------------------------------------------
# PÁGINA 2 — RESPOSTAS
# --------------------------------------------------
if st.session_state.pagina == "Respostas":
    # Botão seta (voltar)
    col_back, _ = st.columns([1, 9])
    with col_back:
        if st.button("⬅ Voltar à Pesquisa"):
            st.session_state.pagina = "Pesquisa"
            st.rerun()

    st.subheader("Respostas")

    resultados = st.session_state.resultados
    if not resultados:
        st.info("Nenhum resultado para exibir. Volte à página **Pesquisa** e faça uma busca.")
    else:
        # ---------------- Visualizações gerais da lista ----------------
        df_dep = pd.DataFrame(resultados)
        # Garante colunas principais
        for c in ["nome", "siglaPartido", "siglaUf", "email", "id"]:
            if c not in df_dep.columns:
                df_dep[c] = None

        # KPIs
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total de deputados encontrados", len(df_dep))
        with k2:
            st.metric("Partidos únicos", int(df_dep["siglaPartido"].nunique()))
        with k3:
            st.metric("UFs representadas", int(df_dep["siglaUf"].nunique()))

        # Tabela interativa + CSV
        st.markdown("### Tabela de parlamentares")
        st.dataframe(
            df_dep.rename(columns={
                "nome": "Nome", "siglaPartido": "Partido", "siglaUf": "UF", "email": "E-mail"
            })[["Nome", "Partido", "UF", "E-mail"]],
            use_container_width=True,
        )
        csv_dep = df_dep[["nome", "siglaPartido", "siglaUf", "email", "id"]].rename(
            columns={"nome": "Nome", "siglaPartido": "Partido", "siglaUf": "UF", "email": "E-mail", "id": "ID"}
        ).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV (deputados)", data=csv_dep, file_name="deputados.csv", mime="text/csv")

        st.markdown("### Gráficos")
        colg1, colg2 = st.columns(2)
        with colg1:
            st.markdown("**Distribuição por UF (barras)**")
            contagem_uf = df_dep["siglaUf"].value_counts().sort_index()
            st.bar_chart(contagem_uf)
        with colg2:
            st.markdown("**Distribuição por Partido (pizza ou barras)**")
            dist_partido = df_dep["siglaPartido"].value_counts().sort_values(ascending=False)
            if not dist_partido.empty:
                if HAS_MPL:
                    fig, ax = plt.subplots()
                    ax.pie(dist_partido.values, labels=dist_partido.index, autopct="%1.1f%")
                    ax.axis("equal")
                    st.pyplot(fig, clear_figure=True)
                else:
                    st.info("matplotlib não encontrado — exibindo barras como fallback.")
                    st.bar_chart(dist_partido)
            else:
                st.write("Sem dados de partido para exibir.")

        st.markdown("---")
        st.markdown("### Detalhes e despesas do parlamentar")

        # Seleção do resultado
        opcoes = {
            f"{d['nome']} — {d.get('siglaPartido','?')}/{d.get('siglaUf','?')} (ID {d['id']})": d['id']
            for d in resultados
        }
        escolha_rotulo = st.selectbox(
            "Selecione o(a) deputado(a)",
            options=list(opcoes.keys()),
            index=0,
        )
        dep_id = opcoes.get(escolha_rotulo)
        st.session_state.dep_id = dep_id

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

            col1, col2 = st.columns([1, 2], vertical_alignment="top")
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

            # Extras em tabela
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
            if st.session_state.get("tabela_compacta", True):
                st.table({"Campo": list(info_tabela.keys()), "Valor": list(info_tabela.values())})
            else:
                st.json(info_tabela)

            # ---------------- Relatório de despesas ----------------
            st.markdown("#### Despesas do deputado")
            ano_atual = datetime.now().year
            ano = st.selectbox(
                "Ano",
                options=list(range(2015, ano_atual + 1))[::-1],
                index=0,
            )
            df_desp = get_despesas(dep_id, ano=ano)

            if df_desp.empty:
                st.info("Nenhuma despesa encontrada para os filtros selecionados.")
            else:
                # Normaliza colunas chave
                cols_keep = [
                    "ano","mes","dataDocumento","descricaoTipoDespesa","tipoDespesa","nomeFornecedor",
                    "cnpjCpfFornecedor","valorDocumento","valorLiquido","urlDocumento"
                ]
                for c in cols_keep:
                    if c not in df_desp.columns:
                        df_desp[c] = None

                # Filtro por tipo (usando descricaoTipoDespesa)
                tipos = sorted(df_desp["descricaoTipoDespesa"].dropna().unique().tolist())
                tipo_escolhido = st.selectbox("Tipo de despesa (opcional)", options=[""] + tipos, index=0)
                if tipo_escolhido:
                    df_desp = df_desp[df_desp["descricaoTipoDespesa"].fillna("") == tipo_escolhido]

                # Ordena por data e mostra
                df_desp["dataDocumento"] = pd.to_datetime(df_desp["dataDocumento"], errors="coerce")
                df_view = df_desp[cols_keep].sort_values("dataDocumento", ascending=False).copy()

                # KPIs
                total_liq = pd.to_numeric(df_view["valorLiquido"], errors="coerce").fillna(0).sum()
                total_doc = pd.to_numeric(df_view["valorDocumento"], errors="coerce").fillna(0).sum()
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Total (valor líquido)", f"R$ {total_liq:,.2f}".replace(",","X").replace(".",",").replace("X","."))
                with c2:
                    st.metric("Total (valor documento)", f"R$ {total_doc:,.2f}".replace(",","X").replace(".",",").replace("X","."))

                st.dataframe(df_view, use_container_width=True)

                # CSV
                csv_desp = df_view.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Baixar CSV (despesas)", data=csv_desp, file_name=f"despesas_{dep_id}_{ano}.csv", mime="text/csv"
                )

            # Link para API
            if st.session_state.get("mostrar_link_api", True):
                st.markdown(f"Ver na API: [deputados/{dep_id}]({API_BASE}/deputados/{dep_id})")

# Rodapé
st.markdown("\n—\n*App didático. Confira detalhes e metadados na API oficial.*")
