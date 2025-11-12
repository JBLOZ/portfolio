import pandas as pd
import numpy as np
import os
import warnings
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import KernelDensity  # Para Parzen y k-NN density
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from scipy.stats import multivariate_normal  # Para MLE full Gaussian
from sklearn.model_selection import cross_val_score


# Silenciar warnings
os.environ['LOKY_MAX_CPU_COUNT'] = '4'
warnings.filterwarnings('ignore', category=UserWarning, module='joblib')

# Clases del Zoo dataset (1-7 -> labels para report)
class_names = ['mammal', 'bird', 'reptile', 'fish', 'amphibian', 'invertebrate', 'insect']

print("=" * 80)
print("ANÁLISIS DEL DATASET ZOO (Multiclass Classification)")
print("=" * 80)

# Cargar datos: zoo.data (col 0: animal name (ignorar), col 1-17: features binarias, col 18: class 1-7)
df = pd.read_csv('./zoo/zoo.data', header=None)
df.columns = ['animal'] + [f'feature_{i}' for i in range(1, 17)] + ['class']
X = df.iloc[:, 1:-1]  # Features 1-17 (binarias 0/1)
y = df.iloc[:, -1].values - 1  # Clase 0-6 para sklearn

print("Información del dataset:")
print(f"Forma: {X.shape} (instancias x features)")
print(f"Clases: {len(np.unique(y))} (multiclass: {class_names})")
print("\nDistribución de clases:")
unique, counts = np.unique(y, return_counts=True)
for i, (cls, count) in enumerate(zip(class_names, counts)):
    print(f"Clase {i+1} ({cls}): {count} muestras ({count/len(y)*100:.1f}%)")

# División: 80% train - 20% test, estratificada para multiclass
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTotal de muestras: {len(X)}")
print(f"Train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
print(f"Test: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")

print("\nDistribución en train:")
print(pd.Series(y_train).value_counts().sort_index())
print("\nDistribución en test:")
print(pd.Series(y_test).value_counts().sort_index())

# CV estratificado (5 folds) para train
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Función helper para evaluar modelo (pred en test + report)
def evaluate_model(model, X_test, y_test, model_name):
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1_mac = f1_score(y_test, preds, average='macro')
    print(f"\n--- Resultados en Test ({model_name}) ---")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1-macro: {f1_mac:.4f}")
    print("\nReporte de clasificación:")
    print(classification_report(y_test, preds, target_names=class_names))
    cm = confusion_matrix(y_test, preds)
    print("\nMatriz de confusión:")
    print(cm)
    return acc, f1_mac, cm

# 1. NAIVE BAYES GAUSSIANO (T2: asume independencia)
print("\n" + "=" * 80)
print("1. NAIVE BAYES GAUSSIANO")
print("=" * 80)

nb = GaussianNB()
nb.fit(X_train, y_train)
nb_acc, nb_f1, nb_cm = evaluate_model(nb, X_test, y_test, "Naive Bayes")

# CV score para NB (sin hypers)
nb_cv_scores = cross_val_score(nb, X_train, y_train, cv=skf, scoring='f1_macro')
print(f"\nCV F1-macro (mean ± std): {nb_cv_scores.mean():.4f} ± {nb_cv_scores.std():.4f}")

# 2. MLE MULTIVARIANTE FULL BAYESIAN (T2: covarianza completa por clase)
print("\n" + "=" * 80)
print("2. MLE MULTIVARIANTE (Full Bayesian Gaussian)")
print("=" * 80)

class FullGaussianBayes:
    def __init__(self):
        self.priors = None
        self.means = None
        self.covs = None
        self.classes = None
    
    def fit(self, X, y):
        self.classes = np.unique(y)
        self.priors = np.bincount(y) / len(y)
        self.means = np.array([X[y == c].mean(axis=0) for c in self.classes])
        self.covs = np.array([np.cov(X[y == c].T) + 1e-6 * np.eye(X.shape[1]) for c in self.classes])  # Regularización
        return self
    
    def predict(self, X):
        n_classes, n_samples, _ = X.shape[0], *X.shape  # Error fix
        ll = np.zeros((n_samples, len(self.classes)))
        for i, c in enumerate(self.classes):
            ll[:, i] = multivariate_normal(mean=self.means[i], cov=self.covs[i]).logpdf(X)
        posteriors = np.exp(ll) * self.priors
        posteriors /= posteriors.sum(axis=1, keepdims=True)
        return np.argmax(posteriors, axis=1)

mle = FullGaussianBayes()
mle.fit(X_train.values, y_train)  # .values para np
mle_acc, mle_f1, mle_cm = evaluate_model(mle, X_test.values, y_test, "MLE Full")

# CV para MLE (custom, usa misma lógica)
def cv_full_bayes(X_train, y_train, cv):
    scores = []
    for train_idx, val_idx in cv.split(X_train, y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train[train_idx], y_train[val_idx]
        model = FullGaussianBayes()
        model.fit(X_tr.values, y_tr)
        preds = model.predict(X_val.values)
        scores.append(f1_score(y_val, preds, average='macro'))
    return np.array(scores)

mle_cv_scores = cv_full_bayes(pd.DataFrame(X_train), y_train, skf)
print(f"\nCV F1-macro (mean ± std): {mle_cv_scores.mean():.4f} ± {mle_cv_scores.std():.4f}")

# 3. NO PARAMÉTRICOS: HISTOGRAMA (T4: Histogram approach)
print("\n" + "=" * 80)
print("3. DENSIDAD NO PARAMÉTRICA - HISTOGRAMA")
print("=" * 80)

# Para binario (0/1), histogram es conteo por clase; bins=2 por dim, pero multivariado curse of dim -> usa univariate product approx
class HistogramBayes:
    def __init__(self, bins=2):
        self.bins = bins
        self.priors = None
        self.hist_per_class = None  # Dict de histograms por feature por class
        self.edges = None
    
    def fit(self, X, y):
        self.classes = np.unique(y)
        self.priors = np.bincount(y) / len(y)
        self.hist_per_class = {}
        for c in self.classes:
            X_c = X[y == c]
            hists = []
            edges_list = []
            for feat in range(X.shape[1]):
                hist, edges = np.histogram(X_c.iloc[:, feat], bins=self.bins, density=True)
                hists.append(hist)
                edges_list.append(edges)
            self.hist_per_class[c] = (np.array(hists), edges_list)
        self.edges = edges_list[0] if edges_list else None  # Same for all
        return self
    
    def _density_hist(self, x, c):
        hists, edges = self.hist_per_class[c]
        dens = 1.0
        for i, feat_val in enumerate(x):
            bin_idx = np.digitize(feat_val, edges[i]) - 1
            if 0 <= bin_idx < len(hists[i]):
                dens *= hists[i][bin_idx]
            else:
                dens *= 0
        return dens
    
    def predict(self, X):
        n_samples = len(X)
        preds = np.zeros(n_samples, dtype=int)
        for i in range(n_samples):
            posteriors = []
            for c in self.classes:
                dens = self._density_hist(X.iloc[i], c)
                post = self.priors[c] * dens
                posteriors.append(post)
            preds[i] = self.classes[np.argmax(posteriors)]
        return preds

hist_bayes = HistogramBayes(bins=2)
hist_bayes.fit(pd.DataFrame(X_train), y_train)
hist_acc, hist_f1, hist_cm = evaluate_model(hist_bayes, pd.DataFrame(X_test), y_test, "Histogram Bayes")

# CV para Histogram (custom)
def cv_hist_bayes(X_train, y_train, cv):
    scores = []
    for train_idx, val_idx in cv.split(X_train, y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train[train_idx], y_train[val_idx]
        model = HistogramBayes()
        model.fit(X_tr, y_tr)
        preds = model.predict(X_val)
        scores.append(f1_score(y_val, preds, average='macro'))
    return np.array(scores)

hist_cv_scores = cv_hist_bayes(pd.DataFrame(X_train), y_train, skf)
print(f"\nCV F1-macro (mean ± std): {hist_cv_scores.mean():.4f} ± {hist_cv_scores.std():.4f}")

# 4. PARZEN WINDOWS (T4: Parzen windows)
print("\n" + "=" * 80)
print("4. DENSIDAD NO PARAMÉTRICA - PARZEN WINDOWS")
print("=" * 80)

# Usa KernelDensity por clase, luego Bayes
class ParzenBayes:
    def __init__(self, bandwidth=0.5):
        self.bandwidth = bandwidth
        self.priors = None
        self.kdes = None  # Dict de KDE por class
        self.classes = None
    
    def fit(self, X, y):
        self.classes = np.unique(y)
        self.priors = np.bincount(y) / len(y)
        self.kdes = {}
        for c in self.classes:
            X_c = X[y == c].values.reshape(-1, X.shape[1])
            kde = KernelDensity(kernel='gaussian', bandwidth=self.bandwidth).fit(X_c)
            self.kdes[c] = kde
        return self
    
    def predict(self, X):
        X_val = X.values.reshape(-1, X.shape[1])
        n_samples = len(X_val)
        ll = np.zeros((n_samples, len(self.classes)))
        for i, c in enumerate(self.classes):
            ll[:, i] = np.exp(self.kdes[c].score_samples(X_val))
        posteriors = ll * self.priors
        posteriors /= posteriors.sum(axis=1, keepdims=True) + 1e-10
        return np.argmax(posteriors, axis=1)

# GridSearch para bandwidth (h)
print("\n--- Búsqueda de hiperparámetros (en train) ---")
params_parzen = {'bandwidth': [0.1, 0.5, 1.0, 1.5, 2.0]}
# Custom GridSearch simulado con loop (ya que class no es sklearn estimator estándar)
best_h = None
best_cv_score = -np.inf
for h in params_parzen['bandwidth']:
    model_temp = ParzenBayes(bandwidth=h)
    cv_scores_temp = []
    for train_idx, val_idx in skf.split(X_train, y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train[train_idx], y_train[val_idx]
        model_temp.fit(X_tr, y_tr)
        preds_temp = model_temp.predict(X_val)
        cv_scores_temp.append(f1_score(y_val, preds_temp, average='macro'))
    mean_score = np.mean(cv_scores_temp)
    if mean_score > best_cv_score:
        best_cv_score = mean_score
        best_h = h
print(f"\nMejor bandwidth h: {best_h}")
print(f"Mejor F1-macro CV (train): {best_cv_score:.4f}")

# Entrenar con best h y evaluar
parzen_bayes = ParzenBayes(bandwidth=best_h)
parzen_bayes.fit(pd.DataFrame(X_train), y_train)
parzen_acc, parzen_f1, parzen_cm = evaluate_model(parzen_bayes, pd.DataFrame(X_test), y_test, "Parzen Bayes")

# 5. k-NN DENSITY ESTIMATOR (T4: kn-Nearest Neighbor estimator) - Similar a Parzen con k
print("\n" + "=" * 80)
print("5. DENSIDAD NO PARAMÉTRICA - k-NN ESTIMATOR")
print("=" * 80)

# Usa KernelDensity con kd_tree (aprox k-NN), bandwidth = 1/sqrt(k) approx
class KNNDensityBayes:
    def __init__(self, k=5):
        self.k = k
        self.priors = None
        self.kdes = None
        self.classes = None
    
    def fit(self, X, y):
        self.classes = np.unique(y)
        self.priors = np.bincount(y) / len(y)
        self.kdes = {}
        for c in self.classes:
            X_c = X[y == c].values.reshape(-1, X.shape[1])
            bandwidth = 1.0 / np.sqrt(self.k / len(X_c)) if len(X_c) > 0 else 0.5
            kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth, algorithm='kd_tree').fit(X_c)
            self.kdes[c] = kde
        return self
    
    def predict(self, X):
        X_val = X.values.reshape(-1, X.shape[1])
        n_samples = len(X_val)
        ll = np.zeros((n_samples, len(self.classes)))
        for i, c in enumerate(self.classes):
            ll[:, i] = np.exp(self.kdes[c].score_samples(X_val))
        posteriors = ll * self.priors
        posteriors /= posteriors.sum(axis=1, keepdims=True) + 1e-10
        return np.argmax(posteriors, axis=1)

# GridSearch para k
print("\n--- Búsqueda de hiperparámetros (en train) ---")
params_knn_density = [3, 5, 7, 9, 11]
best_k_density = None
best_cv_score_density = -np.inf
for k in params_knn_density:
    model_temp = KNNDensityBayes(k=k)
    cv_scores_temp = []
    for train_idx, val_idx in skf.split(X_train, y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train[train_idx], y_train[val_idx]
        model_temp.fit(X_tr, y_tr)
        preds_temp = model_temp.predict(X_val)
        cv_scores_temp.append(f1_score(y_val, preds_temp, average='macro'))
    mean_score = np.mean(cv_scores_temp)
    if mean_score > best_cv_score_density:
        best_cv_score_density = mean_score
        best_k_density = k
print(f"\nMejor k: {best_k_density}")
print(f"Mejor F1-macro CV (train): {best_cv_score_density:.4f}")

knn_density_bayes = KNNDensityBayes(k=best_k_density)
knn_density_bayes.fit(pd.DataFrame(X_train), y_train)
knn_d_acc, knn_d_f1, knn_d_cm = evaluate_model(knn_density_bayes, pd.DataFrame(X_test), y_test, "k-NN Density Bayes")

# 6. K-NN RULE DIRECTO (T4: The Nearest Neighbor rule)
print("\n" + "=" * 80)
print("6. K-NEAREST NEIGHBORS RULE (Directo)")
print("=" * 80)

print("\n--- Búsqueda de hiperparámetros (en train) ---")
print("Buscando mejor k con CV 5-fold...")
params_knn = {'n_neighbors': [1, 3, 5, 7, 9, 11]}
grid_knn = GridSearchCV(
    KNeighborsClassifier(metric='euclidean'),
    params_knn,
    cv=skf,
    scoring='f1_macro',
    n_jobs=-1,
    verbose=0
)
grid_knn.fit(X_train, y_train)
print(f"\nMejor k: {grid_knn.best_params_['n_neighbors']}")
print(f"Mejor F1-macro CV (train): {grid_knn.best_score_:.4f}")

best_knn = grid_knn.best_estimator_
knn_acc, knn_f1, knn_cm = evaluate_model(best_knn, X_test, y_test, "k-NN Rule")

# COMPARACIÓN FINAL (Test: Accuracy y F1-macro)
print("\n" + "=" * 80)
print("COMPARACIÓN FINAL DE MODELOS (en Test)")
print("=" * 80)

results = {
    'Naive Bayes': (nb_acc, nb_f1),
    'MLE Full': (mle_acc, mle_f1),
    'Histogram Bayes': (hist_acc, hist_f1),
    'Parzen Bayes': (parzen_acc, parzen_f1),
    'k-NN Density Bayes': (knn_d_acc, knn_d_f1),
    f'k-NN Rule (k={grid_knn.best_params_["n_neighbors"]})': (knn_acc, knn_f1)
}

print(f"\n{'Modelo':<25} {'Accuracy':>10} {'F1-macro':>10}")
print("-" * 50)
for model, (acc, f1) in results.items():
    print(f"{model:<25} {acc:>10.4f} {f1:>10.4f}")
print("-" * 50)

# Mejor modelo por F1-macro (prioridad para multiclass)
best_model = max(results, key=lambda k: results[k][1])
print(f"\n✓ Mejor modelo (por F1-macro): {best_model} (F1: {results[best_model][1]:.4f})")

print("=" * 80)
print("Análisis completo. Usa estos resultados en tu memoria, refiriendo T2-T4 de las slides.")
