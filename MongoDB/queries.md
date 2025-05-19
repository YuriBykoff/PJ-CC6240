### Queries MongoDB 

```javascript
// Query 1: Histórico escolar de um aluno específico (ex: aluno com _id = 1).
db.alunos.findOne(
    { "_id": 1 },
    { 
        "nome": 1,
        "historico.codigo": 1,
        "historico.nome": 1,
        "historico.semestre": 1,
        "historico.ano": 1,
        "historico.nota_final": 1,
        "_id": 0
    }
);
```

```javascript
// Query 2: Histórico de disciplinas ministradas por um professor específico (ex: professor com _id = 1),
db.professores.aggregate([
    {
        $match: { "_id": 1 } // ID do professor desejado
    },
    {
        $unwind: "$disciplinas_ministradas"
    },
    {
        $lookup: {
            from: "disciplinas",
            localField: "disciplinas_ministradas.disciplina_id",
            foreignField: "_id",
            as: "infoDisciplina"
        }
    },
    {
        $unwind: { path: "$infoDisciplina", preserveNullAndEmptyArrays: true }
    },
    {
        $project: {
            "_id": 0,
            "nomeProfessor": "$nome",
            "codigoDisciplina": "$infoDisciplina.codigo",
            "nomeDisciplina": "$infoDisciplina.nome",
            "semestreMinistrado": "$disciplinas_ministradas.semestre",
            "anoMinistrado": "$disciplinas_ministradas.ano"
        }
    }
]).pretty();
```

```javascript
// Query 3: Listar alunos que já se formaram (graduado = true)
db.alunos.find(
    { 
        "graduado": true, 
        "semestre_graduacao": "2024.1" // Semestre de graduação desejado
    },
    { "nome": 1, "curso_id": 1, "semestre_graduacao": 1, "_id": 0 }
).pretty();
```

```javascript
// Query 4: Listar todos os professores que são chefes de departamento (eh_chefe = true),
db.professores.aggregate([
    {
        $match: { "eh_chefe": true }
    },
    {
        $lookup: {
            from: "departamentos",
            localField: "departamento_id",
            foreignField: "_id",
            as: "departamentoInfo"
        }
    },
    {
        $unwind: { path: "$departamentoInfo", preserveNullAndEmptyArrays: true } // Garante que o professor apareça mesmo se o depto não for encontrado
    },
    {
        $project: {
            "_id": 0,
            "nomeProfessor": "$nome",
            "idDepartamentoChefiado": "$departamento_id",
            "nomeDepartamentoChefiado": "$departamentoInfo.nome"
        }
    }
]).pretty();
```

```javascript
// Query 5: Saber quais alunos (nomes) formaram um grupo de TCC específico (ex: grupo com _id = 1)
db.grupos_tcc.aggregate([
    {
        $match: { "_id": 1 } // ID do grupo de TCC desejado
    },
    {
        $lookup: {
            from: "professores",
            localField: "orientador_id",
            foreignField: "_id",
            as: "orientadorDetails"
        }
    },
    {
        $unwind: { path: "$orientadorDetails", preserveNullAndEmptyArrays: true }
    },
    {
        $lookup: {
            from: "alunos",
            localField: "alunos_ids",
            foreignField: "_id",
            as: "alunosDetails"
        }
    },
    {
        $project: {
            "_id": 0,
            "idGrupo": "$_id",
            "semestreGrupo": "$semestre",
            "nomeOrientador": "$orientadorDetails.nome",
            "nomesAlunosMembros": "$alunosDetails.nome"
        }
    }
]).pretty();
```
