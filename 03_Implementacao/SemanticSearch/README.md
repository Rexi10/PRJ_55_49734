# Projeto API de Pesquisa SemÃ¢ntica

## Pré-requisitos

- Docker instalado ([link oficial](https://docs.docker.com/get-docker/))
- Docker Compose (normalmente já incluído com o Docker)

## Como correr o sistema

Abrir o docker, na raiz do projeto, execute o seguinte comando para iniciar os serviços em background:

```bash
docker-compose up -d
```

aceder à pagina via: http://localhost:5000/


## Como inserir documentos

Para adicionar novos documentos ao sistema:

1. Crie uma pasta local para os documentos, por exemplo: `./Bucket/buckets/bucket_novo`
2. Coloque os ficheiros de texto, PDF, DOCX, MD, etc., nessa pasta
3. Adicione o serviço no ficheiro `docker-compose.yml` que monte essa pasta para o container. Exemplo:

```yaml
services:
      bucket_novo:
    build:
      context: ./bucket
      dockerfile: Dockerfile
    ports:
      - "5001:5000"
    volumes:
      - ./bucket:/app
      - ./bucket/buckets:/app/buckets
    environment:
      - FLASK_ENV=development
      - BUCKET_NAME=bucket_novo
      - BUCKET_URL=http://bucket_novo:5000
      - BUCKET_FOLDER=/app/buckets/bucket_novo
      - OLLAMA_HOST=http://host.docker.internal:11434
    networks:
      - app-network
```

4. Inicie o composer para aplicar as alterações:

```bash
docker-compose up -d
```

## Como fazer uma consulta

A API REST está disponi­vel na porta configurada (exemplo: `http://localhost:5000`).


## OrganizaÃ§Ã£o do repositÃ³rio

- `docker-compose.yml`: configurações dos buckets
- `bucket/`: estrutura dos buckets e inclui a pasta onde se encontram os documentos
- `interface/`: estrutura das interfaces
- `teste_de_modelos/`: scripts auxiliares e testes

---
