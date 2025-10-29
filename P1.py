import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional

# matplotlib é opcional — se não houver, usamos fallback nativo do Streamlit
try:
    import matplotlib.pyplot as plt  # type: ignore
    HAS_MPL = True
except Exception:
    HAS_MPL = False

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"User-Agent": "Streamlit Busca Deputado/2.6", "Accept": "application/json"}

st.set_page_config(page_title="Buscar Deputado (2 páginas)", page_icon="🔎", layout="wide")
st.title("🔎 Busca de Deputado")
st.caption("Fonte: API de Dados Abertos da Câmara dos Deputados")

# ----------------------
# Funções de API
# ----------------------
@st.cache_data(ttl=1200)
def search_deputados_by_name(nome: str):
    params = {"nome": nome, "ordem": "ASC", "ordenarPor": "nome", "itens": 100}
    r = requests.get(f"{API_BASE}/deputados", params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get("dados", [])

@st.cache_data(ttl=1200)
def list_deputados_by_partido(sigla_partido: str):
    """Lista deputados em exercício de um partido (sigla)."""
    params = {"siglaPartido": sigla_partido, "ordem": "ASC", "ordenarPor": "nome", "itens": 100}
    r = requests.get(f"{API_BASE}/deputados", params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get("dados", [])

@st.cache_data(ttl=1800)
def get_deputado_details(dep_id: int):
    r = requests.get(f"{API_BASE}/deputados/{dep_id}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get("dados", {})

@st.cache_data(ttl=600)
def get_despesas(dep_id: int, ano: Optional[int] = None) -> pd.DataFrame:
    """Busca despesas do deputado e retorna DataFrame."""
    url = f"{API_BASE}/deputados/{dep_id}/despesas"
    params = {"ordem": "DESC", "ordenarPor": "dataDocumento"}
    if ano is not None:
        params["ano"] = ano

    dados_total: list[dict] = []
    pagina = 1
    for _ in range(50):  # limite de segurança
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

@st.cache_data(ttl=900)
def get_despesas_por_ano(dep_id: int, ano_ini: int = 2015, ano_fim: Optional[int] = None) -> pd.DataFrame:
    """Agrega despesas por ano (valor líquido) para o deputado selecionado."""
    if ano_fim is None:
        ano_fim = datetime.now().year
    rows = []
    for ano in range(ano_ini, ano_fim + 1):
        df = get_despesas(dep_id, ano=ano)
        total = 0.0
        if not df.empty:
            total = pd.to_numeric(df.get("valorLiquido"), errors="coerce").fillna(0).sum()
        rows.append({"Ano": ano, "TotalLiquido": float(total)})
    return pd.DataFrame(rows)

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
    "mostrar_despesas": True,
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
    st.session_state.mostrar_despesas = st.checkbox(
        "Mostrar seção de despesas", value=st.session_state.mostrar_despesas
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
        c1, c2, _ = st.columns([1, 1, 6])
        with c1:
            submitted = st.form_submit_button("Buscar")
        with c2:
            limpar = st.form_submit_button("Limpar")

    if submitted and (nome_query or "").strip():
        st.session_state.nome_query = (nome_query or "").strip()
        try:
            st.session_state.resultados = search_deputados_by_name(st.session_state.nome_query)
        except requests.RequestException as e:
            st.error(f"Erro ao buscar deputados: {e}")
            st.stop()
        st.session_state.dep_id = None
        st.session_state.pagina = "Respostas"
        st.rerun()

    if 'limpar' in locals() and limpar:
        st.session_state.nome_query = ""
        st.session_state.resultados = []
        st.session_state.dep_id = None
        st.info("Campos limpos. Faça nova pesquisa.")

    st.markdown("> Dica: após enviar a busca, você será levado(a) automaticamente à página **Respostas**.")

# --------------------------------------------------
# PÁGINA 2 — RESPOSTAS
# --------------------------------------------------
if st.session_state.pagina == "Respostas":
    # Botão seta (voltar)
    cb, _ = st.columns([1, 9])
    with cb:
        if st.button("⬅ Voltar à Pesquisa"):
            st.session_state.pagina = "Pesquisa"
            st.rerun()

    st.subheader("Respostas")

    resultados = st.session_state.resultados
    if not resultados:
        st.info("Nenhum resultado para exibir. Volte à página **Pesquisa** e faça uma busca.")
    else:
        # Tabela interativa + CSV
        df_dep = pd.DataFrame(resultados)
        for c in ["nome", "siglaPartido", "siglaUf", "email", "id"]:
            if c not in df_dep.columns:
                df_dep[c] = None

        st.markdown("### Tabela de parlamentares")
        tabela_base = df_dep.rename(columns={
            "nome": "Nome", "siglaPartido": "Partido", "siglaUf": "UF", "email": "E-mail"
        })[["Nome", "Partido", "UF", "E-mail"]]

        if st.session_state.get("tabela_compacta", True):
            st.dataframe(tabela_base, use_container_width=True)
        else:
            st.table(tabela_base)

        csv_dep = df_dep[["nome", "siglaPartido", "siglaUf", "email", "id"]].rename(
            columns={"nome": "Nome", "siglaPartido": "Partido", "siglaUf": "UF", "email": "E-mail", "id": "ID"}
        ).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV (deputados)", data=csv_dep, file_name="deputados.csv", mime="text/csv")

        st.markdown("---")
        st.markdown("### Detalhes e despesas do parlamentar")

        # Seleção do resultado
        opcoes = {
            f"{d['nome']} — {d.get('siglaPartido','?')}/{d.get('siglaUf','?')} (ID {d['id']})": d['id']
            for d in resultados
        }
        escolha_rotulo = st.selectbox("Selecione o(a) deputado(a)", options=list(opcoes.keys()), index=0)
        dep_id = opcoes.get(escolha_rotulo)
        st.session_state.dep_id = dep_id

        if dep_id:
            try:
                detalhes = get_deputado_details(dep_id)
            except requests.RequestException as e:
                st.error(f"Erro ao buscar detalhes do deputado: {e}")
                st.stop()

            ultimo = detalhes.get("ultimoStatus", {}) or {}
            gabinete = ultimo.get("gabinete", {}) or {}

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

            c1, c2 = st.columns([1, 2], vertical_alignment="top")
            with c1:
                if url_foto:
                    st.image(url_foto, caption=nome_eleitoral or nome_civil, use_container_width=True)
                else:
                    st.write("Sem foto disponível")
            with c2:
                st.subheader(nome_eleitoral or nome_civil or "Deputado(a)")
                st.write(f"**Partido/UF:** {sigla_partido or '—'}/{sigla_uf or '—'}")
                st.write(f"**Situação no cargo:** {situacao or '—'}")
                st.write(f"**Condição eleitoral:** {condicao or '—'}")
                st.write(f"**E-mail do gabinete:** {email or '—'}")
                st.write(f"**Gabinete:** {nome_gab or '—'} • Prédio {predio or '—'}, sala {sala or '—'}, andar {andar or '—'}")
                st.write(f"**Telefone:** {telefone or '—'}")

            # --- Gráfico: partido do deputado por UF ---
            st.markdown("### Distribuição do partido por UF")
            if sigla_partido:
                try:
                    lista_partido = list_deputados_by_partido(sigla_partido)
                    df_part = pd.DataFrame(lista_partido)
                    if not df_part.empty and "siglaUf" in df_part.columns:
                        contagem_uf = df_part["siglaUf"].value_counts().sort_index()
                        st.bar_chart(contagem_uf)
                    else:
                        st.info("Não foi possível calcular a distribuição por UF para este partido.")
                except requests.RequestException as e:
                    st.error(f"Erro ao buscar deputados do partido {sigla_partido}: {e}")
            else:
                st.info("Partido não disponível para o(a) deputado(a) selecionado(a).")

            # --- Seção de despesas (opcional via sidebar) ---
            if st.session_state.get("mostrar_despesas", True):
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
                    cols_keep = [
                        "ano","mes","dataDocumento","descricaoTipoDespesa","tipoDespesa",
                        "nomeFornecedor","cnpjCpfFornecedor","valorDocumento","valorLiquido","urlDocumento"
                    ]
                    for c in cols_keep:
                        if c not in df_desp.columns:
                            df_desp[c] = None

                    tipos = sorted(df_desp["descricaoTipoDespesa"].dropna().unique().tolist())
                    tipo_escolhido = st.selectbox("Tipo de despesa (opcional)", options=[""] + tipos, index=0)
                    if tipo_escolhido:
                        df_desp = df_desp[df_desp["descricaoTipoDespesa"].fillna("") == tipo_escolhido]

                    df_desp["dataDocumento"] = pd.to_datetime(df_desp["dataDocumento"], errors="coerce")
                    df_view = df_desp[cols_keep].sort_values("dataDocumento", ascending=False).copy()

                    total_liq = pd.to_numeric(df_view["valorLiquido"], errors="coerce").fillna(0).sum()
                    total_doc = pd.to_numeric(df_view["valorDocumento"], errors="coerce").fillna(0).sum()
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Total (valor líquido)", f"R$ {total_liq:,.2f}".replace(",","X").replace(".",",").replace("X","."))
                    with m2:
                        st.metric("Total (valor documento)", f"R$ {total_doc:,.2f}".replace(",","X").replace(".",",").replace("X","."))

                    st.dataframe(df_view, use_container_width=True)

                    csv_desp = df_view.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Baixar CSV (despesas)", data=csv_desp, file_name=f"despesas_{dep_id}_{ano}.csv", mime="text/csv"
                    )

                # --- Linha: total de despesas por ano (filtra anos sem dados) ---
                st.markdown("#### Evolução anual de despesas (valor líquido)")
                df_anos = get_despesas_por_ano(dep_id, ano_ini=2015)
                if not df_anos.empty:
                    df_anos = df_anos[pd.to_numeric(df_anos["TotalLiquido"], errors="coerce").fillna(0) > 0]

                if df_anos.empty:
                    st.info("Sem dados de despesas por ano para exibir.")
                else:
                    if HAS_MPL:
                        fig2, ax2 = plt.subplots()
                        ax2.plot(df_anos["Ano"], df_anos["TotalLiquido"], marker="o")
                        ax2.set_xlabel("Ano")
                        ax2.set_ylabel("Total (R$)")
                        ax2.grid(True, linestyle=":", alpha=0.5)
                        st.pyplot(fig2, clear_figure=True)
                    else:
                        st.line_chart(df_anos.set_index("Ano")["TotalLiquido"])

            # Link para API
            if st.session_state.get("mostrar_link_api", True):
                st.markdown(f"Ver na API: [deputados/{dep_id}]({API_BASE}/deputados/{dep_id})")

# Rodapé
st.markdown("\n—\n*App didático. Confira detalhes e metadados na API oficial.*")
