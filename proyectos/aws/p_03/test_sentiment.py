#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para el análisis de sentimientos sin servidor web
"""

import re
import bz2
import _pickle as cPickle
import os

# Expresiones regulares para limpieza de texto
REPLACE_BY_SPACE_RE = re.compile(r'[/(){}\[\]\|@,;]')
BAD_SYMBOLS_RE = re.compile(r'[^\w\s]')

def decompress_pickle(file):
    data = bz2.BZ2File(file, 'rb')
    data = cPickle.load(data)
    return data

class SentimentAnalysisSpanish:
    def __init__(self):
        try:
            # Rutas a los modelos comprimidos
            vectorizer_path = 'saved_model/ngram_vectorized_compressed.pbz2'
            classifier_path = 'saved_model/classifier_naive_bayes_compressed.pbz2'
            
            # Verificar que los archivos existen
            if not os.path.exists(vectorizer_path):
                raise FileNotFoundError(f"No se encontró el archivo: {vectorizer_path}")
            if not os.path.exists(classifier_path):
                raise FileNotFoundError(f"No se encontró el archivo: {classifier_path}")
            
            print("Cargando vectorizador desde:", vectorizer_path)
            self.vectorizer = decompress_pickle(vectorizer_path)
            print("Vectorizador cargado exitosamente.")
            
            print("Cargando clasificador desde:", classifier_path)
            self.classifier = decompress_pickle(classifier_path)
            print("Clasificador cargado exitosamente.")
            
        except Exception as e:
            print(f"Error al inicializar SentimentAnalysisSpanish: {e}")
            raise

    def clean_text(self, text):
        """Limpia el texto eliminando caracteres especiales y normalizando"""
        text = text.lower()
        text = REPLACE_BY_SPACE_RE.sub(' ', text)
        text = BAD_SYMBOLS_RE.sub('', text)
        return text

    def sentiment(self, text: str):
        """
        Devuelve la puntuación de sentimiento de un texto.
        Valores cercanos a 1 = sentimiento positivo
        Valores cercanos a 0 = sentimiento negativo
        """
        try:
            # Limpiar el texto
            cleaned_text = self.clean_text(text)
            
            # Vectorizar el texto
            vals = self.vectorizer.transform([cleaned_text])
            
            # Obtener la probabilidad de sentimiento positivo
            sentiment_score = self.classifier.predict_proba(vals)[0][1]
            
            return sentiment_score
            
        except Exception as e:
            print(f"Error en análisis de sentimiento: {e}")
            raise

def test_sentiment_analysis():
    """Función de prueba del análisis de sentimientos"""
    
    print("=== INICIANDO PRUEBAS DE ANÁLISIS DE SENTIMIENTOS ===\n")
    
    try:
        # Inicializar el analizador
        analyzer = SentimentAnalysisSpanish()
        print("\n=== ANALIZADOR INICIALIZADO CORRECTAMENTE ===\n")
        
        # Frases de prueba
        test_phrases = [
            "Me encanta este día tan hermoso",
            "Qué día más horrible y terrible",
            "El producto es excelente, lo recomiendo mucho",
            "El servicio fue pésimo, no vuelvo nunca",
            "Está bien, nada especial",
            "¡Fantástico! Me ha encantado la experiencia"
        ]
        
        print("=== RESULTADOS DE LAS PRUEBAS ===\n")
        
        for phrase in test_phrases:
            sentiment_score = analyzer.sentiment(phrase)
            is_positive = sentiment_score > 0.5
            sentiment_label = "POSITIVO" if is_positive else "NEGATIVO"
            
            print(f"Texto: '{phrase}'")
            print(f"Puntuación: {sentiment_score:.3f}")
            print(f"Sentimiento: {sentiment_label}")
            print("-" * 60)
        
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN LAS PRUEBAS: {e}")
        return False

if __name__ == "__main__":
    success = test_sentiment_analysis()
    if success:
        print("\n🎉 El modelo de análisis de sentimientos funciona correctamente!")
    else:
        print("\n⚠️  Hay problemas con el modelo de análisis de sentimientos.")