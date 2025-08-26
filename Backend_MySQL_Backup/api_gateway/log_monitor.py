#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Monitor para API Gateway
Script para monitorear logs en tiempo real
"""

import time
import os
import json
from datetime import datetime
import argparse

LOG_FILE = 'logs/api_gateway.log'

def tail_logs(follow=True, lines=10):
    """Monitorear logs en tiempo real (similar a tail -f)"""
    if not os.path.exists(LOG_FILE):
        print(f"❌ Archivo de log no encontrado: {LOG_FILE}")
        return
    
    # Leer las últimas líneas
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
        last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
    
    # Mostrar las últimas líneas
    print(f"📝 Últimas {len(last_lines)} líneas del log:")
    print("-" * 80)
    for line in last_lines:
        print(line.strip())
    
    if not follow:
        return
    
    print(f"\n🔄 Monitoreando logs en tiempo real... (Ctrl+C para salir)")
    print("-" * 80)
    
    # Monitorear en tiempo real
    file_size = os.path.getsize(LOG_FILE)
    
    try:
        while True:
            current_size = os.path.getsize(LOG_FILE)
            
            if current_size > file_size:
                # Nuevas líneas disponibles
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    f.seek(file_size)
                    new_lines = f.readlines()
                    
                    for line in new_lines:
                        if line.strip():
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] {line.strip()}")
                
                file_size = current_size
            
            time.sleep(0.1)  # Verificar cada 100ms
            
    except KeyboardInterrupt:
        print("\n👋 Monitoreo detenido")

def parse_and_display_log(line):
    """Parsear y mostrar una línea de log de manera formateada"""
    try:
        # Buscar JSON en la línea
        start = line.find('{')
        if start == -1:
            return line
        
        json_str = line[start:]
        data = json.loads(json_str)
        
        # Extraer información relevante
        timestamp = data.get('timestamp', 'N/A')
        method = data.get('method', 'N/A')
        path = data.get('path', 'N/A')
        service = data.get('service', 'N/A')
        status = data.get('status_code', 'N/A')
        response_time = data.get('response_time_ms', 'N/A')
        user = data.get('user', {}).get('username', 'anonymous')
        
        # Determinar tipo de log
        if 'REQUEST_START' in line:
            log_type = "📤 REQUEST"
        elif 'RESPONSE_END' in line:
            log_type = "📥 RESPONSE"
            # Icono según status
            status_icon = "✅" if status < 400 else "⚠️" if status < 500 else "❌"
        else:
            log_type = "📋 LOG"
            status_icon = ""
        
        # Formatear timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = timestamp
        
        # Mostrar información formateada
        if 'RESPONSE_END' in line:
            print(f"{time_str} {log_type} {status_icon} {method:6s} {path:30s} | "
                  f"Service: {service:12s} | Status: {status:3s} | "
                  f"Time: {response_time:6s}ms | User: {user}")
        else:
            print(f"{time_str} {log_type} {method:6s} {path:30s} | "
                  f"Service: {service:12s} | User: {user}")
        
    except (json.JSONDecodeError, ValueError):
        # Si no es JSON, mostrar la línea original
        print(line.strip())

def monitor_formatted(follow=True, lines=10):
    """Monitorear logs con formato mejorado"""
    if not os.path.exists(LOG_FILE):
        print(f"❌ Archivo de log no encontrado: {LOG_FILE}")
        return
    
    # Leer las últimas líneas
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
        last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
    
    # Mostrar las últimas líneas formateadas
    print(f"📝 Últimas {len(last_lines)} entradas del log:")
    print("-" * 100)
    for line in last_lines:
        if line.strip():
            parse_and_display_log(line)
    
    if not follow:
        return
    
    print(f"\n🔄 Monitoreando logs en tiempo real... (Ctrl+C para salir)")
    print("-" * 100)
    
    # Monitorear en tiempo real
    file_size = os.path.getsize(LOG_FILE)
    
    try:
        while True:
            current_size = os.path.getsize(LOG_FILE)
            
            if current_size > file_size:
                # Nuevas líneas disponibles
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    f.seek(file_size)
                    new_lines = f.readlines()
                    
                    for line in new_lines:
                        if line.strip():
                            parse_and_display_log(line)
                
                file_size = current_size
            
            time.sleep(0.1)  # Verificar cada 100ms
            
    except KeyboardInterrupt:
        print("\n👋 Monitoreo detenido")

def main():
    parser = argparse.ArgumentParser(description='Log Monitor para API Gateway')
    parser.add_argument('--lines', type=int, default=10,
                       help='Número de líneas iniciales a mostrar (default: 10)')
    parser.add_argument('--no-follow', action='store_true',
                       help='No seguir el archivo en tiempo real')
    parser.add_argument('--raw', action='store_true',
                       help='Mostrar logs en formato raw (sin formatear)')
    
    args = parser.parse_args()
    
    print("🔍 Iniciando monitor de logs...")
    print(f"📁 Archivo: {LOG_FILE}")
    print(f"📊 Líneas iniciales: {args.lines}")
    print(f"🔄 Seguimiento en tiempo real: {'No' if args.no_follow else 'Sí'}")
    print(f"📝 Formato: {'Raw' if args.raw else 'Formateado'}")
    print("=" * 80)
    
    if args.raw:
        tail_logs(follow=not args.no_follow, lines=args.lines)
    else:
        monitor_formatted(follow=not args.no_follow, lines=args.lines)

if __name__ == '__main__':
    main() 