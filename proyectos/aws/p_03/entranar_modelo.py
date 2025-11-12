import joblib
import numpy as np
from sklearn.linear_model import LinearRegression


# Crear un conjunto de datos de ejemplo
x_train = np.array([[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]])
y_train = np.array([2.1, 4.2, 5.8, 8.1, 10.3, 11.9, 14.2, 16.0, 18.2, 20.5])


# Entrenar el modelo y guardarlo
model = LinearRegression()
model.fit(x_train, y_train)
joblib.dump(model, 'modelo.pkl')


print("Modelo entrenado y guardado como 'modelo.pkl'.")