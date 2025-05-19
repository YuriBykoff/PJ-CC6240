from pymongo import MongoClient
import json
import os

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "MongoDB"
JSON_FILES = ["departamentos.json", "cursos.json", "disciplinas.json", "alunos.json", "professores.json", "grupos_tcc.json"] # etc
DATA_DIR = "data"

try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    print("Conectado.")

    for filename in JSON_FILES:
        collection_name = filename.split('.')[0]
        collection = db[collection_name]
        file_path = os.path.join(DATA_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                result = collection.insert_many(data)
                print(f"Inseriu {len(result.inserted_ids)} em {collection_name}")
            else:
                print(f"Arquivo {filename} vazio ou formato inválido.")
        except FileNotFoundError:
            print(f"Erro: Arquivo {file_path} não encontrado.")
        except Exception as e:
            print(f"Erro processando {filename}: {e}") # Erro genérico

    client.close()
    print("Fechado.")

except Exception as e:
    print(f"Erro geral: {e}")