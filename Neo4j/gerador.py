from faker import Faker
import random

fake = Faker('pt_BR')

QTD_ALUNOS = 100
QTD_PROFESSORES = 20
QTD_DEPARTAMENTOS = 10
QTD_MATRIZES = 5
QTD_TCCS = 15
QTD_ALUNOS_FORMADOS_APROX = QTD_ALUNOS // 2
MIN_DISCIPLINAS_POR_MATRIZ = 4
MAX_DISCIPLINAS_POR_MATRIZ = 7
MIN_ALUNOS_POR_TCC = 4
MAX_ALUNOS_POR_TCC = 5
ANOS_PERIODO_GERACAO = list(range(2022, 2025))
SEMESTRES_PERIODO_GERACAO = [1, 2]
NOTA_MINIMA_APROVACAO = 5.0

ANOS_EXEMPLO_FORMATURA = [2023, 2022]
SEMESTRES_EXEMPLO_FORMATURA = [1, 2]

NOMES_BASE_DISCIPLINAS = [
    "Desenvolvimento de Jogo", "Sistemas Distribuídos", "Trabalho de Final de Curso",
    "Tópicos Avançados de Engenharia de Software", "Gestão de Projeto de Software",
    "Inteligência Artificial e Robótica", "Bancos de Dados Avançados"
]

contadores_id = {
    "aluno": 1, "professor": 1, "disciplina_idx": 0,
    "departamento": 1, "matriz": 1, "tcc": 1
}
armazenamento_dados = {
    "alunos": {}, "professores": {}, "disciplinas": {},
    "departamentos": {}, "matrizes": {}, "tccs": {}
}
comandos_nos_cypher = []
comandos_rels_cypher = []

formaturas_exemplo_geradas = []

def formatar_valor_propriedade_cypher(valor):
    if isinstance(valor, str):
        return f"'{str(valor).replace("'", "\\'")}'"
    return str(valor)

def propriedades_para_string_cypher(propriedades):
    return ", ".join(f"{k}: {formatar_valor_propriedade_cypher(v)}" for k, v in propriedades.items())

def adicionar_no_cypher(rotulo_no, propriedades_no):
    comandos_nos_cypher.append(f"CREATE (:{rotulo_no} {{{propriedades_para_string_cypher(propriedades_no)}}});")

def adicionar_relacionamento_cypher(rotulo_origem, props_origem, tipo_rel, props_rel, rotulo_destino, props_destino):
    match_origem_str = f"(a:{rotulo_origem} {{{propriedades_para_string_cypher(props_origem)}}})"
    match_destino_str = f"(b:{rotulo_destino} {{{propriedades_para_string_cypher(props_destino)}}})"
    props_rel_str = f" {{{propriedades_para_string_cypher(props_rel)}}}" if props_rel else ""
    comandos_rels_cypher.append(f"MATCH {match_origem_str}, {match_destino_str} CREATE (a)-[:{tipo_rel}{props_rel_str}]->(b);")

for nome_disciplina_base in NOMES_BASE_DISCIPLINAS:
    contadores_id["disciplina_idx"] += 1
    codigo_disciplina_gerado = f"DISC{contadores_id['disciplina_idx']:03d}"
    # As chaves 'codigo_disciplina' e 'nome_disciplina' são nomes de propriedades Neo4j, mantidas em inglês.
    armazenamento_dados["disciplinas"][codigo_disciplina_gerado] = {'codigo_disciplina': codigo_disciplina_gerado, 'nome_disciplina': nome_disciplina_base}
    adicionar_no_cypher("Disciplina", armazenamento_dados["disciplinas"][codigo_disciplina_gerado])

configuracoes_nos = [
    ("Aluno", QTD_ALUNOS, "alunos", "id_aluno", "nome_aluno", lambda: fake.name(), "aluno"),
    ("Professor", QTD_PROFESSORES, "professores", "id_professor", "nome_professor", lambda: fake.name(), "professor"),
    ("Departamento", QTD_DEPARTAMENTOS, "departamentos", "id_departamento", "nome_departamento", lambda: f"Depto. {fake.bs().split(' ')[0]}", "departamento"),
    ("MatrizCurricular", QTD_MATRIZES, "matrizes", "id_matriz", "nome_matriz", lambda: f"Matriz {fake.color_name()} {random.choice(ANOS_PERIODO_GERACAO)-2}", "matriz"),
    ("TCC", QTD_TCCS, "tccs", "id_tcc", "titulo_tcc", lambda: f"TCC: {fake.catch_phrase()}", "tcc")
]

for rotulo, quantidade, chave_armazenamento_entidade, nome_chave_id_prop, nome_chave_nome_prop, funcao_gerar_nome, chave_contador_id_entidade in configuracoes_nos:
    print(f"    Gerando {quantidade} nós do tipo '{rotulo}'...")
    for _ in range(quantidade):
        id_atual_entidade = contadores_id[chave_contador_id_entidade]
        # As chaves nome_chave_id_prop e nome_chave_nome_prop (e.g. "id_aluno", "nome_aluno") são nomes de propriedades Neo4j.
        armazenamento_dados[chave_armazenamento_entidade][id_atual_entidade] = {nome_chave_id_prop: id_atual_entidade, nome_chave_nome_prop: funcao_gerar_nome()}
        adicionar_no_cypher(rotulo, armazenamento_dados[chave_armazenamento_entidade][id_atual_entidade])
        contadores_id[chave_contador_id_entidade] += 1

todos_ids_professores = list(armazenamento_dados["professores"].keys())
todos_ids_alunos = list(armazenamento_dados["alunos"].keys())
todos_codigos_disciplinas = list(armazenamento_dados["disciplinas"].keys())
todos_ids_matrizes = list(armazenamento_dados["matrizes"].keys())
todos_ids_departamentos = list(armazenamento_dados["departamentos"].keys())
todos_ids_tccs = list(armazenamento_dados["tccs"].keys())

ids_professores_chefia_embaralhados = random.sample(todos_ids_professores, k=min(len(todos_ids_professores), len(todos_ids_departamentos)))
for indice_dep, id_dep_atual in enumerate(todos_ids_departamentos):
    if indice_dep < len(ids_professores_chefia_embaralhados):
        adicionar_relacionamento_cypher("Professor", {'id_professor': ids_professores_chefia_embaralhados[indice_dep]},
                "CHEFE_DE", {},
                "Departamento", {'id_departamento': id_dep_atual})

mapa_matriz_disciplinas = {}
for id_matriz_atual in todos_ids_matrizes:
    qtd_disciplinas_na_matriz = random.randint(MIN_DISCIPLINAS_POR_MATRIZ, min(MAX_DISCIPLINAS_POR_MATRIZ, len(todos_codigos_disciplinas)))
    disciplinas_selecionadas_para_matriz = random.sample(todos_codigos_disciplinas, qtd_disciplinas_na_matriz)
    mapa_matriz_disciplinas[id_matriz_atual] = disciplinas_selecionadas_para_matriz
    for codigo_disc_matriz in disciplinas_selecionadas_para_matriz:
        adicionar_relacionamento_cypher("MatrizCurricular", {'id_matriz': id_matriz_atual},
                "CONTEM_DISCIPLINA", {},
                "Disciplina", {'codigo_disciplina': codigo_disc_matriz})

aprovacoes_por_aluno = {id_al: {} for id_al in todos_ids_alunos}
max_ano_cursado_por_aluno = {id_al: ANOS_PERIODO_GERACAO[0] -1 for id_al in todos_ids_alunos}

alunos_candidatos_a_formatura = set(random.sample(todos_ids_alunos, QTD_ALUNOS_FORMADOS_APROX))

for id_aluno_corrente in todos_ids_alunos:
    if id_aluno_corrente in alunos_candidatos_a_formatura:
        qtd_disciplinas_a_cursar = random.randint(MIN_DISCIPLINAS_POR_MATRIZ, min(MAX_DISCIPLINAS_POR_MATRIZ + 2, len(todos_codigos_disciplinas)))
    else:
        qtd_disciplinas_a_cursar = random.randint(max(1, len(todos_codigos_disciplinas) // 5), max(2, len(todos_codigos_disciplinas) // 3))

    disciplinas_cursadas_pelo_aluno_atual = random.sample(todos_codigos_disciplinas, qtd_disciplinas_a_cursar)
    for codigo_disciplina_cursada in disciplinas_cursadas_pelo_aluno_atual:
        ano_em_que_cursou = random.choice(ANOS_PERIODO_GERACAO[:-1]) if len(ANOS_PERIODO_GERACAO) > 1 else ANOS_PERIODO_GERACAO[0]
        semestre_em_que_cursou = random.choice(SEMESTRES_PERIODO_GERACAO)
        nota_obtida = round(random.uniform(0.0, 10.0), 1)

        propriedades_rel_cursou = {'semestre': semestre_em_que_cursou, 'ano': ano_em_que_cursou, 'nota_final': nota_obtida}
        adicionar_relacionamento_cypher("Aluno", {'id_aluno': id_aluno_corrente}, "CURSOU", propriedades_rel_cursou, "Disciplina", {'codigo_disciplina': codigo_disciplina_cursada})

        if ano_em_que_cursou > max_ano_cursado_por_aluno[id_aluno_corrente]:
            max_ano_cursado_por_aluno[id_aluno_corrente] = ano_em_que_cursou
        if nota_obtida >= NOTA_MINIMA_APROVACAO:
            aprovacoes_por_aluno[id_aluno_corrente][codigo_disciplina_cursada] = nota_obtida

ids_alunos_formatura_embaralhados = list(alunos_candidatos_a_formatura)
random.shuffle(ids_alunos_formatura_embaralhados)
contador_alunos_formados = 0
ids_alunos_que_ja_formaram = set()

anos_prioritarios_para_formar = ANOS_EXEMPLO_FORMATURA + [ano for ano in ANOS_PERIODO_GERACAO if ano not in ANOS_EXEMPLO_FORMATURA]

for id_aluno_formando in ids_alunos_formatura_embaralhados:
    if id_aluno_formando in ids_alunos_que_ja_formaram or contador_alunos_formados >= QTD_ALUNOS_FORMADOS_APROX :
        continue

    for id_matriz_formando, disciplinas_da_matriz in mapa_matriz_disciplinas.items():
        if all(cod_disciplina_matriz in aprovacoes_por_aluno[id_aluno_formando] for cod_disciplina_matriz in disciplinas_da_matriz):
            ano_minimo_formacao = max(max_ano_cursado_por_aluno[id_aluno_formando] + 1, ANOS_PERIODO_GERACAO[0])
            
            ano_definitivo_formacao = None
            semestre_definitivo_formacao = None

            max_alunos_por_periodo_exemplo = (QTD_ALUNOS_FORMADOS_APROX // (len(ANOS_EXEMPLO_FORMATURA) * len(SEMESTRES_EXEMPLO_FORMATURA) or 1)) // 2 or 1
            if contador_alunos_formados < len(ANOS_EXEMPLO_FORMATURA) * len(SEMESTRES_EXEMPLO_FORMATURA) * max_alunos_por_periodo_exemplo:
                for ano_fmt_exemplo in ANOS_EXEMPLO_FORMATURA:
                    if ano_fmt_exemplo >= ano_minimo_formacao:
                        for sem_fmt_exemplo in SEMESTRES_EXEMPLO_FORMATURA:
                            chave_periodo_fmt_exemplo = (ano_fmt_exemplo, sem_fmt_exemplo)
                            if formaturas_exemplo_geradas.count(chave_periodo_fmt_exemplo) < max_alunos_por_periodo_exemplo + 1:
                                ano_definitivo_formacao = ano_fmt_exemplo
                                semestre_definitivo_formacao = sem_fmt_exemplo
                                break
                    if ano_definitivo_formacao:
                        break
            
            if ano_definitivo_formacao is None:
                anos_validos_para_nova_formacao = [ano_valido for ano_valido in anos_prioritarios_para_formar if ano_valido >= ano_minimo_formacao and ano_valido <= ANOS_PERIODO_GERACAO[-1]]
                if not anos_validos_para_nova_formacao:
                    ano_definitivo_formacao = ANOS_PERIODO_GERACAO[-1]
                else:
                    ano_definitivo_formacao = random.choice(anos_validos_para_nova_formacao)
                semestre_definitivo_formacao = random.choice(SEMESTRES_PERIODO_GERACAO)

            propriedades_rel_formado = {'semestre_formacao': semestre_definitivo_formacao, 'ano_formacao': ano_definitivo_formacao}
            adicionar_relacionamento_cypher("Aluno", {'id_aluno': id_aluno_formando}, "FORMADO_EM", propriedades_rel_formado, "MatrizCurricular", {'id_matriz': id_matriz_formando})
            
            formaturas_exemplo_geradas.append((ano_definitivo_formacao, semestre_definitivo_formacao))
            ids_alunos_que_ja_formaram.add(id_aluno_formando)
            contador_alunos_formados += 1
            break

for id_professor_ministrante in todos_ids_professores:
    qtd_disciplinas_a_ministrar = random.randint(1, max(1, len(todos_codigos_disciplinas) // 3))
    disciplinas_selecionadas_para_ministrar = random.sample(todos_codigos_disciplinas, qtd_disciplinas_a_ministrar)
    for codigo_disciplina_ministrada in disciplinas_selecionadas_para_ministrar:
        adicionar_relacionamento_cypher("Professor", {'id_professor': id_professor_ministrante}, "MINISTROU",
                {'semestre': random.choice(SEMESTRES_PERIODO_GERACAO), 'ano': random.choice(ANOS_PERIODO_GERACAO)},
                "Disciplina", {'codigo_disciplina': codigo_disciplina_ministrada})

for id_tcc_corrente in todos_ids_tccs:
    id_professor_orientador = random.choice(todos_ids_professores)
    adicionar_relacionamento_cypher("Professor", {'id_professor': id_professor_orientador}, "ORIENTA", {}, "TCC", {'id_tcc': id_tcc_corrente})

    qtd_alunos_no_grupo_tcc = random.randint(MIN_ALUNOS_POR_TCC, MAX_ALUNOS_POR_TCC)
    ids_alunos_disponiveis_para_tcc = random.sample(todos_ids_alunos, min(qtd_alunos_no_grupo_tcc, len(todos_ids_alunos)))
    for id_aluno_participante_tcc in ids_alunos_disponiveis_para_tcc:
        adicionar_relacionamento_cypher("Aluno", {'id_aluno': id_aluno_participante_tcc}, "PARTICIPA_DE", {}, "TCC", {'id_tcc': id_tcc_corrente})

nomes_arquivos_saida = {"nodes": "data/nodes.cypher", "relationships": "data/relationships.cypher"}

with open(nomes_arquivos_saida["nodes"], "w", encoding="utf-8") as arquivo_nos:
    arquivo_nos.write("MATCH (n) DETACH DELETE n;\n\n")
    
    comandos_constraints_indices_cypher = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Aluno) REQUIRE a.id_aluno IS UNIQUE;",
        "CREATE INDEX IF NOT EXISTS FOR (a:Aluno) ON (a.nome_aluno);",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Professor) REQUIRE p.id_professor IS UNIQUE;",
        "CREATE INDEX IF NOT EXISTS FOR (p:Professor) ON (p.nome_professor);",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disciplina) REQUIRE d.codigo_disciplina IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (dp:Departamento) REQUIRE dp.id_departamento IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (m:MatrizCurricular) REQUIRE m.id_matriz IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (t:TCC) REQUIRE t.id_tcc IS UNIQUE;"
    ]
    arquivo_nos.write("// Constraints e Índices\n")
    arquivo_nos.write("\n".join(comandos_constraints_indices_cypher))
    arquivo_nos.write("\n\n// Criação de Nós\n")
    arquivo_nos.write("\n".join(comandos_nos_cypher))

with open(nomes_arquivos_saida["relationships"], "w", encoding="utf-8") as arquivo_rels:
    arquivo_rels.write("// Criação de Relacionamentos\n")
    arquivo_rels.write("\n".join(comandos_rels_cypher))

print("\nProcesso de geração de dados concluído!")