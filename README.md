# Base de dados — Hackathon Jovens Talentos AI Builder (Seazone)

Snapshot estático do mercado imobiliário de **Itapema (SC)**, com dados de anúncios de Airbnb e de venda (VivaReal). É a mesma base para todos os candidatos, para garantir comparação justa.

## Arquivos (`data/`)

| Arquivo | O que tem | Como conecta |
|---|---|---|
| `Details_Itapema.csv` | Cada anúncio de Airbnb: título, reviews, star rating, descrição, host_id, nº de quartos, tipo de imóvel | Base principal dos listings |
| `Hosts_ids_Itapema.csv` | Dados do anfitrião: nº de reviews, anos como host, superhost, taxa de resposta | Liga com Details pelo `owner_id` |
| `Mesh_Ids_Data_Itapema.csv` | Latitude/longitude + bairro de cada anúncio | Liga por listing |
| `Price_AV_Itapema.csv` | Preço por anúncio, por data de estadia e por data de captura | Liga por listing |
| `VivaReal_Itapema.csv` | Anúncios de venda: preço, condomínio, área, vendedor | Mercado de compra |

## Como usar
Faça um **fork** deste repositório para começar. As instruções completas do desafio estão no documento enviado no processo seletivo.
