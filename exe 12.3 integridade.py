
import joblib
import hashlib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

# 1. Criar um dataset de exemplo
X, y = make_classification(
    n_samples=200,
    n_features=4,
    n_informative=3,
    n_redundant=0,
    random_state=42
)

# 2. Treinar o melhor modelo
modelo = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
modelo.fit(X, y)

# 3. Salvar o modelo
arquivo = "modelo_seguranca.pkl"
joblib.dump(modelo, arquivo)
print(f"Modelo salvo: {arquivo}")

# 4. Calcular o hash SHA-256 do arquivo
def calcular_hash(caminho):
    sha256 = hashlib.sha256()

    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(4096), b""):
            sha256.update(bloco)

    return sha256.hexdigest()

hash_original = calcular_hash(arquivo)
print(f"Hash SHA-256: {hash_original}")

# 5. Recarregar e verificar a integridade
print("Recarregando e verificando integridade...")

modelo_carregado = joblib.load(arquivo)
hash_atual = calcular_hash(arquivo)

if hash_original == hash_atual:
    print("Hash confere: modelo íntegro.")
    previsao = modelo_carregado.predict([X[0]])
    print(f"Previsão de teste: {previsao}")
else:
    print("ALERTA: arquivo do modelo foi modificado!")
