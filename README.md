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

A API inicial expõe apenas a verificação de saúde. Adaptadores PubMed e Firecrawl existem como funções internas, ainda sem endpoints públicos. O backend inicializa PostgreSQL/pgvector, registra as fontes e reutiliza respostas por 24 horas. O teto local do Firecrawl é de 800 reservas por mês UTC. Configure `FIRECRAWL_MONTHLY_LIMIT=0` para bloquear novas extrações.

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
docker compose up -d --no-build
```

## Codex

Leia AGENTS.md. Configure Firecrawl MCP separadamente conforme a documentação oficial. Não inclua chaves no Git.

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Auditoria da fase inicial](docs/AUDITORIA.md)
- [Roadmap](docs/ROADMAP.md)
- [Segurança](docs/SECURITY.md)

Licenciamento definitivo a confirmar antes de distribuição como software livre.
