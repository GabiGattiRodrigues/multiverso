"""Exemplo mastigado de como o controle sintético chega nos pesos (aba 🧬 do app).

Números pequenos e redondos: 1 cidade testada (Alvo), 3 cidades sem TV (A, B, C),
6 semanas antes da TV e 2 semanas com TV. Tudo calculado de verdade pelo motor.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from geolift.motor import exemplo_didatico

CORES = {"w_A": "#1F6FEB", "w_B": "#E0A100", "w_C": "#E4572E"}


def _n(x: float, casas: int, lang: str) -> str:
    s = f"{x:.{casas}f}"
    return s.replace(".", ",") if lang == "pt" else s


def _pct(x: float, casas: int, lang: str) -> str:
    return ("+" if x > 0 else "") + _n(x * 100, casas, lang) + "%"


@st.cache_data
def _dados():
    return exemplo_didatico()


def renderizar(lang: str, layout) -> None:
    e = _dados()
    pt = lang == "pt"
    n = lambda x, c=3: _n(x, c, lang)  # noqa: E731
    p = lambda x, c=1: _pct(x, c, lang)  # noqa: E731
    br, md, idx, n_pre = e["brutos"], e["medias"], e["indices"], e["n_pre"]
    wi, wf = e["w_inicial"], e["w_final"]
    ti, tf, hist = e["tab_inicial"], e["tab_final"], e["historico"]
    sse_i = float((ti["erro"].iloc[:n_pre] ** 2).sum() * 1e4)
    sse_f = float((tf["erro"].iloc[:n_pre] ** 2).sum() * 1e4)
    semanas = list(br.index)
    sl = (lambda s: s) if pt else (lambda s: s.replace("S", "W"))  # noqa: E731
    rot_sem = lambda s: sl(s) + (" (TV)" if semanas.index(s) >= n_pre else "")  # noqa: E731
    nl = lambda x, c=3: n(x, c).replace(",", "{,}")  # noqa: E731  (vírgula decimal dentro do LaTeX)

    st.markdown("### 🧮 " + ("Como o algoritmo chega nos pesos: exemplo mastigado" if pt
                             else "How the algorithm finds the weights: a worked example"))
    st.markdown(
        "Para enxergar a conta inteira, vamos usar um exemplo pequeno: **1 cidade testada (Alvo)**, **3 cidades sem "
        "TV (A, B e C)**, **6 semanas antes** da TV e **2 semanas com TV**. No projeto é exatamente a mesma conta, "
        "só que com 37 cidades no lugar de 3 e 119 dias no lugar de 6 semanas." if pt else
        "To see the whole calculation, let's use a small example: **1 tested city (Target)**, **3 cities without TV "
        "(A, B and C)**, **6 weeks before** TV and **2 weeks with TV**. The project does exactly the same math, just "
        "with 37 cities instead of 3 and 119 days instead of 6 weeks.")

    # Passo 1 -------------------------------------------------------------
    st.markdown("#### " + ("Passo 1 · Os dados: contas novas por semana" if pt else "Step 1 · The data: new accounts per week"))
    t1 = br.astype(int).copy()
    t1.index = [rot_sem(s) for s in semanas]
    t1.loc["Média" if pt else "Mean"] = md.round(0).astype(int)
    if not pt:
        t1 = t1.rename(columns={"Alvo": "Target"})
    st.dataframe(t1, width="stretch")

    # Passo 2 -------------------------------------------------------------
    st.markdown("#### " + ("Passo 2 · Colocar todo mundo na mesma régua (índice)" if pt
                           else "Step 2 · Put everyone on the same ruler (index)"))
    st.markdown(
        f"O Alvo abre ~{n(md['Alvo'], 0)} contas por semana e a cidade C só ~{n(md['C'], 0)}. Para comparar formatos e não "
        "tamanhos, dividimos cada semana pela **média das 6 semanas antes da TV** daquela cidade. Índice 1,00 = "
        "uma semana normal; 1,10 = 10% acima do normal.\n\n"
        f"- A na S1: {int(br.loc['S1', 'A'])} ÷ {n(md['A'], 0)} = **{n(idx.loc['S1', 'A'], 2)}**\n"
        f"- Alvo na S1: {int(br.loc['S1', 'Alvo'])} ÷ {n(md['Alvo'], 0)} = **{n(idx.loc['S1', 'Alvo'], 2)}**"
        if pt else
        f"Target opens ~{n(md['Alvo'], 0)} accounts a week and city C only ~{n(md['C'], 0)}. To compare shapes, not sizes, "
        "we divide each week by that city's **average of the 6 weeks before TV**. Index 1.00 = a normal week; "
        "1.10 = 10% above normal.\n\n"
        f"- A in W1: {int(br.loc['S1', 'A'])} ÷ {n(md['A'], 0)} = **{n(idx.loc['S1', 'A'], 2)}**\n"
        f"- Target in W1: {int(br.loc['S1', 'Alvo'])} ÷ {n(md['Alvo'], 0)} = **{n(idx.loc['S1', 'Alvo'], 2)}**")
    t2 = idx.map(lambda v: n(v, 3))
    t2.index = [rot_sem(s) for s in semanas]
    st.dataframe(t2.rename(columns={"Alvo": "Alvo (y)" if pt else "Target (y)", "A": "A (x₁)", "B": "B (x₂)",
                                    "C": "C (x₃)"}), width="stretch")

    # Passo 3 -------------------------------------------------------------
    st.markdown("#### " + ("Passo 3 · Peso ANTES: o chute inicial" if pt else "Step 3 · Weights BEFORE: the first guess"))
    s1 = idx.loc["S1"]
    st.markdown(
        "Sem saber nada, o algoritmo começa dando **o mesmo peso para todas**: ⅓ para A, ⅓ para B e ⅓ para C "
        "(33,3% cada, somando 100%). A gêmea de cada semana é a mistura:" if pt else
        "Knowing nothing yet, the algorithm starts by giving **every city the same weight**: ⅓ to A, ⅓ to B and ⅓ "
        "to C (33.3% each, adding up to 100%). Each week's twin is the blend:")
    st.latex(r"\text{%s}_{%s} = %s \times %s + %s \times %s + %s \times %s = %s" % (
        "gêmea" if pt else "twin", sl("S1"), nl(wi[0]), nl(s1['A'], 2), nl(wi[1]), nl(s1['B'], 2), nl(wi[2]),
        nl(s1['C'], 2), nl(ti.loc['S1', 'gemea'])))
    st.markdown(
        f"O Alvo de verdade foi **{n(s1['Alvo'])}**, então o **erro** da S1 é {n(s1['Alvo'])} − {n(ti.loc['S1', 'gemea'])} "
        f"= **{p(ti.loc['S1', 'erro'])}**. Fazendo isso nas 6 semanas e somando os erros ao quadrado (o quadrado faz "
        "erro pra cima e pra baixo contarem igual, e pune mais os erros grandes):" if pt else
        f"The real Target was **{n(s1['Alvo'])}**, so W1's **error** is {n(s1['Alvo'])} − {n(ti.loc['S1', 'gemea'])} "
        f"= **{p(ti.loc['S1', 'erro'])}**. Doing this for all 6 weeks and adding up the squared errors (squaring "
        "makes errors up and down count the same, and punishes big errors more):")

    def tab_erros(t):
        x = t.iloc[:n_pre].copy()
        x.index = [sl(i) for i in x.index]
        return pd.DataFrame({
            ("Alvo (y)" if pt else "Target (y)"): x["y_alvo"].map(lambda v: n(v, 3)),
            ("Gêmea" if pt else "Twin"): x["gemea"].map(lambda v: n(v, 3)),
            ("Erro" if pt else "Error"): x["erro"].map(lambda v: p(v, 2)),
            ("Erro²" if pt else "Error²"): (x["erro"] ** 2 * 1e4).map(lambda v: n(v, 2)),
        })
    a, b = st.columns(2)
    with a:
        st.caption("Pesos iguais (⅓, ⅓, ⅓)" if pt else "Equal weights (⅓, ⅓, ⅓)")
        st.dataframe(tab_erros(ti), width="stretch")
        st.markdown(("**Soma dos erros² = %s**" if pt else "**Sum of errors² = %s**") % n(sse_i, 1))
    with b:
        st.markdown(
            f"Repare na **S3**: o Alvo subiu ({n(idx.loc['S3', 'Alvo'], 2)}), A também subiu ({n(idx.loc['S3', 'A'], 2)}), "
            f"mas C **caiu** ({n(idx.loc['S3', 'C'], 2)}). E na **S2** C subiu ({n(idx.loc['S2', 'C'], 2)}) enquanto o Alvo "
            "ficou abaixo do normal. C anda na contramão do Alvo: dar peso a ela atrapalha a imitação." if pt else
            f"Look at **W3**: Target went up ({n(idx.loc['S3', 'Alvo'], 2)}), A went up too ({n(idx.loc['S3', 'A'], 2)}), "
            f"but C **went down** ({n(idx.loc['S3', 'C'], 2)}). And in **W2** C went up ({n(idx.loc['S2', 'C'], 2)}) while "
            "Target was below normal. C moves against Target: giving it weight hurts the imitation.")
        st.caption("(erros em pontos percentuais; erro² em %²)" if pt else "(errors in percentage points; error² in %²)")

    # Passo 4 -------------------------------------------------------------
    st.markdown("#### " + ("Passo 4 · Ajustando os pesos, rodada por rodada" if pt
                           else "Step 4 · Adjusting the weights, round by round"))
    st.markdown(
        "Agora o algoritmo repete um ciclo simples, como quem acerta o tempero provando a comida:\n"
        "1. **Prova:** calcula a gêmea com os pesos atuais e mede a soma dos erros².\n"
        "2. **Vê pra que lado melhora:** para cada cidade, pergunta \"se eu der um pouquinho mais de peso pra ela, "
        "o erro cai ou sobe?\" (isso é a derivada, ou gradiente).\n"
        "3. **Mexe um pouquinho:** aumenta o peso de quem ajuda e diminui o de quem atrapalha.\n"
        "4. **Aplica as regras:** se algum peso ficou negativo, vira 0; e todos são reajustados para somar 100%.\n"
        "5. **Repete** até o erro parar de cair." if pt else
        "Now the algorithm repeats a simple cycle, like adjusting the seasoning by tasting the food:\n"
        "1. **Taste:** compute the twin with the current weights and measure the sum of errors².\n"
        "2. **See which way is better:** for each city, ask \"if I give it a bit more weight, does the error go down "
        "or up?\" (that's the derivative, or gradient).\n"
        "3. **Nudge:** increase the weight of cities that help and decrease those that hurt.\n"
        "4. **Apply the rules:** any negative weight becomes 0, and all are rescaled to add up to 100%.\n"
        "5. **Repeat** until the error stops falling.")
    linhas = [0, 1, 2, 3, 5, 10, 15, 20, len(hist) - 1]
    th = hist.iloc[linhas].copy()
    th = pd.DataFrame({
        ("Rodada" if pt else "Round"): th["iteracao"].astype(int).astype(str).where(th.index != len(hist) - 1,
                                                                                   "final"),
        "w_A": (th["w_A"] * 100).map(lambda v: n(v, 1) + "%"),
        "w_B": (th["w_B"] * 100).map(lambda v: n(v, 1) + "%"),
        "w_C": (th["w_C"] * 100).map(lambda v: n(v, 1) + "%"),
        ("Soma dos erros²" if pt else "Sum of errors²"): (th["soma_erros2"] * 1e4).map(lambda v: n(v, 2)),
    })
    a, b = st.columns([1, 1.2])
    a.dataframe(th, width="stretch", hide_index=True)
    h = hist.iloc[:41]
    fig = go.Figure()
    for col, nome in [("w_A", "A"), ("w_B", "B"), ("w_C", "C")]:
        fig.add_trace(go.Scatter(x=h["iteracao"], y=h[col] * 100, name=f"{'peso de' if pt else 'weight of'} {nome}",
                                 line=dict(color=CORES[col], width=3)))
    fig.add_trace(go.Scatter(x=h["iteracao"], y=h["soma_erros2"] * 1e4, name=("soma dos erros²" if pt else "sum of errors²"),
                             line=dict(color="#0B2545", dash="dot"), yaxis="y2"))
    fig = layout(fig, 360, xaxis_title=("rodada" if pt else "round"), yaxis_title=("peso (%)" if pt else "weight (%)"),
                 yaxis_range=[0, 65],
                 yaxis2=dict(overlaying="y", side="right", showgrid=False, range=[0, 68],
                             title=("soma dos erros²" if pt else "sum of errors²")))
    fig.update_layout(legend=dict(orientation="h", y=-0.25, x=0))
    b.plotly_chart(fig, width="stretch")
    zero = int(hist.loc[hist["w_C"] <= 1e-9, "iteracao"].iloc[0])
    st.markdown(
        f"Na rodada 1, A sobe de 33,3% para {n(hist.loc[1, 'w_A'] * 100, 1)}% e C cai para {n(hist.loc[1, 'w_C'] * 100, 1)}%. "
        f"Na rodada {zero}, C **bate no zero e fica lá**: ela até \"queria\" um peso negativo, mas a regra não deixa. "
        f"Daí em diante só A e B se ajustam, até o erro parar de cair." if pt else
        f"In round 1, A goes from 33.3% to {n(hist.loc[1, 'w_A'] * 100, 1)}% and C drops to {n(hist.loc[1, 'w_C'] * 100, 1)}%. "
        f"In round {zero}, C **hits zero and stays there**: it \"wanted\" a negative weight, but the rule won't allow it. "
        "From then on only A and B adjust, until the error stops falling.")

    # Passo 5 -------------------------------------------------------------
    st.markdown("#### " + ("Passo 5 · Peso DEPOIS: a receita final" if pt else "Step 5 · Weights AFTER: the final recipe"))
    resumo = pd.DataFrame({
        "": ["A", "B", "C", ("Soma" if pt else "Sum"), ("Soma dos erros²" if pt else "Sum of errors²")],
        ("Peso antes (chute)" if pt else "Weight before (guess)"):
            [n(v * 100, 1) + "%" for v in wi] + ["100%", n(sse_i, 1)],
        ("Peso depois (final)" if pt else "Weight after (final)"):
            [n(v * 100, 2) + "%" for v in wf] + ["100%", n(sse_f, 2)],
    })
    st.dataframe(resumo, width="stretch", hide_index=True)
    st.latex(r"\text{%s}_{%s} = %s \times %s + %s \times %s + %s \times %s = %s" % (
        "gêmea" if pt else "twin", sl("S1"), nl(wf[0], 4), nl(s1['A'], 2), nl(wf[1], 4), nl(s1['B'], 2), nl(wf[2], 0),
        nl(s1['C'], 2), nl(tf.loc['S1', 'gemea'])))
    st.markdown(
        f"Agora a gêmea da S1 dá {n(tf.loc['S1', 'gemea'])} contra {n(s1['Alvo'])} do Alvo: erro de "
        f"**{p(tf.loc['S1', 'erro'], 2)}** (antes era {p(ti.loc['S1', 'erro'])}). A soma dos erros² caiu de "
        f"**{n(sse_i, 1)} para {n(sse_f, 2)}**. A receita da gêmea do Alvo é: "
        f"**{n(wf[0] * 100, 1)}% de A + {n(wf[1] * 100, 1)}% de B + 0% de C**." if pt else
        f"Now W1's twin is {n(tf.loc['S1', 'gemea'])} vs Target's {n(s1['Alvo'])}: an error of "
        f"**{p(tf.loc['S1', 'erro'], 2)}** (it was {p(ti.loc['S1', 'erro'])}). The sum of errors² fell from "
        f"**{n(sse_i, 1)} to {n(sse_f, 2)}**. Target's twin recipe is: "
        f"**{n(wf[0] * 100, 1)}% A + {n(wf[1] * 100, 1)}% B + 0% C**.")
    st.dataframe(tab_erros(tf), width="stretch")

    # Passo 6 -------------------------------------------------------------
    st.markdown("#### " + ("Passo 6 · Usando a receita nas semanas com TV" if pt else "Step 6 · Using the recipe in the TV weeks"))
    base = md["Alvo"]
    linhas_tv = []
    for s in semanas[n_pre:]:
        g = tf.loc[s, "gemea"]
        linhas_tv.append({
            ("Semana" if pt else "Week"): sl(s),
            ("Gêmea (índice)" if pt else "Twin (index)"): f"{n(wf[0], 4)}×{n(idx.loc[s, 'A'], 2)} + {n(wf[1], 4)}×{n(idx.loc[s, 'B'], 2)} = {n(g)}",
            ("Gêmea (contas)" if pt else "Twin (accounts)"): f"{n(g)} × {n(base, 0)} = {n(g * base, 1)}",
            ("Alvo real" if pt else "Real Target"): int(br.loc[s, "Alvo"]),
            ("Efeito da TV" if pt else "TV effect"): ("+" if br.loc[s, "Alvo"] > g * base else "") + n(br.loc[s, "Alvo"] - g * base, 1),
        })
    st.dataframe(pd.DataFrame(linhas_tv), width="stretch", hide_index=True)
    real_tv = br["Alvo"].iloc[n_pre:].sum()
    gem_tv = (tf["gemea"].iloc[n_pre:] * base).sum()
    st.markdown(
        "A receita **não muda** quando a TV entra: os pesos foram aprendidos só com as semanas sem TV e agora "
        "são aplicados às cidades A, B e C (que não viram a TV). Multiplicando o índice pela média do Alvo, voltamos "
        f"para contas. Somando as 2 semanas: o Alvo abriu {int(br['Alvo'].iloc[n_pre])} + {int(br['Alvo'].iloc[n_pre + 1])} = "
        f"**{int(real_tv)}** contas e a gêmea {n(tf['gemea'].iloc[n_pre] * base, 1)} + {n(tf['gemea'].iloc[n_pre + 1] * base, 1)} = "
        f"**{n(gem_tv, 1)}**. **Efeito da TV = {int(real_tv)} ÷ {n(gem_tv, 1)} − 1 = {p(real_tv / gem_tv - 1)}** "
        f"(≈ {n(real_tv - gem_tv, 0)} contas a mais)." if pt else
        "The recipe **doesn't change** when TV starts: the weights were learned only from the no-TV weeks and are now "
        "applied to cities A, B and C (which didn't see TV). Multiplying the index by Target's mean brings us back "
        f"to accounts. Adding the 2 weeks: Target opened {int(br['Alvo'].iloc[n_pre])} + {int(br['Alvo'].iloc[n_pre + 1])} = "
        f"**{int(real_tv)}** accounts and the twin {n(tf['gemea'].iloc[n_pre] * base, 1)} + {n(tf['gemea'].iloc[n_pre + 1] * base, 1)} = "
        f"**{n(gem_tv, 1)}**. **TV effect = {int(real_tv)} ÷ {n(gem_tv, 1)} − 1 = {p(real_tv / gem_tv - 1)}** "
        f"(≈ {n(real_tv - gem_tv, 0)} extra accounts).")

    st.caption(
        "No código do projeto, os pesos finais saem direto de um solver (NNLS, scipy) em vez das rodadas acima — "
        "o resultado é o mesmo; as rodadas existem aqui só para mostrar o caminho." if pt else
        "In the project code, the final weights come straight from a solver (NNLS, scipy) instead of the rounds above — "
        "the result is the same; the rounds are here only to show the path.")
