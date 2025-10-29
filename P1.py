# app.py
# -*- coding: utf-8 -*-
"""
Painel interativo (Streamlit) para explorar dados de deputados federais em exercício
usando a API de Dados Abertos da Câmara dos Deputados.

Funcionalidades:
- Filtros por nome, partido (sigla), UF e legislatura
- Tabela interativa com nome, partido, UF e e-mail
- Gráfico de barras por UF (contagem de deputados)
- Gráfico de pizza por partido (distribuição)
- Relatório detalhado de despesas por deputado, com filtros por ano e por tipo de gasto
- Exportação CSV

Como rodar:
1) Instale dependências:  
   pip install streamlit requests pandas matplotlib
2) Execute:  
   streamlit run app.py
"""

import io
import math
import time
import json
import typing as t
from datetime import datetime

import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"User-Agent": "Streamlit Deputados/1.0", "Accept": "application/json"}

# ----------------------------
# Utilidades de requisição
# ----------------------------

def _get(url: str, params: dict | None = None) -> dict:
    """Faz GET simples com tratamento de erros e retorno JSON.
    Lida com erros de rede e HTTP. Retorna dicionário JSON.
    """
    try:
        r = requests.get(url, params=params or {}, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        st.error(f"Erro HTTP ao acessar {url}: {e}")
        return {"dados": [], "links": []}
    except requests.RequestException as e:
        st.error(f"Erro de rede ao acessar {url}: {e}")
        return {"dados": [], "links": []}


def _paginate(url: str, params: dict | None = None, max_pages: int | None = None) -> list[dict]:
    """Percorre paginação do serviço ('links' com rel='next') e acumula 'dados'."""
    collected: list[dict] = []
    page = int(params.get("pagina", 1) if params else 1)
    params = {**(params or {}), "itens": 100, "pagina": page}
    pages_read = 0

    while True:
        resp = _get(url, params)
        dados = resp.get("dados", []) or []
        collected.extend(dados)
        pages_read += 1

        # Verifica link 'next'
        links = resp.get("links", [])
        next_link = next((l for l in links if l.get("rel") == "next"), None)
        if next_link and (max_pages is None or pages_read < max_pages):
            params["pagina"] = params.get("pagina", 1) + 1
            # pequenas pausas para não sobrecarregar API
            time.sleep(0.15)
            continue
        break

    return collected


# ----------------------------
# Endpoints de dados
# ----------------------------

@st.cache_data(ttl=3600)
def listar_partidos_siglas() -> list[str]:
    url = f"{API_BASE}/partidos"
    dados = _paginate(url, {"ordem": "ASC", "ordenarPor": "sigla"})
    siglas = [d.get("sigla") for d in dados if d.get("sigla")]
    return sorted(set(siglas))


@st.cache_data(ttl=3600)
def listar_legislaturas() -> pd.DataFrame:
    """Retorna DF com legislaturas (id, dataInicio, dataFim)."""
    url = f"{API_BASE}/legislaturas"
    dados = _paginate(url, {"ordem": "DESC", "ordenarPor": "id"})
    if not dados:
        return pd.DataFrame(columns=["id", "dataInicio", "dataFim"])
    return pd.DataFrame(dados)


@st.cache_data(ttl=900)
def buscar_deputados(nome: str | None, partido: str | None, uf: str | None, legislatura: int | None) -> pd.DataFrame:
    params = {"ordem": "ASC", "ordenarPor": "nome"}
    if nome:
        params["nome"] = nome
    if partido:
        params["siglaPartido"] = partido
    if uf:
        params["siglaUf"] = uf
    if legislatura:
        params["idLegislatura"] = legislatura

    url = f"{API_BASE}/deputados"
    dados = _paginate(url, params)

    if not dados:
        return pd.DataFrame(columns=["id", "nome", "siglaPartido", "siglaUf", "email"])

    # Campos principais já vêm em 'dados'. Campos de e-mail podem estar em 'uri' detalhada; 
    # mas frequentemente já vem 'email'. Manteremos o que a API fornece.
    df = pd.DataFrame(dados)
    # Normaliza colunas importantes
    keep = ["id", "nome", "siglaPartido", "siglaUf", "email"]
    for c in keep:
        if c not in df.columns:
            df[c] = None
    return df[keep]


@st.cache_data(ttl=900)
def detalhes_deputado(deputado_id: int) -> dict:
    url = f"{API_BASE}/deputados/{deputado_id}"
    resp = _get(url)
    return (resp.get("dados") or {})


@st.cache_data(ttl=600)
def despesas_deputado(
    deputado_id: int,
    ano: int | None = None,
    tipo_despesa: str | None = None,
) -> pd.DataFrame:
    """Busca despesas do deputado. 'tipo_despesa' aqui é filtrado pela descrição presente nos dados.
    A API aceita 'tipoDespesa' (código), mas vamos filtrar client-side pela coluna 'tipoDespesa'/'descricaoTipoDespesa'.
    """
    url = f"{API_BASE}/deputados/{deputado_id}/despesas"
    params = {"ordem": "DESC", "ordenarPor": "dataDocumento"}
    if ano:
        params["ano"] = ano

    dados = _paginate(url, params, max_pages=50)  # limite defensivo
    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados)

    # Algumas chaves comuns: 'ano', 'mes', 'tipoDespesa', 'descricaoTipoDespesa', 'nomeFornecedor', 'cnpjCpfFornecedor',
    # 'valorDocumento', 'valorLiquido', 'urlDocumento', 'dataDocumento'
    if tipo_despesa and "descricaoTipoDespesa" in df.columns:
        df = df[df["descricaoTipoDespesa"].fillna("").str.contains(tipo_despesa, case=False, na=False)]

    return df


# ----------------------------
# UI
# ----------------------------

st.set_page_config(page_title="Painel de Deputados (Câmara)", page_icon="🏛️", layout="wide")
st.title("🏛️ Painel de Deputados – Câmara dos Deputados (Dados Abertos)")
st.caption("Dados oficiais: API de Dados Abertos da Câmara dos Deputados • Atualização em tempo real das consultas")

with st.sidebar:
    st.header("Filtros")
    nome = st.text_input("Nome do deputado(a)")

    # Siglas de partidos a partir do endpoint /partidos
    try:
        partidos = [""] + listar_partidos_siglas()
    except Exception:
        partidos = [""]
    partido = st.selectbox("Partido (sigla)", options=partidos, index=0)
    partido = partido or None

    # Lista de UFs fixas
    UFS = [
        "", "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
        "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO",
    ]
    uf = st.selectbox("Unidade Federativa (UF)", options=UFS, index=0)
    uf = uf or None

    # Legislaturas disponíveis
    try:
        df_leg = listar_legislaturas()
        ids_leg = [""] + [int(x) for x in df_leg.get("id", [])]
    except Exception:
        ids_leg = [""]
    leg_raw = st.selectbox("Legislatura (id)", options=ids_leg, index=0)
    legislatura = int(leg_raw) if str(leg_raw).strip().isdigit() else None

    st.markdown("---")
    st.caption("Selecione filtros e clique em **Buscar**.")
    buscar = st.button("🔎 Buscar deputados")

if buscar:
    df_dep = buscar_deputados(nome, partido, uf, legislatura)
else:
    # Busca inicial sem filtros pesados (exibe todos em exercício)
    df_dep = buscar_deputados(None, None, None, legislatura)

st.subheader("Resultados")
if df_dep.empty:
    st.info("Nenhum deputado encontrado para os filtros selecionados.")
else:
    # KPIs básicos
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de deputados encontrados", len(df_dep))
    with col2:
        st.metric("Partidos únicos", df_dep["siglaPartido"].nunique())
    with col3:
        st.metric("UFs representadas", df_dep["siglaUf"].nunique())

    # Tabela
    st.dataframe(
        df_dep.rename(columns={
            "nome": "Nome",
            "siglaPartido": "Partido",
            "siglaUf": "UF",
            "email": "E-mail",
        }),
        use_container_width=True,
    )

    # Exportação CSV dos resultados de deputados
    csv_dep = df_dep.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar CSV (deputados)", data=csv_dep, file_name="deputados.csv", mime="text/csv")

    # Gráficos
    st.markdown("---")
    st.subheader("Visualizações")
    colg1, colg2 = st.columns(2)

    with colg1:
        st.markdown("**Distribuição por UF (barras)**")
        contagem_uf = df_dep["siglaUf"].value_counts().sort_index()
        st.bar_chart(contagem_uf)

    with colg2:
        st.markdown("**Distribuição por Partido (pizza)**")
        dist_partido = df_dep["siglaPartido"].value_counts().sort_values(ascending=False)
        if not dist_partido.empty:
            fig, ax = plt.subplots()
            ax.pie(dist_partido.values, labels=dist_partido.index, autopct="%1.1f%%")
            ax.axis("equal")
            st.pyplot(fig, clear_figure=True)
        else:
            st.write("Sem dados de partido para exibir.")

    # ----------------------------
    # Seção: Despesas por deputado
    # ----------------------------
    st.markdown("---")
    st.subheader("Relatório de despesas por deputado")

    # Seleciona um deputado
    opcoes_deps = [f"{row.nome} (ID {row.id}) - {row.siglaPartido}/{row.siglaUf}" for _, row in df_dep.iterrows()]
    if opcoes_deps:
        escolha = st.selectbox("Escolha o deputado(a)", options=[""] + opcoes_deps, index=0)
        if escolha:
            # Extrai ID
            try:
                dep_id = int(escolha.split("ID ")[1].split(")")[0])
            except Exception:
                dep_id = None

            if dep_id:
                # Mostrar cartão com dados básicos
                info = detalhes_deputado(dep_id)
                nome_dep = info.get("ultimoStatus", {}).get("nome") or info.get("nomeCivil")
                email_dep = info.get("ultimoStatus", {}).get("gabinete", {}).get("email") or info.get("email")
                partido_dep = info.get("ultimoStatus", {}).get("siglaPartido")
                uf_dep = info.get("ultimoStatus", {}).get("siglaUf")

                with st.container(border=True):
                    st.markdown(f"**{nome_dep or '—'}**  ")
                    st.write(f"Partido/UF: {partido_dep or '—'}/{uf_dep or '—'}")
                    if email_dep:
                        st.write(f"E-mail: {email_dep}")

                # Filtros de despesas
                ano_atual = datetime.now().year
                ano = st.selectbox(
                    "Ano das despesas",
                    options=list(range(2015, ano_atual + 1))[::-1],
                    index=0,
                )

                # Primeiro busca despesas do ano, depois lista tipos para filtrar
                df_desp = despesas_deputado(dep_id, ano=ano)
                tipos_disp = sorted(df_desp.get("descricaoTipoDespesa", pd.Series(dtype=str)).dropna().unique().tolist()) if not df_desp.empty else []
                tipo_escolhido = st.selectbox("Filtrar por tipo de despesa (opcional)", options=[""] + tipos_disp, index=0)
                tipo_use = tipo_escolhido or None

                if tipo_use:
                    df_desp = despesas_deputado(dep_id, ano=ano, tipo_despesa=tipo_use)

                if df_desp.empty:
                    st.info("Nenhuma despesa encontrada para os filtros selecionados.")
                else:
                    # Colunas amigáveis
                    cols_keep = [
                        "ano","mes","dataDocumento","descricaoTipoDespesa","nomeFornecedor","cnpjCpfFornecedor",
                        "valorDocumento","valorLiquido","urlDocumento",
                    ]
                    for c in cols_keep:
                        if c not in df_desp.columns:
                            df_desp[c] = None
                    df_view = df_desp[cols_keep].copy()

                    # Ordena por data
                    if "dataDocumento" in df_view.columns:
                        df_view["dataDocumento"] = pd.to_datetime(df_view["dataDocumento"], errors="coerce")
                        df_view = df_view.sort_values("dataDocumento", ascending=False)

                    # KPIs de despesas
                    total_liq = pd.to_numeric(df_view["valorLiquido"], errors="coerce").fillna(0).sum()
                    total_doc = pd.to_numeric(df_view["valorDocumento"], errors="coerce").fillna(0).sum()

                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Total (valor líquido)", f"R$ {total_liq:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    with c2:
                        st.metric("Total (valor documento)", f"R$ {total_doc:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                    st.dataframe(df_view, use_container_width=True)

                    # Export CSV despesas
                    csv_desp = df_view.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Baixar CSV (despesas)", data=csv_desp, file_name=f"despesas_{dep_id}_{ano}.csv", mime="text/csv"
                    )
            else:
                st.warning("Não foi possível identificar o ID do deputado selecionado.")
    else:
        st.info("Carregue resultados de deputados para selecionar e ver despesas.")

st.markdown("\n\n—\n*Aplicação educacional. Verifique detalhes e metadados diretamente na API oficial quando necessário.*")
