
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV

# Utilize o dataset definido no exercício anterior:
# X = atributos
# y = classes

modelos = {
    "RandomForest": RandomForestClassifier(
        n_estimators=100,
        random_state=42
    ),
    "SVM": SVC(),
    "KNN": KNeighborsClassifier()
}

# Comparação dos algoritmos
resultados = {}

for nome, modelo in modelos.items():
    scores = cross_val_score(modelo, X, y, cv=5, scoring="accuracy")
    media = scores.mean()
    resultados[nome] = media

    print(f"{nome}: {media:.2f}")

# Identificar o vencedor
vencedor_nome = max(resultados, key=resultados.get)
print(f"\nVencedor: {vencedor_nome}")

# Otimizar o vencedor com GridSearchCV
parametros = {
    "RandomForest": {
        "n_estimators": [50, 100, 200],
        "max_depth": [None, 5, 10]
    },
    "SVM": {
        "C": [0.1, 1, 10],
        "kernel": ["linear", "rbf"],
        "gamma": ["scale", "auto"]
    },
    "KNN": {
        "n_neighbors": [3, 5, 7, 9],
        "weights": ["uniform", "distance"],
        "metric": ["euclidean", "manhattan"]
    }
}

grid = GridSearchCV(
    estimator=modelos[vencedor_nome],
    param_grid=parametros[vencedor_nome],
    cv=5,
    scoring="accuracy",
    n_jobs=-1
)

grid.fit(X, y)

print("Melhores parâmetros:", grid.best_params_)
print(f"Melhor acurácia: {grid.best_score_:.2f}")
