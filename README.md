# Med-Jon

Protótipo open source de pesquisa médica baseada em evidências. Não validado para uso clínico. Não inserir dados de pacientes.

## Início local

Requisitos: Docker e Docker Compose.

```bash
cp .env.example .env
# Edite .env localmente: configure senha do banco e, opcionalmente, chaves de API.
docker compose up --build
curl http://localhost:8000/health
```

Abra http://localhost:3000 para pesquisar temas bibliográficos no PubMed. A interface exibe até cinco publicações por consulta, com link para o registro original, PMID, DOI quando disponível e data de recuperação. O navegador envia o tema ao servidor Next.js, que chama a rota local `POST /api/pubmed/search`. Firecrawl continua disponível apenas como adaptador interno. O backend inicializa PostgreSQL/pgvector, registra as fontes e reutiliza respostas por 24 horas. O teto local do Firecrawl é de 800 reservas por mês UTC. Configure `FIRECRAWL_MONTHLY_LIMIT=0` para bloquear novas extrações.

## Testes locais

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests
```

Para executar também o teste de integração, use um banco descartável chamado
`medjon_test`. O teste limpa as tabelas desse banco. Com o Compose em execução:

```bash
docker compose exec db createdb -U medjon medjon_test
docker compose run --rm --no-deps -e PGDATABASE=medjon_test -v "$PWD/backend/tests:/tests:ro" api python -m unittest discover -s /tests -v
```

Em ambientes com inspeção TLS, o build aceita um certificado de autoridade
local como segredo temporário do BuildKit:

```bash
docker build --secret id=pip_ca,src=/caminho/ca.pem -t med-jon-api backend
docker build --secret id=npm_ca,src=/caminho/ca.pem -t med-jon-web frontend
docker compose up -d --no-build
```

## Teste de navegador

Com Node.js 24 e as dependências Python do backend instaladas:

```bash
cd frontend
npm ci
npm run build
python -m pip install playwright
python -m playwright install chromium
python tests/browser.py
```

O teste inicia a interface e uma API local com transporte HTTP e armazenamento simulados. Valida publicação, repetição com cache, retorno vazio e indisponibilidade do PubMed. Para usar um Chromium já instalado, defina `CHROMIUM_PATH`.

## Codex

Leia AGENTS.md. Configure Firecrawl MCP separadamente conforme a documentação oficial. Não inclua chaves no Git.

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Auditoria da fase inicial](docs/AUDITORIA.md)
- [Roadmap](docs/ROADMAP.md)
- [Segurança](docs/SECURITY.md)

Licenciamento definitivo a confirmar antes de distribuição como software livre.
