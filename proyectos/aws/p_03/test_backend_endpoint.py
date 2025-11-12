#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba HTTP para el backend de análisis de sentimientos
"""

import requests
import json
import time

def test_backend_endpoint():
    """Prueba el endpoint del backend"""
    
    print("=== PRUEBA DEL ENDPOINT DEL BACKEND ===\n")
    
    url = 'http://127.0.0.1:5000/predict'
    headers = {'Content-Type': 'application/json'}
    
    # Esperar un poco para que el servidor esté listo
    print("Esperando que el servidor esté listo...")
    time.sleep(3)
    
    test_cases = [
        {
            "text": "Me encanta este día tan hermoso",
            "expected": "positivo"
        },
        {
            "text": "Qué día más horrible y terrible", 
            "expected": "negativo"
        },
        {
            "text": "El producto es excelente, lo recomiendo mucho",
            "expected": "positivo"
        }
    ]
    
    print("Probando endpoint:", url)
    print("-" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n🧪 PRUEBA {i}:")
            print(f"Texto: '{test_case['text']}'")
            print(f"Esperado: {test_case['expected']}")
            
            # Hacer la petición
            response = requests.post(url, json={"text": test_case["text"]}, headers=headers, timeout=10)
            
            print(f"Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Respuesta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                # Verificar el formato de respuesta
                required_fields = ['sentiment', 'sentiment_score', 'sentiment_label']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"⚠️  Campos faltantes: {missing_fields}")
                else:
                    sentiment = result['sentiment']
                    sentiment_label = result['sentiment_label']
                    sentiment_score = result['sentiment_score']
                    
                    print(f"✅ Sentimiento: {sentiment} ({sentiment_label})")
                    print(f"✅ Puntuación: {sentiment_score:.3f}")
                    
                    # Verificar coherencia
                    expected_positive = test_case['expected'] == 'positivo'
                    actual_positive = sentiment == 1
                    
                    if expected_positive == actual_positive:
                        print("✅ Resultado esperado: CORRECTO")
                    else:
                        print("❌ Resultado esperado: INCORRECTO")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"❌ Contenido: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se pudo conectar con el servidor")
            print("   Verifica que el servidor esté ejecutándose en http://127.0.0.1:5000")
        except requests.exceptions.Timeout:
            print("❌ Error: Timeout en la conexión")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        print("-" * 60)
    
    print("\n=== PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    test_backend_endpoint()