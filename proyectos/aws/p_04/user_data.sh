#!/bin/bash
# Verificar instalación de AWS CLI
echo "=== Verificando instalación de AWS CLI ==="
which aws
aws --version

# 2. Configurar Credenciales AWS CLI (Obligatorio para autenticar la descarga)
# Reemplaza TUS_CLAVES y tu-region
sudo aws configure set aws_access_key_id YOUR_AWS_ACCESS_KEY_ID
sudo aws configure set aws_secret_access_key YOUR_AWS_SECRET_ACCESS_KEY
sudo aws configure set aws_session_token YOUR_AWS_SESSION_TOKEN
sudo aws configure set default.region us-east-1
sudo aws configure set default.output json

sudo mkdir -p /home/ubuntu/.aws
sudo cp /root/.aws/credentials /home/ubuntu/.aws/credentials
sudo chown ubuntu:ubuntu /home/ubuntu/.aws/credentials
sudo chmod 600 /home/ubuntu/.aws/credentials


# 3. Descargar Artefactos de S3 (Se accede por el VPC Endpoint)
mkdir -p /home/ubuntu/app
cd /home/ubuntu/app

# Usamos SUDO HOME=/home/ubuntu para que la CLI encuentre las credenciales
sudo HOME=/home/ubuntu aws s3 cp s3://p4-buquet/backend/modelv1prod.py .
sudo HOME=/home/ubuntu aws s3 cp s3://p4-buquet/backend/modelv2canary.py .
sudo HOME=/home/ubuntu aws s3 cp s3://p4-buquet/backend/modelo.pkl .


# 4. Asignar propiedad a los archivos
sudo chown -R ubuntu:ubuntu /home/ubuntu/app

# 5. Mostrar la lista de los archivos descargados
ls -lh /home/ubuntu/app/


# 6. Ejecución (Requiere conexión SSH posterior del estudiante)
# Los estudiantes deben conectarse por SSH y ejecutar el modelo correcto:
# Para V1: python3 model_v1_prod.py > /dev/null 2>&1 &
# Para V2: python3 model_v2_canary.py > /dev/null 2>&1 &