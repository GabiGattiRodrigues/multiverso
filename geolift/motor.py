"""
Motor do GeoLift do Multiverso.

Tudo o que o app mostra sai daqui. A ideia é simples:

1. CONTROLE SINTÉTICO (uma gêmea para cada cidade testada)
   A gente quer saber quantas contas as cidades com TV teriam aberto SE a TV
   não tivesse passado. Esse "mundo sem TV" não existe, então, para CADA
   cidade testada, montamos uma cidade de mentira (a "cidade gêmea")
   misturando pedaços das cidades que NÃO viram a TV. A receita da mistura
   (os pesos) é escolhida para que a gêmea imite a cidade de verdade o mais
   perto possível ANTES da campanha.

2. LIFT
   Durante a campanha, a diferença entre o real e a gêmea é o efeito da TV.
   O efeito do teste todo = soma das cidades reais ÷ soma das gêmeas − 1.

3. INFERÊNCIA (o efeito é real ou é sorte?)
   - Inferência conforme (a mesma família usada pelo GeoLift do Meta):
     para cada efeito candidato θ ("e se a TV deu +θ%?"), tiramos θ do
     período de teste, ajustamos a gêmea em TODO o período e olhamos os
     erros. Se θ for o efeito certo, os erros do teste parecem com os do
     pré. Embaralhando os erros no tempo (deslocamentos circulares),
     vemos se os erros do teste são "estranhos". θ que não fica estranho
     entra no intervalo de confiança. O p-valor é o teste de θ = 0.
   - Placebo no espaço: fingimos que cada cidade controle recebeu a TV.
     Se a nossa cidade tratada se destaca de todas elas, o efeito é real.

4. SELEÇÃO DE MERCADOS (antes do teste)
   Para cada grupo candidato de cidades, rodamos o placebo no tempo
   (fingimos campanhas em semanas do passado em que NADA aconteceu; o
   "efeito" que aparece ali é puro erro do método) e medimos o tamanho
   desse erro. Ruído pequeno = dá para enxergar efeitos
   pequenos (MDE baixo). Escolhemos o grupo com menor MDE que caiba no
   orçamento.

Detalhes técnicos:
- Cada série é indexada pela média do período pré (fica tudo na mesma
  escala, uma cidade grande não "pesa" mais só por ser grande).
- Pesos não negativos que somam 1 (combinação convexa, Abadie et al.),
  com intercepto (versão "demeaned", Ferman & Pinto 2021): a gêmea precisa
  acompanhar o FORMATO da curva, não o nível exato.
- Resolvido com NNLS + uma linha extra de penalização para forçar soma = 1.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.optimize import nnls

Z_POWER = 1.96 + 0.84  # 5% bicaudal + 80% de poder


# ---------------------------------------------------------------------------
# 1. Controle sintético
# ---------------------------------------------------------------------------
def pesos_sinteticos(y_pre: np.ndarray, X_pre: np.ndarray, penal: float = 1e3) -> np.ndarray:
    """Pesos w >= 0, soma(w) = 1, que minimizam ||(y - ȳ) - (X - X̄) w||².

    y_pre: (T,) série tratada (indexada) no pré
    X_pre: (T, J) séries das cidades controle (indexadas) no pré
    """
    yc = y_pre - y_pre.mean()
    Xc = X_pre - X_pre.mean(axis=0)
    # linha extra: penal * (soma(w) - 1) = 0  -> força soma = 1
    A = np.vstack([Xc, penal * np.ones((1, Xc.shape[1]))])
    b = np.concatenate([yc, [penal]])
    w, _ = nnls(A, b, maxiter=50 * Xc.shape[1])
    s = w.sum()
    return w / s if s > 0 else np.full(Xc.shape[1], 1 / Xc.shape[1])


def contrafactual(y: np.ndarray, X: np.ndarray, n_pre: int) -> tuple[np.ndarray, np.ndarray]:
    """Devolve (série sintética completa, pesos). Intercepto = diferença de médias no pré."""
    w = pesos_sinteticos(y[:n_pre], X[:n_pre])
    sint = X @ w
    sint = sint + (y[:n_pre].mean() - sint[:n_pre].mean())
    return sint, w


# ---------------------------------------------------------------------------
# Preparação dos dados
# ---------------------------------------------------------------------------
def matriz(df: pd.DataFrame) -> pd.DataFrame:
    """Formato largo: linhas = datas, colunas = cidades, valor = contas novas."""
    return df.pivot(index="data", columns="cidade", values="contas").sort_index()


def indexar(serie: np.ndarray, n_pre: int) -> tuple[np.ndarray, float]:
    base = serie[:n_pre].mean()
    return serie / base, base


def preparar(wide: pd.DataFrame, tratadas: list[str], n_pre: int):
    """Y: (T, k) uma coluna indexada por cidade tratada; bases: média do pré de cada uma
    (para voltar a contas); X: (T, J) controles indexados."""
    Yabs = wide[tratadas].to_numpy(float)
    bases = Yabs[:n_pre].mean(axis=0)
    controles = [c for c in wide.columns if c not in tratadas]
    Xabs = wide[controles].to_numpy(float)
    return Yabs / bases, X_indexado(Xabs, n_pre), controles, bases


def X_indexado(Xabs: np.ndarray, n_pre: int) -> np.ndarray:
    return Xabs / Xabs[:n_pre].mean(axis=0)


def ajustar(Y: np.ndarray, X: np.ndarray, n_fit: int) -> tuple[np.ndarray, np.ndarray]:
    """Uma gêmea por coluna de Y. Devolve S (T, k) e pesos W (J, k)."""
    S, W = np.empty_like(Y), np.empty((X.shape[1], Y.shape[1]))
    for i in range(Y.shape[1]):
        S[:, i], W[:, i] = contrafactual(Y[:, i], X, n_fit)
    return S, W


# ---------------------------------------------------------------------------
# 2. Lift
# ---------------------------------------------------------------------------
@dataclass
class Resultado:
    datas: pd.DatetimeIndex
    n_pre: int
    tratadas: list
    real: np.ndarray            # contas reais (soma das tratadas)
    sintetico: np.ndarray       # contas das gêmeas (soma)
    real_cidade: pd.DataFrame   # contas reais por cidade tratada
    sint_cidade: pd.DataFrame   # gêmea de cada cidade tratada
    pesos: pd.DataFrame         # receita de cada gêmea (linhas = controles, colunas = tratadas)
    lift_cidade: pd.Series      # lift de cada cidade (%)
    lift_pct: float             # efeito médio no período de teste (%)
    incrementais: float         # contas a mais por causa da TV
    mape_pre: float             # erro das gêmeas antes da campanha (%), no agregado
    r2_pre: float
    mape_cidade: pd.Series
    ic_baixo: float
    ic_alto: float
    p_valor: float
    curva_p: pd.DataFrame       # p-valor para cada efeito testado (θ)
    p_valor_espaco: float
    placebos_espaco: pd.DataFrame
    interceptos: pd.Series      # α de cada gêmea (em índice)
    bases: pd.Series            # média do pré de cada cidade tratada (índice 1 = essa média)
    indices: pd.DataFrame       # séries indexadas das cidades controle (o "x" da conta)


def estimar_lift(Y, X, bases, n_pre: int, n_teste: int) -> float:
    S, _ = ajustar(Y[: n_pre + n_teste], X[: n_pre + n_teste], n_pre)
    post = slice(n_pre, n_pre + n_teste)
    return (Y[post] @ bases).sum() / (S[post] @ bases).sum() - 1


def placebo_tempo(Y, X, bases, n_pre: int, n_teste: int, min_treino: int = 56, passo: int = 3) -> np.ndarray:
    """Finge campanhas no passado (só pré) e guarda o 'lift' falso de cada uma."""
    return np.array([estimar_lift(Y[: i + n_teste], X[: i + n_teste], bases, i, n_teste)
                     for i in range(min_treino, n_pre - n_teste + 1, passo)])


def p_valor_conforme(Y, X, bases, n_pre: int, theta: float) -> float:
    """Testa H0: 'o efeito da TV foi θ' (multiplicativo) com permutação circular dos resíduos."""
    T = len(Y)
    Ya = Y.copy()
    Ya[n_pre:] = Ya[n_pre:] / (1 + theta)           # remove o efeito hipotético
    S, _ = ajustar(Ya, X, T)                         # ajusta em todo o período (sob H0)
    u = (Ya - S) @ bases / bases.sum()               # erro do agregado
    obs = abs(u[n_pre:].sum())
    perm = np.array([abs(np.roll(u, k)[n_pre:].sum()) for k in range(T)])
    return float(np.mean(perm >= obs))


def intervalo_conforme(Y, X, bases, n_pre, alfa=0.10, grade=None):
    if grade is None:
        grade = np.round(np.arange(-0.30, 0.50001, 0.005), 4)
    ps = np.array([p_valor_conforme(Y, X, bases, n_pre, t) for t in grade])
    curva = pd.DataFrame({"efeito_pct": grade * 100, "p_valor": ps})
    aceitos = curva[curva["p_valor"] > alfa]["efeito_pct"]
    lo, hi = (aceitos.min(), aceitos.max()) if len(aceitos) else (np.nan, np.nan)
    return curva, lo, hi, p_valor_conforme(Y, X, bases, n_pre, 0.0)


def placebo_espaco(wide: pd.DataFrame, tratadas: list[str], n_pre: int, n_teste: int) -> pd.DataFrame:
    """Cada cidade controle vira 'tratada de mentira'. Métrica: RMSPE pós / RMSPE pré."""
    controles = [c for c in wide.columns if c not in tratadas]
    wide = wide.iloc[: n_pre + n_teste]

    def razao(Y, X, bases):
        S, _ = ajustar(Y, X, n_pre)
        e = (Y - S) @ bases / bases.sum()
        pre = np.sqrt(np.mean(e[:n_pre] ** 2))
        pos = np.sqrt(np.mean(e[n_pre:] ** 2))
        lift = (Y[n_pre:] @ bases).sum() / (S[n_pre:] @ bases).sum() - 1
        return pos / pre, lift

    Y, X, _, b = preparar(wide, tratadas, n_pre)
    r, l = razao(Y, X, b)
    linhas = [{"cidade": "Grupo tratado", "razao_rmspe": r, "lift_pct": l * 100, "tratado": True}]
    for c in controles:
        doadores = [d for d in controles if d != c]   # tratadas ficam de fora (estão contaminadas)
        Yc, bc = indexar(wide[c].to_numpy(float), n_pre)
        Xc = X_indexado(wide[doadores].to_numpy(float), n_pre)
        r, l = razao(Yc[:, None], Xc, np.array([bc]))
        linhas.append({"cidade": c, "razao_rmspe": r, "lift_pct": l * 100, "tratado": False})
    return pd.DataFrame(linhas).sort_values("razao_rmspe", ascending=False).reset_index(drop=True)


def rodar_geolift(df: pd.DataFrame, tratadas: list[str], inicio_teste, fim_teste) -> Resultado:
    wide = matriz(df).loc[: pd.Timestamp(fim_teste)]
    datas = wide.index
    n_pre = int((datas < pd.Timestamp(inicio_teste)).sum())
    n_teste = len(datas) - n_pre

    Y, X, controles, bases = preparar(wide, tratadas, n_pre)
    S, W = ajustar(Y, X, n_pre)
    Rabs, Sabs = Y * bases, S * bases
    real, sint = Rabs.sum(axis=1), Sabs.sum(axis=1)

    post = slice(n_pre, None)
    lift = real[post].sum() / sint[post].sum() - 1
    incr = real[post].sum() - sint[post].sum()
    pre_e = real[:n_pre] - sint[:n_pre]
    mape = np.mean(np.abs(pre_e) / real[:n_pre]) * 100
    r2 = 1 - np.sum(pre_e ** 2) / np.sum((real[:n_pre] - real[:n_pre].mean()) ** 2)

    curva, ic_b, ic_a, p0 = intervalo_conforme(Y, X, bases, n_pre)
    esp = placebo_espaco(wide, tratadas, n_pre, n_teste)
    rank = int(esp.index[esp["tratado"]][0]) + 1

    return Resultado(
        datas=datas, n_pre=n_pre, tratadas=list(tratadas), real=real, sintetico=sint,
        real_cidade=pd.DataFrame(Rabs, index=datas, columns=tratadas),
        sint_cidade=pd.DataFrame(Sabs, index=datas, columns=tratadas),
        pesos=pd.DataFrame(W, index=controles, columns=tratadas),
        lift_cidade=pd.Series(Rabs[post].sum(0) / Sabs[post].sum(0) * 100 - 100, index=tratadas),
        lift_pct=lift * 100, incrementais=incr, mape_pre=mape, r2_pre=r2,
        mape_cidade=pd.Series(np.mean(np.abs(Rabs[:n_pre] - Sabs[:n_pre]) / Rabs[:n_pre], 0) * 100,
                              index=tratadas),
        ic_baixo=ic_b, ic_alto=ic_a, p_valor=p0, curva_p=curva,
        p_valor_espaco=rank / len(esp), placebos_espaco=esp,
        interceptos=pd.Series(Y[:n_pre].mean(0) - (X[:n_pre] @ W).mean(0), index=tratadas),
        bases=pd.Series(bases, index=tratadas),
        indices=pd.DataFrame(X, index=datas, columns=controles),
    )


# ---------------------------------------------------------------------------
# 3b. Funções de apoio para as explicações do app
# ---------------------------------------------------------------------------
def residuos_hipotese(df: pd.DataFrame, tratadas: list[str], inicio_teste, fim_teste, theta: float):
    """Para a hipótese 'a TV deu +θ', devolve os erros diários das gêmeas (em % da média do pré),
    as datas, o tamanho do pré e o p-valor da hipótese. É o que a inferência conforme olha."""
    wide = matriz(df).loc[: pd.Timestamp(fim_teste)]
    n_pre = int((wide.index < pd.Timestamp(inicio_teste)).sum())
    Y, X, _, b = preparar(wide, tratadas, n_pre)
    T = len(Y)
    Ya = Y.copy()
    Ya[n_pre:] = Ya[n_pre:] / (1 + theta)
    S, _ = ajustar(Ya, X, T)
    u = (Ya - S) @ b / b.sum()
    return wide.index, u * 100, n_pre, p_valor_conforme(Y, X, b, n_pre, theta)


def gemea_de_controle(df: pd.DataFrame, tratadas: list[str], cidade: str, inicio_teste, fim_teste):
    """Monta a gêmea de uma cidade SEM TV (placebo), como na fila de suspeitos. Devolve (datas, real, gêmea, n_pre)."""
    wide = matriz(df).loc[: pd.Timestamp(fim_teste)]
    n_pre = int((wide.index < pd.Timestamp(inicio_teste)).sum())
    doadores = [c for c in wide.columns if c not in tratadas and c != cidade]
    y, base = indexar(wide[cidade].to_numpy(float), n_pre)
    X = X_indexado(wide[doadores].to_numpy(float), n_pre)
    sint, _ = contrafactual(y, X, n_pre)
    return wide.index, y * base, sint * base, n_pre


# ---------------------------------------------------------------------------
# 4. Seleção de mercados (feita só com dados ANTES do teste)
# ---------------------------------------------------------------------------
GRADE_PODER = np.round(np.arange(0.0, 0.2501, 0.025), 4)


def poder_historico(Y, X, bases, n_pre: int, n_teste: int, alfa: float = 0.10,
                    min_treino: int = 56, passo: int = 3) -> pd.DataFrame:
    """Análise de poder por simulação (no espírito do GeoLift).

    Para várias 'campanhas de mentira' no passado, injetamos um efeito θ
    conhecido e rodamos o teste conforme. Poder(θ) = % de vezes que o teste
    detectou o efeito. Em θ = 0, isso é a taxa de falso positivo.
    """
    linhas = []
    for inicio in range(min_treino, n_pre - n_teste + 1, passo):
        YY, XX = Y[: inicio + n_teste], X[: inicio + n_teste]
        for th in GRADE_PODER:
            Yt = YY.copy()
            Yt[inicio:] = Yt[inicio:] * (1 + th)
            p = p_valor_conforme(Yt, XX, bases, inicio, 0.0)
            linhas.append({"efeito_pct": th * 100, "janela": inicio, "detectou": p <= alfa})
    return (pd.DataFrame(linhas).groupby("efeito_pct", as_index=False)["detectou"].mean()
            .rename(columns={"detectou": "poder"}))


def avaliar_grupo(wide_pre: pd.DataFrame, grupo: list[str], n_teste: int) -> dict:
    n_pre = len(wide_pre)
    Y, X, _, b = preparar(wide_pre, list(grupo), n_pre)
    pod = poder_historico(Y, X, b, n_pre, n_teste)
    ok = pod[(pod["efeito_pct"] > 0) & (pod["poder"] >= 0.8)]
    mde = float(ok["efeito_pct"].min()) if len(ok) else np.inf
    S, _ = ajustar(Y, X, n_pre)
    real, sint = Y @ b, S @ b
    mape = float(np.mean(np.abs(real - sint) / real) * 100)
    nulos = placebo_tempo(Y, X, b, n_pre, n_teste, min_treino=56, passo=4)
    return {"mde_pct": mde, "falso_positivo": float(pod.loc[pod["efeito_pct"] == 0, "poder"].iloc[0]),
            "erro_placebo_pct": float(np.sqrt(np.mean(nulos ** 2)) * 100), "mape_pre": mape,
            "poder": pod["poder"].round(3).tolist()}


def selecionar_mercados(df: pd.DataFrame, cidades: pd.DataFrame, fim_pre, n_teste: int = 28,
                        tamanho: int = 3, n_finalistas: int = 14, excluir: tuple = ("São Paulo", "Rio de Janeiro"),
                        teto_custo_pct: float = 12.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Etapa 1: nota de cada cidade sozinha. Etapa 2: combina as finalistas em grupos.

    Custo da TV ~ proporcional à população (proxy de preço da praça).
    Devolve (ranking_individual, ranking_grupos).
    """
    wide = matriz(df).loc[: pd.Timestamp(fim_pre)]
    pop = cidades.set_index("cidade")["populacao_mil"]
    pop_total = pop.sum()

    indiv = []
    for c in wide.columns:
        if c in excluir:
            continue
        m = avaliar_grupo(wide, [c], n_teste)
        indiv.append({"cidade": c, **m, "custo_pct": pop[c] / pop_total * 100})
    indiv = (pd.DataFrame(indiv).sort_values(["mde_pct", "erro_placebo_pct"])
             .reset_index(drop=True))

    finalistas = indiv.head(n_finalistas)["cidade"].tolist()
    regiao = cidades.set_index("cidade")["regiao"]
    grupos = []
    for g in combinations(finalistas, tamanho):
        if regiao[list(g)].nunique() < tamanho:   # uma cidade por região: um choque regional não contamina o teste todo
            continue
        custo = pop[list(g)].sum() / pop_total * 100
        m = avaliar_grupo(wide, list(g), n_teste)
        grupos.append({"grupo": " + ".join(g), "cidades": list(g), **m, "custo_pct": custo,
                       "cabe_orcamento": custo <= teto_custo_pct})
    grupos = (pd.DataFrame(grupos).sort_values(["mde_pct", "falso_positivo", "erro_placebo_pct"])
              .reset_index(drop=True))
    return indiv, grupos


# ---------------------------------------------------------------------------
# 5. Exemplo didático: como o algoritmo chega nos pesos (números pequenos)
# ---------------------------------------------------------------------------
def projetar_simplex(v: np.ndarray) -> np.ndarray:
    """Ponto mais próximo de v com todos >= 0 e soma 1 (Duchi et al., 2008)."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u)
    k = np.nonzero(u * np.arange(1, len(v) + 1) > (css - 1))[0][-1]
    tau = (css[k] - 1) / (k + 1)
    return np.maximum(v - tau, 0)


def pesos_passo_a_passo(y: np.ndarray, X: np.ndarray, passo: float = 2.0, n_iter: int = 300):
    """Gradiente descendente projetado: começa com pesos iguais e, a cada passo,
    mexe os pesos na direção em que o erro cai, sem deixar nenhum negativo e
    mantendo a soma = 1. Devolve o histórico (pesos e soma dos erros²)."""
    w = np.full(X.shape[1], 1 / X.shape[1])
    hist = []
    for it in range(n_iter + 1):
        erro = y - X @ w
        hist.append((it, *w, float(np.sum(erro ** 2))))
        grad = -2 * X.T @ erro
        w = projetar_simplex(w - passo * grad)
    return pd.DataFrame(hist, columns=["iteracao", *[f"w_{i}" for i in range(X.shape[1])], "soma_erros2"])


def exemplo_didatico() -> dict:
    """Uma cidade testada ('Alvo') e 3 cidades sem TV (A, B, C), 6 semanas antes e 2 com TV."""
    semanas = [f"S{i}" for i in range(1, 9)]
    brutos = pd.DataFrame({
        "Alvo": [291, 291, 318, 304, 296, 300, 370, 385],
        "A": [180, 200, 220, 190, 210, 200, 230, 240],
        "B": [105, 95, 100, 110, 90, 100, 108, 112],
        "C": [50, 55, 45, 50, 52, 48, 49, 51],
    }, index=semanas).astype(float)
    n_pre = 6
    medias = brutos.iloc[:n_pre].mean()
    idx = brutos / medias
    y, X = idx["Alvo"].to_numpy(), idx[["A", "B", "C"]].to_numpy()
    hist = pesos_passo_a_passo(y[:n_pre], X[:n_pre])
    hist.columns = ["iteracao", "w_A", "w_B", "w_C", "soma_erros2"]
    w_final = hist.iloc[-1][["w_A", "w_B", "w_C"]].to_numpy()

    def tabela(w):
        g = X @ w
        t = pd.DataFrame({"y_alvo": y, "gemea": g, "erro": y - g, "erro2": (y - g) ** 2}, index=semanas)
        return t

    return {"brutos": brutos, "medias": medias, "indices": idx, "n_pre": n_pre, "historico": hist,
            "w_inicial": np.full(3, 1 / 3), "w_final": w_final,
            "tab_inicial": tabela(np.full(3, 1 / 3)), "tab_final": tabela(w_final)}


def ensaios_detalhe(df: pd.DataFrame, grupo: list[str], fim_pre, theta: float, n_teste: int = 28,
                    min_treino: int = 56, passo: int = 3, alfa: float = 0.10) -> pd.DataFrame:
    """Lista cada ensaio no passado (campanha de mentira com efeito θ) e se o GeoLift percebeu."""
    wide = matriz(df).loc[: pd.Timestamp(fim_pre)]
    n_pre = len(wide)
    Y, X, _, b = preparar(wide, list(grupo), n_pre)
    linhas = []
    for inicio in range(min_treino, n_pre - n_teste + 1, passo):
        Yt = Y[: inicio + n_teste].copy()
        Yt[inicio:] = Yt[inicio:] * (1 + theta)
        p = p_valor_conforme(Yt, X[: inicio + n_teste], b, inicio, 0.0)
        linhas.append({"inicio": wide.index[inicio], "fim": wide.index[inicio + n_teste - 1],
                       "p_valor": p, "detectou": p <= alfa})
    return pd.DataFrame(linhas)
