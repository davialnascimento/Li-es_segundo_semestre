import numpy as np

y_verdadeiro = np.array([0,0,0,0,0,0,0,0,1,1])   
y_previsto   = np.array([0,0,0,0,0,0,0,0,0,1])   

# Componentes da matriz de confusão
tn = np.sum((y_verdadeiro == 0) & (y_previsto == 0))
fp = np.sum((y_verdadeiro == 0) & (y_previsto == 1))
fn = np.sum((y_verdadeiro == 1) & (y_previsto == 0))
tp = np.sum((y_verdadeiro == 1) & (y_previsto == 1))

cm = np.array([[tn, fp],
               [fn, tp]])

# Métricas (com proteção contra divisão por zero)
def div(a, b):
    return a / b if b > 0 else 0.0

precisao = div(tp, tp + fp)
recall   = div(tp, tp + fn)
f1       = div(2 * precisao * recall, precisao + recall)
acuracia = np.mean(y_verdadeiro == y_previsto)

print("Matriz:", cm.tolist())
print(f"TN={tn} FP={fp} FN={fn} TP={tp}")
print(f"Precisão: {precisao:.2f} | Recall: {recall:.2f} | "
      f"F1: {f1:.2f} | Acurácia: {acuracia:.2f}")
