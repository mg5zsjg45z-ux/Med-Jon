# Auditoria da fase inicial

Na revisão 3976374, o FastAPI expunha apenas /health. Os dois testes existentes passaram e cobriam a rejeição de URLs antes do HTTP. O Compose restringia a API ao loopback e mantinha o banco em volume próprio, mas faltavam configuração da conexão, espera pela disponibilidade do PostgreSQL e inicialização do esquema.

## Contratos verificados

- Firecrawl v2. O adaptador envia POST /v2/scrape com autenticação Bearer e solicita markdown. O mock cobre o envelope success/data, markdown e falha HTTP. O perfil de custo usa proxy básico e desativa parsers, inclusive a cobrança por página de PDF. A validação usou a especificação pública e respostas simuladas. [Referência Firecrawl](https://docs.firecrawl.dev/api-reference/endpoint/scrape)
- PubMed. Uma consulta pública por “chromatin” confirmou esearchresult.idlist. ESummary confirmou result, uids e os campos title, pubdate e articleids. Os testes reproduzem esse formato com registros sintéticos e verificam a passagem dos IDs entre as duas operações. [Referência NCBI](https://www.ncbi.nlm.nih.gov/books/NBK25499/)

O endpoint público continua restrito à saúde do serviço. A coluna vector foi exercitada com distância euclidiana entre vetores sintéticos. A geração de embeddings e a validação clínica continuam pendentes.

## Resultado da verificação

Oito testes passaram no Compose, incluindo concorrência entre reservas, bloqueio pelo orçamento, expiração de cache, persistência de fonte e operação pgvector em PostgreSQL 16. O banco ficou saudável e GET /health retornou HTTP 200. Nenhum teste usou dados de pacientes ou chamou serviços bibliográficos ou tarifados. A inspeção TLS do ambiente exigiu fornecer a autoridade certificadora ao build. O teste da imagem também revelou permissões de leitura insuficientes no código copiado, corrigidas no Dockerfile.
