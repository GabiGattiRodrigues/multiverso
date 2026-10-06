"""Textos das abas O case, Desenho do teste, Robustez e Laboratório (PT e EN).

Os números vêm do dicionário `c`, montado no app a partir dos resultados reais.
"""


def _d(x, casas=1, lang="pt"):
    s = f"{x:.{casas}f}"
    return s.replace(".", ",") if lang == "pt" else s


# ---------------------------------------------------------------------------
# O case
# ---------------------------------------------------------------------------
def txt_case(c, lang):
    d = lambda x, k=1: _d(x, k, lang)  # noqa: E731
    if lang == "pt":
        return f"""
## O case

### O problema de negócio
O **Orbe** é um banco digital (fictício) que traz clientes principalmente por mídia digital, onde cada conta tem
rastro: clique, link, cupom. O time de marketing quer testar **TV aberta**, que alcança muita gente mas **não deixa
rastro**: ninguém clica num comercial. A diretoria fez três perguntas:

1. A TV traz **contas novas que não viriam de outro jeito**?
2. Quanto custa **cada conta extra**?
3. **Vale escalar** para o Brasil todo?

### Por que não dá para medir do jeito de sempre
- **Não tem clique:** não dá para atribuir conta por conta à TV.
- **Antes × depois engana:** se as contas subirem em maio, pode ser salário, sazonalidade, concorrente… não dá
  para separar o que foi da TV.
- **Teste A/B comum não funciona:** não dá para mostrar o comercial para uma pessoa e esconder do vizinho.
  Quem "recebe" a TV é a cidade inteira.

### A solução: um teste geográfico (GeoLift)
Ligar a TV em **poucas cidades** e comparar com o que essas cidades teriam feito **sem** a TV. Esse "sem TV"
não existe, então ele é construído: para cada cidade testada, montamos uma **cidade gêmea** misturando cidades
que não viram o comercial. A diferença entre a cidade real e a gêmea durante a campanha é o efeito da TV.

### Como foi feito
| Quando | O quê |
|---|---|
| jan–abr/2026 | Histórico de contas novas por dia em 40 cidades (sem TV em lugar nenhum) |
| antes de ligar a TV | **Desenho do teste:** ensaios com o histórico para escolher onde testar → **{c['cidades_txt']}** |
| 4 a 31/mai/2026 | **Campanha:** TV nas 3 cidades, R$ {c['invest_txt']} de investimento, ~{d(c['custo_pct'])}% da população coberta |
| depois | **Leitura:** cidades gêmeas, efeito, checagens de sorte e custo por conta |

### A resposta
- **A TV funciona:** **+{d(c['lift'])}%** de contas novas nas cidades testadas (~{c['incr_txt']} contas a mais em 4 semanas).
- **Não foi sorte:** a chance de um resultado assim sem efeito nenhum é de {d(c['p'] * 100)}%.
- **Custo de cada conta extra:** R$ {c['cac_txt']}, abaixo do alvo de R$ {c['cac_meta_txt']} → **recomendação: escalar**
  para praças parecidas, medindo de novo, e usar o resultado para calibrar o MMM.

### De onde vem este projeto
É a reconstrução pública de um projeto real que fiz no varejo: um GeoLift para medir se inserções de TV traziam
novos clientes. Aqui o cenário é outro (banco digital) e **os dados são 100% sintéticos**, o que tem uma vantagem:
como fui eu que gerei os dados, **sei o efeito verdadeiro** (+{d(c['v_lift'])}%) e dá para conferir se o método acerta.

### Guia das abas
| Aba | O que tem |
|---|---|
| 🎯 Resultado | O efeito da TV, o gráfico real × gêmeas e a conferência com a verdade |
| 🗺️ Mapa | Onde estão as cidades testadas e quem forma a gêmea de cada uma |
| 🧭 Desenho do teste | Como as 3 cidades foram escolhidas, com os ensaios no passado |
| 🧬 As gêmeas | A receita de cada cidade gêmea |
| 🧮 A conta da gêmea | A matemática, com um exemplo pequeno feito à mão |
| 🔍 Robustez | Como sabemos que não foi sorte |
| 🧪 Laboratório | Você escolhe o efeito verdadeiro e vê o método acertar ou errar |
| 📊 Dados | Os dados usados |
| 📚 Como funciona | O método resumido, com as fórmulas |
"""
    return f"""
## The case

### The business problem
**Orbe** is a (fictional) digital bank that acquires customers mostly through digital media, where every account
leaves a trail: click, link, coupon. Marketing wants to test **broadcast TV**, which reaches lots of people but
**leaves no trail**: nobody clicks on a TV ad. Leadership asked three questions:

1. Does TV bring **new accounts that wouldn't have come otherwise**?
2. How much does **each extra account** cost?
3. Is it **worth scaling** nationwide?

### Why the usual measurement doesn't work
- **No clicks:** you can't attribute accounts one by one to TV.
- **Before × after is misleading:** if accounts rise in May, it could be paydays, seasonality, a competitor…
- **A regular A/B test doesn't work:** you can't show the ad to one person and hide it from the neighbor.
  The whole city "receives" TV.

### The solution: a geo test (GeoLift)
Turn TV on in **a few cities** and compare with what those cities would have done **without** TV. That "no TV"
world doesn't exist, so it's built: for each tested city, we make a **twin city** by blending cities that didn't
see the ad. The gap between the real city and its twin during the campaign is the TV effect.

### How it was done
| When | What |
|---|---|
| Jan–Apr 2026 | Daily new accounts in 40 cities (no TV anywhere) |
| before TV | **Test design:** rehearsals on history to choose where to test → **{c['cidades_txt']}** |
| May 4–31, 2026 | **Campaign:** TV in the 3 cities, R$ {c['invest_txt']} invested, ~{d(c['custo_pct'])}% of population covered |
| after | **Readout:** twin cities, effect, luck checks and cost per account |

### The answer
- **TV works:** **+{d(c['lift'])}%** new accounts in the tested cities (~{c['incr_txt']} extra accounts in 4 weeks).
- **It wasn't luck:** the chance of a result like this with no effect at all is {d(c['p'] * 100)}%.
- **Cost per extra account:** R$ {c['cac_txt']}, below the R$ {c['cac_meta_txt']} target → **recommendation: scale**
  to similar markets, measuring again, and use the result to calibrate the MMM.

### Where this project comes from
It's a public rebuild of a real project I did in retail: a GeoLift to measure whether TV spots brought new
customers. Here the setting is different (digital bank) and **the data is 100% synthetic**, which has an upside:
since I generated the data, **I know the true effect** (+{d(c['v_lift'])}%) and can check whether the method gets it right.

### Tab guide
| Tab | What's in it |
|---|---|
| 🎯 Result | The TV effect, the real × twins chart and the check against the truth |
| 🗺️ Map | Where the tested cities are and who makes up each twin |
| 🧭 Test design | How the 3 cities were chosen, with the rehearsals in the past |
| 🧬 The twins | Each twin city's recipe |
| 🧮 The twin's math | The math, with a small hand-worked example |
| 🔍 Robustness | How we know it wasn't luck |
| 🧪 Lab | You choose the true effect and watch the method get it right or wrong |
| 📊 Data | The data used |
| 📚 How it works | The method in short, with formulas |
"""


# ---------------------------------------------------------------------------
# Desenho do teste
# ---------------------------------------------------------------------------
def txt_desenho_intro(c, lang):
    if lang == "pt":
        return """
### Antes de ligar a TV: onde testar?

**Exemplo:** imagine que você quer ouvir um sussurro. Numa festa barulhenta você não ouve nada; numa biblioteca,
ouve tudo. Algumas cidades são "festas barulhentas": as contas sobem e descem sozinhas e o efeito da TV some no meio
do barulho. Queremos as cidades-biblioteca.

Essa escolha é feita **só com os dados do passado** (jan–abr), antes de gastar qualquer real com TV. E a
ferramenta para medir o "barulho" de cada cidade são os **ensaios no passado**.
"""
    return """
### Before turning TV on: where to test?

**Example:** imagine you want to hear a whisper. At a noisy party you hear nothing; in a library you hear it all.
Some cities are "noisy parties": accounts go up and down on their own and the TV effect gets lost in the noise.
We want library cities.

This choice is made **only with past data** (Jan–Apr), before spending a cent on TV. And the tool to measure each
city's "noise" is the **rehearsals in the past**.
"""


def txt_ensaios(c, lang):
    d = lambda x, k=1: _d(x, k, lang)  # noqa: E731
    if lang == "pt":
        return f"""
#### O que são os ensaios no passado?

São **campanhas de mentira** feitas em cima do histórico, em semanas em que **a gente sabe que nada aconteceu**.

**Exemplo:** para saber se uma balança é boa, você coloca um peso que conhece (uma moeda de 10 g) e vê se ela
marca. Se ela não percebe a moeda, não adianta usá-la para pesar coisas pequenas. Aqui, a "moeda" é um efeito de
TV inventado, de tamanho conhecido, e a "balança" é o GeoLift.

**Passo a passo de um ensaio:**
1. Escolhemos uma data de início de mentira no histórico, por exemplo **{c['ens_ini']}**, e 28 dias de "campanha"
   ({c['ens_ini']} a {c['ens_fim']}). Nesses dias não teve TV nenhuma.
2. Nas cidades candidatas, **multiplicamos as contas desses 28 dias** por um efeito que nós escolhemos. Com +2,5%,
   um dia com 200 contas vira 205.
3. Rodamos o GeoLift inteiro, como se fosse a campanha de verdade: monta as gêmeas com os dias **antes** do início
   de mentira, compara e calcula o p-valor.
4. Anotamos: o GeoLift **percebeu** o efeito (p-valor ≤ 0,10)? Sim ou não.

Repetimos isso com **{c['n_janelas']} datas de início diferentes** (a cada 3 dias, de {c['ens_primeiro']} a
{c['ens_ultimo']}) e com vários tamanhos de efeito (0%, 2,5%, 5%… até 25%).

- Com **efeito 0%** (não colocamos nada), o certo é o GeoLift **não** perceber. Se ele "percebe", é um **alarme falso**.
- O **poder** para um efeito é a fração dos {c['n_janelas']} ensaios em que ele percebeu.
- O **MDE** (menor efeito detectável) é o menor efeito percebido em **pelo menos 80%** dos ensaios.

Veja abaixo os {c['n_janelas']} ensaios das cidades escolhidas. Mude o tamanho do efeito de mentira:
"""
    return f"""
#### What are the rehearsals in the past?

They're **fake campaigns** run on historical data, in weeks when **we know nothing happened**.

**Example:** to know if a scale is good, you put a known weight on it (a 10 g coin) and see if it registers. If it
can't feel the coin, it's no use for weighing small things. Here the "coin" is a made-up TV effect of known size,
and the "scale" is GeoLift.

**Step by step of one rehearsal:**
1. We pick a fake start date in the history, e.g. **{c['ens_ini']}**, and 28 days of "campaign"
   ({c['ens_ini']} to {c['ens_fim']}). There was no TV on those days.
2. In the candidate cities, we **multiply the accounts of those 28 days** by an effect we choose. With +2.5%,
   a day with 200 accounts becomes 205.
3. We run the whole GeoLift as if it were the real campaign: build the twins with the days **before** the fake
   start, compare and compute the p-value.
4. We write down: did GeoLift **notice** the effect (p-value ≤ 0.10)? Yes or no.

We repeat this with **{c['n_janelas']} different start dates** (every 3 days, from {c['ens_primeiro']} to
{c['ens_ultimo']}) and with several effect sizes (0%, 2.5%, 5%… up to 25%).

- With **0% effect** (we added nothing), the right answer is for GeoLift **not** to notice. If it does, that's a **false alarm**.
- The **power** for an effect is the share of the {c['n_janelas']} rehearsals in which it noticed.
- The **MDE** (minimum detectable effect) is the smallest effect noticed in **at least 80%** of rehearsals.

Below are the {c['n_janelas']} rehearsals of the chosen cities. Change the size of the fake effect:
"""


def txt_poder(c, lang):
    d = lambda x, k=1: _d(x, k, lang)  # noqa: E731
    if lang == "pt":
        return f"""
#### A curva de poder: resumo de todos os ensaios

Cada ponto do gráfico é **um tamanho de efeito de mentira** (eixo horizontal) e mostra **em quantos dos
{c['n_janelas']} ensaios o GeoLift percebeu** (eixo vertical). Como ler:

- **Em 0%:** não colocamos efeito nenhum, então o ideal é **0%** (nenhum alarme falso). Aqui deu {d(c['fp'] * 100, 0)}%.
- **Em 2,5%:** o GeoLift percebeu em **{d(c['poder25'] * 100, 0)}%** dos ensaios, acima da linha de 80%.
  Por isso o **MDE é {d(c['mde'])}%**.
- **De 5% para cima:** percebeu em todos.

**De onde vem o "+10% esperado"?** É a hipótese de planejamento: antes do teste ninguém sabe o efeito da TV, então o
time usa uma estimativa (campanhas parecidas, benchmarks de mercado ou o MMM) para checar se o teste tem chance de
enxergá-lo. Como o esperado (~10%) é bem maior que o MDE, o teste tem folga. O efeito de verdade só aparece depois,
na leitura do teste.
"""
    return f"""
#### The power curve: a summary of all rehearsals

Each point is **one fake effect size** (horizontal axis) and shows **in how many of the {c['n_janelas']} rehearsals
GeoLift noticed it** (vertical axis). How to read it:

- **At 0%:** we added no effect, so the ideal is **0%** (no false alarms). Here it was {d(c['fp'] * 100, 0)}%.
- **At 2.5%:** GeoLift noticed in **{d(c['poder25'] * 100, 0)}%** of rehearsals, above the 80% line.
  That's why the **MDE is {d(c['mde'])}%**.
- **From 5% up:** it noticed every time.

**Where does the "expected +10%" come from?** It's the planning hypothesis: before the test nobody knows TV's effect,
so the team uses an estimate (similar campaigns, market benchmarks or the MMM) to check whether the test can see it.
Since the expected (~10%) is well above the MDE, the test has room to spare. The real effect only shows up later, in
the test readout.
"""


def txt_funil(c, lang):
    d = lambda x, k=1: _d(x, k, lang)  # noqa: E731
    if lang == "pt":
        return f"""
#### Do Brasil todo até 3 cidades: o funil da escolha

Todas as etapas usam só o histórico. Cada linha do funil é um filtro:

1. **{c['n_cidades']} cidades avaliadas sozinhas.** Todas menos São Paulo e Rio, onde a TV é cara demais para um
   teste. Cada uma passa pelos ensaios e ganha um MDE próprio.
2. **{c['n_final']} finalistas.** As cidades mais "silenciosas" (menor MDE; no empate, menor erro nos ensaios).
3. **{c['n_grupos']} grupos de 3.** Todas as combinações de 3 finalistas **de regiões diferentes**. Se as 3 fossem do
   Sul, uma chuva forte no Sul estragaria o teste inteiro.
4. **{c['n_orc']} cabem no orçamento.** O preço da TV acompanha o tamanho da cidade, então o grupo pode cobrir no
   máximo {d(c['teto'], 0)}% da população das 40 cidades.
5. **{c['n_mde']} enxergam um efeito de {d(c['mde'])}%.** Ficam os grupos com o menor MDE possível.
6. **{c['n_fp']} sem nenhum alarme falso.** Entre esses, ficam os que nunca "perceberam" efeito nos ensaios com 0%.
7. **Escolhido: {c['cidades_txt']}**, cobrindo {d(c['custo_pct'])}% da população.

Juntar 3 cidades ajuda: o barulho de uma compensa o da outra. Por isso grupos chegam a MDEs menores que as cidades sozinhas.
"""
    return f"""
#### From all of Brazil to 3 cities: the selection funnel

Every step uses only historical data. Each funnel row is a filter:

1. **{c['n_cidades']} cities assessed alone.** All except São Paulo and Rio, where TV is too expensive for a test.
   Each goes through the rehearsals and gets its own MDE.
2. **{c['n_final']} finalists.** The "quietest" cities (lowest MDE; on ties, lowest rehearsal error).
3. **{c['n_grupos']} groups of 3.** Every combination of 3 finalists **from different regions**. If all 3 were in the
   South, a storm in the South would ruin the whole test.
4. **{c['n_orc']} fit the budget.** TV prices follow city size, so a group can cover at most
   {d(c['teto'], 0)}% of the 40 cities' population.
5. **{c['n_mde']} can see a {d(c['mde'])}% effect.** The groups with the lowest possible MDE remain.
6. **{c['n_fp']} with no false alarms.** Among those, the ones that never "noticed" an effect in the 0% rehearsals remain.
7. **Chosen: {c['cidades_txt']}**, covering {d(c['custo_pct'])}% of the population.

Pooling 3 cities helps: one city's noise offsets another's. That's why groups reach lower MDEs than single cities.
"""


def txt_comparar_grupos(lang):
    if lang == "pt":
        return ("**Por que esse grupo e não outro?** O gráfico compara a curva de poder do escolhido com dois "
                "concorrentes. O **2º colocado** também enxerga 2,5%, mas deu alarme falso em um ensaio (ponto acima de "
                "zero em 0%). O grupo com **MDE de 5%** só passa da linha de 80% a partir de 5%: ele deixaria passar "
                "um efeito pequeno.")
    return ("**Why this group and not another?** The chart compares the chosen group's power curve with two "
            "competitors. The **runner-up** also sees 2.5%, but raised a false alarm in one rehearsal (point above "
            "zero at 0%). The **5% MDE** group only crosses the 80% line from 5% on: it would miss a small effect.")


def txt_ranking(lang):
    if lang == "pt":
        return """
#### Ranking dos grupos

A tabela mostra os 15 melhores grupos, já na ordem da escolha. O que cada coluna quer dizer:

| Coluna | O que é | Melhor quando |
|---|---|---|
| **Custo** | % da população das 40 cidades que o grupo cobre (o preço da TV acompanha) | menor (e no máximo 12%) |
| **MDE** | menor efeito que o GeoLift percebe em pelo menos 80% dos ensaios | menor |
| **Alarmes falsos** | % dos ensaios com efeito 0% em que o GeoLift "viu" um efeito que não existia | menor (ideal 0%) |
| **Poder em 2,5%** | % dos ensaios em que um efeito de 2,5% foi percebido | maior |
| **Erro de imitação** | erro médio diário das gêmeas antes da TV (MAPE). Mostra se a gêmea copia bem | menor |

A ordem é: menor MDE → menos alarmes falsos → menor erro nos ensaios.
"""
    return """
#### Group ranking

The table shows the top 15 groups, already in selection order. What each column means:

| Column | What it is | Better when |
|---|---|---|
| **Cost** | % of the 40 cities' population the group covers (TV price follows it) | lower (and at most 12%) |
| **MDE** | smallest effect GeoLift notices in at least 80% of rehearsals | lower |
| **False alarms** | % of 0%-effect rehearsals in which GeoLift "saw" an effect that wasn't there | lower (ideally 0%) |
| **Power at 2.5%** | % of rehearsals in which a 2.5% effect was noticed | higher |
| **Imitation error** | the twins' mean daily error before TV (MAPE). Shows how well the twin copies | lower |

The order is: lowest MDE → fewest false alarms → lowest rehearsal error.
"""


# ---------------------------------------------------------------------------
# Robustez
# ---------------------------------------------------------------------------
def txt_rob_intro(lang):
    if lang == "pt":
        return """
### Foi sorte?

Mesmo sem TV nenhuma, uma cidade às vezes se descola da sua gêmea: um evento local, um feriado, puro acaso.
Então precisamos responder: **o descolamento que vimos é grande demais para ser acaso?** Fazemos duas checagens.
"""
    return """
### Was it luck?

Even with no TV at all, a city sometimes drifts away from its twin: a local event, a holiday, pure chance.
So we need to answer: **is the drift we saw too big to be chance?** We run two checks.
"""


def txt_fila(c, lang):
    d = lambda x, k=2: _d(x, k, lang)  # noqa: E731
    if lang == "pt":
        return f"""
#### Checagem 1 · A fila de suspeitos (placebo no espaço)

**Exemplo:** num teste de remédio, um grupo toma o remédio e outro toma placebo (pílula de farinha). Se o remédio
funciona, quem tomou o remédio tem que melhorar **mais** do que todo mundo que tomou placebo.

Aqui, as **{c['n_rank'] - 1} cidades sem TV** fazem o papel de quem tomou placebo:
1. Fingimos que **cada uma** delas teve TV em maio.
2. Montamos uma gêmea para cada uma, do mesmo jeito que fizemos com as cidades testadas.
3. Medimos o **descolamento** de cada uma:
   - **antes da TV:** o tamanho típico da diferença diária entre a cidade e a gêmea. É o "barulho normal" dela.
   - **durante a campanha:** o mesmo tamanho típico, só nas 4 semanas de maio.
   - **descolamento = durante ÷ antes.** Perto de 1 = nada mudou. Bem acima de 1 = a cidade se descolou da gêmea.

**Resultado:** nosso grupo teve descolamento de **{d(c['razao_trat'])}**: em maio, a distância para a gêmea ficou
{d(c['razao_trat'], 1)} vezes maior que o normal. A cidade sem TV que mais se descolou foi **{c['top_placebo']}**,
com {d(c['razao_top'])}. Nosso grupo ficou em **{c['rank']}º lugar entre {c['n_rank']}**.

**O p-valor dessa checagem:** se a TV não tivesse feito nada, nosso grupo seria só mais um na fila, e a chance de
cair em 1º lugar por acaso seria de 1 em {c['n_rank']} = **{d(c['p_esp'], 3)}**.
"""
    return f"""
#### Check 1 · The line-up of suspects (placebo in space)

**Example:** in a drug trial, one group takes the drug and another takes a placebo (a sugar pill). If the drug
works, those who took it must improve **more** than everyone who took the placebo.

Here, the **{c['n_rank'] - 1} cities without TV** play the placebo group:
1. We pretend **each one** of them had TV in May.
2. We build a twin for each, the same way we did for the tested cities.
3. We measure each one's **drift**:
   - **before TV:** the typical size of the daily gap between the city and its twin. That's its "normal noise".
   - **during the campaign:** the same typical size, only for the 4 weeks of May.
   - **drift = during ÷ before.** Close to 1 = nothing changed. Well above 1 = the city drifted away from its twin.

**Result:** our group had a drift of **{d(c['razao_trat'])}**: in May, the distance to its twin was
{d(c['razao_trat'], 1)} times bigger than normal. The non-TV city that drifted the most was **{c['top_placebo']}**,
with {d(c['razao_top'])}. Our group ranked **#{c['rank']} out of {c['n_rank']}**.

**This check's p-value:** if TV had done nothing, our group would be just another one in the line-up, and the chance
of ranking #1 by luck would be 1 in {c['n_rank']} = **{d(c['p_esp'], 3)}**.
"""


def txt_conforme(c, lang):
    if lang == "pt":
        return """
#### Checagem 2 · Quais efeitos são plausíveis? (inferência conforme)

A primeira checagem diz **se** teve efeito. Esta diz **de que tamanho** ele pode ser. É a mesma família de método
usada pelo GeoLift da Meta.

**Exemplo:** é como testar suspeitas. "Suspeito que a TV deu +9%." Se for verdade, então **tirando 9%** das contas
das cidades testadas em maio, elas deveriam voltar a andar coladas nas gêmeas, como andavam antes. Se mesmo tirando
9% elas continuam descoladas (ou passam a ficar abaixo), a suspeita está errada.

**Como o teste decide se ficou "colado como antes":**
1. Calcula o erro de cada dia (cidade real − gêmea), depois de tirar o efeito suspeito.
2. Soma os erros dos 28 dias da campanha.
3. **Roleta:** gira a série de erros dia a dia (cada dia vira o começo uma vez) e, em cada giro, soma os 28 dias que
   caem no lugar da campanha. Isso mostra quão grande essa soma costuma ser por acaso.
4. **p-valor** = fração dos giros com soma tão grande quanto a da campanha. p alto = erros normais = suspeita
   plausível. p baixo (≤ 0,10) = erros estranhos = suspeita descartada.

Teste você mesma: escolha uma suspeita e veja os erros.
"""
    return """
#### Check 2 · Which effects are plausible? (conformal inference)

The first check says **whether** there was an effect. This one says **how big** it could be. It's the same family of
methods used by Meta's GeoLift.

**Example:** it's like testing suspicions. "I suspect TV gave +9%." If that's true, then **removing 9%** from the
tested cities' accounts in May, they should go back to tracking their twins closely, like before. If even after
removing 9% they're still off (or now fall below), the suspicion is wrong.

**How the test decides whether they're "tracking like before":**
1. Compute each day's error (real city − twin), after removing the suspected effect.
2. Add up the errors of the 28 campaign days.
3. **Roulette:** rotate the error series day by day (each day becomes the start once) and, in each rotation, add up
   the 28 days that land where the campaign is. This shows how big that sum usually is by chance.
4. **p-value** = share of rotations with a sum as big as the campaign's. High p = normal errors = plausible
   suspicion. Low p (≤ 0.10) = strange errors = suspicion ruled out.

Try it: pick a suspicion and look at the errors.
"""


def txt_conforme_resultado(theta, p, media_pre, media_tv, lang):
    plaus = p > 0.10
    if lang == "pt":
        return (f"Com a suspeita de **{('+' if theta > 0 else '') + _d(theta, 1)}%**: erro médio antes da TV = {_d(media_pre, 2)}%, erro médio na "
                f"campanha = **{_d(media_tv, 2)}%**, p-valor = **{_d(p, 3, lang)}** → "
                + ("✅ **plausível**: tirando esse efeito, as cidades voltam a andar coladas nas gêmeas."
                   if plaus else "❌ **descartada**: mesmo tirando esse efeito, os erros da campanha são estranhos."))
    return (f"Suspecting **{theta:+.1f}%**: mean error before TV = {media_pre:.2f}%, mean error during the campaign = "
            f"**{media_tv:.2f}%**, p-value = **{p:.3f}** → "
            + ("✅ **plausible**: removing this effect, the cities track their twins again."
               if plaus else "❌ **ruled out**: even removing this effect, the campaign errors are strange."))


def txt_curva_p(c, lang):
    d = lambda x, k=1: _d(x, k, lang)  # noqa: E731
    if lang == "pt":
        return f"""
**Fazendo isso para todas as suspeitas de −30% a +50%**, de meio em meio ponto, sai o gráfico abaixo. Cada ponto da
curva é uma suspeita e seu p-valor:
- **Acima da linha tracejada (10%)** = plausível. A faixa azul junta todas as plausíveis: é o **intervalo de 90%**,
  de **{d(c['ic_lo'])}% a {d(c['ic_hi'])}%**.
- **Efeito zero** tem p-valor de **{d(c['p'], 3)}**: muito improvável que a TV não tenha feito nada.
- A linha laranja é a **verdade** (+{d(c['v_lift'])}%), que só conhecemos porque os dados são sintéticos. Ela cai dentro da faixa.
"""
    return f"""
**Doing this for every suspicion from −30% to +50%**, in half-point steps, gives the chart below. Each point on the
curve is one suspicion and its p-value:
- **Above the dashed line (10%)** = plausible. The blue band gathers all plausible ones: it's the **90% interval**,
  from **{c['ic_lo']:.1f}% to {c['ic_hi']:.1f}%**.
- **Zero effect** has a p-value of **{c['p']:.3f}**: it's very unlikely that TV did nothing.
- The orange line is the **truth** (+{c['v_lift']:.1f}%), known only because the data is synthetic. It falls inside the band.
"""


# ---------------------------------------------------------------------------
# Laboratório
# ---------------------------------------------------------------------------
def txt_lab_intro(c, lang):
    d = lambda x, k=1: _d(x, k, lang)  # noqa: E731
    if lang == "pt":
        return f"""
### Laboratório: aqui você manda na verdade

No mundo real, nunca sabemos o efeito verdadeiro da TV. Aqui sabemos, porque os dados são sintéticos. O
laboratório usa isso para mostrar **quando o método acerta e quando ele pode errar**.

**O que acontece quando você mexe nos controles:**
1. Você escolhe o **efeito verdadeiro** da TV (o quanto ela "realmente" funcionou).
2. O app refaz as contas das 3 cidades testadas nas 4 semanas de TV com esse efeito. O resto dos dados fica igual.
3. Ele sorteia o **acaso do dia a dia** (gente que abre conta num dia e não no outro). A **semente** é o número
   desse sorteio: mesma semente = mesmo acaso; outra semente = mesmo efeito, outro acaso.
4. O GeoLift roda **do zero, sem saber a verdade**: monta as gêmeas, mede o efeito, calcula intervalo e p-valor.
5. O app compara o que o GeoLift disse com a verdade que você escolheu.

**Como ler os números:**
- **Verdade:** o efeito que você escolheu, já considerando que a TV demora uns dias para "pegar".
- **GeoLift:** o efeito que o método estimou. Embaixo, a diferença para a verdade, em pontos percentuais.
- **Intervalo de 90%:** a faixa de efeitos plausíveis. O ideal é a verdade cair dentro.
- **p-valor:** abaixo de 0,10, o GeoLift diz "teve efeito"; acima, diz "não dá para afirmar".

**Experimentos para fazer:**
- **0%:** a TV não fez nada. O certo é p-valor alto e o intervalo passando pelo zero.
- **2%:** um efeito pequeno. Troque a semente algumas vezes: o GeoLift não consegue afirmar que teve efeito, mas
  o intervalo continua contendo a verdade.
- **5%:** perto do limite. Troque a semente: às vezes ele confirma, às vezes não.
- **10%:** parecido com o caso real.
- **−3%:** a TV atrapalhou (raro, mas possível). O método também precisa enxergar efeito negativo.
"""
    return f"""
### Lab: here you control the truth

In the real world, we never know TV's true effect. Here we do, because the data is synthetic. The lab uses that to
show **when the method gets it right and when it can get it wrong**.

**What happens when you move the controls:**
1. You choose TV's **true effect** (how much it "really" worked).
2. The app rebuilds the 3 tested cities' accounts in the 4 TV weeks with that effect. The rest of the data stays the same.
3. It draws the **day-to-day chance** (people opening accounts one day and not the next). The **seed** is the number
   of that draw: same seed = same chance; another seed = same effect, different chance.
4. GeoLift runs **from scratch, without knowing the truth**: builds the twins, measures the effect, computes interval and p-value.
5. The app compares what GeoLift said with the truth you chose.

**How to read the numbers:**
- **Truth:** the effect you chose, already accounting for TV taking a few days to "kick in".
- **GeoLift:** the effect the method estimated. Below it, the gap to the truth in percentage points.
- **90% interval:** the range of plausible effects. Ideally the truth falls inside.
- **p-value:** below 0.10, GeoLift says "there was an effect"; above, it says "can't tell".

**Experiments to try:**
- **0%:** TV did nothing. The right answer is a high p-value and an interval crossing zero.
- **2%:** a small effect. Change the seed a few times: GeoLift can't confirm an effect, but the interval still
  contains the truth.
- **5%:** near the limit. Change the seed: sometimes it confirms, sometimes not.
- **10%:** close to the real case.
- **−3%:** TV hurt (rare, but possible). The method must also see negative effects.
"""


def txt_lab_veredito(verd, est, lo, hi, p, lang):
    dentro = lo <= verd <= hi
    detectou = p <= 0.10
    if lang == "pt":
        a = "✅ A verdade está **dentro** do intervalo." if dentro else "❌ A verdade ficou **fora** do intervalo."
        if abs(verd) < 0.5:
            b = ("✅ O GeoLift **não viu efeito**, como devia." if not detectou else
                 "⚠️ O GeoLift viu um efeito que **não existe** (alarme falso). Acontece em ~10% das vezes com p ≤ 0,10.")
        else:
            b = ("✅ O GeoLift **detectou** o efeito." if detectou else
                 "⚠️ O GeoLift **não conseguiu afirmar** que teve efeito: ele é pequeno demais para este teste, ou o acaso atrapalhou.")
        return a + " " + b
    a = "✅ The truth is **inside** the interval." if dentro else "❌ The truth fell **outside** the interval."
    if abs(verd) < 0.5:
        b = ("✅ GeoLift **saw no effect**, as it should." if not detectou else
             "⚠️ GeoLift saw an effect that **doesn't exist** (false alarm). It happens ~10% of the time with p ≤ 0.10.")
    else:
        b = ("✅ GeoLift **detected** the effect." if detectou else
             "⚠️ GeoLift **couldn't confirm** an effect: it's too small for this test, or chance got in the way.")
    return a + " " + b


def txt_lab_exemplo(e, lang):
    """e: dict com os números do cenário de 10% (semente 7)."""
    d = lambda x, k=1: _d(x, k, lang)  # noqa: E731
    if lang == "pt":
        return f"""
#### Exemplo guiado: a TV deu +10%

1. **Você escolhe +10%.** Isso quer dizer que, depois de "pegar", a TV aumenta as contas das 3 cidades em 10%.
2. **Por que a verdade aparece como +{d(e['verd'])}% e não +10%?** Porque a TV demora uns dias para fazer efeito:
   na primeira semana o efeito ainda está subindo (2%, 4%, 6%…) e só depois chega aos 10%. A média das 4 semanas
   fica em **+{d(e['verd'])}%**. Esse é o número que o GeoLift precisa acertar.
3. **O GeoLift roda sem saber de nada** e estima **+{d(e['est'])}%**. Errou por {d(e['est'] - e['verd'])} ponto percentual.
4. **O intervalo de 90%** vai de **{d(e['lo'])}% a {d(e['hi'])}%**. A verdade (+{d(e['verd'])}%) está dentro ✅.
5. **O p-valor** é **{d(e['p'], 3)}**, abaixo de 0,10: o GeoLift afirma que teve efeito ✅.

**Conclusão do exemplo:** com um efeito desse tamanho, o método acerta a direção, chega perto do tamanho e o
intervalo contém a verdade.

#### O mesmo teste com outros efeitos

A tabela abaixo roda o laboratório para vários efeitos verdadeiros (todos com a semente 7):
"""
    return f"""
#### Guided example: TV gave +10%

1. **You choose +10%.** That means that, once it "kicks in", TV increases the 3 cities' accounts by 10%.
2. **Why does the truth show +{e['verd']:.1f}% and not +10%?** Because TV takes a few days to work: in the first week
   the effect is still ramping up (2%, 4%, 6%…) and only then reaches 10%. The 4-week average is **+{e['verd']:.1f}%**.
   That's the number GeoLift has to hit.
3. **GeoLift runs knowing nothing** and estimates **+{e['est']:.1f}%**. It missed by {e['est'] - e['verd']:.1f} percentage point.
4. **The 90% interval** goes from **{e['lo']:.1f}% to {e['hi']:.1f}%**. The truth (+{e['verd']:.1f}%) is inside ✅.
5. **The p-value** is **{e['p']:.3f}**, below 0.10: GeoLift says there was an effect ✅.

**Takeaway:** with an effect this size, the method gets the direction right, gets close on the size, and the
interval contains the truth.

#### The same test with other effects

The table below runs the lab for several true effects (all with seed 7):
"""


def txt_lab_leitura(lang):
    if lang == "pt":
        return """
**O que a tabela ensina:**
- **0%:** o GeoLift não vê efeito, como devia. Nada de alarme falso.
- **2% e −3%:** efeitos pequenos se escondem no barulho do dia a dia. O GeoLift **não consegue afirmar** nada, mas
  o intervalo ainda contém a verdade. "Não consegui ver" é diferente de "não teve efeito".
- **A partir de ~5%:** o efeito começa a aparecer com p-valor abaixo de 0,10.
- **10% e 15%:** detecta com folga, e o intervalo contém a verdade.
- **Os palpites ficam ~1 ponto acima da verdade em todos os casos.** Não é azar repetido: a semente só muda o acaso
  das 3 cidades testadas, e as gêmeas são as mesmas em todas as linhas. Nesse maio específico, as gêmeas ficaram
  ~1 ponto abaixo do que deveriam, e esse erro aparece em todos os cenários. Por isso o intervalo existe.

**Uma lição honesta:** no Desenho do teste, os ensaios estimaram um MDE de 2,5%. Aqui, na prática, efeitos de até
~4% passam sem ser confirmados. Os ensaios usam só 12 janelas do passado, então o MDE é uma estimativa e tende a ser
otimista. Na vida real, vale planejar com folga: a TV deveria trazer algo perto de +10%, então o teste continuava
seguro, mas um efeito de 3% passaria batido.
"""
    return """
**What the table teaches:**
- **0%:** GeoLift sees no effect, as it should. No false alarm.
- **2% and −3%:** small effects hide in the day-to-day noise. GeoLift **can't confirm** anything, but the interval
  still contains the truth. "I couldn't see it" is not the same as "there was no effect".
- **From ~5% up:** the effect starts showing with a p-value below 0.10.
- **10% and 15%:** detected with room to spare, and the interval contains the truth.
- **Estimates land ~1 point above the truth in every case.** It's not repeated bad luck: the seed only changes the
  chance in the 3 tested cities, and the twins are the same in every row. In this particular May, the twins came out
  ~1 point below where they should be, and that error shows up in every scenario. That's why the interval exists.

**An honest lesson:** in Test design, the rehearsals estimated a 2.5% MDE. Here, in practice, effects up to ~4% go
unconfirmed. The rehearsals use only 12 past windows, so the MDE is an estimate and tends to be optimistic. In real
life, plan with slack: TV was expected to bring around +10%, so the test was still safe, but a 3% effect would slip by.
"""
