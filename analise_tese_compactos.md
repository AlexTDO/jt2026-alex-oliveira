# Análise da Tese dos Compactos no Centro — Itapema/SC

> **Pergunta:** "Apartamentos compactos (studio/1 quarto) na região do Centro são a aposta mais eficiente para a Seazone?"
> **Resultado da comparação:** **SIM, se sustenta — com ressalvas.** Compactos no Centro têm o melhor ROI entre as 4 combinações testadas, mas a vantagem sobre o 2q no Centro é pequena e a liquidez de oferta é baixa.

---

## 1. Metodologia

### 1.1 Fontes e preparação
| Fonte | Uso | Preparação |
|---|---|---|
| `Details_Itapema.csv` | Perfil do imóvel (nº quartos, tipo) | Join 1:1 com Mesh |
| `Mesh_Ids_Data_Itapema.csv` | Bairro real (coordenadas) | Bairros normalizados (case-insensitive, acentos) |
| `Price_AV_Itapema.csv` | Receita potencial | Removidos preços > R$ 5.000/noite (183 outliers); métricas por listing |
| `VivaReal_Itapema.csv` | Custo de compra | Apartamentos p/ venda; removidos preço < R$ 50k e área > 1.500 m² |
| `Hosts_ids_Itapema.csv` | Apoio | Deduplicar `owner_id` (4.440 linhas × 3.057 chaves) |

### 1.2 Definições
- **Perfil compacto:** studio ou 1 quarto (`number_of_bedrooms ≤ 1`).
- **Perfil médio:** 2 quartos.
- **Receita anual potencial (cenário A):** `ADR médio da diária × 365` (ocupação plena — teto teórico).
- **Receita anual realista (cenário B):** `ADR × 365 × 0,60` (60% de ocupação).
- **Custo de compra:** mediana de `sale_price` no VivaReal, por bairro × perfil (robusto a outliers).
- **ROI anual:** `Receita anual ÷ Preço de compra × 100`.
- **Amostra:** dos 4.441 anúncios, **999 têm série de preço** na Price_AV (janela 06/01 a 20/04/2025) e foram usados. É o subconjunto com dados de receita.

### 1.3 Reprodução
```bash
pip install pandas numpy matplotlib seaborn
python scripts/analise_tese_compactos.py
```
Gera `data_preparada_airbnb.csv` e `roi_comparativo.csv`.

---

## 2. Resultados

### 2.1 Receita por bairro × perfil (mediana por listing)
| Bairro | Perfil | Anúncios c/ preço | Noites cobertas (med.) | ADR (R$) | Receita anual potencial (R$) |
|---|---|---|---|---|---|
| **Centro** | **Studio/1q** | **82** | 76 | **449,95** | **164.232** |
| Centro | 2q | 67 | 67 | 575,98 | 210.232 |
| **Meia Praia** | **Studio/1q** | **41** | 65 | **415,15** | **151.531** |
| Meia Praia | 2q | 190 | 56 | 487,47 | 177.925 |

### 2.2 Custo de compra (mediana VivaReal)
| Bairro | Perfil | Preço compra (R$) | Nº ofertas |
|---|---|---|---|
| Centro | Studio/1q | 890.000 | 21 |
| Centro | 2q | 1.170.000 | 88 |
| Meia Praia | Studio/1q | 877.500 | 56 |
| Meia Praia | 2q | 1.075.000 | 244 |

### 2.3 ROI comparativo
| Combinação | Receita anual realista (60%) | Preço compra | **ROI (60%)** | Payback (anos) | ROI pleno (100%) |
|---|---|---|---|---|---|
| **Studio/1q — Centro** | R$ 98.539 | R$ 890.000 | **11,1%** | 9,0 | 18,5% |
| 2q — Centro | R$ 126.139 | R$ 1.170.000 | 10,8% | 9,3 | 18,0% |
| Studio/1q — Meia Praia | R$ 90.918 | R$ 877.500 | 10,4% | 9,7 | 17,3% |
| 2q — Meia Praia | R$ 106.755 | R$ 1.075.000 | 9,9% | 10,1 | 16,6% |
| 3q+ — Centro (ref.) | R$ 173.781 | R$ 2.798.800 | 6,2% | 16,1 | 10,4% |
| 3q+ — Meia Praia (ref.) | R$ 159.761 | R$ 2.499.270 | 6,4% | 15,6 | 10,7% |

---

## 3. Conclusão — a tese se sustenta?

**Sustenta, com ressalvas.** Pontos a favor e contra:

### A favor (a tese está na direção certa)
1. **Compactos no Centro têm o melhor ROI das 4 combinações testadas** (11,1% realista / 18,5% pleno), com payback menor (~9 anos).
2. **O ADR dos compactos no Centro é o mais alto entre compactos** (R$ 449,95 vs R$ 415,15 na Meia Praia): o Centro cobra mais pela localização.
3. **A tipologia "compacta" domina todas as dualidades do mesmo bairro:** no Centro studio/1q (18,5%) > 2q (18,0%) > 3q+ (10,4%). Ou seja, **quanto menor o imóvel, mais eficiente o capital** — o motor real da tese é a eficiência de capital (receita vs. preço de compra), e não o bairro.
4. **A amostra do Centro é a maior entre compactos** (82 anúncios com preço), dando mais robustez estatística ao resultado.

### Contra (ressalvas à tese)
1. **A vantagem sobre o 2q no Centro é pequena:** 18,45% vs 17,97% (menos de 0,5 p.p. de ROI pleno). Em termos absolutos o 2q no Centro gera **R$ 27,6 mil/ano a mais de receita realista** (R$ 126k vs R$ 99k) — exige mais capital (R$ 280k a mais), mas com retorno absoluto maior e praticamente o mesmo ROI.
2. **Liquidez de oferta é o ponto fraco:** só **21 imóveis studio/1q à venda no Centro** (vs 88 de 2q). Na prática, executar "compra de compacto no Centro" em escala é difícil. A Meia Praia tem mais oferta de compactos (56) — porém com ROI ligeiramente menor.
3. **Sazonalidade e janela curta:** os preços cobrem apenas jan-fev-mar-abr (alta temporada). Os meses de inverno tendem a derrubar a média anual; o cenário realista (60%) já pondera parcialmente isso, mas é uma estimativa.
4. **Ocupação não observada:** os dados mostram preço (disponibilidade), não reservas. Assumimos 60% ocupação no cenário base; se compactos rodarem com ocupação maior (menor preço de diária, perfil de negócios/trabalho), o resultado só melhora — o que reforça a tese, não a enfraquece.

**Veredito:** a tese **não é redonda**, mas é a **mais defensável**. "Compacto no Centro" é a escolha que maximiza ROI % com menor capital inicial. O desafio prático é a oferta escassa (21 unidades). Uma leitura mais precisa: **a Seazone deveria priorizar eficiência de capital — imóveis compactos — e, dentro disso, dar preferência ao Centro** quando houver estoque; em escala, o 2q na Meia Praia oferece quase o mesmo ROI com muito mais produto disponível.

---

## 4. Recomendação

**Prioridade 1 — Compactos (studio/1q) no Centro:** melhor ROI, menor desembolso (≈R$ 890k), ADR mais alto. Comprar quando disponível, dado estoque limitado.

**Prioridade 2 — 2q no Centro / compacto na Meia Praia:** ROI quase idêntico (10,8% / 10,4%), com liquidez muito maior. Melhor alternativa para escalar sem perda relevante de eficiência.

**Evitar — 3q+ (2,5–2,8M):** ROI de apenas 6,2–6,4% (payback ~15–16 anos). O preço de compra alto penaliza a receita proporcional.

### Critério de decisão proposto (síntese)
> Maximizar **ROI anual por real investido** → priorizar tipologias compactas. O bairro Centro agrega por causa do **ADR premium**, mas a escassez de estoque (21 ofertas) sugere política com "fallback": captar compactos no Centro quando surgirem; caso contrário, não recusar 2q em Centro/Meia Praia com ROI ≥ 10%.

### Limitações e próximos passos
- Cruzar com ocupação real (não disponível) para refinar o cenário B.
- Incluir `cleaning_fee` e custos (limpeza, condomínio, IPTU, gestão) para chegar a **ROI líquido**.
- Estender a janela de preços (3,5 meses) para capturar o ano inteiro e o inverno.
- Modelar valorização do imóvel como componente do retorno total.

---

### Anexo — Tabela-resumo pedida
| Critério | Compactos no Centro | Alternativa (2q no Centro) |
|---|---|---|
| Receita mensal estimada (60% occ.) | R$ 8.212/mês | R$ 10.512/mês |
| Preço de compra estimado | R$ 890.000 | R$ 1.170.000 |
| ROI estimado | **11,1%** | 10,8% |
| Payback estimado | 9,0 anos | 9,3 anos |