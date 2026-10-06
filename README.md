# 🌌 Multiverso — GeoLift com controle sintético

> **A TV trouxe contas novas?** O Multiverso compara o mundo real com o universo paralelo onde o comercial nunca foi ao ar.

**App:** https://multiverso-geolift.streamlit.app/ (em construção) · **Portfólio:** https://gabigattirodrigues.github.io/#multiverso

🇧🇷 Português · [🇺🇸 English](#-english)

**Cenário fictício:** o **Orbe**, um banco digital, quer saber se comerciais em TV aberta trazem contas novas. Antes de investir no Brasil todo, ele testa em 3 cidades por 4 semanas e mede o efeito com **GeoLift**.

Reconstrução pública, com dados 100% sintéticos, de um projeto real que fiz no varejo.

## Resultado

| | |
|---|---|
| Cidades testadas | Sorocaba, Curitiba e Recife (escolhidas pela análise de poder) |
| Lift estimado | **+8,8%** de contas novas (IC 90%: +3,0% a +14,0%) |
| Contas incrementais | ~1.013 em 28 dias |
| CAC incremental | R$ 237 (alvo: R$ 400) → **escalar** |
| p-valor (efeito zero) | 0,020 |
| Verdade (dado sintético) | +8,7% ✅ dentro do intervalo |

## O que é GeoLift?

Você tem duas sorveterias iguaizinhas. Numa você põe um palhaço na porta, na outra não. No fim do dia, a do palhaço vendeu mais? Então o palhaço funciona! 🤡🍦

GeoLift é isso com cidades: liga a propaganda em algumas, deixa outras sem, e compara. Como TV não dá pra mostrar pra uma pessoa e esconder do vizinho, o "sorteio" é de cidades, não de pessoas.

**O problema:** não existem duas cidades iguais. Então, para cada cidade testada, a gente **fabrica** uma cidade gêmea, misturando pedacinhos de várias cidades que não viram a TV — como uma receita de suco que, antes da campanha, tinha exatamente o mesmo gosto das cidades testadas. Se depois da TV as cidades reais "ficam mais doces" que a mistura, o açúcar extra foi a TV.

## As 4 etapas

| Etapa | Pergunta | Exemplo | Técnico |
|---|---|---|---|
| 1. Desenho | Onde testar? | Escolher a sala mais silenciosa pra ouvir um sussurro | Análise de poder por simulação em janelas históricas → MDE |
| 2. Campanha | — | Pôr o palhaço na porta | TV em 3 cidades por 28 dias |
| 3. Gêmea | O que teria acontecido sem TV? | Montar uma plantinha de mentira com pedaços de outras | Controle sintético (pesos ≥ 0, soma 1, com intercepto) |
| 4. Leitura | Foi sorte? Valeu o dinheiro? | Fila de suspeitos | Inferência conforme + placebo no espaço; CAC incremental |

### 1. Como as cidades foram escolhidas
Fazemos **ensaios no passado**: campanhas de mentira em 12 datas do histórico (jan–abr, quando não teve TV). Em cada uma, multiplicamos as contas das cidades candidatas nos 28 dias por um efeito conhecido (0%, 2,5%, 5%… 25%), rodamos o GeoLift inteiro e anotamos se ele percebeu (p ≤ 0,10). É como testar uma balança com uma moeda de peso conhecido. O menor efeito percebido em ≥ 80% dos ensaios é o **MDE**; perceber efeito com 0% é **alarme falso**.

O funil da escolha:
1. 38 cidades avaliadas sozinhas (menos SP e Rio, caras demais) → 14 finalistas.
2. 176 grupos de 3 finalistas, uma por região (um choque regional não contamina o teste todo).
3. 173 cabem no orçamento (custo ∝ população, até 12%).
4. 31 enxergam um efeito de 2,5% (o menor MDE).
5. 1 sem nenhum alarme falso → **Sorocaba, Curitiba e Recife**.

### 2. Como as cidades gêmeas são montadas
Cada cidade testada ganha **a sua** gêmea (no mapa do app, cada uma tem uma cor e as cidades que a formam aparecem na mesma cor). O efeito do teste é a soma das 3 cidades reais ÷ soma das 3 gêmeas − 1.
1. Cada cidade vira um índice (contas ÷ média do pré).
2. Pesos `w ≥ 0`, somando 100%, que deixam a mistura mais parecida com as tratadas no pré (NNLS — Abadie, 2010).
3. Intercepto livre: a gêmea copia o **formato** da curva, não o nível (Ferman & Pinto, 2021).

#### A conta: uma regressão com regras

**Exemplo:** a gêmea é uma receita de bolo. A receita diz quanto de cada ingrediente vai na massa; aqui, quanto de cada cidade sem TV entra na mistura.

Parece uma regressão: a cidade testada é o `y`, as cidades sem TV são os `x` e os **pesos são os coeficientes**:

$$y_t \approx \alpha + w_1 x_{1t} + w_2 x_{2t} + \dots + w_J x_{Jt}$$

Os pesos saem de

$$\min_w \sum_{t \in \text{pré}} \Big(y_t - \alpha - \sum_j w_j x_{jt}\Big)^2 \quad \text{s.a.} \quad w_j \ge 0,\ \sum_j w_j = 1$$

As **regras**: não existe "menos 2 xícaras de farinha" (peso negativo) e as porcentagens fecham 100% (soma 1). Assim a gêmea é sempre uma mistura de cidades reais. Como as séries foram indexadas, o `α` sai praticamente zero. No código: `scipy.optimize.nnls` com uma linha extra que força a soma 1.

**Exemplo mastigado (como chegamos nos pesos).** Alvo + 3 cidades sem TV (A, B, C), 6 semanas antes e 2 com TV (`exemplo_didatico()` em `geolift/motor.py`):

1. **Índice:** cada semana ÷ média das 6 semanas antes da TV (ex.: A na S1 = 180 ÷ 200 = 0,90).
2. **Peso antes (chute):** ⅓ para cada cidade → gêmea S1 = 0,333×0,90 + 0,333×1,05 + 0,333×1,00 = 0,983; erro −1,3%; soma dos erros² nas 6 semanas = 62,4.
3. **Rodadas:** a cada rodada o algoritmo vê pra que lado o erro cai (gradiente), mexe um pouco nos pesos, zera quem ficou negativo e reajusta para somar 100%. C (que anda na contramão do Alvo) chega a 0% na rodada 20.
4. **Peso depois (final):** A 56,25%, B 43,75%, C 0% → gêmea S1 = 0,966; erro +0,4%; soma dos erros² = 1,1.
5. **Com TV:** a mesma receita aplicada a A e B dá 335,8 e 349,5 contas (total 685,3); o Alvo abriu 370 e 385 (total 755) → efeito = 755 ÷ 685,3 − 1 = **+10,2%**.

No app, a aba 🧮 faz a conta inteira num dia de verdade: índice de cada cidade × peso, soma, e a conversão para contas.

### 3. Foi sorte?
- **Fila de suspeitos (placebo no espaço):** cada cidade sem TV finge ter recebido TV. O grupo tratado precisa se destacar de todas.
- **Inferência conforme** (mesma família do GeoLift do Meta): para cada efeito θ, tiramos θ do teste, embaralhamos os erros no tempo e vemos se o pedaço da campanha parece "estranho". Os θ não estranhos formam o intervalo.

## Estrutura

```
multiverso/
├── app.py                 # app Streamlit (PT/EN)
├── textos.py              # todos os textos e explicações, PT e EN
├── geolift/motor.py       # controle sintético, inferência, seleção de mercados
├── dados/
│   ├── gerar_dados.py     # gera a base sintética e roda a seleção de mercados
│   ├── contas_diarias.csv # o que o analista enxerga
│   ├── verdade.csv        # contrafactual verdadeiro (só para conferência)
│   ├── cidades.csv, campanha.json, selecao_*.csv, brasil_contorno.json
├── assets/multiverso.jpg  # imagem da barra lateral
├── requirements.txt
└── rodar_app.bat          # Windows: instala e abre o app
```

## Como rodar

```bash
pip install -r requirements.txt
python dados/gerar_dados.py   # opcional: os dados já vêm prontos (~1 min)
streamlit run app.py
```
No Windows, é só dar dois cliques em `rodar_app.bat`.

## Abas do app
📖 O case · 🎯 Resultado · 🗺️ Mapa · 🧭 Desenho do teste (ensaios no passado, curva de poder, funil da escolha) · 🧬 As gêmeas · 🧮 A conta da gêmea (exemplo feito à mão) · 🔍 Robustez (fila de suspeitos e suspeitas testadas) · 🧪 Laboratório (você escolhe a verdade e vê o método acertar ou errar) · 📊 Dados · 📚 Como funciona

## Limitações
- Supõe que a TV de uma cidade não vaza para as cidades da gêmea.
- Mede o efeito nessas cidades, nesse período; escalar para o Brasil é extrapolação.
- 4 semanas medem curto prazo; efeito de marca de longo prazo fica de fora.

Inspirado no [GeoLift](https://github.com/facebookincubator/GeoLift) (Meta, em R), reimplementado do zero em Python. O lift deste teste pode virar **prior de ROI** no MMM do projeto Prisma.

**Stack:** Python · NumPy · pandas · SciPy · Plotly · Streamlit
Contorno do Brasil: Natural Earth (domínio público).

---

## 🇺🇸 English

**Fictional scenario:** **Orbe**, a digital bank, wants to know whether broadcast TV ads bring new accounts. Before spending nationwide, it tests in 3 cities for 4 weeks and measures the effect with **GeoLift**. Public rebuild, with 100% synthetic data, of a real project I did in retail.

**Result:** +8.8% new accounts (90% CI +3.0% to +14.0%), ~1,013 incremental accounts, incremental CAC R$ 237 vs R$ 400 target → scale. True effect (synthetic): +8.7%, inside the interval.

**How it works:** (1) choose test cities with a simulation-based power analysis on historical windows (MDE); (2) run TV in the chosen cities; (3) build a **synthetic twin for each tested city** — a non-negative, sum-to-one blend of untreated cities that mimics the treated ones before the campaign; (4) read the gap, with conformal inference and in-space placebos to rule out luck.

**Run:** `pip install -r requirements.txt` → `streamlit run app.py`. The app is bilingual (PT/EN toggle in the sidebar).

By Gabriela Gatti Rodrigues · [LinkedIn](https://www.linkedin.com/in/gabriela-gatti-rodrigues) · [Portfolio](https://gabigattirodrigues.github.io/)
