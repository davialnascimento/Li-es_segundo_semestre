from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
import numpy as np

pipeline = Pipeline([
    ("scaler", StandardScaler()),                             
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42)),
])



X = np.array([
    [500,80,0.1],[1200,80,0.5],[64,22,0.02],[64000,4444,10.0],[45000,8080,15.0],
    [60000,31337,20.0],[800,443,0.3],[300,53,0.05],[55000,9999,18.0],[200,25,0.2],
    [700,443,0.2],[52000,6666,17.0],[150,53,0.03],[58000,4444,19.0],[900,80,0.4],
])
y = np.array([0,0,0,1,1,1,0,0,1,0,0,1,0,1,0])


cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipeline, X, y, cv=5)
print(f"Acurácia: {scores.mean():.3f} (+/- {scores.std():.3f})")


