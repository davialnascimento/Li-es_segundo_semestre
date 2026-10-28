import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

acessos = np.array([
    [9, 1, 200], [10, 1, 500], [14, 2, 300], [11, 1, 250], [16, 1, 400],
    [3, 40, 900000],   # madrugada, muitas tentativas, download enorme
    [10, 1, 350], [15, 2, 280],
    [2, 55, 800000],
])

X = StandardScaler().fit_transform(acessos)   # coloca as 3 features na mesma escala
modelo = IsolationForest(n_estimators=200, contamination=0.2, random_state=42)
pred = modelo.fit_predict(X)          # -1 = anomalia, 1 = normal
scores = modelo.score_samples(X)      # quanto menor, mais anômalo

print("Anomalias:")
for i in np.where(pred == -1)[0]:
    h, t, b = acessos[i]
    print(f"  amostra {i}: hora={h}h tentativas={t} bytes={b} score={scores[i]:.3f}")
print("Normais:", np.where(pred == 1)[0].tolist())
