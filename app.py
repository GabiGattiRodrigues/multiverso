"""Multiverso — GeoLift com controle sintético (app Streamlit, PT/EN).

Rodar:  streamlit run app.py
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import didatico

from geolift.motor import ensaios_detalhe, gemea_de_controle, residuos_hipotese, rodar_geolift
from textos import (UI, br, conferencia, txt_como_funciona, txt_conta_depois, txt_conta_intro,
                    txt_conta_regras, txt_conta_resultado, txt_dados, txt_gemea, txt_mapa, veredito)
from textos_abas import (txt_case, txt_comparar_grupos, txt_conforme, txt_conforme_resultado, txt_curva_p,
                         txt_desenho_intro, txt_ensaios, txt_fila, txt_funil, txt_lab_intro, txt_lab_veredito,
                         txt_lab_exemplo, txt_lab_leitura, txt_poder, txt_ranking, txt_rob_intro)

RAIZ = Path(__file__).parent
DADOS = RAIZ / "dados"
AZUL_ESCURO, AZUL, AZUL_CLARO, CORAL, CINZA = "#0B2545", "#1F6FEB", "#8DB8F2", "#E4572E", "#A0AEC0"
CORES_CIDADE = ["#E4572E", "#E0A100", "#14A38B"]   # uma cor por cidade testada (e pela sua gêmea)
CAC_META_PADRAO = 400

st.set_page_config(page_title="Multiverso · GeoLift", page_icon="🌌", layout="wide")


# ---------------------------------------------------------------------------
# Dados e modelo (com cache)
# ---------------------------------------------------------------------------
@st.cache_data
def carregar():
    df = pd.read_csv(DADOS / "contas_diarias.csv", parse_dates=["data"])
    cid = pd.read_csv(DADOS / "cidades.csv")
    meta = json.loads((DADOS / "campanha.json").read_text(encoding="utf-8"))
    verdade = pd.read_csv(DADOS / "verdade.csv", parse_dates=["data"])
    indiv = pd.read_csv(DADOS / "selecao_individual.csv")
    grupos = pd.read_csv(DADOS / "selecao_grupos.csv")
    contorno = json.loads((DADOS / "brasil_contorno.json").read_text())
    return df, cid, meta, verdade, indiv, grupos, contorno


@st.cache_data
def resultado(df, tratadas, ini, fim):
    return rodar_geolift(df, list(tratadas), ini, fim)


@st.cache_data
def ensaios(df, grupo, fim_pre, theta):
    return ensaios_detalhe(df, list(grupo), fim_pre, theta)


@st.cache_data
def hipotese(df, tratadas, ini, fim, theta):
    return residuos_hipotese(df, list(tratadas), ini, fim, theta)


@st.cache_data
def placebo_cidade(df, tratadas, cidade, ini, fim):
    return gemea_de_controle(df, list(tratadas), cidade, ini, fim)


df, cid, meta, verdade, indiv, grupos, contorno = carregar()
TRAT = tuple(meta["cidades_tratadas"])
r = resultado(df, TRAT, meta["inicio_teste"], meta["fim_teste"])
COR = dict(zip(TRAT, CORES_CIDADE))

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    for nome in ("multiverso.jpg", "multiverso.png", "multiverso.webp"):
        if (RAIZ / "assets" / nome).exists():
            _, meio, _ = st.columns([1, 4, 1])
            meio.image(str(RAIZ / "assets" / nome), width="stretch")
            break
    lang = "en" if st.radio("🌐", ["Português", "English"], horizontal=True, key="lang") == "English" else "pt"
    t = UI[lang]
    st.markdown(t["cenario"])
    invest = st.number_input(t["invest"], value=int(meta["investimento_tv"]), step=10_000)
    cac_meta = st.number_input(t["cac_meta"], value=CAC_META_PADRAO, step=10)
    st.caption(t["rodape"])

st.title(f"🌌 {t['titulo']}")
st.caption(t["subtitulo"])

# dicionário com os números usados nos textos
NOMES_COR = {"pt": ["laranja", "amarelo", "verde"], "en": ["orange", "yellow", "green"]}
c = {
    "lift": r.lift_pct, "incr": r.incrementais, "ic_lo": r.ic_baixo, "ic_hi": r.ic_alto, "p": r.p_valor,
    "cac": invest / r.incrementais, "cac_meta": cac_meta, "mape": r.mape_pre, "r2": r.r2_pre,
    "cidades_txt": ", ".join(TRAT[:-1]) + (" e " if lang == "pt" else " and ") + TRAT[-1],
    "v_lift": meta["verdade_lift_pct"], "v_incr": meta["verdade_incrementais"],
    "cores_txt": ", ".join(f"{cd} = {n}" for cd, n in zip(TRAT, NOMES_COR[lang])),
    "mde": float(grupos.iloc[0]["mde_pct"]), "n_finalistas": 14, "teto": 12,
    "rank": int(r.placebos_espaco.index[r.placebos_espaco["tratado"]][0]) + 1,
    "n_rank": len(r.placebos_espaco), "p_esp": r.p_valor_espaco,
}

# números extras para O case, Desenho do teste e Robustez
FIM_PRE = (pd.Timestamp(meta["inicio_teste"]) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
_datas_pre = pd.date_range(df["data"].min(), FIM_PRE)
_inicios = list(range(56, len(_datas_pre) - 28 + 1, 3))
_fd = (lambda d: d.strftime("%d/%m")) if lang == "pt" else (lambda d: d.strftime("%b %d"))
_gb = grupos[grupos["cabe_orcamento"]]
_gm = _gb[_gb["mde_pct"] == _gb["mde_pct"].min()]
_pe = r.placebos_espaco
_top = _pe[~_pe["tratado"]].iloc[0]
_cac = invest / r.incrementais
c.update({
    "invest_txt": br(invest), "incr_txt": br(r.incrementais), "cac_txt": br(_cac), "cac_meta_txt": br(cac_meta),
    "custo_pct": float(grupos.iloc[0]["custo_pct"]),
    "n_janelas": len(_inicios), "ens_ini": _fd(_datas_pre[_inicios[3]]), "ens_fim": _fd(_datas_pre[_inicios[3] + 27]),
    "ens_primeiro": _fd(_datas_pre[_inicios[0]]), "ens_ultimo": _fd(_datas_pre[_inicios[-1]]),
    "fp": float(grupos.iloc[0]["falso_positivo"]), "poder25": float(ast.literal_eval(grupos.iloc[0]["poder"])[1]),
    "n_cidades": len(indiv), "n_final": 14, "n_grupos": len(grupos), "n_orc": len(_gb), "n_mde": len(_gm),
    "n_fp": int((_gm["falso_positivo"] == _gm["falso_positivo"].min()).sum()),
    "razao_trat": float(_pe.loc[_pe["tratado"], "razao_rmspe"].iloc[0]),
    "top_placebo": _top["cidade"], "razao_top": float(_top["razao_rmspe"]),
})


def layout(fig, h=420, hovermode="x unified", **kw):
    kw = {k: v for k, v in kw.items() if v is not None}   # title=None virava "undefined" no gráfico
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=40, b=10), template="plotly_white",
                      legend=dict(orientation="h", y=1.1, x=0), hovermode=hovermode, **kw)
    return fig


def grafico_real_vs_gemea(res, titulo=None):
    fig = go.Figure()
    fig.add_vrect(x0=res.datas[res.n_pre], x1=res.datas[-1], fillcolor=AZUL_CLARO, opacity=0.18,
                  line_width=0, annotation_text=t["inicio_tv"], annotation_position="top left")
    fig.add_trace(go.Scatter(x=res.datas, y=res.real, name=t["real"], line=dict(color=AZUL_ESCURO, width=2)))
    fig.add_trace(go.Scatter(x=res.datas, y=res.sintetico, name=t["gemea"],
                             line=dict(color=AZUL, width=2, dash="dot")))
    return layout(fig, yaxis_title=t["contas_dia"], title=titulo)


abas = st.tabs(t["abas"])

# ---------------------------------------------------------------------------
# 0. O case
# ---------------------------------------------------------------------------
with abas[0]:
    st.markdown(txt_case(c, lang))

# ---------------------------------------------------------------------------
# 1. Resultado
# ---------------------------------------------------------------------------
with abas[1]:
    k = st.columns(5)
    k[0].metric(t["lift"], f"+{r.lift_pct:.1f}%")
    k[1].metric(t["incr"], br(r.incrementais))
    k[2].metric(t["cac"], f"R$ {br(c['cac'])}")
    k[3].metric(t["pval"], f"{r.p_valor:.3f}")
    k[4].metric(t["ic"], f"{r.ic_baixo:.1f}–{r.ic_alto:.1f}%")
    st.markdown(veredito(c, lang))
    st.plotly_chart(grafico_real_vs_gemea(r), width="stretch")

    post = slice(r.n_pre, None)
    acum = np.cumsum(r.real[post] - r.sintetico[post])
    v = verdade[verdade["cidade"].isin(TRAT) & (verdade["data"] >= meta["inicio_teste"])
                & (verdade["data"] <= meta["fim_teste"])].groupby("data")[
        ["contas_esperadas_com_tv", "contas_esperadas_sem_tv"]].sum()
    acum_v = np.cumsum(v["contas_esperadas_com_tv"] - v["contas_esperadas_sem_tv"]).to_numpy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r.datas[post], y=acum, name="GeoLift", fill="tozeroy",
                             line=dict(color=AZUL, width=2)))
    fig.add_trace(go.Scatter(x=r.datas[post], y=acum_v, name=t["verdade"],
                             line=dict(color=CORAL, width=2, dash="dash")))
    st.plotly_chart(layout(fig, 320, yaxis_title=t["acumulado"]), width="stretch")
    st.info(conferencia(c, lang))

    st.markdown("#### " + ("Cidade por cidade" if lang == "pt" else "City by city"))
    cols = st.columns(3)
    for col, cd in zip(cols, TRAT):
        vc = verdade[(verdade["cidade"] == cd) & (verdade["data"] >= meta["inicio_teste"])
                     & (verdade["data"] <= meta["fim_teste"])]
        v_cd = (vc["contas_esperadas_com_tv"].sum() / vc["contas_esperadas_sem_tv"].sum() - 1) * 100
        col.markdown(f"<span style='color:{COR[cd]};font-weight:700'>● {cd}</span> &nbsp; "
                     f"**{r.lift_cidade[cd]:+.1f}%** · {t['verdade'].split(' ')[0].lower()} {v_cd:+.1f}%",
                     unsafe_allow_html=True)
        jan = slice(r.n_pre - 35, None)
        f = go.Figure()
        f.add_vrect(x0=r.datas[r.n_pre], x1=r.datas[-1], fillcolor=AZUL_CLARO, opacity=0.18, line_width=0)
        f.add_trace(go.Scatter(x=r.datas[jan], y=r.real_cidade[cd].iloc[jan], name=t["real"],
                               line=dict(color=COR[cd], width=2)))
        f.add_trace(go.Scatter(x=r.datas[jan], y=r.sint_cidade[cd].iloc[jan], name=t["gemea"],
                               line=dict(color=AZUL_ESCURO, width=1.5, dash="dot")))
        col.plotly_chart(layout(f, 230, showlegend=False), width="stretch")
    st.caption("Sozinha, cada cidade oscila mais (o efeito de cada uma varia em torno da verdade); somadas, o ruído "
               "se compensa — por isso a leitura principal é a do conjunto." if lang == "pt" else
               "Alone, each city is noisier (each one's effect scatters around the truth); summed, the noise "
               "cancels out — that's why the main readout is the combined one.")

# ---------------------------------------------------------------------------
# 2. Mapa
# ---------------------------------------------------------------------------
def mapa(foco="todas", h=620):
    """Estrelas = cidades com TV. Bolinhas = doadoras, na cor da gêmea em que mais pesam."""
    W = r.pesos * 100
    m = cid.copy().set_index("cidade")
    fig = go.Figure()
    lon, lat = zip(*contorno)
    fig.add_trace(go.Scatter(x=lon, y=lat, mode="lines", line=dict(color=CINZA, width=1), fill="toself",
                             fillcolor="rgba(141,184,242,0.08)", hoverinfo="skip", showlegend=False))
    alvos = list(TRAT) if foco == "todas" else [foco]
    Wf = W[alvos]
    dono = Wf.idxmax(axis=1).where(Wf.max(axis=1) > 0.5)
    detalhe = W.apply(lambda row: "<br>".join(f"{t['leg_doad']} {k}: {v:.1f}%" for k, v in row.items() if v > 0.5)
                      or "—", axis=1)
    fora = [cd for cd in m.index if cd not in TRAT and pd.isna(dono.get(cd))]
    fig.add_trace(go.Scatter(x=m.loc[fora, "lon"], y=m.loc[fora, "lat"], mode="markers", name=t["leg_fora"],
                             marker=dict(color=CINZA, size=7, symbol="circle-open"),
                             text=fora, hovertemplate="%{text}<extra></extra>"))
    for cd in alvos:
        doad = dono[dono == cd].index
        peso = Wf.loc[doad, cd]
        fig.add_trace(go.Scatter(
            x=m.loc[doad, "lon"], y=m.loc[doad, "lat"], mode="markers+text", name=f"{t['leg_doad']} {cd}",
            marker=dict(color=COR[cd], size=8 + peso * 1.4, opacity=0.75, line=dict(color="white", width=1)),
            text=[d if p >= 9 else "" for d, p in zip(doad, peso)], textposition="bottom center",
            textfont=dict(size=10, color=AZUL_ESCURO),
            customdata=np.stack([doad, detalhe[doad]], axis=1),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>"))
    for cd in alvos:
        fig.add_trace(go.Scatter(
            x=[m.loc[cd, "lon"]], y=[m.loc[cd, "lat"]], mode="markers+text", name=f"{cd} ({t['leg_trat']})",
            marker=dict(color=COR[cd], size=22, symbol="star", line=dict(color=AZUL_ESCURO, width=1.5)),
            text=[f"<b>{cd}</b>"], textposition="middle right", textfont=dict(size=13, color=AZUL_ESCURO),
            hovertemplate=f"<b>{cd}</b> — {t['leg_trat']}<extra></extra>"))
    fig.update_xaxes(visible=False, range=[-75, -33])
    fig.update_yaxes(visible=False, range=[-34.5, 6], scaleanchor="x", scaleratio=1)
    fig.update_layout(height=h, margin=dict(l=0, r=0, t=10, b=0), template="plotly_white",
                      legend=dict(orientation="h", y=-0.02), hovermode="closest")
    return fig


with abas[2]:
    st.markdown(txt_mapa(c, lang))
    rot_todas = "Todas as gêmeas" if lang == "pt" else "All twins"
    foco = st.radio("👁️", [rot_todas, *TRAT], horizontal=True, key="foco_mapa")
    st.plotly_chart(mapa("todas" if foco == rot_todas else foco), width="stretch")

# ---------------------------------------------------------------------------
# 3. Desenho do teste
# ---------------------------------------------------------------------------
with abas[3]:
    st.markdown(txt_desenho_intro(c, lang))
    st.markdown(txt_ensaios(c, lang))
    rot_ef = {0.0: "0%", 0.025: "+2,5%" if lang == "pt" else "+2.5%", 0.05: "+5%"}
    th = st.radio("🪙 " + ("Efeito de mentira colocado nos ensaios" if lang == "pt" else "Fake effect added in the rehearsals"),
                  list(rot_ef), format_func=rot_ef.get, index=1, horizontal=True, key="ef_ensaio")
    ens = ensaios(df, TRAT, FIM_PRE, th)
    fig = go.Figure()
    datas_pre = pd.date_range(df["data"].min(), FIM_PRE)
    for i, e in ens.iterrows():
        cor = AZUL if e["detectou"] else CORAL
        fig.add_trace(go.Scatter(x=[e["inicio"], e["fim"]], y=[i + 1, i + 1], mode="lines",
                                 line=dict(color=cor, width=9), showlegend=False,
                                 hovertemplate=(f"{'Ensaio' if lang == 'pt' else 'Rehearsal'} {i + 1}<br>"
                                                f"{e['inicio']:%d/%m} → {e['fim']:%d/%m}<br>p = {e['p_valor']:.3f}<extra></extra>")))
    for cor, nome in [(AZUL, "percebeu" if lang == "pt" else "noticed"), (CORAL, "não percebeu" if lang == "pt" else "missed")]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color=cor, width=9), name=nome))
    fig.add_vrect(x0=df["data"].min(), x1=pd.Timestamp(FIM_PRE), fillcolor=AZUL_CLARO, opacity=0.08, line_width=0,
                  annotation_text=("histórico sem TV (jan–abr)" if lang == "pt" else "history without TV (Jan–Apr)"),
                  annotation_position="top left")
    fig = layout(fig, 360, hovermode="closest", yaxis_title=("ensaio" if lang == "pt" else "rehearsal"),
                 yaxis=dict(autorange="reversed", dtick=1),
                 xaxis_range=[df["data"].min(), pd.Timestamp(FIM_PRE) + pd.Timedelta(days=2)],
                 xaxis_tickformat="%d/%m" if lang == "pt" else "%b %d")
    st.plotly_chart(fig, width="stretch")
    n_ok = int(ens["detectou"].sum())
    if lang == "pt":
        st.markdown(f"Cada barra é uma campanha de mentira de 28 dias. Com efeito de **{rot_ef[th]}**, o GeoLift percebeu "
                    f"em **{n_ok} de {len(ens)}** ensaios ({n_ok / len(ens):.0%})."
                    + (" Como o efeito colocado é zero, cada barra laranja seria um **acerto** e cada azul, um alarme falso."
                       if th == 0 else ""))
    else:
        st.markdown(f"Each bar is a 28-day fake campaign. With a **{rot_ef[th]}** effect, GeoLift noticed it in "
                    f"**{n_ok} of {len(ens)}** rehearsals ({n_ok / len(ens):.0%})."
                    + (" Since the added effect is zero, each orange bar is a **correct answer** and each blue one a false alarm."
                       if th == 0 else ""))

    st.divider()
    st.markdown(txt_poder(c, lang))
    efeitos = np.arange(0, 25.01, 2.5)
    escolhido = grupos.iloc[0]
    fig = go.Figure(go.Scatter(x=efeitos, y=np.array(ast.literal_eval(escolhido["poder"])) * 100,
                               mode="lines+markers", line=dict(color=AZUL, width=3), name=escolhido["grupo"],
                               hovertemplate="%{x:.1f}% → %{y:.0f}%<extra></extra>"))
    fig.add_hline(y=80, line_dash="dash", line_color=CORAL, annotation_text="80%")
    st.plotly_chart(layout(fig, 320, hovermode="closest",
                           xaxis_title=("Efeito de mentira colocado (%)" if lang == "pt" else "Fake effect added (%)"),
                           yaxis_title=("% dos ensaios em que percebeu" if lang == "pt" else "% of rehearsals noticed"),
                           title=("Curva de poder do grupo escolhido" if lang == "pt" else "Power curve of the chosen group")),
                    width="stretch")

    st.divider()
    st.markdown(txt_funil(c, lang))
    f1, f2 = st.columns([1, 1.6])
    fig = go.Figure(go.Funnel(
        y=["Cidades avaliadas", "Finalistas"] if lang == "pt" else ["Cities assessed", "Finalists"],
        x=[c["n_cidades"], c["n_final"]], textinfo="value", marker=dict(color=[AZUL_CLARO, AZUL])))
    f1.plotly_chart(layout(fig, 260, hovermode="closest",
                           title=("Etapas 1–2 · cidades" if lang == "pt" else "Steps 1–2 · cities")), width="stretch")
    fig = go.Figure(go.Funnel(
        y=(["Grupos de 3", "Cabem no orçamento", f"MDE de {c['mde']:.1f}%".replace(".", ","), "Sem alarme falso"]
           if lang == "pt" else ["Groups of 3", "Fit the budget", f"{c['mde']:.1f}% MDE", "No false alarms"]),
        x=[c["n_grupos"], c["n_orc"], c["n_mde"], c["n_fp"]], textinfo="value",
        marker=dict(color=[AZUL_CLARO, AZUL_CLARO, AZUL, CORAL])))
    f2.plotly_chart(layout(fig, 260, hovermode="closest",
                           title=("Etapas 3–6 · grupos de 3 finalistas" if lang == "pt" else "Steps 3–6 · groups of 3 finalists")),
                    width="stretch")

    st.markdown(txt_comparar_grupos(lang))
    rival = grupos.iloc[1]
    mde5 = grupos[grupos["mde_pct"] > c["mde"]].iloc[0]
    fig = go.Figure()
    for g_, cor, nome, dash in [(escolhido, CORAL, ("Escolhido: " if lang == "pt" else "Chosen: ") + escolhido["grupo"], None),
                                (rival, AZUL, ("2º: " if lang == "pt" else "Runner-up: ") + rival["grupo"], "dot"),
                                (mde5, CINZA, f"MDE {mde5['mde_pct']:.0f}%: " + mde5["grupo"], "dash")]:
        fig.add_trace(go.Scatter(x=efeitos, y=np.array(ast.literal_eval(g_["poder"])) * 100, mode="lines+markers",
                                 name=nome, line=dict(color=cor, width=3, dash=dash)))
    fig.add_hline(y=80, line_dash="dash", line_color=CINZA)
    fig = layout(fig, 340, hovermode="x unified", xaxis_title=("Efeito de mentira (%)" if lang == "pt" else "Fake effect (%)"),
                 yaxis_title=("% dos ensaios em que percebeu" if lang == "pt" else "% of rehearsals noticed"),
                 xaxis_range=[-0.5, 12.5])
    fig.update_layout(legend=dict(orientation="h", y=-0.3, x=0))
    st.plotly_chart(fig, width="stretch")

    st.divider()
    st.markdown(txt_ranking(lang))
    top = grupos.head(15).copy()
    pod25 = top["poder"].map(lambda v: ast.literal_eval(v)[1])
    if lang == "pt":
        tab_rank = pd.DataFrame({
            "#": range(1, len(top) + 1), "Grupo": top["grupo"],
            "Custo": top["custo_pct"].map(lambda v: f"{v:.1f}%".replace(".", ",")),
            "MDE": top["mde_pct"].map(lambda v: f"{v:.1f}%".replace(".", ",")),
            "Alarmes falsos": top["falso_positivo"].map(lambda v: f"{v:.0%}"),
            "Poder em 2,5%": pod25.map(lambda v: f"{v:.0%}"),
            "Erro de imitação": top["mape_pre"].map(lambda v: f"{v:.1f}%".replace(".", ",")),
        })
    else:
        tab_rank = pd.DataFrame({
            "#": range(1, len(top) + 1), "Group": top["grupo"],
            "Cost": top["custo_pct"].map(lambda v: f"{v:.1f}%"), "MDE": top["mde_pct"].map(lambda v: f"{v:.1f}%"),
            "False alarms": top["falso_positivo"].map(lambda v: f"{v:.0%}"),
            "Power at 2.5%": pod25.map(lambda v: f"{v:.0%}"),
            "Imitation error": top["mape_pre"].map(lambda v: f"{v:.1f}%"),
        })
    st.dataframe(tab_rank.style.apply(lambda row: ["background-color: #FDE7E0; font-weight: 600" if row.name == 0 else ""
                                                   for _ in row], axis=1),
                 width="stretch", hide_index=True)
    with st.expander("Ranking das cidades sozinhas (etapa 1 do funil)" if lang == "pt"
                     else "Single-city ranking (funnel step 1)"):
        st.markdown("Cada cidade passou sozinha pelos ensaios. As 14 primeiras viraram finalistas. Repare que sozinhas "
                    "elas precisam de efeitos bem maiores (MDE de 5% a 10%) para serem percebidas." if lang == "pt" else
                    "Each city went through the rehearsals alone. The top 14 became finalists. Note that alone they need "
                    "much larger effects (5% to 10% MDE) to be noticed.")
        ti = indiv.copy()
        st.dataframe(pd.DataFrame({
            "#": range(1, len(ti) + 1), ("Cidade" if lang == "pt" else "City"): ti["cidade"],
            "MDE": ti["mde_pct"].map(lambda v: f"{v:.1f}%"),
            ("Alarmes falsos" if lang == "pt" else "False alarms"): ti["falso_positivo"].map(lambda v: f"{v:.0%}"),
            ("Erro de imitação" if lang == "pt" else "Imitation error"): ti["mape_pre"].map(lambda v: f"{v:.1f}%"),
            ("Finalista" if lang == "pt" else "Finalist"): ["✅" if i < 14 else "" for i in range(len(ti))],
        }), width="stretch", hide_index=True, height=400)

# ---------------------------------------------------------------------------
# 4. As gêmeas
# ---------------------------------------------------------------------------
with abas[4]:
    sel = st.radio("🧬 " + ("Ver a gêmea de" if lang == "pt" else "Show the twin of"), TRAT, horizontal=True,
                   key="gemea_sel")
    pc = (r.pesos[sel] * 100)
    pc = pc[pc > 0.5].sort_values(ascending=False)
    c2 = {**c, "cidade_sel": sel, "top_pesos": list(pc.head(5).items()), "n_doadoras": len(pc),
          "mape_sel": r.mape_cidade[sel]}
    col1, col2 = st.columns([1, 1.4])
    with col1:
        st.markdown(txt_gemea(c2, lang))
    with col2:
        p = pc.sort_values()
        fig = go.Figure(go.Bar(x=p.values, y=p.index, orientation="h", marker_color=COR[sel],
                               text=[f"{v:.1f}%" for v in p.values], textposition="outside"))
        st.plotly_chart(layout(fig, 30 * len(p) + 90, hovermode="closest",
                               title=(f"A receita da gêmea de {sel}" if lang == "pt" else f"{sel}'s twin recipe"),
                               xaxis_title=t["peso"] + " (%)", xaxis_range=[0, p.max() * 1.2]),
                        width="stretch")
        fig = go.Figure()
        fig.add_vrect(x0=r.datas[r.n_pre], x1=r.datas[-1], fillcolor=AZUL_CLARO, opacity=0.18, line_width=0,
                      annotation_text=t["inicio_tv"], annotation_position="top left")
        fig.add_trace(go.Scatter(x=r.datas, y=r.real_cidade[sel], name=sel, line=dict(color=COR[sel], width=2)))
        fig.add_trace(go.Scatter(x=r.datas, y=r.sint_cidade[sel], name=t["gemea"],
                                 line=dict(color=AZUL_ESCURO, dash="dot")))
        st.plotly_chart(layout(fig, 330, title=(f"{sel} × sua gêmea" if lang == "pt" else f"{sel} × its twin")),
                        width="stretch")

# ---------------------------------------------------------------------------
# 5. A conta da gêmea
# ---------------------------------------------------------------------------
with abas[5]:
    sel = st.radio("🧮 " + ("Fazer a conta da gêmea de" if lang == "pt" else "Do the math for the twin of"), TRAT,
                   horizontal=True, key="conta_sel")
    pc = (r.pesos[sel] * 100)
    pc = pc[pc > 0.5].sort_values(ascending=False)
    c2 = {**c, "cidade_sel": sel, "top_pesos": list(pc.head(5).items()), "n_doadoras": len(pc),
          "mape_sel": r.mape_cidade[sel]}
    alfa = float(r.interceptos[sel])
    c3 = {**c2, "alfa": alfa}
    st.markdown(txt_conta_intro(c3, lang))
    st.latex(r"\underbrace{y_t}_{\text{%s}} \;\approx\; \alpha \;+\; w_1\,x_{1t} + w_2\,x_{2t} + \dots + w_J\,x_{Jt}"
             % sel)
    st.markdown(txt_conta_regras(c3, lang))
    st.latex(r"\min_{w}\; \sum_{t \,\in\, \text{%s}} \Big( y_t - \alpha - \sum_{j} w_j\, x_{jt} \Big)^2"
             r"\quad \text{%s}\quad w_j \ge 0,\;\; \sum_j w_j = 1" % (("pré", "s.a.") if lang == "pt" else ("pre", "s.t.")))
    didatico.renderizar(lang, layout)
    st.divider()
    st.markdown(txt_conta_depois(c3, lang))

    pre_seg = [d for d in r.datas[:r.n_pre] if d.dayofweek == 0][-1]
    tv_seg = [d for d in r.datas[r.n_pre:] if d.dayofweek == 0][2]
    fmt_d = (lambda d: d.strftime("%d/%m/%Y")) if lang == "pt" else (lambda d: d.strftime("%b %d, %Y"))
    rot = {pre_seg: (f"{fmt_d(pre_seg)} — antes da TV" if lang == "pt" else f"{fmt_d(pre_seg)} — before TV"),
           tv_seg: (f"{fmt_d(tv_seg)} — com TV no ar" if lang == "pt" else f"{fmt_d(tv_seg)} — TV on air")}
    escolha = st.radio("📅", list(rot.values()), horizontal=True, key="dia_conta")
    dia = [d for d, v in rot.items() if v == escolha][0]
    w = r.pesos[sel]
    w = w[w > 0.005].sort_values(ascending=False)
    xi = r.indices.loc[dia, w.index]
    tab = pd.DataFrame({
        ("Cidade" if lang == "pt" else "City"): w.index,
        ("Índice no dia (x)" if lang == "pt" else "Index that day (x)"): xi.values.round(3),
        ("Peso (w)" if lang == "pt" else "Weight (w)"): w.values.round(3),
        ("x × w"): (xi.values * w.values).round(4),
    })
    ind = float((xi * w).sum() + alfa)
    st.dataframe(tab, width="stretch", hide_index=True, height=min(38 * len(tab) + 40, 420))
    dec = (lambda x: f"{x:.3f}".replace(".", "{,}")) if lang == "pt" else (lambda x: f"{x:.3f}")
    st.latex(r"\sum_j w_j\,x_{jt} = %s \qquad \alpha = %s \qquad \Rightarrow\quad \hat y_t = %s"
             % (dec(float((xi * w).sum())), dec(alfa), dec(float((xi * w).sum()) + alfa)))
    st.markdown(txt_conta_resultado({**c3, "ind_gemea": ind, "base": float(r.bases[sel]),
                                     "contas_gemea": ind * float(r.bases[sel]),
                                     "contas_real": float(r.real_cidade.loc[dia, sel]),
                                     "dia_tv": dia >= r.datas[r.n_pre]}, lang))

# ---------------------------------------------------------------------------
# 6. Robustez
# ---------------------------------------------------------------------------
with abas[6]:
    st.markdown(txt_rob_intro(lang))
    st.markdown(txt_fila(c, lang))
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_vrect(x0=r.datas[r.n_pre], x1=r.datas[-1], fillcolor=AZUL_CLARO, opacity=0.18, line_width=0)
        fig.add_trace(go.Scatter(x=r.datas, y=r.real, name=t["real"], line=dict(color=CORAL, width=1.6)))
        fig.add_trace(go.Scatter(x=r.datas, y=r.sintetico, name=t["gemea"], line=dict(color=AZUL_ESCURO, width=1.4, dash="dot")))
        st.plotly_chart(layout(fig, 280, title=(f"Nosso grupo (com TV) · descolamento {c['razao_trat']:.2f}"
                                                .replace(".", ",") if lang == "pt" else
                                                f"Our group (with TV) · drift {c['razao_trat']:.2f}"),
                               showlegend=False), width="stretch")
    with col2:
        dd, ra, sa, npre = placebo_cidade(df, TRAT, c["top_placebo"], meta["inicio_teste"], meta["fim_teste"])
        fig = go.Figure()
        fig.add_vrect(x0=dd[npre], x1=dd[-1], fillcolor=AZUL_CLARO, opacity=0.18, line_width=0)
        fig.add_trace(go.Scatter(x=dd, y=ra, name=c["top_placebo"], line=dict(color=CINZA, width=1.6)))
        fig.add_trace(go.Scatter(x=dd, y=sa, name=t["gemea"], line=dict(color=AZUL_ESCURO, width=1.4, dash="dot")))
        st.plotly_chart(layout(fig, 280, title=(f"{c['top_placebo']} (sem TV) · descolamento {c['razao_top']:.2f}"
                                                .replace(".", ",") if lang == "pt" else
                                                f"{c['top_placebo']} (no TV) · drift {c['razao_top']:.2f}"),
                               showlegend=False), width="stretch")
    pe = r.placebos_espaco.head(15).sort_values("razao_rmspe")
    nomes = [("Nossas 3 cidades" if lang == "pt" else "Our 3 cities") if x else cd
             for cd, x in zip(pe["cidade"], pe["tratado"])]
    fig = go.Figure(go.Bar(x=pe["razao_rmspe"], y=nomes, orientation="h",
                           marker_color=[CORAL if x else AZUL_CLARO for x in pe["tratado"]],
                           text=[f"{v:.2f}" for v in pe["razao_rmspe"]], textposition="outside"))
    fig.add_vline(x=1, line_dash="dot", line_color=CINZA, annotation_position="bottom right",
                  annotation_text=("1 = nada mudou" if lang == "pt" else "1 = nothing changed"))
    st.plotly_chart(layout(fig, 460, hovermode="closest",
                           title=("A fila: as 15 que mais se descolaram (de 38)" if lang == "pt"
                                  else "The line-up: top 15 drifters (of 38)"),
                           xaxis_title=("descolamento = durante ÷ antes" if lang == "pt" else "drift = during ÷ before"),
                           xaxis_range=[0, pe["razao_rmspe"].max() * 1.15]), width="stretch")

    st.divider()
    st.markdown(txt_conforme(c, lang))
    theta = st.slider(("Suspeita: a TV deu quanto? (%)" if lang == "pt" else "Suspicion: how much did TV give? (%)"),
                      -5.0, 25.0, 0.0, 1.0, key="theta_susp")
    dts, u, npre, pth = hipotese(df, TRAT, meta["inicio_teste"], meta["fim_teste"], theta / 100)
    fig = go.Figure()
    fig.add_vrect(x0=dts[npre], x1=dts[-1], fillcolor=AZUL_CLARO, opacity=0.18, line_width=0,
                  annotation_text=t["inicio_tv"], annotation_position="top left")
    fig.add_trace(go.Bar(x=dts[:npre], y=u[:npre], marker_color=CINZA, name=("antes da TV" if lang == "pt" else "before TV")))
    fig.add_trace(go.Bar(x=dts[npre:], y=u[npre:], marker_color=CORAL if pth <= 0.10 else AZUL,
                         name=("campanha" if lang == "pt" else "campaign")))
    fig.add_hline(y=0, line_color=AZUL_ESCURO, line_width=1)
    st.plotly_chart(layout(fig, 300, hovermode="closest",
                           yaxis_title=("erro do dia: real − gêmea (%)" if lang == "pt" else "daily error: real − twin (%)"),
                           xaxis_tickformat="%d/%m" if lang == "pt" else "%b %d"),
                    width="stretch")
    st.markdown(txt_conforme_resultado(theta, pth, float(np.mean(u[:npre])), float(np.mean(u[npre:])), lang))

    st.markdown(txt_curva_p(c, lang))
    cp = r.curva_p
    fig = go.Figure(go.Scatter(x=cp["efeito_pct"], y=cp["p_valor"], line=dict(color=AZUL, width=2),
                               fill="tozeroy", fillcolor="rgba(31,111,235,0.12)",
                               hovertemplate=("suspeita %{x:.1f}% → p = %{y:.3f}" if lang == "pt"
                                              else "suspicion %{x:.1f}% → p = %{y:.3f}") + "<extra></extra>"))
    fig.add_hline(y=0.10, line_dash="dash", line_color=CORAL, annotation_text="p = 0,10" if lang == "pt" else "p = 0.10")
    fig.add_vrect(x0=r.ic_baixo, x1=r.ic_alto, fillcolor=AZUL_CLARO, opacity=0.25, line_width=0,
                  annotation_text=("intervalo de 90%" if lang == "pt" else "90% interval"), annotation_position="top left")
    fig.add_vline(x=meta["verdade_lift_pct"], line_color=CORAL, line_width=2,
                  annotation_text=t["verdade"], annotation_position="top right")
    st.plotly_chart(layout(fig, 360, hovermode="closest", xaxis_range=[-10, 30],
                           xaxis_title=("Suspeita: efeito da TV (%)" if lang == "pt" else "Suspicion: TV effect (%)"),
                           yaxis_title="p-valor" if lang == "pt" else "p-value"), width="stretch")

# ---------------------------------------------------------------------------
# 7. Laboratório
# ---------------------------------------------------------------------------
@st.cache_data
def simular(lift_alvo: float, seed: int):
    """Recria as cidades tratadas no teste com um efeito escolhido e roda o GeoLift."""
    rng = np.random.default_rng(seed)
    d = df.merge(verdade, on=["data", "cidade"])
    m = d["cidade"].isin(TRAT) & (d["data"] >= meta["inicio_teste"])
    forma = d.loc[m, "contas_esperadas_com_tv"] / d.loc[m, "contas_esperadas_sem_tv"] - 1
    forma = forma / (meta["lift_plato_pct"] / 100)          # rampa normalizada (0 → 1)
    mu = d.loc[m, "contas_esperadas_sem_tv"] * (1 + lift_alvo / 100 * forma)
    d.loc[m, "contas"] = rng.poisson(mu)
    verd = (mu.sum() / d.loc[m, "contas_esperadas_sem_tv"].sum() - 1) * 100
    res = rodar_geolift(d[["data", "cidade", "contas"]], list(TRAT), meta["inicio_teste"], meta["fim_teste"])
    return res, verd


with abas[7]:
    _marca = "**Experimentos para fazer:**" if lang == "pt" else "**Experiments to try:**"
    _intro, _exp = txt_lab_intro(c, lang).split(_marca)
    st.markdown(_intro)
    with st.spinner("Rodando os cenários de exemplo..." if lang == "pt" else "Running the example scenarios..."):
        cenarios = {ef: simular(ef, 7) for ef in [0.0, 2.0, 5.0, 10.0, 15.0, -3.0]}
    r10, v10 = cenarios[10.0]
    st.markdown(txt_lab_exemplo({"verd": v10, "est": r10.lift_pct, "lo": r10.ic_baixo, "hi": r10.ic_alto,
                                 "p": r10.p_valor}, lang))
    linhas = []
    for ef, (rr, vv) in cenarios.items():
        dentro = rr.ic_baixo <= vv <= rr.ic_alto
        det = rr.p_valor <= 0.10
        if lang == "pt":
            leitura = ("não viu efeito ✅" if not det else "alarme falso ⚠️") if ef == 0 else \
                      ("detectou ✅" if det else "não conseguiu afirmar ⚠️")
            linhas.append({"Efeito escolhido": f"{ef:+.0f}%", "Verdade (média 4 sem.)": f"{vv:+.1f}%".replace(".", ","),
                           "GeoLift estimou": f"{rr.lift_pct:+.1f}%".replace(".", ","),
                           "Intervalo de 90%": f"{rr.ic_baixo:.1f}% a {rr.ic_alto:.1f}%".replace(".", ","),
                           "Verdade no intervalo?": "sim ✅" if dentro else "não ❌",
                           "p-valor": f"{rr.p_valor:.3f}".replace(".", ","), "Leitura": leitura})
        else:
            leitura = ("saw no effect ✅" if not det else "false alarm ⚠️") if ef == 0 else \
                      ("detected ✅" if det else "couldn't confirm ⚠️")
            linhas.append({"Chosen effect": f"{ef:+.0f}%", "Truth (4-wk avg)": f"{vv:+.1f}%",
                           "GeoLift estimated": f"{rr.lift_pct:+.1f}%",
                           "90% interval": f"{rr.ic_baixo:.1f}% to {rr.ic_alto:.1f}%",
                           "Truth in interval?": "yes ✅" if dentro else "no ❌",
                           "p-value": f"{rr.p_valor:.3f}", "Reading": leitura})
    st.dataframe(pd.DataFrame(linhas), width="stretch", hide_index=True)
    st.markdown(txt_lab_leitura(lang))
    st.divider()
    st.markdown("#### " + ("Agora é com você" if lang == "pt" else "Now it's your turn"))
    st.markdown(_marca + _exp)
    a, b = st.columns(2)
    alvo = a.slider("Efeito verdadeiro da TV (%)" if lang == "pt" else "True TV effect (%)", -5.0, 20.0, 10.0, 0.5,
                    key="lab_alvo")
    semente = b.number_input("Semente (qual sorteio do acaso)" if lang == "pt" else "Seed (which draw of chance)",
                             1, 9999, 7, key="lab_seed")
    res, verd = simular(alvo, int(semente))
    k = st.columns(4)
    k[0].metric(t["verdade"], f"{verd:+.1f}%")
    k[1].metric(("GeoLift estimou" if lang == "pt" else "GeoLift estimated"), f"{res.lift_pct:+.1f}%",
                f"{res.lift_pct - verd:+.1f} p.p. " + ("da verdade" if lang == "pt" else "from truth"), delta_color="off")
    k[2].metric(t["ic"], f"{res.ic_baixo:.1f}–{res.ic_alto:.1f}%")
    k[3].metric(t["pval"], f"{res.p_valor:.3f}")
    st.markdown(txt_lab_veredito(verd, res.lift_pct, res.ic_baixo, res.ic_alto, res.p_valor, lang))
    st.plotly_chart(grafico_real_vs_gemea(res), width="stretch")

# ---------------------------------------------------------------------------
# 8. Dados
# ---------------------------------------------------------------------------
with abas[8]:
    st.markdown(txt_dados(lang))
    tot = df.groupby("data")["contas"].sum()
    fig = go.Figure(go.Scatter(x=tot.index, y=tot.values, line=dict(color=AZUL)))
    st.plotly_chart(layout(fig, 300, title=("Brasil — contas novas por dia" if lang == "pt"
                                            else "Brazil — new accounts per day")), width="stretch")
    reg = df.merge(cid[["cidade", "regiao"]]).groupby(["data", "regiao"])["contas"].sum().unstack()
    reg = reg / reg.iloc[:28].mean()
    fig = go.Figure([go.Scatter(x=reg.index, y=reg[cn].rolling(7).mean(), name=cn) for cn in reg.columns])
    st.plotly_chart(layout(fig, 320, title=("Regiões (índice, média móvel 7d)" if lang == "pt"
                                            else "Regions (index, 7-day moving avg)")), width="stretch")
    dow = df.assign(dia=df["data"].dt.dayofweek).groupby("dia")["contas"].mean()
    nomes = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"] if lang == "pt" else \
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    col1, col2 = st.columns(2)
    col1.plotly_chart(layout(go.Figure(go.Bar(x=nomes, y=dow.values, marker_color=AZUL)), 280,
                             title=("Média por dia da semana" if lang == "pt" else "Mean by weekday")),
                      width="stretch")
    resumo = df.groupby("cidade")["contas"].agg(["mean", "std", "sum"]).round(1).sort_values("sum", ascending=False)
    col2.dataframe(resumo, width="stretch", height=280)

# ---------------------------------------------------------------------------
# 9. Como funciona
# ---------------------------------------------------------------------------
with abas[9]:
    st.markdown(txt_como_funciona(c, lang))
