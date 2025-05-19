from cassandra.cluster import Cluster
import os
"""
Estabelece conexão com o Cassandra em execução local via Docker.
Caso o container do Cassandra utilize um IP ou hostname diferente, ajuste '127.0.0.1'.
A conexão é realizada no keyspace 'cassandra'.
"""
CLUSTER_IPS = ['127.0.0.1']
KEYSPACE = 'cassandra'
CQL_FILES_DIR = "data"
CQL_FILENAMES = [
    "alunos_formados.cql", "alunos.cql", "departamentos.cql",
    "grupo_proj.cql", "professores.cql"
]

print(f"--- Iniciando Inserção CQL (Super Concisa) em {KEYSPACE} ---")
cluster = None
session = None
errors = False

try:
    cluster = Cluster(CLUSTER_IPS)
    session = cluster.connect(KEYSPACE)
    print("Conectado.")

    for filename in CQL_FILENAMES:
        filepath = os.path.join(CQL_FILES_DIR, filename)
        print(f"Executando: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                commands = [cmd.strip() for cmd in f.read().split(';') if cmd.strip()]

            for command in commands:
                try:
                    session.execute(command)
                except Exception as exec_err:
                    print(f"  ERRO Execução: {command[:80]}... -> {exec_err}")
                    errors = True
        except FileNotFoundError:
            print(f"  ERRO: Arquivo não encontrado: {filepath}")
            errors = True
        except Exception as file_err:
            print(f"  ERRO ao ler/processar arquivo {filepath}: {file_err}")
            errors = True

except Exception as conn_err:
    print(f"ERRO CRÍTICO (conexão?): {conn_err}")
    errors = True
finally:
    if cluster:
        cluster.shutdown()
        print("Conexão fechada.")

print("\n--- Processo Finalizado ---")
if errors:
    print("ERROS ocorreram. Verifique as mensagens acima.")
else:
    print("Concluído (sem erros reportados na execução dos comandos).")