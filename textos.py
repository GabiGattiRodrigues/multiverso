"""Textos do app em PT e EN. Os textos longos recebem `c` (dicionário com os números do resultado)
para que as explicações usem os valores reais do teste, não exemplos genéricos."""

def br(n: float) -> str:
    """1234.5 -> '1.235' (milhar com ponto)."""
    return f"{n:,.0f}".replace(",", ".")


UI = {
    "pt": {
        "titulo": "Multiverso",
        "subtitulo": "GeoLift: a TV trouxe contas novas? Comparando o mundo real com o universo onde o comercial nunca foi ao ar.",
        "idioma": "Idioma",
        "abas": ["📖 O case", "🎯 Resultado", "🗺️ Mapa", "🧭 Desenho do teste", "🧬 As gêmeas",
                 "🧮 A conta da gêmea", "🔍 Robustez", "🧪 Laboratório", "📊 Dados", "📚 Como funciona"],
        "cenario": "**Cenário fictício:** o **Orbe**, um banco digital, quer saber se comerciais em TV aberta "
                   "trazem contas novas. Antes de gastar no Brasil todo, testou em 3 cidades por 4 semanas.",
        "lift": "Lift (efeito da TV)", "incr": "Contas incrementais", "cac": "CAC incremental",
        "pval": "p-valor", "ic": "Intervalo de 90%", "verdade": "Verdade (dado sintético)",
        "real": "Real (cidades com TV)", "gemea": "Cidade gêmea (sem TV)", "inicio_tv": "TV no ar",
        "contas_dia": "Contas novas por dia", "acumulado": "Contas incrementais acumuladas",
        "data": "Data", "peso": "Peso na gêmea", "cidade": "Cidade",
        "rodape": "Dados 100% sintéticos. Reconstrução pública de um projeto real que fiz no varejo. "
                  "Por Gabriela Gatti Rodrigues.",
        "cac_meta": "CAC-alvo do banco (R$)",
        "invest": "Investimento em TV (R$)",
        "leg_trat": "com TV", "leg_doad": "gêmea de",
        "leg_fora": "Não entraram na gêmea", "leg_excl": "Fora do sorteio e da gêmea",
    },
    "en": {
        "titulo": "Multiverso",
        "subtitulo": "GeoLift: did TV bring new accounts? Comparing the real world with the universe where the ad never aired.",
        "idioma": "Language",
        "abas": ["📖 The case", "🎯 Result", "🗺️ Map", "🧭 Test design", "🧬 The twins",
                 "🧮 The twin's math", "🔍 Robustness", "🧪 Lab", "📊 Data", "📚 How it works"],
        "cenario": "**Fictional scenario:** **Orbe**, a digital bank, wants to know whether broadcast TV ads "
                   "bring new accounts. Before spending nationwide, it tested in 3 cities for 4 weeks.",
        "lift": "Lift (TV effect)", "incr": "Incremental accounts", "cac": "Incremental CAC",
        "pval": "p-value", "ic": "90% interval", "verdade": "Truth (synthetic data)",
        "real": "Actual (TV cities)", "gemea": "Twin city (no TV)", "inicio_tv": "TV on air",
        "contas_dia": "New accounts per day", "acumulado": "Cumulative incremental accounts",
        "data": "Date", "peso": "Weight in the twin", "cidade": "City",
        "rodape": "100% synthetic data. Public rebuild of a real project I did in retail. "
                  "By Gabriela Gatti Rodrigues.",
        "cac_meta": "Bank's target CAC (R$)",
        "invest": "TV investment (R$)",
        "leg_trat": "with TV", "leg_doad": "twin of",
        "leg_fora": "Not used by the twin", "leg_excl": "Out of the draw and the twin",
    },
}


def veredito(c, lang):
    bom = c["cac"] <= c["cac_meta"]
    if lang == "pt":
        sig = ("O efeito **é real**: a chance de ver uma diferença desse tamanho só por acaso é de "
               f"**{c['p']:.1%}**." if c["p"] <= 0.10 else
               f"⚠️ O efeito **não é conclusivo** (p = {c['p']:.2f}): pode ser acaso.")
        neg = (f"Cada conta nova custou **R\\$ {br(c['cac'])}**, abaixo do alvo de R\\$ {br(c['cac_meta'])}. "
               "👉 **Recomendação: escalar a TV** para praças parecidas e usar esse lift para calibrar o MMM."
               if bom else
               f"Cada conta nova custou **R\\$ {br(c['cac'])}**, acima do alvo de R\\$ {br(c['cac_meta'])}. "
               "👉 **Recomendação: não escalar do jeito que está** — rever criativo, praça ou verba.")
        return (f"### A TV trouxe **+{c['lift']:.1f}%** de contas novas em {c['cidades_txt']}\n"
                f"Foram **~{br(c['incr'])} contas a mais** em 4 semanas (intervalo de 90%: "
                f"{c['ic_lo']:+.1f}% a {c['ic_hi']:+.1f}%). {sig}\n\n{neg}")
    sig = ("The effect **is real**: the chance of a gap this large by pure luck is "
           f"**{c['p']:.1%}**." if c["p"] <= 0.10 else
           f"⚠️ The effect is **not conclusive** (p = {c['p']:.2f}): it may be noise.")
    neg = (f"Each new account cost **R\\$ {c['cac']:,.0f}**, below the R\\$ {c['cac_meta']:,.0f} target. "
           "👉 **Recommendation: scale TV** to similar markets and use this lift to calibrate the MMM."
           if bom else
           f"Each new account cost **R\\$ {c['cac']:,.0f}**, above the R\\$ {c['cac_meta']:,.0f} target. "
           "👉 **Recommendation: don't scale as is** — revisit creative, markets or budget.")
    return (f"### TV brought **+{c['lift']:.1f}%** new accounts in {c['cidades_txt']}\n"
            f"That's **~{c['incr']:,.0f} extra accounts** in 4 weeks (90% interval: "
            f"{c['ic_lo']:+.1f}% to {c['ic_hi']:+.1f}%). {sig}\n\n{neg}")


def conferencia(c, lang):
    acertou = c["ic_lo"] <= c["v_lift"] <= c["ic_hi"]
    if lang == "pt":
        return (f"🔬 **Conferindo com a verdade.** Como os dados são sintéticos, a gente sabe o efeito real: "
                f"**+{c['v_lift']:.1f}%** (~{br(c['v_incr'])} contas). O GeoLift estimou **+{c['lift']:.1f}%**"
                + (" e o intervalo **contém a verdade** ✅." if acertou else " — a verdade ficou fora do intervalo ❌."))
    return (f"🔬 **Checking against the truth.** Since the data is synthetic, we know the real effect: "
            f"**+{c['v_lift']:.1f}%** (~{c['v_incr']:,.0f} accounts). GeoLift estimated **+{c['lift']:.1f}%**"
            + (" and the interval **contains the truth** ✅." if acertou else " — the truth fell outside the interval ❌."))


# ---------------------------------------------------------------------------
# Textos explicativos por aba
# ---------------------------------------------------------------------------
def txt_mapa(c, lang):
    cores = c["cores_txt"]
    if lang == "pt":
        return (f"As **estrelas** são as 3 cidades onde a TV passou, cada uma com sua cor ({cores}). "
                "Cada cidade testada tem a **sua própria gêmea**, e as bolinhas da mesma cor são as cidades que formam "
                "essa gêmea — quanto maior a bolinha, mais ela pesa na receita. Uma cidade pode ajudar a formar mais de "
                "uma gêmea: no mapa ela aparece na cor da gêmea em que pesa mais (toque nela para ver os três pesos). "
                "Repare que a gêmea não precisa ser vizinha: o que importa é que as curvas de contas **sobem e descem "
                "junto**, não a distância. São Paulo e Rio ficaram fora do *sorteio das cidades testadas* (TV cara "
                "demais), mas podem entrar na receita das gêmeas.")
    return (f"The **stars** are the 3 cities where TV aired, each with its own color ({cores}). "
            "Each tested city has **its own twin**, and the dots in the same color are the cities that make up that twin "
            "— the bigger the dot, the more it weighs in the recipe. A city can help build more than one twin: on the "
            "map it takes the color of the twin where it weighs the most (tap it to see all three weights). "
            "The twin doesn't need to be a neighbor: what matters is that the account curves **move up and down "
            "together**, not distance. São Paulo and Rio were left out of the *draw of test cities* (TV too "
            "expensive), but they can still be part of the twins' recipes.")


def txt_gemea(c, lang):
    top = c["top_pesos"]
    receita = "\n".join(f"- **{p:.0f}%** {cid}" for cid, p in top)
    if lang == "pt":
        return f"""
**Exemplo:** você quer saber se o adubo fez sua plantinha crescer. Mas não existe outra plantinha igual
pra comparar. Então você pega **pedacinhos de várias outras plantinhas** e monta uma plantinha de mentira que,
até ontem, crescia **igualzinho** à sua. Se hoje a sua cresceu mais que a de mentira, foi o adubo. 🌱

Aqui a "plantinha" é o número de contas abertas. A cidade gêmea é uma **receita de suco misturado**: pegamos
um pouco de cada cidade que **não** viu a TV, em proporções diferentes, até o gosto ficar igual ao das cidades
testadas *antes* da campanha. Cada cidade testada ganha **a sua** gêmea, porque cada uma tem seu jeito
(o Nordeste tem um ritmo, o Sul tem outro). A receita que o algoritmo achou para **{c['cidade_sel']}** foi:

{receita}
- … e pitadas de outras ({c['n_doadoras']} cidades no total)

**Como o algoritmo acha a receita (técnico):**
1. Cada cidade vira um **índice** (contas ÷ média do pré). Assim cidades grandes e pequenas ficam na mesma régua.
2. Procuramos pesos **w ≥ 0** que **somam 100%** e deixam a mistura o mais perto possível das tratadas no pré
   (mínimos quadrados não negativos — Abadie, 2010).
3. Deixamos um **intercepto** livre: a gêmea precisa copiar o *formato* da curva (sobe na segunda, cai no domingo,
   pico no dia de pagamento, buraco no Carnaval), não o nível exato (Ferman & Pinto, 2021).
4. **Nota da imitação** da gêmea de {c['cidade_sel']}: erro médio diário (MAPE) de **{c['mape_sel']:.1f}%** antes da TV.
5. **Junta tudo:** o efeito do teste = soma das 3 cidades reais ÷ soma das 3 gêmeas − 1. Sozinha, cada cidade é ruidosa; somadas, o ruído se compensa (MAPE do conjunto: **{c['mape']:.1f}%**, R² **{c['r2']:.2f}**).

Pesos ≥ 0 e somando 100% são importantes: a gêmea é sempre uma *mistura* de cidades reais — nada de
"menos meia Brasília" ou "300% de Teresina", que imitariam o passado mas inventariam o futuro.
"""
    return f"""
**Example:** you want to know if fertilizer made your plant grow. But there's no identical plant to compare.
So you take **little pieces of many other plants** and build a pretend plant that, until yesterday, grew
**exactly like** yours. If today yours grew more than the pretend one, it was the fertilizer. 🌱

Here the "plant" is the number of accounts opened. The twin city is a **mixed-juice recipe**: we take a bit of each
city that did **not** see TV, in different amounts, until the taste matches the tested cities *before* the campaign.
Each tested city gets **its own** twin, because each has its own rhythm. The recipe the algorithm found for
**{c['cidade_sel']}**:

{receita}
- … plus pinches of others ({c['n_doadoras']} cities in total)

**How the algorithm finds the recipe (technical):**
1. Each city becomes an **index** (accounts ÷ pre-period mean), so big and small cities share the same ruler.
2. We look for weights **w ≥ 0** that **sum to 100%** and bring the blend as close as possible to the treated cities
   in the pre-period (non-negative least squares — Abadie, 2010).
3. A free **intercept**: the twin must copy the curve's *shape* (Monday peak, Sunday dip, payday spikes,
   the Carnival hole), not its exact level (Ferman & Pinto, 2021).
4. **Imitation score** of {c['cidade_sel']}'s twin: mean daily error (MAPE) of **{c['mape_sel']:.1f}%** before TV.
5. **Put it together:** test effect = sum of the 3 real cities ÷ sum of the 3 twins − 1. Alone, each city is noisy; summed, the noise cancels out (combined MAPE **{c['mape']:.1f}%**, R² **{c['r2']:.2f}**).

Non-negative weights summing to 100% matter: the twin is always a *blend* of real cities — no "minus half a
Brasília" or "300% Teresina", which would mimic the past but invent the future.
"""


def txt_dados(lang):
    if lang == "pt":
        return ("Contas novas por dia em 40 cidades, de jan a mai/2026. Os dados têm o que dados de verdade têm: "
                "crescimento do banco, segunda-feira forte e domingo fraco, picos nos dias 5 e 20 (salário), "
                "o buraco do Carnaval, ondas regionais e ruído de cada cidade.")
    return ("New accounts per day across 40 cities, Jan–May 2026. The data has what real data has: bank growth, "
            "strong Mondays and weak Sundays, spikes on the 5th and 20th (paydays), the Carnival dip, regional "
            "waves and city-level noise.")


def txt_como_funciona(c, lang):
    if lang == "pt":
        return f"""
## O que é GeoLift?

**Exemplo:** você tem duas sorveterias iguaizinhas. Numa você põe um palhaço na porta, na
outra não. No fim do dia, a do palhaço vendeu mais? Então o palhaço funciona! 🤡🍦

GeoLift é isso com cidades: **liga a propaganda em algumas cidades, deixa outras sem** e compara.
O nome vem de *geo* (lugar) + *lift* (o quanto a propaganda "levantou" o resultado).

**Por que não comparar antes vs depois?** Porque o mundo muda sozinho: maio pode ser melhor que abril por causa do
salário, do clima, de um concorrente. **Por que não um teste A/B comum?** Porque TV não dá pra mostrar pra uma
pessoa e esconder do vizinho — quem decide é a cidade inteira. Então o "sorteio" é de cidades.

## O problema: não existem duas cidades iguais

Curitiba não é igual a Teresina. Por isso, em vez de achar uma cidade-gêmea, a gente **fabrica** uma para cada
cidade testada, misturando várias (o **controle sintético**). É a parte mágica do método — veja a aba 🧬.

## As 4 etapas

| Etapa | Pergunta | Exemplo | Técnico |
|---|---|---|---|
| 1. Desenho | Onde testar? | Escolher a sala mais silenciosa pra ouvir o sussurro | Análise de poder por simulação em janelas históricas (MDE) |
| 2. Campanha | — | Pôr o palhaço na porta | TV em {c['cidades_txt']} por 28 dias |
| 3. Gêmea | O que teria acontecido sem TV? | Montar a plantinha de mentira | Um controle sintético por cidade (pesos ≥ 0, soma 1, com intercepto) |
| 4. Leitura | Foi sorte? Valeu o dinheiro? | Fila de suspeitos | Inferência conforme + placebo no espaço; CAC incremental |

## A matemática em 4 linhas

1. Índice de cada cidade: $\\tilde y_{{jt}} = y_{{jt}} / \\bar y_{{j,\\text{{pré}}}}$
2. Pesos: $\\min_w \\sum_{{t \\in \\text{{pré}}}} \\big[(\\tilde y_{{1t}} - \\bar{{\\tilde y}}_1) - \\sum_j w_j(\\tilde y_{{jt}} - \\bar{{\\tilde y}}_j)\\big]^2$, com $w_j \\ge 0$ e $\\sum_j w_j = 1$
3. Contrafactual: $\\hat y_{{1t}}(0) = \\sum_j w_j \\tilde y_{{jt}} + \\alpha$, onde $\\alpha$ alinha as médias no pré
4. Lift: $\\dfrac{{\\sum_{{t \\in \\text{{teste}}}} y_{{1t}}}}{{\\sum_{{t \\in \\text{{teste}}}} \\hat y_{{1t}}(0)}} - 1$

## E depois do teste?

- **CAC incremental** = investimento ÷ contas incrementais. É o custo de cada conta que **só existe por causa da TV**
  (as que viriam de qualquer jeito não contam).
- O lift vira **prior de ROI** para o MMM: o experimento ensina ao modelo o quanto a TV rende de verdade
  (veja o projeto Prisma).

## Limitações honestas

- Supõe que a TV de uma cidade não "vaza" para as cidades da gêmea (por isso cidades muito próximas de praças
  tratadas merecem cuidado).
- Mede o efeito **nessas** cidades, **nesse** período. Escalar para o Brasil todo é uma extrapolação.
- Quatro semanas medem o efeito de curto prazo; efeito de marca de longo prazo fica de fora.

*Inspirado no [GeoLift](https://github.com/facebookincubator/GeoLift) (Meta, em R). Aqui tudo foi
reimplementado do zero em Python para ficar transparente.*
"""
    return f"""
## What is GeoLift?

**Example:** you have two identical ice-cream shops. You put a clown at one door and not the other.
At the end of the day, did the clown shop sell more? Then the clown works! 🤡🍦

GeoLift is that with cities: **turn the ad on in some cities, leave others without** and compare.
The name comes from *geo* (place) + *lift* (how much the ad "lifted" the result).

**Why not compare before vs after?** Because the world changes on its own: May may beat April because of paydays,
weather, a competitor. **Why not a regular A/B test?** Because you can't show TV to one person and hide it from the
neighbor — the whole city sees it. So we "randomize" cities.

## The problem: no two cities are alike

Curitiba isn't Teresina. So instead of finding a twin city, we **build** one for each tested city by blending several (the
**synthetic control**). That's the magic part — see the 🧬 tab.

## The 4 stages

| Stage | Question | Example | Technical |
|---|---|---|---|
| 1. Design | Where to test? | Pick the quietest room to hear the whisper | Simulation-based power analysis on historical windows (MDE) |
| 2. Campaign | — | Put the clown at the door | TV in {c['cidades_txt']} for 28 days |
| 3. Twin | What would have happened without TV? | Build the pretend plant | One synthetic control per city (weights ≥ 0, sum 1, with intercept) |
| 4. Readout | Was it luck? Worth the money? | Line-up of suspects | Conformal inference + placebo in space; incremental CAC |

## The math in 4 lines

1. City index: $\\tilde y_{{jt}} = y_{{jt}} / \\bar y_{{j,\\text{{pre}}}}$
2. Weights: $\\min_w \\sum_{{t \\in \\text{{pre}}}} \\big[(\\tilde y_{{1t}} - \\bar{{\\tilde y}}_1) - \\sum_j w_j(\\tilde y_{{jt}} - \\bar{{\\tilde y}}_j)\\big]^2$, with $w_j \\ge 0$ and $\\sum_j w_j = 1$
3. Counterfactual: $\\hat y_{{1t}}(0) = \\sum_j w_j \\tilde y_{{jt}} + \\alpha$, where $\\alpha$ aligns pre-period means
4. Lift: $\\dfrac{{\\sum_{{t \\in \\text{{test}}}} y_{{1t}}}}{{\\sum_{{t \\in \\text{{test}}}} \\hat y_{{1t}}(0)}} - 1$

## After the test

- **Incremental CAC** = investment ÷ incremental accounts: the cost of each account that **only exists because of TV**.
- The lift becomes a **ROI prior** for the MMM: the experiment tells the model how much TV really pays
  (see the Prisma project).

## Honest limitations

- Assumes TV in one city doesn't "leak" into the twin's cities.
- Measures the effect in **these** cities, in **this** period. Scaling to all of Brazil is an extrapolation.
- Four weeks capture the short-term effect; long-term brand effect is left out.

*Inspired by [GeoLift](https://github.com/facebookincubator/GeoLift) (Meta, in R). Everything here was
rebuilt from scratch in Python to stay transparent.*
"""


# ---------------------------------------------------------------------------
# A conta da gêmea (regressão com regras)
# ---------------------------------------------------------------------------
def txt_conta_intro(c, lang):
    if lang == "pt":
        return f"""
### 🧮 A conta da gêmea, passo a passo

**Exemplo:** pense numa receita de bolo. A receita diz *quanto* de cada ingrediente vai na massa: 20% de farinha,
15% de açúcar... A gêmea de **{c['cidade_sel']}** é uma receita igual: diz quanto de cada cidade entra na mistura.
Achar a receita é descobrir esses "quantos".

**E sim, é parecido com uma regressão.** De um lado, a cidade testada (o *y*). Do outro, as cidades sem TV
(os *x*). Os **pesos são os coeficientes**:
"""
    return f"""
### 🧮 The twin's math, step by step

**Example:** think of a cake recipe. It says *how much* of each ingredient goes in: 20% flour, 15% sugar...
**{c['cidade_sel']}**'s twin is the same kind of recipe: how much of each city goes into the blend. Finding the
recipe means finding those "how muches".

**And yes, it looks like a regression.** On one side, the tested city (the *y*). On the other, the cities without TV
(the *x*'s). The **weights are the coefficients**:
"""


def txt_conta_regras(c, lang):
    if lang == "pt":
        return f"""
onde $y_t$ é o índice de {c['cidade_sel']} no dia $t$ (contas do dia ÷ média antes da TV), $x_{{jt}}$ é o índice da
cidade $j$ e $w_j$ é o peso dela na receita.

**Os pesos precisam obedecer duas regras:**
- **Nenhum peso negativo:** $w_j \\ge 0$
- **Os pesos somam 100%:** $\\sum_j w_j = 1$

Na receita do bolo: não existe "menos 2 xícaras de farinha" (peso negativo) e as porcentagens precisam fechar
100% (soma 1). Com essas regras, a gêmea sempre fica **dentro** do que as cidades reais fazem — ela não consegue
inventar um comportamento que nenhuma cidade teve.

**Como os pesos são escolhidos:** minimizando o erro quadrático **só no período antes da TV**:
"""
    return f"""
where $y_t$ is {c['cidade_sel']}'s index on day $t$ (accounts that day ÷ pre-TV mean), $x_{{jt}}$ is city $j$'s
index and $w_j$ is its weight in the recipe.

**The weights must follow two rules:**
- **No negative weights:** $w_j \\ge 0$
- **Weights add up to 100%:** $\\sum_j w_j = 1$

In the cake recipe: there's no "minus 2 cups of flour" (negative weight), and the percentages must add up to 100%
(sum to 1). With these rules, the twin always stays **within** what real cities do — it can't invent behavior no
city ever had.

**How the weights are chosen:** by minimizing squared error **only in the period before TV**:
"""


def txt_conta_depois(c, lang):
    if lang == "pt":
        return f"""
#### Agora com os dados do projeto: a gêmea de {c['cidade_sel']}

O $\\alpha$ (intercepto) alinha o nível médio da gêmea com o da cidade antes da TV. Como aqui tudo foi
**indexado** (cada cidade dividida pela própria média do pré), as médias já batem e o $\\alpha$ sai praticamente
zero: $\\alpha = {c['alfa']:.3f}$.

**No código:** a otimização com essas regras é um *mínimos quadrados não negativos* (NNLS, `scipy.optimize.nnls`)
com uma linha extra que "multa" quando a soma dos pesos foge de 1. Depois, **a mesma receita** é aplicada nos dias
com TV — é aí que a gêmea vira o "universo sem comercial".

**A conta num dia de verdade.** Escolha um dia e veja a receita sendo aplicada. Cada linha é um
ingrediente: o índice da cidade naquele dia × o peso dela na receita.
"""
    return f"""
#### Now with the project's data: {c['cidade_sel']}'s twin

The $\\alpha$ (intercept) aligns the twin's average level with the city's before TV. Since everything here was
**indexed** (each city divided by its own pre-period mean), the averages already match and $\\alpha$ comes out
practically zero: $\\alpha = {c['alfa']:.3f}$.

**In code:** the optimization with these rules is a *non-negative least squares* (NNLS, `scipy.optimize.nnls`)
with an extra row that "fines" the sum of weights for drifting from 1. Then **the same recipe** is applied to the
TV days — that's when the twin becomes the "universe without the ad".

**Doing the math on a real day.** Pick a day and watch the recipe being applied. Each row is an ingredient:
the city's index that day × its weight in the recipe.
"""


def txt_conta_resultado(c, lang):
    tv = c["dia_tv"]
    if lang == "pt":
        d = lambda x, n: f"{x:.{n}f}".replace(".", ",")  # noqa: E731
        base = (f"**Somando tudo:** índice da gêmea = **{d(c['ind_gemea'], 3)}**. Como 1,000 = {d(c['base'], 1)} contas "
                f"(a média de {c['cidade_sel']} antes da TV), a gêmea \"abriu\" {d(c['ind_gemea'], 3)} × {d(c['base'], 1)} = "
                f"**{c['contas_gemea']:.0f} contas**. A {c['cidade_sel']} de verdade abriu **{c['contas_real']:.0f}**.")
        fim = (f" Como esse dia é **durante a TV**, a diferença de **{c['contas_real'] - c['contas_gemea']:+.0f} contas** "
               "é o efeito estimado da TV naquele dia." if tv else
               f" Como esse dia é **antes da TV**, a diferença ({c['contas_real'] - c['contas_gemea']:+.0f}) é só o erro "
               "normal da imitação — é por isso que olhamos o efeito na soma de 28 dias, e não num dia solto.")
        return base + fim
    base = (f"**Adding it all up:** twin index = **{c['ind_gemea']:.3f}**. Since 1.000 = {c['base']:.1f} accounts "
            f"({c['cidade_sel']}'s pre-TV mean), the twin \"opened\" {c['ind_gemea']:.3f} × {c['base']:.1f} = "
            f"**{c['contas_gemea']:.0f} accounts**. The real {c['cidade_sel']} opened **{c['contas_real']:.0f}**.")
    fim = (f" Since this day is **during TV**, the gap of **{c['contas_real'] - c['contas_gemea']:+.0f} accounts** is the "
           "estimated TV effect that day." if tv else
           f" Since this day is **before TV**, the gap ({c['contas_real'] - c['contas_gemea']:+.0f}) is just the normal "
           "imitation error — that's why we read the effect over the 28-day sum, not on a single day.")
    return base + fim


