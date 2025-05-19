# Projeto 2 - Wide-column Store

## Requisitos

- Docker Desktop - [Download](https://www.docker.com/products/docker-desktop/)
- Python 3.7.9 ou inferior
- Bibliotecas
  - `cassandra-driver`
  - `faker`

## Configurando Ambiente

1.  Navegue até a pasta dentro do projeto Cassandra.

2.  Criação da venv:

    ```python
    python3.7 -m venv .venv
    ```

3.  Ativar o ambiente:

    ```bash
    # Windows command prompt
    .venv\Scripts\activate.bat

    # Windows PowerShell
    .venv\Scripts\Activate.ps1

    # macOS and Linux
    source .venv/bin/activate
    ```

4.  Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

## Configuração Docker

### Requisitos

- Docker Desktop

### Passos

1.  Baixar imagem:

    ```bash
    docker pull cassandra:latest
    ```

2.  Executar o container:

    ```bash
    docker run --name my-cassandra -p 9042:9042 -d cassandra:latest
    ```

3.  Verifique se o container `my-cassandra` foi listado. Caso não, espere mais alguns segundos:

    ```bash
    docker ps
    ```

4.  Conectar ao `cqlsh`:

    ```bash
    docker exec -it my-cassandra cqlsh
    ```

5.  Criar o keyspace:

    ```sql
    CREATE KEYSPACE cassandra WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    ```

6.  Selecionar keyspace:

    ```sql
    USE cassandra;
    ```

## Executar o Código

1.  Criar tabela:

    ```bash
    python tabela.py
    ```

2.  Criar dados:

    ```bash
    python gerador.py
    ```

3.  Injetar dados:

    ```bash
    python injetor.py
    ```

## [Link Queries](/Cassandra/queries.md)