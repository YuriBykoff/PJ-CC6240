from faker import Faker
import random
import os # Adicionado para manipulação de diretórios

# Inicializa o Faker para gerar dados em português do Brasil
fake = Faker('pt_BR')

# Lista de disciplinas disponíveis
disciplinas = ["Desenvolvimento de Jogo", "Sistemas Distribuídos", "Trabalho de Final de Curso", 
                "Tópicos Avançados de Engenharia de Software", "Gestão de Projeto de Software", 
                "Inteligência Artificial e Robótica", "Bancos de Dados Avançados"]

# Contadores globais para gerar IDs sequenciais
contador_aluno = 1
contador_professor = 1
contador_departamento = 1
contador_grupo = 1

# Listas globais para armazenar os IDs gerados e garantir referências válidas
ids_departamentos = []
ids_alunos = []
ids_professores = []

# Função auxiliar para escrever em um arquivo (movida para o nível superior)
def gravar_arquivo(nome_arquivo, consultas):
    # Garante que o diretório de destino exista
    os.makedirs(os.path.dirname(nome_arquivo), exist_ok=True)
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        for consulta in consultas:
            arquivo.write(consulta + '\n')

# Função principal para gerar os comandos INSERT para todas as tabelas
def gerar_comandos_insert(num_alunos=75, num_professores=20, num_departamentos=10, num_alunos_formados=40, num_grupos=15):
    global contador_aluno, contador_professor, contador_departamento, contador_grupo

    # Listas para armazenar os comandos INSERT gerados
    inserts_alunos = []
    inserts_professores = []
    inserts_departamentos = []
    inserts_alunos_formados = []
    inserts_grupo_proj = []

    # --- Geração de Departamentos ---
    for _ in range(num_departamentos):
        id_departamento = contador_departamento
        ids_departamentos.append(id_departamento)
        nome_departamento = fake.company()
        num_disciplinas_dep = random.randint(1, 3)
        disciplinas_departamento = random.sample(disciplinas, num_disciplinas_dep)
        # Mantendo a forma original aqui por simplicidade, ou podemos alterar também se desejado
        disciplinas_string = ', '.join([f"'{d}'" for d in disciplinas_departamento])
        inserts_departamentos.append(
            (id_departamento, nome_departamento, disciplinas_string)
        )
        contador_departamento += 1

    # --- Geração de Professores ---
    for _ in range(num_professores):
        id_professor = contador_professor
        ids_professores.append(id_professor)
        nome = fake.name()
        id_departamento = random.choice(ids_departamentos)
        disciplinas_ministradas = {}
        num_disciplinas_ministradas = random.randint(1, 4)
        disciplinas_selecionadas = random.sample(disciplinas, num_disciplinas_ministradas)
        for disciplina in disciplinas_selecionadas:
            semestre = random.randint(1, 2)
            ano = random.randint(2018, 2024)
            disciplinas_ministradas[disciplina] = (semestre, ano)

        # Alterando a forma de construir a string
        items_disciplinas_ministradas = []
        for k, v in disciplinas_ministradas.items():
            items_disciplinas_ministradas.append(f"'{k}': ({v[0]}, {v[1]})")
        disciplinas_ministradas_string = '{' + ', '.join(items_disciplinas_ministradas) + '}'

        inserts_professores.append(
            f"INSERT INTO professor (id_professor, nome, id_departamento, disciplinas_ministradas) "
            f"VALUES ({id_professor}, '{nome}', {id_departamento}, {disciplinas_ministradas_string});"
        )
        contador_professor += 1

    # --- Atualização de Departamentos com Chefes ---
    inserts_departamentos_finais = []
    ids_professores_temp = ids_professores[:] # Copia para manipulação
    for id_dep, nome_dep, disciplinas_string_dep in inserts_departamentos:
        if ids_professores_temp:
            id_chefe = random.choice(ids_professores_temp)
            ids_professores_temp.remove(id_chefe)
        elif ids_professores:
             id_chefe = random.choice(ids_professores)
        else:
            id_chefe = 0 # Define id_chefe como 0 (ou algum valor padrão) se não houver professores

        inserts_departamentos_finais.append(
            f"INSERT INTO departamento (id_departamento, nome, id_chefe_departamento, disciplinas) "
            f"VALUES ({id_dep}, '{nome_dep}', {id_chefe}, {{ {disciplinas_string_dep} }});"
        )

    # --- Geração de Alunos ---
    for _ in range(num_alunos):
        id_aluno = contador_aluno
        ids_alunos.append(id_aluno)
        nome = fake.name()

        disciplinas_concluidas = {}
        num_disciplinas_concluidas = random.randint(1, len(disciplinas))
        disciplinas_selecionadas = random.sample(disciplinas, num_disciplinas_concluidas)
        for disciplina in disciplinas_selecionadas:
            semestre = random.randint(1, 8)
            ano = random.randint(2018, 2024)
            nota = round(random.uniform(0, 10), 2)
            disciplinas_concluidas[disciplina] = (semestre, ano, nota)

        # Alterando a forma de construir a string
        items_disciplinas_concluidas = []
        for k, v in disciplinas_concluidas.items():
            items_disciplinas_concluidas.append(f"'{k}': ({v[0]}, {v[1]}, {v[2]})")
        disciplinas_concluidas_string = '{' + ', '.join(items_disciplinas_concluidas) + '}'
        
        inserts_alunos.append(
            f"INSERT INTO alunos (id_aluno, nome, disciplinas_concluidas) VALUES ({id_aluno}, '{nome}', {disciplinas_concluidas_string});"
        )
        contador_aluno += 1

    # --- Geração de Alunos Formados ---
    amostra_alunos_formados = random.sample(ids_alunos, min(num_alunos_formados, len(ids_alunos)))
    for id_aluno_formado in amostra_alunos_formados:
        ano = random.randint(2020, 2024)
        semestre = random.randint(1, 2)
        nome_formado = fake.name() # Mantendo a geração de nome fake
        inserts_alunos_formados.append(
            f"INSERT INTO alunos_formado (ano, semestre, id_aluno, nome) VALUES ({ano}, {semestre}, {id_aluno_formado}, '{nome_formado}');"
        )

    # --- Geração de Grupos de Projeto ---
    if ids_professores and len(ids_alunos) >= 2:
        for _ in range(num_grupos):
            id_grupo = contador_grupo
            id_professor_grupo = random.choice(ids_professores)
            num_membros = random.randint(2, min(5, len(ids_alunos)))
            ids_membros = random.sample(ids_alunos, num_membros)
            
            # Alterando a forma de construir a string
            membros_str_list = []
            for membro_id in ids_membros:
                membros_str_list.append(str(membro_id))
            membros_string = '[' + ', '.join(membros_str_list) + ']'

            inserts_grupo_proj.append(
                f"INSERT INTO grupo_proj (id_grupo, id_professor, membros) VALUES ({id_grupo}, {id_professor_grupo}, {membros_string});"
            )
            contador_grupo += 1

    return (
        inserts_alunos,
        inserts_professores,
        inserts_departamentos_finais,
        inserts_alunos_formados,
        inserts_grupo_proj,
    )

# Função para salvar os comandos INSERT gerados em arquivos .cql separados
def salvar_cql(alunos, professores, departamentos, formados, grupos):
    arquivos_e_dados = [
        ('data/alunos.cql', alunos),
        ('data/professores.cql', professores),
        ('data/departamentos.cql', departamentos),
        ('data/alunos_formados.cql', formados),
        ('data/grupo_proj.cql', grupos)
    ]

    for nome_arquivo, dados in arquivos_e_dados:
        gravar_arquivo(nome_arquivo, dados)

# Bloco principal que executa ao rodar o script
alunos, professores, departamentos, formados, grupos = gerar_comandos_insert()
salvar_cql(alunos, professores, departamentos, formados, grupos)
print("Arquivos CQL foram gerados com sucesso")