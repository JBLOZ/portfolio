#!/bin/bash
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 42fa237a0948d1ceb29232ede3f74fd9ab574339

echo "--- Iniciando script de User Data para el Back-End (Análisis de Sentimientos) ---"

# 1. Actualizar sistema e instalar Python y pip
echo "Actualizando sistema e instalando Python y pip..."
yum update -y
yum install python3-pip python3-devel gcc -y

# Verificar instalación de Python
echo "Verificando instalación de Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python3 no está instalado correctamente"
    exit 1
fi

# Verificar instalación de pip
echo "Verificando instalación de pip..."
python3 -m pip --version
if [ $? -ne 0 ]; then
    echo "ERROR: pip no está instalado correctamente"
    exit 1
fi

echo "Python y pip instalados y verificados."

# 2. Instalar dependencias de Python necesarias para la aplicación
echo "Instalando dependencias de Python (Flask y librerías para análisis de sentimientos)..."

# Actualizar pip primero
echo "Actualizando pip..."
python3 -m pip install --upgrade pip

# Instalar dependencias una por una para mejor control de errores
echo "Instalando Flask..."
python3 -m pip install flask
if [ $? -ne 0 ]; then
    echo "Intentando instalar Flask con método alternativo..."
    yum install python3-flask -y
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo instalar Flask"
        exit 1
    fi
fi

echo "Instalando scikit-learn versión específica..."
python3 -m pip install scikit-learn==0.23.2
if [ $? -ne 0 ]; then
    echo "ADVERTENCIA: No se pudo instalar scikit-learn 0.23.2, intentando versión más reciente..."
    python3 -m pip install scikit-learn
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo instalar scikit-learn"
        exit 1
    fi
fi

echo "Instalando numpy y pandas..."
python3 -m pip install numpy pandas
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo instalar numpy/pandas"
    exit 1
fi

echo "Dependencias de Python instaladas exitosamente."

# 3. Crear directorios para la aplicación
echo "Creando directorios de la aplicación en /app..."
mkdir -p /app
mkdir -p /app/saved_model
cd /app
echo "Directorios creados y nos hemos movido a /app."

# 4. Descargar los archivos del back-end desde S3 usando wget
echo "Descargando archivos del back-end desde S3..."
wget -O app_backend.py https://baqueet-p3.s3.us-east-1.amazonaws.com/back-end/app_backend.py
wget -O saved_model/classifier_naive_bayes_compressed.pbz2 https://baqueet-p3.s3.us-east-1.amazonaws.com/back-end/saved_model/classifier_naive_bayes_compressed.pbz2
wget -O saved_model/ngram_vectorized_compressed.pbz2 https://baqueet-p3.s3.us-east-1.amazonaws.com/back-end/saved_model/ngram_vectorized_compressed.pbz2

# 5. Verificar que los archivos existen antes de continuar
echo "Verificando archivos descargados..."
if [ ! -f "app_backend.py" ]; then
    echo "ERROR: app_backend.py no se encontró después de la descarga."
    exit 1
fi

if [ ! -f "saved_model/classifier_naive_bayes_compressed.pbz2" ]; then
    echo "ERROR: classifier_naive_bayes_compressed.pbz2 no se encontró después de la descarga."
    exit 1
fi

if [ ! -f "saved_model/ngram_vectorized_compressed.pbz2" ]; then
    echo "ERROR: ngram_vectorized_compressed.pbz2 no se encontró después de la descarga."
    exit 1
fi

echo "Todos los archivos del modelo de análisis de sentimientos descargados correctamente."

# 6. Mostrar estructura de archivos para verificación
echo "Estructura de archivos en /app:"
ls -la
echo "Archivos en saved_model:"
ls -la saved_model/

# 7. Probar que Python puede importar las dependencias
echo "Verificando dependencias Python..."

echo "Verificando Flask..."
python3 -c "import flask; print('Flask OK - versión:', flask.__version__)" 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Flask no está disponible"
    exit 1
fi

echo "Verificando sklearn..."
python3 -c "import sklearn; print('sklearn OK - versión:', sklearn.__version__)" 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: sklearn no está disponible"
    exit 1
fi

echo "Verificando numpy..."
python3 -c "import numpy; print('numpy OK - versión:', numpy.__version__)" 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: numpy no está disponible"
    exit 1
fi

echo "Verificando pandas..."
python3 -c "import pandas; print('pandas OK - versión:', pandas.__version__)" 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: pandas no está disponible"
    exit 1
fi

echo "Todas las dependencias verificadas correctamente."

# 8. Test rápido del modelo de análisis de sentimientos
echo "=== PROBANDO EL MODELO DE ANÁLISIS DE SENTIMIENTOS ==="
python3 -c "
import sys
sys.path.append('/app')
print('Importando librerías...')
import warnings
warnings.filterwarnings('ignore')
import re
import bz2
import _pickle as cPickle
import os

print('Cargando modelo...')
def decompress_pickle(file):
    data = bz2.BZ2File(file, 'rb')
    data = cPickle.load(data)
    return data

try:
    vectorizer = decompress_pickle('saved_model/ngram_vectorized_compressed.pbz2')
    print('✅ Vectorizador cargado correctamente')
    
    classifier = decompress_pickle('saved_model/classifier_naive_bayes_compressed.pbz2')
    print('✅ Clasificador cargado correctamente')
    
    # Prueba rápida
    text = 'me gusta mucho'
    vals = vectorizer.transform([text])
    result = classifier.predict_proba(vals)[0][1]
    print(f'✅ Prueba exitosa: \"{text}\" -> {result:.3f}')
    print('🎉 MODELO FUNCIONANDO CORRECTAMENTE')
    
except Exception as e:
    print(f'❌ ERROR EN EL MODELO: {e}')
    sys.exit(1)
" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ ERROR: El modelo no funciona correctamente"
    exit 1
fi

# 9. Ejecutar el servidor de Flask con logs directos en cloud-init
echo "=== INICIANDO SERVIDOR DE ANÁLISIS DE SENTIMIENTOS ==="

# Ejecutar servidor en background pero mostrar los primeros logs
echo "Iniciando servidor Flask..."
python3 app_backend.py 2>&1 &
SERVER_PID=$!

echo "Servidor iniciado con PID: $SERVER_PID"

# Esperar un poco para que se inicie
sleep 3

# Verificar que sigue ejecutándose
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ SERVIDOR EJECUTÁNDOSE CORRECTAMENTE"
    echo "🌐 Puerto: 5000"
    echo "📍 IP privada de la instancia: $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)"
    echo "🧪 Para probar: curl http://IP_PRIVADA:5000/predict -H 'Content-Type: application/json' -d '{\"text\":\"hola mundo\"}'"
else
    echo "❌ ERROR: El servidor se detuvo"
    
    # Intentar ejecutar en foreground para ver el error
    echo "=== EJECUTANDO EN FOREGROUND PARA VER ERRORES ==="
    timeout 10s python3 app_backend.py 2>&1
    exit 1
fi

<<<<<<< HEAD
echo "--- Script de User Data del Back-End finalizado con éxito. ---"
=======
echo "--- Script de User Data del Back-End finalizado con éxito. ---"
=======
# Redirigir toda la salida a un archivo de log para una depuración sencilla
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

# Detener la ejecución inmediatamente si un comando falla
set -e

echo "--- Iniciando script de User Data ---"

# 1. Actualizar sistema e instalar las dependencias de Python
echo "Actualizando el sistema e instalando dependencias..."
yum update -y
yum install python3-pip -y
pip3 install flask joblib scikit-learn
# Nota: Ya no es necesario instalar boto3 para esta aplicación
echo "Dependencias instaladas correctamente."

# 2. Crear el directorio de la aplicación
echo "Creando el directorio de la aplicación en /app..."
mkdir -p /app
cd /app
echo "Directorio creado y nos hemos movido a /app."

# 3. Descargar el script de la aplicación y el modelo desde S3 usando wget
echo "Descargando archivos desde S3..."
wget -O app_backend.py https://baqueet-p3.s3.us-east-1.amazonaws.com/back-end/app_backend.py
wget -O modelo.pkl https://baqueet-p3.s3.us-east-1.amazonaws.com/back-end/modelo.pkl
echo "Archivos descargados."

# 4. Verificar que ambos archivos existen antes de continuar
if [ ! -f "app_backend.py" ] || [ ! -f "modelo.pkl" ]; then
    echo "ERROR: Uno o ambos archivos (app_backend.py, modelo.pkl) no se encontraron después de la descarga."
    exit 1
fi

echo "Ambos archivos verificados. Iniciando el servidor de Flask..."
# 5. Ejecutar el servidor de Flask en segundo plano para que siga corriendo
nohup python3 app_backend.py &

echo "--- Script de User Data finalizado con éxito. El servidor debería estar en ejecución. ---"
>>>>>>> 3b028249 (modelo)
>>>>>>> 42fa237a0948d1ceb29232ede3f74fd9ab574339
