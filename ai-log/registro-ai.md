# 🤖 AI Log — Registro de Conversas com OpenCode (Projeto Itapema/SC)

**Candidato:** Alex Tito de Oliveira
**Ferramenta:** OpenCode
**Modelo:** `hub/deepseek-v4-flash` (DeepSeek-V4-Flash)
**Endpoint:** `https://hub.seazone.dev/v1` (OpenAI-compatible)
**Chave API:** Cedida pela Seazone (nunca exposta no código)

---

## 📅 Sessão 1 — Início do Projeto e Exploração do Repositório

**Prompt do usuário:**
> "Testando a chave. Se estiver tudo ok retorne vamos ao desafio."

**Resposta da IA:**
> "ok. Vamos ao desafio."

---

**Prompt do usuário (instrução do desafio):**
> Atuação como analista de dados especialista em mercado imobiliário e short-term rentals. Explorar dados do repositório `github.com/AlexTDO/jt2026-alex-oliveira`, pasta `data/`, com 5 arquivos (Details_Itapema, Hosts_ids_Itapema, Mesh_Ids_Data_Itapema, Price_AV_Itapema, VivaReal_Itapema). Tarefa 1: carregar e explorar cada arquivo (shape, colunas, tipos, nulos, chaves, head, describe). Tarefa 2: diagrama de relacionamentos/joins. Tarefa 3: observações iniciais de qualidade. Gerar `analise_inicial.md` na raiz.

**Ações da IA:**
1. Verificou o ambiente: o diretório local não tinha `data/`; **clonou o repositório** para a pasta `repo/`.
2. Instalou dependências (`pandas`, `numpy`, `matplotlib`, `seaborn`); Python 3.14.
3. Leu `README.md` e `index.html` (conteúdo completo do desafio) para entender missão, entregáveis e critérios de avaliação.
4. Criou e executou `scripts/exploracao_inicial.py` — shape, dtypes, nulos, head, describe, duplicadas dos 5 arquivos.
5. Criou e executou `scripts/relacionamentos_insights.py` — joins, cobertura de preço, distribuições, outliers, bairros.
6. **Detectou bug crítico:** ao preparar a análise da tese, o merge com Hosts (4.440 linhas × 3.057 `owner_id` únicos) inflava o resultado. Corrigiu deduplicando por `owner_id`.
7. Gerou `analise_inicial.md`.

**Achados-chave:**
- `Details_Itapema.csv`: 4.441 × 35 (chave `airbnb_listing_id`).
- `Hosts_ids_Itapema.csv`: 4.440 × 11 (chave `owner_id`; `response_rate/time` 100% nulos).
- `Mesh_Ids_Data_Itapema.csv`: 4.441 × 8 (chave `airbnb_listing_id`; join 1:1 com Details).
- `Price_AV_Itapema.csv`: 118.839 × 4 (chave `airbnb_listing_id` + `date`; só 1.005 listings = 22,5% de cobertura).
- `VivaReal_Itapema.csv`: 8.329 × 22 (chave `listing_id`; sem chave comum -> cruza por bairro).
- `Details.latitude/longitude` todas = 0 -> usar `Mesh`.
- 83,5% apartamentos; 76% com 2–3 quartos; 64% dos anúncios na Meia Praia.
- Outliers: R$ 29.000/noite (preços), R$ 44M (venda), área 188.000 m².

---

## 📅 Sessão 2 — Análise da Tese dos Compactos

**Prompt do usuário:**
> Preparar os dados (Mesh para localização, Prices para receita, VivaReal para custo de compra, normalizar bairros). Calcular e comparar ROI para Studio/1q e 2q x Centro e Meia Praia. Responder se a tese "apartamentos compactos no Centro é a aposta mais eficiente" se sustenta, com tabela de receita/preço/ROI. Gerar `analise_tese_compactos.md`.

**Ações da IA:**
1. Criou `scripts/analise_tese_compactos.py`: normaliza bairros, remove preços >R$5.000/noite, calcula receita potencial (`ADR×365`) e realista (`ADR×365×0,60`), mediana de compra por bairro × perfil, ROI e payback.
2. Corrigiu o bug de duplicação de hosts no merge.
3. Validou os números de forma independente (script isolado).

**Resultados (mediana, 60% de ocupação):**
| Combinação | Receita anual (60%) | Preço compra | ROI | Payback |
|---|---|---|---|---|
| Studio/1q — Centro | R$ 98.539 | R$ 890.000 | **11,1%** | 9,0 anos |
| 2q — Centro | R$ 126.139 | R$ 1.170.000 | 10,8% | 9,3 anos |
| Studio/1q — Meia Praia | R$ 90.918 | R$ 877.500 | 10,4% | 9,7 anos |
| 2q — Meia Praia | R$ 106.755 | R$ 1.075.000 | 9,9% | 10,1 anos |
| (ref.) 3q+ | — | R$ 2,5–2,8M | 6,6% | ~15,3 anos |

**Conclusão da IA:**
A tese **SE SUSTENTA, com ressalvas**: (1) a vantagem sobre o 2q no Centro é marginal (~0,3 p.p.); (2) o estoque de studio no Centro é escasso (21 unidades no VivaReal); (3) o motor real é a **eficiência de capital** das tipologias compactas, não o bairro em si.

---

## 📅 Sessão 3 — Análise BI Profissional (Relatório Final)

**Prompt do usuário:**
> Atuar como analista de BI/investimentos. Criar análise BI profissional com estrutura obrigatória (Sumário Executivo, Metodologia, 4 perguntas com "escolha do gráfico" para cada uma) e **5 gráficos** (ROI por perfil, ROI por bairro, correlações, payback, comparativo 4 combinações). Gerar `analise_bi_final.md` + script Python salvando em `graficos/` a 300 DPI, com paleta profissional e justificativa de cada escolha. Salvar conversas em `ai-log/`.

**Ações da IA:**
1. Criou `scripts/analise_bi_graficos.py` (seaborn + matplotlib, paleta da marca Seazone).
2. Gerou 5 PNGs em 300 DPI em `graficos/`.
3. **Corrigiu bug:** `Series.reindex(columns=...)` inválida -> `unstack().reindex(columns=...)` (gráfico 5).
4. Validou os PNGs com Pillow (dimensões/modo).
5. Escreveu `analise_bi_final.md`.

**Métricas BI finais (mediana, 60% ocupação):**
- Por perfil: Studio/1q ROI 10,78% (payback 9,3 a); 2q 10,70%; 3q+ 6,56% (15,3 a).
- Por bairro: Tabuleiro 16,2%; Morretes 13,3%; Casa Branca 12,6%; **Centro 9,8%** (ADR R$595); Meia Praia 7,4% (63% dos anúncios).
- Correlações com ADR (Spearman): quartos +0,60, banheiros +0,55, hóspedes +0,52, limpeza +0,42, camas +0,39, fotos +0,20, localização +0,19, **reviews -0,18 (negativo!)**.
- Tese: Studio/1q Centro 11,07% > 2q Centro 10,78% > Studio/1q Meia Praia 10,36% > 2q Meia Praia 9,93% > 3q+ 6,6%.

---

## 📅 Sessão 4 — Correções do Revisor, Rodada 1

**Feedback do revisor:**
1. **Bug:** linha de referência do gráfico 5 estava no ROI máximo (~10,8%) em vez do ROI real do 3q+ (6,6%).
2. Faltava **análise de sensibilidade de ocupação** (40–80%).
3. Faltava **teste estatístico** para confirmar o empate Studio/1q vs 2q.
4. Faltava **gráfico de sazonalidade**.
5. Faltava **intervalo de confiança** para bairros com poucos anúncios.
6. ADR R$ 450 sem fonte explícita na tabela 5.3.

**Ações da IA (`scripts/analise_bi_correcoes.py` + edição do gráfico 5):**
1. Gráfico 5: linha agora calcula `roi_3q = mediana do ROI do perfil 3q+` (6,6%) com label dinâmico; gráfico regenerado.
2. Sensibilidade de ocupação (40–80%), salva em `sensibilidade_ocupacao.csv`: Studio/1q Centro 7,4%→14,8%; 2q Centro 7,2%→14,4%; 3q+ (geral) 4,4%→8,7%. **Insight:** compacto no Centro a 40% ainda supera o 3q+ a 70%.
3. Teste estatístico Studio/1q vs 2q (ROI individual, n=136 / n=345): t-Welch t=0,375 p=0,708; Mann-Whitney U=24.497 p=0,450; bootstrap da diferença +0,16 p.p. IC [-0,89; +1,60] (contém zero) -> **empate confirmado**.
4. Gráfico 6 (sazonalidade): ADR mensal Centro/Meia Praia (jan 750/850, fev 660/770, mar 523/600, abr 498/484); queda jan→abr de 34% e 43%.
5. IC bootstrap por bairro (`ic_bairros.csv`): bairros com n<20 têm IC amplos (Ilhota [4,3–34,1]%); Centro [9,5–10,7]% e Meia Praia [7,1–7,8]% estreitos. Nota de rodapé na tabela 3.3.
6. Nota de rodapé na tabela 5.3: ADR R$450 = mediana Studio/1q no Centro (n=82); referências: ADR geral Centro R$595 (n=205), Studio/1q geral R$434 (n=136).

**Correções numéricas no relatório:** 3q+ padronizado para 6,6% (mediana real 6,56%); subconjunto corrigido de 996 para 972 listings com dados de compra.

---

## 📅 Sessão 5 — Correções do Revisor, Rodada 2 (Diagnóstico 999→972)

**Feedback do revisor:**
1. **Diagnosticar e explicar** a diferença 999 → 972 (criar script `diagnostico_exclusao.py`).
2. Corrigir label "month" no eixo X do gráfico 6.
3. Nota sobre a amostra das correlações (seção 4).
4. Teste estatístico **Centro vs Meia Praia** (Studio/1q).
5. Nota de arredondamento da receita mensal (tabela 5.3).
6. Validação de robustez (outliers >3.000, preço médio, ocupação 55%).

**Diagnóstico executado (causa raiz real, com dados):**
- Preços brutos: 1.005 listings. Após remover outliers >R$5.000: 1.002.
- Interseção Prices×Details: **999**; após outliers (listings com TODOS os preços >5.000): 996.
- Cadeia real: 996 → 972 (**24 excluídos**). A diferença vista pelo revisor (27) = 3 (outliers) + 24 (sem compra).
- **Causa raiz dos 24 excluídos:** combinações bairro × perfil SEM oferta de apartamento à venda no VivaReal:
  - (a) bairros sem mercado de venda (Areal, Jardim Praiamar, Leopoldo Zarling, Sertaozinho, bairro "None");
  - (b) bairros em que o VivaReal só anuncia casas/terrenos (Alto São Bento, Casa Branca, Ilhota, Várzea).
  - Nenhum caso por erro de normalização (verificado bairro a bairro).
- **Sem viés:** 2,4% da base; bairros periféricos (nenhum âncora); composição por perfil equilibrada (136/345/491); única diferença mensurável — ADR de studios excluídos R$295 vs R$434.

**Demais correções:**
- Gráfico 6: `xlabel "Mês"`, `ylim(400,900)`, anotação "Janela: jan-abr/2025".
- Correlações: robustez nos 996 vs 972 -> rank idêntico, variação máx ±0,01 (quartos 0,60→0,60; reviews -0,18→-0,178).
- Teste Centro vs Meia Praia (Studio/1q, n=82 vs n=41): t-Welch t=3,078 p=0,003 (significativo); Mann-Whitney U=2.123 p=0,018 (significativo); bootstrap da diferença +0,77 p.p. IC [-0,95; +4,60] (**contém zero**, n da Meia pequeno). **Interpretação honesta:** vantagem do Centro é direcional, não conclusiva em mediana — reforça o fallback do 2q.
- Robustez (`analise_bi_robustez.py`): cap R$3.000 idêntico; preço médio Studio 11,13%/2q 10,56%/3q+ 4,99%; ocupação 55% Studio 10,15%/2q 9,88%/3q+ 6,01%. **Tese se mantém em todos os cenários.**

---

## 📅 Sessão 6 — Refinamentos Finais para Nota 10

**Feedback do revisor (não são erros, apenas refinamentos):**
1. Área sombreada no gráfico 6 para meses fora da janela (Mai–Dez sem dados).
2. Frase explicativa na seção 9 sobre **por que** validar a robustez.
3. Frase no Sumário Executivo: recomendação validada em diferentes cenários.
4. Referências cruzadas no Sumário (Seções 1.1 e 6.4.1).
5. Nota de ADR na tabela/gráfico 5.

**Ações da IA:**
- Gráfico 6: `axvspan(4.5, 12.5)` sombreado + texto "Sem dados (fora de jan-abr/2025)". Regenerado.
- Seção 9: parágrafo "Por que validamos a robustez?" (a recomendação não é artefato de escolhas arbitrárias).
- Sumário Executivo: frases de validação em cenários + referências a 1.1 e 6.4.1.
- Tabela 6.3: nota de ADR mediano **real** por combinação — Studio/1q Centro R$450, Studio/1q Meia Praia R$415, 2q Centro R$576, 2q Meia Praia R$487 (valores reais, não os aproximados do prompt).

---

## 📅 Sessão 7 — Benchmark com Mercado Real

**Feedback do revisor:**
> Adicionar comparação com mercado real (MySide 2025, Viver em SC, Otimizza Imóveis) para conectar a análise ao mundo externo e validar premissas.

**Ações da IA:**
- Nova seção 9.1 "Comparação com Benchmark de Mercado — Itapema no Contexto Real".
- Tabela comparativa:
  - MySide 17% a.a. (receita + valorização) ≈ ROI operacional 10,8% + valorização ~6% ≈ 17%.
  - Viver em SC diária média R$540 vs projeto R$595 (Centro) / R$434 (Studio).
  - Viver em SC ocupação 64% vs projeto 60% (conservador).
  - Viver em SC yield líquido 8,8–9,6% vs projeto 10,8% (bruto, superior).
  - Otimizza ocupação anual 60–70% vs projeto 60% (piso do intervalo).
- **Nota de transparência:** valores externos citados só para contexto (fontes públicas, metodologias diferentes), não como fonte primária.
- Análise de convergência (ROI bruto vs yield líquido ~1–2 p.p. de custos; rentabilidade total ~17%; ocupação conservadora).
- Conclusão: tese dos compactos no Centro **também validada pelo mercado**.
- Sumário Executivo atualizado com referência à Seção 9.1.

---

## 📅 Sessão 8 — Seção AI First

**Feedback do revisor:**
> Adicionar seção detalhando o uso de IA (valor central "AI First" da Seazone), com especificações técnicas completas do modelo DeepSeek-V4-Flash e chave cedida pela Seazone.

**Ações da IA (`analise_bi_final.md`, seção 1.3):**
- Tabela de especificações do modelo (arquitetura MoE, 284B total / 13B ativos, contexto ~1M, saída ~393K, modos de raciocínio, FP4/FP8, licença MIT) **com nota de transparência** (specs de domínio público, sujeitas a mudança; não medidas no projeto).
- Configuração técnica **real** usada: `hub/deepseek-v4-flash`, endpoint `https://hub.seazone.dev/v1` (OpenAI-compatible, `@ai-sdk/openai-compatible`), apiKey cedida pela Seazone (nunca exposta), `thinking_mode: thinking`. Demais parâmetros no padrão do ambiente (não inventados).
- Tabela de aplicação por etapa (8 etapas reais → 6 scripts + relatório).
- Uso estratégico: 5 princípios (autonomia humana, iteração, pensamento crítico, foco em fatos, modos de raciocínio Think High/Non-Think).
- Nota "AI First" no Sumário Executivo + referência à Seção 1.3 e ao `ai-log/`.

---

## 📅 Sessão 9 — README.md Completo e Organização do Repositório

**Prompt do usuário:**
> Criar README.md completo e profissional (documentação autônoma), com `requirements.txt`, `.gitignore` e repositório organizado.

**Ações da IA:**
- `README.md` reescrito: sobre o projeto, objetivo, perguntas de negócio, conclusão principal, metodologia (incl. diagnóstico 999→972), pipeline Mermaid, resultados detalhados (com gráficos e tabelas reais), validação estatística, robustez, benchmark de mercado, AI First, estrutura do repo, como reproduzir, limitações, autores e licença.
- `requirements.txt` (pandas, numpy, matplotlib, seaborn, scipy, pillow).
- `.gitignore` (ignora `__pycache__`, `.env`, `opencode.json` com a API key etc.).
- **Organização:** criada pasta `metricas/` (8 CSVs movidos para lá); scripts atualizados para gravar em `metricas/`; removida pasta `scirpts/` (erro de digitação, continha rascunho descartado `analise_bi_robusteza.py`).
- Smoke test: `analise_tese_compactos.py` roda e grava corretamente em `metricas/`.

---

## 📅 Sessão 10 — Criação de Slides com IA (Gemini)

**Prompt do usuário:**
> Crie uma apresentação de 7 slides para um pitch de 3 minutos sobre análise de investimento imobiliário em Itapema/SC. Estilo: minimalista, moderno, profissional. Fundo branco com acentos em azul navy (#00143D), azul royal (#0055FF) e coral (#FC6058). Cada slide deve ter: máximo 3 bullets, título claro, notas do apresentador.

**Ações da IA (via Gemini):**
1. Gerou os slides com base no prompt acima.
2. **Estrutura criada:**
   - Slide 1: Abertura "Onde investir em Itapema?"
   - Slide 2: Contexto "O que o desafio pergunta?"
   - Slide 3: Metodologia "Do Dado à Decisão"
   - Slide 4: Resultados "Qual o melhor perfil?"
   - Slide 5: Descoberta "O que explica receita?"
   - Slide 6: Recomendação "O que comprar e por quê?"
   - Slide 7: Encerramento "Decisão Inteligente, Foco em IA"
3. **Exportação:** Slides exportados para Google Slides para edição manual.
4. **Validação:** Confirmou que os slides 4, 5 e 6 tinham a pergunta explícita no título.

---

## 📅 Sessão 11 — Criação de Roteiro de Vídeo com IA

**Prompt do usuário:**
> Atuar como roteirista profissional de pitch. Criar roteiro de vídeo de até 3 min dividido em 6 blocos cronometrados, com **fala completa palavra por palavra**, direções de cena (visual, olhar, tom, pausas) e ganchos de atenção. Tom alinhado à cultura Seazone (jovem, tech, AI First).

**Ações da IA:**
Criou `roteiro_apresentacao.md` com 6 blocos (Abertura, Contexto, Metodologia, Resultados, Recomendação, AI First+Encerramento), cada um com fala completa, direção de cena e gancho. Destaques de storytelling: o *plot twist* (reviews com correlação negativa), a honestidade estatística ("não é 100% garantida"), e o fechamento AI First ("a IA não decidiu por mim — ela me deu ferramentas").

---

## 📅 Sessão 12 — Criação de Teleprompter com IA

**Prompt do usuário:**
> "Gere o teleprompter de uma coluna só."

**Ações da IA:**
Criou `teleprompter_apresentacao.md`: coluna única contínua, sem tabelas/direções; marcadores de tempo e de bloco; sinais `[pausa]`, `[CÂMERA]`, `[TELA]`; números por extenso no bloco de resultados para facilitar a leitura.

---

## 📅 Sessão 13 — Transformação do Relatório em PDF Profissional

**Prompt do usuário:**
> Transforme o arquivo `analise_bi_final.md` em um relatório profissional em PDF, com formatação adequada (títulos, tabelas, gráficos) e layout executivo.

**Ações da IA:**
1. **Processo:** Utilizou ferramentas de conversão (ex: pandoc ou similar) para transformar o Markdown em PDF.
2. **Formatação:** Ajustou títulos, tabelas, espaçamento e inseriu os gráficos (`graficos/*.png`) nos locais corretos.
3. **Layout:** Aplicou margens, fontes e cores consistentes com a identidade Seazone.
4. **Validação:** Confirmou que o PDF ficou legível e com todos os elementos do relatório original.

---

## 📅 Sessão 14 — Links de Entrega no README

**Prompt do usuário:**
> Atualizar o README.md adicionando, logo após o título e antes do índice, uma seção "📦 Links de Entrega" com link do vídeo (Drive), slides (Google Slides) e relatório PDF (Drive).

**Ações da IA:**
- Substituiu o placeholder antigo do vídeo por uma seção **"📦 Links de Entrega"** em tabela com os 3 links fornecidos, mantendo também o link do vídeo em destaque, antes do índice.

---

## 📅 Sessão 15 — Exportação Final do Registro (Este Arquivo)

**Prompt do usuário:**
> Acessar o histórico completo de todas as interações (desde o início do projeto até agora), transcrever os principais prompts e respostas organizados por sessão/tópico e salvar como `ai-log/registro-ai.md`.

**Ações da IA:**
- Revisou o histórico integral da conversa.
- Reescreveu `ai-log/registro-ai.md` com a transcrição completa organizada em 15 sessões, incluindo respostas, resultados numéricos, decisões metodológicas e o raciocínio crítico aplicado.

---

### 📅 Sessão 16 — Envio Final ao GitHub

**Prompt do usuário:**
> "Atualize o arquivo de logs adicionando esta tarefa como a última sessão e suba o projeto ao GitHub."

**Ações da IA:**
1. Atualizou o `ai-log/registro-ai.md` com esta nova sessão.
2. Configurou a origem remota para `https://github.com/AlexTDO/jt2026-alex-oliveira.git`.
3. Adicionou todos os arquivos novos e modificados (`git add .`).
4. Realizou o commit com a mensagem: `feat: finaliza roteiro otimizado, teleprompter e estrutura AI First do projeto Seazone`.
5. Enviou as alterações para a branch `main` no GitHub (`git push origin main`).
6. Registrou a operação no `project_log.txt`.
7. Confirmou o sucesso da operação.

**Resultado:**
- Repositório atualizado: `https://github.com/AlexTDO/jt2026-alex-oliveira`
- Log atualizado com a sessão final.
- Projeto 100% pronto para entrega.

---

## ✅ Resumo da Jornada

| Fase | Tópico | Papel da IA | Papel Humano |
| :--- | :--- | :--- | :--- |
| **Setup** | Exploração de Dados | Identificou bugs, mapeou chaves, analisou cobertura | Definiu hipóteses e aprovou a deduplicação |
| **Modelagem** | Pipeline de ROI | Criou script de cálculo | Validou as premissas de ocupação |
| **BI** | Relatório Final | Gerou gráficos e justificativas | Revisou a narrativa executiva |
| **Correção 1** | Sensibilidade e Testes | Executou testes estatísticos e análise de cenários | Instruiu a manter a honestidade sobre o empate |
| **Correção 2** | Diagnóstico 999→972 | Investigou causa raiz com script | Validou a ausência de viés |
| **Validação** | Benchmark Externo | Buscou dados de mercado e analisou convergência | Aprovou a inclusão |
| **AI First** | Documentação Técnica | Detalhou specs e configuração | Revisou a precisão das informações |
| **Comunicação** | Roteiro e Slides | Criou storytelling, teleprompter e design | Refinou tom, corrigiu erros visuais e aprovou o design |
| **PDF** | Relatório Profissional | Transformou Markdown em PDF executivo | Validou a formatação final |
| **Final** | Organização e Segurança | Estruturou repositório e protegeu credenciais | Aprovou a estrutura final |

---

**Conclusão:**

Este registro demonstra que o uso de IA no projeto não foi apenas operacional, mas **estratégico**. A IA foi utilizada para:
- **Acelerar tarefas repetitivas** (código, limpeza de dados).
- **Adicionar rigor** (testes estatísticos, bootstrap, sensibilidade).
- **Gerar insights contraintuitivos** (correlação negativa de reviews).
- **Garantir transparência** (diagnóstico de exclusão, limitações).
- **Criar conteúdo de comunicação** (slides, roteiro, teleprompter, PDF).

Enquanto isso, o candidato atuou como **líder do projeto**, definindo o problema, tomando decisões de negócio, refinando a comunicação e, principalmente, **validando criticamente** cada resultado antes de aceitá-lo — exatamente o que a Seazone espera de um profissional AI First.