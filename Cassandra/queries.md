```cql
-- Query 1: Histórico escolar de um aluno específico (ex: id_aluno = 1).
-- Retorna o nome do aluno e o mapa de disciplinas concluídas (nome_disciplina -> detalhes como ano, semestre, nota).
SELECT nome, disciplinas_concluidas FROM alunos WHERE id_aluno = 1;
```

```cql
-- Query 2: Histórico de disciplinas ministradas por um professor específico (ex: id_professor = 1).
-- Retorna o nome do professor e o mapa de disciplinas ministradas (nome_disciplina -> detalhes como semestre, ano).
SELECT nome, disciplinas_ministradas FROM professor WHERE id_professor = 1;
```

```cql
-- Query 3: Listar alunos (ID e nome) que se formaram em um determinado semestre de um ano (ex: ano = 2023, semestre = 1).
SELECT id_aluno, nome FROM alunos_formado WHERE ano = 2023 AND semestre = 1;
```

```cql
-- Query 4: Listar os IDs dos professores que são chefes de departamento, junto com o nome do departamento que chefiam.
SELECT id_chefe_departamento, nome AS nome_departamento FROM departamento;
```

```cql
-- Query 5: Para um grupo de TCC específico (ex: id_grupo = 1), listar o ID do professor orientador e os IDs dos alunos membros.
SELECT id_professor, membros FROM grupo_proj WHERE id_grupo = 1;
```
