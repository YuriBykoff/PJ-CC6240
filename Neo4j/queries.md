# Como usar

1. Abra o Neo4j Browser
2. Cole uma Query:
3. Execute

### 1. Histórico escolar de um aluno 

```cql
MATCH (a:Aluno {id_aluno: 1})-[c:CURSOU]->(d:Disciplina)
RETURN d.codigo_disciplina AS codigo_disciplina, d.nome_disciplina AS nome_disciplina, c.semestre AS semestre, c.ano AS ano, c.nota_final AS nota_final
ORDER BY c.ano, c.semestre;
```

### 2. Histórico de disciplinas ministradas por um professor 

```cql
MATCH (p:Professor {id_professor: 1})-[m:MINISTROU]->(d:Disciplina)
RETURN d.codigo_disciplina AS codigo_disciplina, d.nome_disciplina AS nome_disciplina, m.semestre AS semestre, m.ano AS ano
ORDER BY m.ano, m.semestre;
```

### 3. Listar alunos formados em um determinado semestre/ano 

* É possivel que nenhum aluno tenha satisfeito todas as condições para ser considerado formado. Caso ocorra a consulta vai vir vazia.

Caso occora, coloque os dados manualmente.

```cql
MATCH (a:Aluno {id_aluno: 1}), (mc:MatrizCurricular {id_matriz: 1})
CREATE (a)-[:FORMADO_EM {semestre_formacao: 2, ano_formacao: 2023}]->(mc);
```

```cql
MATCH (a:Aluno)-[f:FORMADO_EM]->(mc:MatrizCurricular)
WHERE f.ano_formacao = 2023 AND f.semestre_formacao = 2
RETURN a.id_aluno AS id_aluno, a.nome_aluno AS nome_aluno, mc.nome_matriz AS matriz_curricular, f.ano_formacao AS ano_formacao, f.semestre_formacao AS semestre_formacao;
```

### 4. Listar professores chefes de departamento e o nome do departamento

```cql
MATCH (p:Professor)-[:CHEFE_DE]->(d:Departamento)
RETURN p.id_professor AS id_professor, p.nome_professor AS nome_professor, d.id_departamento AS id_departamento, d.nome_departamento AS nome_departamento
ORDER BY d.nome_departamento;
```

### 5. Membros e orientador de um grupo de TCC 

```cql
MATCH (tcc:TCC {id_tcc: 1})
OPTIONAL MATCH (aluno:Aluno)-[:PARTICIPA_DE]->(tcc)
OPTIONAL MATCH (orientador:Professor)-[:ORIENTA]->(tcc)
RETURN tcc.id_tcc AS id_tcc, tcc.titulo_tcc AS titulo_tcc, collect(DISTINCT aluno.nome_aluno) AS membros_alunos, orientador.nome_professor AS nome_orientador;
```
