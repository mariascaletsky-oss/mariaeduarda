import requests
import streamlit as st

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"User-Agent": "Streamlit Busca Deputado/2.0", "Accept": "application/json"}

st.set_page_config(page_title="Buscar Deputado (2 páginas)", page_icon="🔎", layout="wide")
st.title("🔎 Busca de Deputado")
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

# Estado global mínimo
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

# Seletor de página (topo)
pagina = st.radio(
    "Navegação",
    options=["Pesquisa", "Respostas"],
    index=0 if st.session_state.pagina == "Pesquisa" else 1,
    horizontal=True,
    help="1) Faça a pesquisa; 2) veja os resultados/detalhes.",
)
st.session_state.pagina = pagina

# --------------------------------------------------
# PÁGINA 1 — PESQUISA
# --------------------------------------------------
if pagina == "Pesquisa":
    st.subheader("Página 1 – Pesquisa")
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
        # navega automaticamente para página de respostas
        st.session_state.pagina = "Respostas"
        st.rerun()

    if limpar:
        st.session_state.nome_query = ""
        st.session_state.resultados = []
        st.session_state.dep_id = None
        st.info("Campos limpos. Faça nova pesquisa.")

    with st.expander("Preferências de exibição"):
        st.session_state.tabela_compacta = st.checkbox(
            "Mostrar tabela compacta", value=st.session_state.tabela_compacta
        )
        st.session_state.mostrar_link_api = st.checkbox(
            "Mostrar link para a API", value=st.session_state.mostrar_link_api
        )

    st.markdown(
        "> Dica: após enviar a busca, você será levado(a) automaticamente à página **Respostas**."
    )

# --------------------------------------------------
# PÁGINA 2 — RESPOSTAS
# --------------------------------------------------
if pagina == "Respostas":
    st.subheader("Página 2 – Respostas")

    resultados = st.session_state.resultados
    if not resultados:
        st.info("Nenhum resultado para exibir. Volte à página **Pesquisa** e faça uma busca.")
    else:
        st.success(
            f"{len(resultados)} resultado(s) encontrado(s) para: **{st.session_state.nome_query}**"
        )

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

            st.markdown("---")
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

            # Link para API
            if st.session_state.get("mostrar_link_api", True):
                st.markdown(f"Ver na API: [deputados/{dep_id}]({API_BASE}/deputados/{dep_id})")

# Rodapé
st.markdown("\n—\n*App didático. Confira detalhes e metadados na API oficial.*")
