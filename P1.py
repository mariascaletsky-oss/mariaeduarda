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
st.download_button("⬇️ Baixar CSV de despesas", data=csv_bytes, file_name=f"despesas_{dep_id}_{ano}.csv", mime="text/csv")
