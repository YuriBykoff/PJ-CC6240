from cassandra.cluster import Cluster

def obter_sessao_cassandra():
    """
    Estabelece conexão com o Cassandra em execução local via Docker.
    Caso o container do Cassandra utilize um IP ou hostname diferente, ajuste '127.0.0.1'.
    A conexão é realizada no keyspace 'cassandra'.
    """
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect('cassandra')
    return session

def criar_tabelas(session):

    session.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id_aluno int PRIMARY KEY,
            nome text,
            -- id_curso int,       // Removido
            -- id_disciplina int,  // Removido
            disciplinas_concluidas map<text, frozen<tuple<int, int, float>>>
        )
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS professor (
            id_professor int PRIMARY KEY,
            nome text,
            id_departamento int,
            disciplinas_ministradas map<text, frozen<tuple<int, int>>>
        )
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS departamento (
            id_departamento int PRIMARY KEY,
            nome text,
            id_chefe_departamento int,
            disciplinas set<text>
        )
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS alunos_formado (
            ano int,
            semestre int,
            id_aluno int,
            nome text,
            PRIMARY KEY ((ano, semestre), id_aluno)
        ) WITH CLUSTERING ORDER BY (id_aluno ASC)
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS grupo_proj (
            id_grupo int PRIMARY KEY,
            id_professor int,
            membros list<int>
        )
    """)

if __name__ == "__main__":
    session = obter_sessao_cassandra()
    criar_tabelas(session)
    print("Tabelas criadas ou atualizadas com sucesso!")
    session.cluster.shutdown()