"""
Gera a base sintética do Multiverso.

Cenário (fictício): o Orbe, um banco digital, quer saber se comerciais de TV
aberta trazem contas novas. Antes de gastar no Brasil todo, ele testa em
poucas cidades. A gente sabe a VERDADE (quanto a TV realmente gerou),
então dá para conferir se o GeoLift acerta.

Etapas:
1. Gera contas novas diárias de 40 cidades SEM nenhuma campanha.
2. Roda a seleção de mercados usando só o período pré (como na vida real).
3. Liga a TV nas cidades escolhidas por 28 dias e injeta o efeito verdadeiro.
4. Salva:
   - contas_diarias.csv  (o que o analista enxerga)
   - verdade.csv         (contrafactual verdadeiro — só para conferência)
   - cidades.csv, campanha.json, selecao_individual.csv, selecao_grupos.csv

Uso:  python dados/gerar_dados.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from geolift.motor import selecionar_mercados  # noqa: E402

SEED = 42
LIFT_VERDADEIRO = 0.10        # TV gera +10% de contas no platô
INVESTIMENTO_TV = 240_000     # R$ no período de teste
INICIO = "2026-01-05"
INICIO_TESTE = "2026-05-04"
DIAS_TESTE = 28

# cidade, UF, região, população (mil hab., aproximada)
CIDADES = [
    ("São Paulo", "SP", "Sudeste", 11450), ("Rio de Janeiro", "RJ", "Sudeste", 6211),
    ("Brasília", "DF", "Centro-Oeste", 2817), ("Fortaleza", "CE", "Nordeste", 2428),
    ("Salvador", "BA", "Nordeste", 2418), ("Belo Horizonte", "MG", "Sudeste", 2315),
    ("Manaus", "AM", "Norte", 2063), ("Curitiba", "PR", "Sul", 1773),
    ("Recife", "PE", "Nordeste", 1488), ("Goiânia", "GO", "Centro-Oeste", 1437),
    ("Porto Alegre", "RS", "Sul", 1332), ("Belém", "PA", "Norte", 1303),
    ("Guarulhos", "SP", "Sudeste", 1291), ("Campinas", "SP", "Sudeste", 1139),
    ("São Luís", "MA", "Nordeste", 1037), ("Maceió", "AL", "Nordeste", 957),
    ("Campo Grande", "MS", "Centro-Oeste", 898), ("Teresina", "PI", "Nordeste", 866),
    ("João Pessoa", "PB", "Nordeste", 833), ("Natal", "RN", "Nordeste", 751),
    ("Ribeirão Preto", "SP", "Sudeste", 698), ("Uberlândia", "MG", "Sudeste", 713),
    ("Sorocaba", "SP", "Sudeste", 723), ("Cuiabá", "MT", "Centro-Oeste", 650),
    ("Aracaju", "SE", "Nordeste", 602), ("Joinville", "SC", "Sul", 616),
    ("Londrina", "PR", "Sul", 555), ("Juiz de Fora", "MG", "Sudeste", 540),
    ("Florianópolis", "SC", "Sul", 537), ("Porto Velho", "RO", "Norte", 460),
    ("Macapá", "AP", "Norte", 442), ("Caxias do Sul", "RS", "Sul", 463),
    ("Vitória", "ES", "Sudeste", 322), ("Maringá", "PR", "Sul", 409),
    ("Feira de Santana", "BA", "Nordeste", 616), ("Campina Grande", "PB", "Nordeste", 419),
    ("Boa Vista", "RR", "Norte", 413), ("Santos", "SP", "Sudeste", 418),
    ("Palmas", "TO", "Norte", 302), ("Anápolis", "GO", "Centro-Oeste", 398),
]

# coordenadas aproximadas (só para o mapa do app)
COORD = {
    "São Paulo": (-23.55, -46.63), "Rio de Janeiro": (-22.91, -43.17), "Brasília": (-15.79, -47.88),
    "Fortaleza": (-3.73, -38.52), "Salvador": (-12.97, -38.50), "Belo Horizonte": (-19.92, -43.94),
    "Manaus": (-3.12, -60.02), "Curitiba": (-25.43, -49.27), "Recife": (-8.05, -34.88),
    "Goiânia": (-16.68, -49.25), "Porto Alegre": (-30.03, -51.23), "Belém": (-1.46, -48.49),
    "Guarulhos": (-23.45, -46.53), "Campinas": (-22.91, -47.06), "São Luís": (-2.53, -44.30),
    "Maceió": (-9.67, -35.74), "Campo Grande": (-20.47, -54.62), "Teresina": (-5.09, -42.80),
    "João Pessoa": (-7.12, -34.86), "Natal": (-5.79, -35.21), "Ribeirão Preto": (-21.18, -47.81),
    "Uberlândia": (-18.92, -48.28), "Sorocaba": (-23.50, -47.46), "Cuiabá": (-15.60, -56.10),
    "Aracaju": (-10.91, -37.07), "Joinville": (-26.30, -48.85), "Londrina": (-23.31, -51.16),
    "Juiz de Fora": (-21.76, -43.35), "Florianópolis": (-27.60, -48.55), "Porto Velho": (-8.76, -63.90),
    "Macapá": (0.03, -51.07), "Caxias do Sul": (-29.17, -51.18), "Vitória": (-20.32, -40.34),
    "Maringá": (-23.42, -51.94), "Feira de Santana": (-12.27, -38.97), "Campina Grande": (-7.23, -35.88),
    "Boa Vista": (2.82, -60.67), "Santos": (-23.96, -46.33), "Palmas": (-10.18, -48.33),
    "Anápolis": (-16.33, -48.95),
}


def gerar_base(rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    fim = pd.Timestamp(INICIO_TESTE) + pd.Timedelta(days=DIAS_TESTE - 1)
    datas = pd.date_range(INICIO, fim, freq="D")
    T = len(datas)
    cid = pd.DataFrame(CIDADES, columns=["cidade", "uf", "regiao", "populacao_mil"])
    cid["lat"] = cid["cidade"].map(lambda c: COORD[c][0])
    cid["lon"] = cid["cidade"].map(lambda c: COORD[c][1])

    # Tendência nacional: crescimento do banco (~+18% no período) + ruído suave
    t = np.arange(T)
    nacional = 0.18 * t / T + np.cumsum(rng.normal(0, 0.006, T))
    # Semana: segunda forte, fim de semana fraco
    semana = np.log(np.array([1.14, 1.08, 1.04, 1.01, 0.97, 0.86, 0.80]))[datas.dayofweek]
    # Dias de pagamento (5º e 20º): pico de abertura de conta
    pagto = np.where(np.isin(datas.day, [5, 6, 20, 21]), np.log(1.07), 0.0)
    # Carnaval 2026 (14 a 17/fev): todo mundo some
    carnaval = np.where((datas >= "2026-02-14") & (datas <= "2026-02-17"), np.log(0.70), 0.0)

    # Fator regional (AR(1)): cada região tem suas ondas próprias
    regionais = {}
    for r in cid["regiao"].unique():
        f = np.zeros(T)
        for i in range(1, T):
            f[i] = 0.90 * f[i - 1] + rng.normal(0, 0.008)
        regionais[r] = f

    linhas, verdade = [], []
    for _, c in cid.iterrows():
        nivel = 0.11 * c.populacao_mil ** 0.97 * rng.uniform(0.8, 1.25)
        sensib_semana = rng.uniform(0.8, 1.2)
        idio = np.zeros(T)
        for i in range(1, T):
            idio[i] = 0.85 * idio[i - 1] + rng.normal(0, 0.018)
        log_mu = (np.log(nivel) + nacional + sensib_semana * semana + pagto + carnaval
                  + regionais[c.regiao] + idio)
        mu = np.exp(log_mu)
        for d, m in zip(datas, mu):
            linhas.append((d, c.cidade, m))
    base = pd.DataFrame(linhas, columns=["data", "cidade", "mu"])
    return base, cid


def main() -> None:
    rng = np.random.default_rng(SEED)
    base, cid = gerar_base(rng)
    base["contas_sem_tv"] = rng.poisson(base["mu"])

    # 2. Seleção de mercados olhando só o pré (como seria na vida real)
    fim_pre = pd.Timestamp(INICIO_TESTE) - pd.Timedelta(days=1)
    pre = base[base["data"] <= fim_pre].rename(columns={"contas_sem_tv": "contas"})
    print("Rodando seleção de mercados (pode levar ~1 min)...")
    indiv, grupos = selecionar_mercados(pre[["data", "cidade", "contas"]], cid, fim_pre, DIAS_TESTE)
    escolha = grupos[grupos["cabe_orcamento"]].iloc[0]
    tratadas = list(escolha["cidades"])
    print("Grupo escolhido:", tratadas, f"MDE {escolha.mde_pct:.1f}%")

    # 3. Liga a TV: efeito sobe em ~1 semana (curva de aprendizado da TV) e estabiliza
    dia = (base["data"] - pd.Timestamp(INICIO_TESTE)).dt.days
    no_teste = (dia >= 0) & base["cidade"].isin(tratadas)
    rampa = 1 - np.exp(-(dia.clip(lower=0) + 1) / 4)
    efeito = np.where(no_teste, LIFT_VERDADEIRO * rampa, 0.0)
    base["contas"] = rng.poisson(base["mu"] * (1 + efeito))
    # nas cidades sem TV, o observado é exatamente o mundo sem TV
    base.loc[~no_teste, "contas"] = base.loc[~no_teste, "contas_sem_tv"]
    # contrafactual "verdadeiro" (esperança sem TV) para conferência
    base["contas_esperadas_sem_tv"] = base["mu"]
    base["contas_esperadas_com_tv"] = base["mu"] * (1 + efeito)

    out = RAIZ / "dados"
    base[["data", "cidade", "contas"]].to_csv(out / "contas_diarias.csv", index=False)
    base[["data", "cidade", "contas_esperadas_sem_tv", "contas_esperadas_com_tv"]].round(
        {"contas_esperadas_sem_tv": 3, "contas_esperadas_com_tv": 3}).to_csv(
        out / "verdade.csv", index=False)
    cid.to_csv(out / "cidades.csv", index=False)
    indiv.to_csv(out / "selecao_individual.csv", index=False)
    grupos.drop(columns=["cidades"]).to_csv(out / "selecao_grupos.csv", index=False)

    v = base[no_teste]
    lift_real = v["contas_esperadas_com_tv"].sum() / v["contas_esperadas_sem_tv"].sum() - 1
    incr_real = (v["contas_esperadas_com_tv"] - v["contas_esperadas_sem_tv"]).sum()
    meta = {
        "empresa": "Orbe (banco digital fictício)",
        "canal": "TV aberta",
        "inicio_teste": INICIO_TESTE,
        "fim_teste": str((pd.Timestamp(INICIO_TESTE) + pd.Timedelta(days=DIAS_TESTE - 1)).date()),
        "dias_teste": DIAS_TESTE,
        "cidades_tratadas": tratadas,
        "investimento_tv": INVESTIMENTO_TV,
        "verdade_lift_pct": round(lift_real * 100, 2),
        "verdade_incrementais": round(incr_real),
        "lift_plato_pct": LIFT_VERDADEIRO * 100,
        "seed": SEED,
    }
    (out / "campanha.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
