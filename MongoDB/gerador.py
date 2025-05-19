from faker import Faker
import datetime
import random
import json
import math
import os

QTD_ALUNOS = 80
QTD_PROFESSORES = 20
QTD_CURSOS = 8
QTD_DEPARTAMENTOS = 10
QTD_DISCIPLINAS = 20
QTD_GRUPOS_TCC = 8

ANO_INICIO_SEMESTRE = 2018
NOTA_APROVACAO = 5.0
STATUS_APROVADO = "Aprovado"
STATUS_REPROVADO = "Reprovado"

fake = Faker('pt_BR')

departamentos, cursos, disciplinas_lista, professores, alunos, grupos_tcc = [], [], [], [], [], []
ids_departamentos, ids_cursos, ids_disciplinas, ids_professores, ids_alunos = [], [], [], [], []
mapa_disciplinas = {}
mapa_cod_departamento = {}
codigos_disciplinas_utilizados = set()

CODIGOS_DEPARTAMENTO_DISPONIVEIS = ["INF", "MAT", "FIS", "QUI", "BIO", "LET", "HIS", "ECO", "ENG", "ADM"]
NOMES_BASE_DEPARTAMENTO = ["Informática", "Matemática", "Física", "Química", "Biologia", "Letras", "História", "Economia", "Engenharia", "Administração"]
DISCIPLINAS_BASE = [
    "Desenvolvimento de Jogo", "Sistemas Distribuídos", "Trabalho de Final de Curso", 
    "Tópicos Avançados de Engenharia de Software", "Gestão de Projeto de Software", 
    "Inteligência Artificial e Robótica", "Bancos de Dados Avançados"
]

def gerar_semestre(ano_inicio=ANO_INICIO_SEMESTRE, ano_fim=None):
    if ano_fim is None:
        ano_fim = datetime.datetime.now().year
    ano_fim = max(ano_inicio, ano_fim)
    ano = random.randint(ano_inicio, ano_fim)
    semestre = random.choice([1, 2])
    return f"{ano}.{semestre}"

def analisar_semestre(semestre_str):
    try:
        ano, sem = map(int, semestre_str.split('.'))
        return ano, sem
    except:
        return 0, 0

def gravar_json(dados, nome_arquivo):
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"   Arquivo salvo: {nome_arquivo}")
    except (IOError, TypeError) as e:
        print(f"   ERRO ao salvar {nome_arquivo}: {e}")

def gerar_dados_academicos():
    print("--- Iniciando Geração de Dados Acadêmicos ---")

    print(f"Gerando {QTD_DEPARTAMENTOS} departamentos...")
    if len(NOMES_BASE_DEPARTAMENTO) < QTD_DEPARTAMENTOS:
        NOMES_BASE_DEPARTAMENTO.extend([f"Área {chr(65+i)}" for i in range(QTD_DEPARTAMENTOS - len(NOMES_BASE_DEPARTAMENTO))])
    mapa_cod_nome_dep = {codigo: nome for codigo, nome in zip(CODIGOS_DEPARTAMENTO_DISPONIVEIS[:QTD_DEPARTAMENTOS], NOMES_BASE_DEPARTAMENTO[:QTD_DEPARTAMENTOS])}

    for i in range(QTD_DEPARTAMENTOS):
        dep_id = i + 1
        dep_codigo = CODIGOS_DEPARTAMENTO_DISPONIVEIS[i]
        dep_nome = mapa_cod_nome_dep.get(dep_codigo, f"Departamento Genérico {i+1}")
        departamentos.append({
            "_id": dep_id,
            "nome": f"Departamento de {dep_nome}",
            "codigo_dept": dep_codigo,
            "chefe_id": None
        })
        ids_departamentos.append(dep_id)
        mapa_cod_departamento[dep_id] = dep_codigo

    print(f"Gerando {QTD_CURSOS} cursos...")
    disciplinas_por_curso = {}
    if not ids_departamentos: print("   AVISO: Não há departamentos para associar aos cursos.")

    for i in range(QTD_CURSOS):
        curso_id = i + 1
        dep_id_curso = random.choice(ids_departamentos) if ids_departamentos else None
        nome_base_curso = random.choice(DISCIPLINAS_BASE)
        curso = {
            "_id": curso_id,
            "nome": f"Graduação em {nome_base_curso}",
            "departamento_id": dep_id_curso,
            "disciplinas_ids": []
        }
        cursos.append(curso)
        ids_cursos.append(curso_id)
        if dep_id_curso is not None:
             disciplinas_por_curso[curso_id] = []

    print(f"Gerando {QTD_DISCIPLINAS} disciplinas...")
    if not cursos: print("   AVISO: Não há cursos para associar disciplinas inicialmente.")
    if not ids_departamentos: print("   AVISO: Não há departamentos para associar códigos de disciplinas.")

    for i in range(QTD_DISCIPLINAS):
        disciplina_id = i + 1
        nome_disciplina = random.choice(DISCIPLINAS_BASE)

        curso_associado = random.choice(cursos) if cursos else None
        dept_id_disciplina = None
        if curso_associado and curso_associado.get('departamento_id') in mapa_cod_departamento:
            dept_id_disciplina = curso_associado['departamento_id']
        elif ids_departamentos:
            dept_id_disciplina = random.choice(ids_departamentos)

        prefixo_codigo = mapa_cod_departamento.get(dept_id_disciplina, "GEN")

        codigo_disciplina = None
        for _ in range(50):
            codigo_tentativa = f"{prefixo_codigo}{random.randint(100, 699)}"
            if codigo_tentativa not in codigos_disciplinas_utilizados:
                codigo_disciplina = codigo_tentativa
                break
        if not codigo_disciplina:
            codigo_disciplina = f"DIS{disciplina_id:03d}"

        if codigo_disciplina in codigos_disciplinas_utilizados:
             codigo_disciplina = f"D{disciplina_id:03d}X{random.randint(100,999)}"

        codigos_disciplinas_utilizados.add(codigo_disciplina)

        disciplina_obj = {"_id": disciplina_id, "codigo": codigo_disciplina, "nome": nome_disciplina}
        disciplinas_lista.append(disciplina_obj)
        ids_disciplinas.append(disciplina_id)
        mapa_disciplinas[disciplina_id] = {"codigo": disciplina_obj["codigo"], "nome": disciplina_obj["nome"]}

        if curso_associado and curso_associado["_id"] in disciplinas_por_curso:
             disciplinas_por_curso[curso_associado["_id"]].append(disciplina_id)

    print("Atribuindo disciplinas aos cursos (matriz curricular)...")
    if ids_disciplinas and cursos:
        min_disciplinas_curso = max(1, QTD_DISCIPLINAS // QTD_CURSOS - 2 if QTD_CURSOS > 0 else 1)
        max_eletivas_curso = 3

        for curso_obj in cursos:
            curso_id = curso_obj["_id"]
            if curso_id in disciplinas_por_curso:
                disciplinas_base_curso = disciplinas_por_curso[curso_id]
                num_a_adicionar = min_disciplinas_curso - len(disciplinas_base_curso)

                disciplinas_disponiveis = [d_id for d_id in ids_disciplinas if d_id not in disciplinas_base_curso]
                random.shuffle(disciplinas_disponiveis)
                if num_a_adicionar > 0 and disciplinas_disponiveis:
                    disciplinas_base_curso.extend(disciplinas_disponiveis[:min(num_a_adicionar, len(disciplinas_disponiveis))])

                num_eletivas = random.randint(0, max_eletivas_curso)
                disciplinas_disponiveis_eletivas = [d_id for d_id in ids_disciplinas if d_id not in disciplinas_base_curso]
                random.shuffle(disciplinas_disponiveis_eletivas)
                if num_eletivas > 0 and disciplinas_disponiveis_eletivas:
                     disciplinas_base_curso.extend(disciplinas_disponiveis_eletivas[:min(num_eletivas, len(disciplinas_disponiveis_eletivas))])

                curso_obj["disciplinas_ids"] = list(set(disciplinas_base_curso))
            else:
                 num_obrigatorias = min_disciplinas_curso + random.randint(0, max_eletivas_curso)
                 if ids_disciplinas:
                    curso_obj["disciplinas_ids"] = random.sample(ids_disciplinas, min(num_obrigatorias, len(ids_disciplinas)))
                 else:
                    curso_obj["disciplinas_ids"] = []

    print(f"Gerando {QTD_PROFESSORES} professores e definindo chefes...")
    if not ids_departamentos: print("   AVISO: Não há departamentos para associar professores ou definir chefes.")

    professores_disponiveis_chefia = list(range(1, QTD_PROFESSORES + 1))
    random.shuffle(professores_disponiveis_chefia)
    departamentos_sem_chefe = list(ids_departamentos)
    random.shuffle(departamentos_sem_chefe)

    for i in range(QTD_PROFESSORES):
        prof_id = i + 1
        prof_dept_id = random.choice(ids_departamentos) if ids_departamentos else None
        eh_chefe_agora = False

        if departamentos_sem_chefe and prof_id in professores_disponiveis_chefia:
             dep_id_para_chefiar = departamentos_sem_chefe.pop()
             prof_dept_id = dep_id_para_chefiar
             eh_chefe_agora = True
             for dep in departamentos:
                 if dep["_id"] == dep_id_para_chefiar:
                     dep["chefe_id"] = prof_id
                     break

        professor_obj = {
            "_id": prof_id,
            "nome": fake.name(),
            "departamento_id": prof_dept_id,
            "eh_chefe": eh_chefe_agora,
            "disciplinas_ministradas": []
        }
        professores.append(professor_obj)
        ids_professores.append(prof_id)

    if departamentos_sem_chefe:
        print(f"   AVISO: {len(departamentos_sem_chefe)} departamento(s) ficaram sem chefe por falta de professores.")

    print("Gerando histórico de disciplinas dos professores...")
    if ids_disciplinas and professores:
        min_hist, max_hist = 2, 5
        for prof in professores:
            num_disciplinas_hist = random.randint(min_hist, max_hist)
            disciplinas_ministradas_semestre = set()

            disciplinas_candidatas = []
            if prof["departamento_id"] and prof["departamento_id"] in mapa_cod_departamento:
                dept_code_prof = mapa_cod_departamento[prof["departamento_id"]]
                disciplinas_candidatas = [
                    disc_id for disc_id, info in mapa_disciplinas.items()
                    if info['codigo'].startswith(dept_code_prof)
                ]
            disciplinas_candidatas.extend([d_id for d_id in ids_disciplinas if d_id not in disciplinas_candidatas])
            random.shuffle(disciplinas_candidatas)

            if not disciplinas_candidatas: continue

            for _ in range(num_disciplinas_hist):
                if not disciplinas_candidatas: break
                disciplina_id = disciplinas_candidatas.pop(random.randrange(len(disciplinas_candidatas)))
                semestre = gerar_semestre()
                ano_sem, _ = analisar_semestre(semestre)
                chave_unica = (disciplina_id, semestre)

                if chave_unica not in disciplinas_ministradas_semestre:
                    prof["disciplinas_ministradas"].append({
                        "disciplina_id": disciplina_id,
                        "semestre": semestre,
                        "ano": ano_sem
                    })
                    disciplinas_ministradas_semestre.add(chave_unica)
    else:
        print("   AVISO: Não há disciplinas ou professores para gerar histórico.")

    print(f"Gerando {QTD_ALUNOS} alunos e seus históricos...")
    alunos_graduados_count = 0
    if not cursos: print("   AVISO: Não há cursos para associar alunos.")
    if not ids_disciplinas: print("   AVISO: Não há disciplinas para gerar histórico escolar.")

    mapa_matriz_curso = {c['_id']: set(c.get("disciplinas_ids", [])) for c in cursos}

    for i in range(QTD_ALUNOS):
        aluno_id = i + 1
        curso_id_aluno = random.choice(ids_cursos) if ids_cursos else None

        aluno_obj = {
            "_id": aluno_id, "nome": fake.name(), "curso_id": curso_id_aluno,
            "historico": [], "graduado": False, "semestre_graduacao": None
        }

        disciplinas_aprovadas_ids = set()
        if ids_disciplinas and curso_id_aluno:
            min_cursadas = math.ceil(QTD_DISCIPLINAS * 0.5)
            num_a_cursar = random.randint(min_cursadas, QTD_DISCIPLINAS)
            disciplinas_para_historico_ids = random.sample(ids_disciplinas, min(num_a_cursar, len(ids_disciplinas)))

            semestre_inicial_ano = ANO_INICIO_SEMESTRE - random.randint(0, 2)
            ultimo_ano = semestre_inicial_ano
            ultimo_sem = 0

            for disc_id in disciplinas_para_historico_ids:
                if ultimo_sem == 2:
                    ano_cursado, sem_cursado = ultimo_ano + 1, 1
                elif ultimo_sem == 1:
                    ano_cursado, sem_cursado = ultimo_ano, 2
                else:
                    ano_cursado, sem_cursado = ultimo_ano, random.choice([1, 2])

                semestre_str = f"{ano_cursado}.{sem_cursado}"
                ultimo_ano, ultimo_sem = ano_cursado, sem_cursado

                nota = round(random.uniform(2.0, 10.0), 1)
                status = STATUS_APROVADO if nota >= NOTA_APROVACAO else STATUS_REPROVADO
                info_disciplina = mapa_disciplinas.get(disc_id)

                if info_disciplina:
                    aluno_obj["historico"].append({
                        "disciplina_id": disc_id,
                        "codigo": info_disciplina["codigo"], "nome": info_disciplina["nome"],
                        "semestre": semestre_str, "ano": ano_cursado,
                        "nota_final": nota, "status": status
                    })
                    if status == STATUS_APROVADO:
                        disciplinas_aprovadas_ids.add(disc_id)

            matriz_curso_atual = mapa_matriz_curso.get(curso_id_aluno, set())
            if matriz_curso_atual and matriz_curso_atual.issubset(disciplinas_aprovadas_ids):
                aluno_obj["graduado"] = True
                alunos_graduados_count += 1
                if aluno_obj["historico"]:
                    try:
                        ultimo_registro = max(aluno_obj["historico"], key=lambda x: analisar_semestre(x.get("semestre", "0.0")))
                        aluno_obj["semestre_graduacao"] = ultimo_registro.get("semestre")
                    except:
                        aluno_obj["graduado"] = False
                        if aluno_obj["_id"] in disciplinas_aprovadas_ids:
                              alunos_graduados_count -=1

        alunos.append(aluno_obj)
        ids_alunos.append(aluno_id)

    print(f"   -> {alunos_graduados_count} alunos marcados como graduados.")

    print(f"Gerando {QTD_GRUPOS_TCC} grupos de TCC...")
    if not ids_alunos: print("   AVISO: Não há alunos para formar grupos de TCC.")
    if not ids_professores: print("   AVISO: Não há professores para orientar TCC.")

    alunos_disponiveis_tcc = list(ids_alunos)
    random.shuffle(alunos_disponiveis_tcc)
    profs_disponiveis_tcc = list(ids_professores)
    random.shuffle(profs_disponiveis_tcc)
    min_alunos_grupo, max_alunos_grupo = 2, 4

    for i in range(QTD_GRUPOS_TCC):
        if not profs_disponiveis_tcc:
            print("   AVISO: Não há mais professores disponíveis para TCC.")
            break
        if len(alunos_disponiveis_tcc) < min_alunos_grupo:
            print(f"   AVISO: Não há alunos suficientes ({len(alunos_disponiveis_tcc)}) para formar mais grupos (mínimo {min_alunos_grupo}).")
            break

        orientador_id = profs_disponiveis_tcc.pop(random.randrange(len(profs_disponiveis_tcc)))
        num_alunos_no_grupo = random.randint(min_alunos_grupo, min(max_alunos_grupo, len(alunos_disponiveis_tcc)))
        ids_alunos_grupo = [alunos_disponiveis_tcc.pop() for _ in range(num_alunos_no_grupo)]

        grupo_obj = {
            "_id": i + 1,
            "orientador_id": orientador_id,
            "alunos_ids": ids_alunos_grupo,
            "semestre": gerar_semestre(datetime.datetime.now().year - 1)
        }
        grupos_tcc.append(grupo_obj)

    print(f"   -> {len(grupos_tcc)} grupos de TCC gerados.")

    print("\nSalvando arquivos JSON...")
    diretorio_saida = "data"
    os.makedirs(diretorio_saida, exist_ok=True)

    dados_para_salvar = [
        (departamentos, "departamentos.json"),
        (cursos, "cursos.json"),
        (disciplinas_lista, "disciplinas.json"),
        (professores, "professores.json"),
        (alunos, "alunos.json"),
        (grupos_tcc, "grupos_tcc.json")
    ]

    for dados, nome_arquivo_base in dados_para_salvar:
        gravar_json(dados, os.path.join(diretorio_saida, nome_arquivo_base))

    print("\n--- Geração Concluída ---")

if __name__ == "__main__":
    gerar_dados_academicos()
