import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)

# Features: [qtd_links, tem_anexo, urgencia_no_assunto, dominio_suspeito, erros_gramaticais]
X = np.array([
    [1, 0, 0, 0, 0], [0, 0, 0, 0, 1], [2, 1, 0, 0, 0], [1, 0, 0, 0, 0],
    [8, 1, 1, 1, 5], [12, 0, 1, 1, 8], [6, 1, 1, 1, 3], [10, 1, 1, 1, 6],
    [0, 0, 0, 0, 0], [15, 1, 1, 1, 9],
])
y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 0, 1])   # 0=legítimo, 1=phishing

# stratify=y garante que treino e teste tenham as duas classes
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_tr, y_tr)
pred = rf.predict(X_te)

print("Matriz:", confusion_matrix(y_te, pred, labels=[0, 1]).tolist())
print(f"Acurácia: {accuracy_score(y_te, pred):.2f} | "
      f"Precisão: {precision_score(y_te, pred, zero_division=0):.2f} | "
      f"Recall: {recall_score(y_te, pred, zero_division=0):.2f} | "
      f"F1: {f1_score(y_te, pred, zero_division=0):.2f}")

novo = np.array([[11, 1, 1, 1, 7]])
print("Caso novo:", "Phishing" if rf.predict(novo)[0] == 1 else "Legítimo",
      "| P(phishing) =", rf.predict_proba(novo)[0][1])
