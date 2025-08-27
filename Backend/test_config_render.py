#!/usr/bin/env python3
"""
Script para probar la configuración de Render localmente
"""
import os
import sys

# Simular variables de entorno de Render
os.environ['PORT'] = '10000'
os.environ['FLASK_ENV'] = 'production'

print("🔍 SIMULANDO CONFIGURACIÓN DE RENDER")
print("=" * 50)
print(f"PORT: {os.getenv('PORT')}")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")

# Probar la lógica de importación del API Gateway
print("\n🔧 PROBANDO IMPORTACIÓN DE CONFIGURACIÓN:")
print("-" * 30)

if os.getenv('PORT') or os.getenv('FLASK_ENV') == 'production':
    print("✅ Condición de Render detectada")
    try:
        from config_production import production_config as config
        print("🚀 [GATEWAY] FORZANDO configuración de PRODUCCIÓN (Render detectado)")
        print(f"   Tipo: {type(config).__name__}")
        print(f"   Módulo: {config.__module__}")
        print(f"   CORS Origins: {config.CORS_ORIGINS}")
    except Exception as e:
        print(f"❌ Error importando config_production: {e}")
        sys.exit(1)
else:
    print("❌ Condición de Render NO detectada")
    try:
        from config import config
        print("🔧 [GATEWAY] Usando configuración de DESARROLLO")
        print(f"   Tipo: {type(config).__name__}")
        print(f"   Módulo: {config.__module__}")
        print(f"   CORS Origins: {config.CORS_ORIGINS}")
    except Exception as e:
        print(f"❌ Error importando config: {e}")
        sys.exit(1)

print("\n" + "=" * 50)
print("✅ Configuración verificada correctamente")
