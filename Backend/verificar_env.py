#!/usr/bin/env python3
"""
Script para verificar variables de entorno en Render
"""
import os
from dotenv import load_dotenv

print("🔍 VERIFICANDO VARIABLES DE ENTORNO EN RENDER")
print("=" * 50)

# Cargar .env.atlas si existe
if os.path.exists('.env.atlas'):
    load_dotenv('.env.atlas')
    print("✅ .env.atlas cargado")
else:
    print("❌ .env.atlas no encontrado")

# Verificar variables críticas
print("\n📋 VARIABLES DE ENTORNO:")
print(f"   FLASK_ENV: {os.getenv('FLASK_ENV', 'NO CONFIGURADO')}")
print(f"   DEBUG: {os.getenv('DEBUG', 'NO CONFIGURADO')}")
print(f"   PORT: {os.getenv('PORT', 'NO CONFIGURADO')}")
print(f"   MONGO_URI_ATLAS: {'CONFIGURADO' if os.getenv('MONGO_URI_ATLAS') else 'NO CONFIGURADO'}")
print(f"   JWT_SECRET_ATLAS: {'CONFIGURADO' if os.getenv('JWT_SECRET_ATLAS') else 'NO CONFIGURADO'}")

# Verificar configuración de producción
print("\n🔧 CONFIGURACIÓN DE PRODUCCIÓN:")
if os.getenv('FLASK_ENV') == 'production':
    print("   ✅ FLASK_ENV = production")
else:
    print("   ❌ FLASK_ENV no es 'production'")

if os.getenv('DEBUG') == 'false':
    print("   ✅ DEBUG = false")
else:
    print("   ❌ DEBUG no es 'false'")

print("\n🌐 CORS ORIGINS:")
try:
    from config_production import production_config
    print(f"   CORS Origins: {production_config.CORS_ORIGINS}")
except Exception as e:
    print(f"   ❌ Error cargando config_production: {e}")

print("\n" + "=" * 50)
