import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from botocore import UNSIGNED

def verificar_accesos_s3(bucket_name):
    """
    Verifica los permisos de acceso a las carpetas 'back-end/' y 'front-end/'
    en un bucket de S3.
    """
    # Cliente S3 estándar (intentará usar credenciales)
    # Ideal para ejecutar desde un entorno con credenciales (como una EC2 con un rol)
    s3_client_auth = boto3.client('s3')

    # Cliente S3 anónimo (sin firmar) para acceder a recursos públicos
    s3_client_public = boto3.client('s3', config=Config(signature_version=UNSIGNED))

    # 1. Verificar que NO se puede acceder a la carpeta 'back-end/'
    # Esta comprobación debe hacerse con un cliente autenticado, ya que la política
    # se basa en el origen de la petición (VPCe), no en si es pública.
    print("1. Verificando que el acceso a 'back-end/' está denegado (ejecutando localmente)...")
    try:
        # Usamos el cliente autenticado. Si no hay credenciales, fallará.
        # Si hay credenciales, AWS denegará el acceso por no estar en la VPCe.
        s3_client_auth.list_objects_v2(Bucket=bucket_name, Prefix='back-end/')
        print("   ERROR: Se ha podido listar la carpeta 'back-end/'. Los permisos no son correctos.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print("   ÉXITO: Acceso a 'back-end/' correctamente denegado (como se esperaba al no estar en la VPC).")
        else:
            print(f"   ERROR: Ha ocurrido un error inesperado al intentar acceder a 'back-end/': {e}")
    except Exception as e:
        # Capturamos el error de 'Unable to locate credentials' si se ejecuta localmente sin configurar AWS CLI.
        print(f"   INFO: No se pudo realizar la comprobación autenticada (probablemente por falta de credenciales locales): {e}")

    print("-" * 30)

    # 2. Verificar que se puede acceder a 'front-end/' y que contiene los archivos esperados
    # Usamos el cliente público (sin firmar) porque la política lo permite.
    print("2. Verificando el acceso a los archivos de 'front-end/' (acceso público)...")
    archivos_a_verificar = ['front-end/app_front.js', 'front-end/index.html']
    todos_accesibles = True

    for archivo_key in archivos_a_verificar:
        try:
            # Usamos el cliente público para esta comprobación
            s3_client_public.head_object(Bucket=bucket_name, Key=archivo_key)
            print(f"   ÉXITO: Se puede acceder al archivo '{archivo_key}'.")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"   ERROR: El archivo '{archivo_key}' no fue encontrado (404).")
            # Un error 403 (Forbidden) aquí significaría que el objeto no es realmente público.
            elif e.response['Error']['Code'] == '403':
                print(f"   ERROR: Acceso denegado (403) al archivo '{archivo_key}'. El objeto no es público.")
            else:
                print(f"   ERROR: No se pudo acceder al archivo '{archivo_key}'. Error: {e}")
            todos_accesibles = False
        except Exception as e:
            print(f"   ERROR: Ha ocurrido un error inesperado al verificar '{archivo_key}': {e}")
            todos_accesibles = False

    print("-" * 30)
    if todos_accesibles:
        print("Comprobación final de 'front-end/': ÉXITO. Todos los archivos esperados son accesibles públicamente.")
    else:
        print("Comprobación final de 'front-end/': FALLO. No todos los archivos esperados son accesibles.")


if __name__ == "__main__":
    # Nombre del bucket extraído de la ARN: arn:aws:s3:::baqueet-p3
    nombre_bucket = "baqueet-p3"
    verificar_accesos_s3(nombre_bucket)
