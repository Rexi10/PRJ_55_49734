# Projeto API de Pesquisa Semântica

## Pré-requisitos

- Docker instalado ([link oficial](https://docs.docker.com/get-docker/))
- Docker Compose (normalmente incluído com o Docker)

## Como executar o sistema

Com o Docker aberto, na raiz do projeto, execute o comando para iniciar os serviços em background:

```bash
docker-compose up -d
```

Acesse a página em: http://localhost:5000/

## Como inserir documentos

Para adicionar novos documentos ao sistema:

1. Crie uma pasta local para os documentos, por exemplo: `./Bucket/buckets/bucket_novo`
2. Coloque os arquivos de texto, PDF, DOCX, MD, etc., nessa pasta
3. Adicione o serviço no arquivo `docker-compose.yml` que monte essa pasta para o container. Exemplo:

```yaml
services:
  bucket_novo:
    build:
      context: ./bucket
      dockerfile: Dockerfile.test
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

4. Inicie o compose para aplicar as alterações:

```bash
docker-compose up -d
```

## Como fazer uma consulta

A API REST está disponível na porta configurada (exemplo: `http://localhost:5000`).

## Organização do repositório

- `docker-compose.yml`: configurações dos buckets
- `bucket/`: estrutura dos buckets e pasta com os documentos
- `interface/`: estrutura das interfaces
- `teste_de_modelos/`: scripts auxiliares e testes