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

A API inicial expõe apenas a verificação de saúde. Adaptadores PubMed e Firecrawl existem como funções internas, ainda sem endpoints públicos. PostgreSQL/pgvector está provisionado, mas não integrado. Interface, RAG, cache e controle de créditos são pendentes.

## Testes locais

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests
```

## Codex

Leia AGENTS.md. Configure Firecrawl MCP separadamente conforme a documentação oficial. Não inclua chaves no Git.

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Segurança](docs/SECURITY.md)

Licenciamento definitivo a confirmar antes de distribuição como software livre.

## Fase 3 (experimental)
Veja [recuperação semântica](docs/PHASE3.md). Os endpoints autenticados de pesquisa substituem a descrição anterior de API somente health nesta branch. Ainda não há geração clínica.

## Fase 4 — Interface
Após configurar .env e iniciar Docker Compose, abra http://localhost:3000. Consulte [PHASE4](docs/PHASE4.md). Uso local experimental; não exponha à rede.
