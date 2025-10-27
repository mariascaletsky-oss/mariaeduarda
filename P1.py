# =============================
# Projeto: Painel dos Deputados — Câmara dos Deputados
# Stack: Python 3.10+, Streamlit, Requests, Pandas, Plotly
# Arquivos:
#   streamlit_app.py
#   utils/api_client.py
#   utils/data_processing.py
#   requirements.txt (opcional)
# =============================

# =============================
# file: utils/api_client.py
# =============================
import time
from typing import Dict, List, Optional
import requests
import pandas as pd

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"User-Agent": "FGV-P2-Streamlit/1.0 (contato@exemplo.com)"}

class CamaraAPIError(Exception):
    pass


def _get(url: str, params: Optional[Dict] = None) -> Dict:
    """Requisição GET com retry simples e tratamento básico de erro."""
    tries = 0
    while True:
        tries += 1
        r = requests.get(url, params=params or {}, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.json()
        if tries >= 3:
            raise CamaraAPIError(f"Erro {r.status_code} ao acessar {url} — {r.text[:200]}")
        time.sleep(1.2)


# -----------------------------
# DEPUTADOS
# -----------------------------

def list_deputados(
    nome: Optional[str] = None,
    sigla_uf: Optional[str] = None,
    sigla_partido: Optional[str] = None,
    id_legislatura: Optional[int] = None,
    itens_por_pagina: int = 100,
    limite_paginas: int = 5,
) -> pd.DataFrame:
    """Lista deputados em exercício, com filtros opcionais."""
    frames: List[pd.DataFrame] = []
    pagina = 1
    while pagina <= limite_paginas:
        params = {
            "pagina": pagina,
            "itens": itens_por_pagina,
            "ordenarPor": "nome",
            "ordem": "ASC",
        }
        if nome:
            params["nome"] = nome
        if sigla_uf:
            params["siglaUf"] = sigla_uf
        if sigla_partido:
            params["siglaPartido"] = sigla_partido
        if id_legislatura:
            params["idLegislatura"] = id_legislatura
        url = f"{BASE_URL}/deputados"
        payload = _get(url, params=params)
        dados = payload.get("dados", [])
        if not dados:
            break
        df = pd.json_normalize(dados)
        frames.append(df)
        pagina += 1
    if not frames:
        return pd.DataFrame()
    df_all = pd.concat(frames, ignore_index=True)
    # Campos comuns esperados: id, nome, siglaPartido, siglaUf, email, uri
    keep = [c for c in ["id","nome","siglaPartido","siglaUf","email","uri"] if c in df_all.columns]
    return df_all[keep].copy()


def get_deputado_detail(deputado_id: int) -> pd.DataFrame:
    """Detalhes do deputado (dados cadastrais)."""
    url = f"{BASE_URL}/deputados/{deputado_id}"
    payload = _get(url)
    dados = payload.get("dados", {})
    return pd.json_normalize(dados)


def get_despesas(
    deputado_id: int,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    itens_por_pagina: int = 100,
    limite_paginas: int = 12,
) -> pd.DataFrame:
    """Despesas do deputado (CEAP). Paginado por padrão."""
    frames: List[pd.DataFrame] = []
    pagina = 1
    while pagina <= limite_paginas:
        params = {"pagina": pagina, "itens": itens_por_pagina}
        if ano:
            params["ano"] = int(ano)
        if mes:
            params["mes"] = int(mes)
        url = f"{BASE_URL}/deputados/{deputado_id}/despesas"
        payload = _get(url, params=params)
        dados = payload.get("dados", [])
        if not dados:
            break
        df = pd.json_normalize(dados)
        frames.append(df)
        pagina += 1
    if not frames:
        return pd.DataFrame()
    df_all = pd.concat(frames, ignore_index=True)
    # Normalização básica
    if "dataDocumento" in df_all.columns:
        df_all["dataDocumento"] = pd.to_datetime(df_all["dataDocumento"], errors="coerce")
    for c in ("valorDocumento","valorLiquido","valorGlosa"):
        if c in df_all.columns:
            df_all[c] = pd.to_numeric(df_all[c], errors="coerce")
    return df_all


# =============================
# file: utils/data_processing.py
# =============================
import pandas as pd


def dist_por_uf(df_dep: pd.DataFrame) -> pd.DataFrame:
    if df_dep.empty or "siglaUf" not in df_dep.columns:
        return pd.DataFrame({"siglaUf": [], "qtd": []})
    return (
        df_dep.groupby("siglaUf").size().reset_index(name="qtd").sort_values(["qtd","siglaUf"], ascending=[False, True])
    )


def dist_por_partido(df_dep: pd.DataFrame) -> pd.DataFrame:
    if df_dep.empty or "siglaPartido" not in df_dep.columns:
        return pd.DataFrame({"siglaPartido": [], "qtd": []})
    return (
        df_dep.groupby("siglaPartido").size().reset_index(name="qtd").sort_values(["qtd","siglaPartido"], ascending=[False, True])
    )


def despesas_por_tipo(df_des: pd.DataFrame) -> pd.DataFrame:
    if df_des.empty or "tipoDespesa" not in df_des.columns:
        return pd.DataFrame({"tipoDespesa": [], "valorLiquido": []})
    base = df_des.copy()
    if "valorLiquido" not in base.columns:
        base["valorLiquido"] = 0.0
    agg = base.groupby("tipoDespesa", dropna=False)["valorLiquido"].sum().reset_index()
    return agg.sort_values("valorLiquido", ascending=False)


# =============================
# file: streamlit_app.py
# =============================
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.api_client import list_deputados, get_deputado_detail, get_despesas
from utils.data_processing import dist_por_uf, dist_por_partido, despesas_por_tipo

st.set_page_config(page_title="Painel — Deputados", layout="wide")
st.title("👤 Painel dos Deputados — Câmara dos Deputados")
st.caption("FGV Direito Rio — P2 | Python + Streamlit")

with st.sidebar:
    st.header("🔎 Filtros")
    nome = st.text_input("Nome (opcional)")
    col1, col2 = st.columns(2)
    with col1:
        partido = st.text_input("Sigla do partido (ex.: PT)")
    with col2:
        uf = st.text_input("UF (ex.: RJ)")
    legislatura = st.number_input("ID da Legislatura (opcional)", min_value=0, value=0, step=1)
    buscar = st.button("Buscar deputados", type="primary")

@st.cache_data(show_spinner=False)
def _buscar_deputados(nome, uf, partido, leg):
    leg_val = int(leg) if leg else None
    if leg_val == 0:
        leg_val = None
    return list_deputados(
        nome=nome or None,
        sigla_uf=(uf or None),
        sigla_partido=(partido or None),
        id_legislatura=leg_val,
        itens_por_pagina=100,
        limite_paginas=10,
    )

if buscar:
    with st.spinner("Carregando dados dos deputados…"):
        df_dep = _buscar_deputados(nome, uf, partido, legislatura)

    if df_dep.empty:
        st.warning("Nenhum deputado encontrado para os filtros fornecidos.")
        st.stop()

    st.success(f"{len(df_dep)} deputados encontrados.")

    # ---- Gráficos de distribuição ----
    colA, colB = st.columns(2)
    with colA:
        duf = dist_por_uf(df_dep)
        if not duf.empty:
            fig_uf = px.bar(duf, x="siglaUf", y="qtd", title="Distribuição por UF")
            st.plotly_chart(fig_uf, use_container_width=True)
    with colB:
        dpart = dist_por_partido(df_dep)
        if not dpart.empty:
            fig_part = px.pie(dpart, names="siglaPartido", values="qtd", title="Distribuição por partido")
            st.plotly_chart(fig_part, use_container_width=True)

    # ---- Tabela principal ----
    st.subheader("Lista de Deputados")
    show_cols = [c for c in ["id","nome","siglaPartido","siglaUf","email","uri"] if c in df_dep.columns]
    st.dataframe(df_dep[show_cols], use_container_width=True, hide_index=True)

    # ---- Detalhe + despesas ----
    st.markdown("---")
    st.subheader("Detalhar deputado e despesas (CEAP)")
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        dep_id = st.selectbox("Escolha o ID do deputado", options=df_dep["id"].tolist())
    with c2:
        ano = st.number_input("Ano (ex.: 2024)", min_value=2009, max_value=2100, value=2024, step=1)
    with c3:
        ver = st.button("Carregar despesas")

    if ver:
        t1, t2 = st.tabs(["📇 Dados cadastrais", "💳 Despesas por tipo"])
        with t1:
            with st.spinner("Carregando dados cadastrais…"):
                df_det = get_deputado_detail(int(dep_id))
            if df_det.empty:
                st.info("Sem dados disponíveis.")
            else:
                # Mostra subset amigável se existir
                cols_pref = [
                    "ultimoStatus.nome","ultimoStatus.siglaPartido","ultimoStatus.siglaUf",
                    "ultimoStatus.email","ultimoStatus.gabinete.nome","ultimoStatus.gabinete.predio",
                    "ultimoStatus.gabinete.sala","ultimoStatus.gabinete.telefone"
                ]
                have = [c for c in cols_pref if c in df_det.columns]
                st.dataframe(df_det[have] if have else df_det, use_container_width=True, hide_index=True)
        with t2:
            with st.spinner("Carregando despesas…"):
                df_des = get_despesas(int(dep_id), ano=int(ano))
            if df_des.empty:
                st.info("Nenhuma despesa encontrada para o período.")
            else:
                agg = despesas_por_tipo(df_des)
                fig = px.bar(agg, x="tipoDespesa", y="valorLiquido", title=f"Despesas por tipo — {ano}")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_des, use_container_width=True, hide_index=True)
                csv_bytes = df_des.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Baixar CSV de despesas", data=csv_bytes, file_name=f"despesas_{dep_id}_{ano}.csv", mime="text/csv")


# =============================
# file: requirements.txt (opcional)
# =============================
# streamlit>=1.38.0
# requests>=2.31.0
# pandas>=2.2.0
# plotly>=5.22.0
