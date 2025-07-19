# Projeto API de Pesquisa Semântica

Este projeto implementa uma API de pesquisa semântica para recuperar documentos com base em consultas em linguagem natural. 

Utiliza modelos de embeddings para capturar o significado semântico dos textos e é projetado para ser escalável e modular, com suporte a múltiplos buckets de documentos.

## Pré-requisitos

- Docker instalado

## Estrutura do Projeto

- `docker-compose.yml`: Configura os serviços principais, incluindo a interface, os buckets e o serviço Ollama.
- `docker-compose.mac.yml`: Configuração alternativa para ambientes Mac.
- `docker-compose.test.yml`: Configuração para execução de testes comparativos de modelos.
- `bucket/`: Contém a lógica dos buckets e as pastas com os documentos.
- `Interface/`: Estrutura da interface web para consultas.
- `test/`: Scripts e configurações para testes de modelos.
- `load_models.sh`: Script para carregar os modelos de embeddings no serviço Ollama.
- `OllamaDAO.py`: Classe para interagir com o serviço Ollama e gerar embeddings.

## Serviços Principais

- **Ollama**: Serviço que executa os modelos de embeddings. Utiliza GPU preferencialmente.
- **Interface**: Interface web para realizar consultas, acessível em `http://localhost:8080`.
- **Buckets**: Serviços que gerenciam conjuntos de documentos:
  - `bucket1`: Crime DataSet (porta 8081)
  - `bucket2`: Medical DataSet (Consultations) (porta 8082)
  - `bucket3`: BBC News DataSet (porta 8083)
  - `bucket4`: Crime DataSet PT (porta 8084)

## Como Executar o Sistema

1. Certifique-se de que o Docker está em execução.
2. Na raiz do projeto, execute o comando para iniciar os serviços em background:

   ```bash
   docker-compose up -d
   ```
3. Acesse a interface web em: `http://localhost:8080`

### Notas para Usuários de Mac

Se estiver usando um Mac, utilize o arquivo de compose específico:

```bash
docker-compose -f docker-compose.mac.yml up -d
```

## Como Adicionar Documentos

Os documentos são organizados em buckets, cada um correspondendo a um conjunto de dados específico. Para adicionar documentos a um bucket existente:

1. Coloque os arquivos (e.g., texto, PDF, DOCX, MD) na pasta correspondente dentro de `./bucket/buckets/`. Por exemplo:
   - Para `bucket1` (Crime DataSet): `./bucket/buckets/bucket1`
   - Para `bucket4` (Crime DataSet PT): `./bucket/buckets/bucket4`
2. Reinicie o serviço do bucket correspondente para que ele processe os novos documentos:

   ```bash
   docker-compose restart bucket1
   ```

### Criando um Novo Bucket

Se desejar adicionar um novo conjunto de documentos em um novo bucket:

1. Crie uma nova pasta para os documentos, por exemplo: `./bucket/buckets/bucket_novo`
2. Adicione um novo serviço no `docker-compose.yml` com as configurações apropriadas. Exemplo:

   ```yaml
   bucket_novo:
     build:
       context: ./bucket
       dockerfile: Dockerfile
     ports:
       - "8085:8080"
     volumes:
       - ./bucket:/app
       - ./bucket/buckets:/app/buckets
     environment:
       - FLASK_ENV=development
       - BUCKET_NAME=Novo DataSet
       - BUCKET_URL=http://bucket_novo:8080
       - BUCKET_FOLDER=/app/buckets/bucket_novo
       - OLLAMA_HOST=http://ollama:11434
       - PORT=8080
     networks:
       - app-network
     depends_on:
       ollama:
         condition: service_healthy
   ```
3. Execute `docker-compose up -d` para aplicar as alterações e iniciar o novo bucket.

## Como Fazer uma Consulta

A interface web permite realizar consultas semânticas nos buckets selecionados:

1. Acesse `http://localhost:8080`.
2. Selecione os buckets que deseja consultar.
3. Insira a consulta no campo de pesquisa.
4. Defina o número de resultados desejados (k).
5. Clique em "Pesquisar" para ver os resultados, que incluirão o nome do documento, a similaridade, o bucket de origem e o trecho relevante.

## Testes Automatizados

O projeto inclui uma configuração para testes automatizados, que pode ser executada com:

```bash
docker-compose -f docker-compose.test.yml up
```

Isso iniciará um ambiente de teste isolado, executando scripts de teste definidos em `./test/run_tests.py`.

## Notas Adicionais

- **Modelos de Embeddings**: Os modelos são carregados automaticamente pelo serviço Ollama a partir do arquivo `models.txt`. Certifique-se de que os modelos listados estão disponíveis no Ollama.
- **Saúde dos Serviços**: Os buckets e a interface dependem do serviço Ollama para funcionarem, isto garante que os modelos estejam carregados antes de iniciar.
- **Portas**: A interface está mapeada para a porta 8080, e cada bucket tem sua própria porta (8081 a 8084). Ajuste conforme necessário para evitar conflitos.