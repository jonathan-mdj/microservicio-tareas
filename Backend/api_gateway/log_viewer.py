#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Viewer para API Gateway
Script para visualizar y analizar logs del sistema de gestión de tareas
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import argparse

LOG_FILE = 'logs/api_gateway.log'

def parse_log_line(line):
    """Parsear una línea de log y extraer la información JSON"""
    try:
        # Buscar el JSON en la línea
        start = line.find('{')
        if start == -1:
            return None
        
        json_str = line[start:]
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        return None

def load_logs():
    """Cargar todos los logs del archivo"""
    logs = []
    
    if not os.path.exists(LOG_FILE):
        print(f"Archivo de log no encontrado: {LOG_FILE}")
        return logs
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            data = parse_log_line(line)
            if data:
                logs.append(data)
    
    return logs

def filter_logs_by_time(logs, hours=24):
    """Filtrar logs por tiempo (últimas N horas)"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    filtered_logs = []
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            if log_time >= cutoff_time:
                filtered_logs.append(log)
        except (ValueError, KeyError):
            continue
    
    return filtered_logs

def analyze_logs(logs):
    """Analizar logs y generar estadísticas"""
    if not logs:
        print("No hay logs para analizar")
        return
    
    # Contadores
    total_requests = len(logs)
    requests_by_service = Counter()
    requests_by_method = Counter()
    requests_by_status = Counter()
    response_times = []
    users = Counter()
    
    # Procesar cada log
    for log in logs:
        # Servicio
        service = log.get('service', 'unknown')
        requests_by_service[service] += 1
        
        # Método HTTP
        method = log.get('method', 'unknown')
        requests_by_method[method] += 1
        
        # Status code
        status = log.get('status_code', 0)
        requests_by_status[status] += 1
        
        # Response time
        response_time = log.get('response_time_ms', 0)
        if response_time > 0:
            response_times.append(response_time)
        
        # Usuario (si está disponible)
        user_info = log.get('user')
        if user_info and user_info.get('username'):
            users[user_info['username']] += 1
    
    # Calcular estadísticas de response time
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    
    # Mostrar estadísticas
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE LOGS DEL API GATEWAY")
    print("="*60)
    
    print(f"\n RESUMEN GENERAL:")
    print(f"   Total de requests: {total_requests}")
    print(f"   Tiempo promedio de respuesta: {avg_response_time:.2f}ms")
    print(f"   Tiempo máximo de respuesta: {max_response_time:.2f}ms")
    print(f"   Tiempo mínimo de respuesta: {min_response_time:.2f}ms")
    
    print(f"\n REQUESTS POR SERVICIO:")
    for service, count in requests_by_service.most_common():
        percentage = (count / total_requests) * 100
        print(f"   {service}: {count} ({percentage:.1f}%)")
    
    print(f"\n REQUESTS POR MÉTODO HTTP:")
    for method, count in requests_by_method.most_common():
        percentage = (count / total_requests) * 100
        print(f"   {method}: {count} ({percentage:.1f}%)")
    
    print(f"\n CÓDIGOS DE ESTADO:")
    for status, count in requests_by_status.most_common():
        percentage = (count / total_requests) * 100
        status_icon = "OK" if status < 400 else "Warning" if status < 500 else "Error"
        print(f"   {status_icon} {status}: {count} ({percentage:.1f}%)")
    
    if users:
        print(f"\n USUARIOS MÁS ACTIVOS:")
        for user, count in users.most_common(5):
            print(f"   {user}: {count} requests")

def show_recent_logs(logs, limit=10):
    """Mostrar los logs más recientes"""
    if not logs:
        print("No hay logs para mostrar")
        return
    
    print(f"\n ÚLTIMOS {limit} LOGS:")
    print("-" * 80)
    
    # Ordenar por timestamp
    sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    for i, log in enumerate(sorted_logs[:limit]):
        timestamp = log.get('timestamp', 'N/A')
        method = log.get('method', 'N/A')
        path = log.get('path', 'N/A')
        service = log.get('service', 'N/A')
        status = log.get('status_code', 'N/A')
        response_time = log.get('response_time_ms', 'N/A')
        user = log.get('user', {}).get('username', 'anonymous')
        
        # Iconos según el status
        status_icon = "OK" if status < 400 else "Warning" if status < 500 else "Error"
        
        print(f"{i+1:2d}. {status_icon} {method:6s} {path:30s} | "
              f"Service: {service:12s} | Status: {status:3s} | "
              f"Time: {response_time:6s}ms | User: {user}")

def show_error_logs(logs, limit=10):
    """Mostrar solo los logs de error"""
    error_logs = [log for log in logs if log.get('status_code', 200) >= 400]
    
    if not error_logs:
        print(" No hay errores en los logs")
        return
    
    print(f"\n ÚLTIMOS {limit} ERRORES:")
    print("-" * 80)
    
    # Ordenar por timestamp
    sorted_errors = sorted(error_logs, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    for i, log in enumerate(sorted_errors[:limit]):
        timestamp = log.get('timestamp', 'N/A')
        method = log.get('method', 'N/A')
        path = log.get('path', 'N/A')
        service = log.get('service', 'N/A')
        status = log.get('status_code', 'N/A')
        response_time = log.get('response_time_ms', 'N/A')
        user = log.get('user', {}).get('username', 'anonymous')
        
        print(f"{i+1:2d}. {method:6s} {path:30s} | "
              f"Service: {service:12s} | Status: {status:3s} | "
              f"Time: {response_time:6s}ms | User: {user}")

def main():
    parser = argparse.ArgumentParser(description='Log Viewer para API Gateway')
    parser.add_argument('--hours', type=int, default=24, 
                       help='Horas hacia atrás para filtrar logs (default: 24)')
    parser.add_argument('--recent', type=int, default=10,
                       help='Número de logs recientes a mostrar (default: 10)')
    parser.add_argument('--errors', action='store_true',
                       help='Mostrar solo logs de error')
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estadísticas de logs')
    
    args = parser.parse_args()
    
    print(" Cargando logs...")
    logs = load_logs()
    
    if not logs:
        print(" No se encontraron logs para analizar")
        return
    
    # Filtrar por tiempo
    filtered_logs = filter_logs_by_time(logs, args.hours)
    print(f"Se encontraron {len(filtered_logs)} logs en las últimas {args.hours} horas")
    
    if args.errors:
        show_error_logs(filtered_logs, args.recent)
    elif args.stats:
        analyze_logs(filtered_logs)
    else:
        show_recent_logs(filtered_logs, args.recent)
        analyze_logs(filtered_logs)

if __name__ == '__main__':
    main() 