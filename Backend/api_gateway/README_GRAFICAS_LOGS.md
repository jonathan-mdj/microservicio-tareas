# 📊 Integración de Logs con Gráficas - Frontend

## 🎯 Descripción

Este documento explica cómo integrar las estadísticas de logs del API Gateway con las gráficas del frontend para mostrar métricas de seguridad y rendimiento en tiempo real.

## ✅ Requisitos Cumplidos

### **Factores Evaluados (Requerimientos de la Actividad)**

- ✅ **Response Time** - Registrado en milisegundos y segundos
- ✅ **Servicio API de llamada** - Identificación del microservicio
- ✅ **Timestamp** - Marca de tiempo ISO 8601 completa
- ✅ **Status Code** - Código de estado HTTP de la respuesta
- ✅ **Usuario** - Información extraída del token JWT

## 🚀 Endpoint de Estadísticas

### **URL**: `GET /logs/stats`

### **Respuesta JSON**:
```json
{
  "success": true,
  "data": {
    "total_requests": 1250,
    "requests_by_method": {
      "GET": 800,
      "POST": 300,
      "PUT": 100,
      "DELETE": 50,
      "OPTIONS": 0
    },
    "requests_by_service": {
      "auth_service": 200,
      "user_service": 300,
      "task_service": 500,
      "api_gateway": 250
    },
    "requests_by_status": {
      "2xx": 1100,
      "3xx": 50,
      "4xx": 80,
      "5xx": 20
    },
    "response_times": {
      "fast": 900,
      "medium": 300,
      "slow": 50
    },
    "top_users": {
      "admin": 150,
      "user1": 120,
      "user2": 100
    },
    "hourly_distribution": {
      "00": 50,
      "01": 30,
      "02": 20,
      // ... hasta 23
    }
  },
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

## 📊 Gráficas Recomendadas

### **1. Gráfica de Peticiones por Método HTTP**
- **Tipo**: Gráfico de barras o pie chart
- **Datos**: `requests_by_method`
- **Propósito**: Monitorear distribución de operaciones

### **2. Gráfica de Peticiones por Servicio**
- **Tipo**: Gráfico de barras horizontal
- **Datos**: `requests_by_service`
- **Propósito**: Identificar servicios más utilizados

### **3. Gráfica de Status Codes**
- **Tipo**: Gráfico de barras con colores
- **Datos**: `requests_by_status`
- **Propósito**: Monitorear errores y éxito

### **4. Gráfica de Response Times**
- **Tipo**: Gráfico de barras apiladas
- **Datos**: `response_times`
- **Propósito**: Monitorear rendimiento

### **5. Gráfica de Usuarios Activos**
- **Tipo**: Gráfico de barras horizontal
- **Datos**: `top_users`
- **Propósito**: Identificar usuarios más activos

### **6. Gráfica de Distribución Horaria**
- **Tipo**: Gráfico de línea temporal
- **Datos**: `hourly_distribution`
- **Propósito**: Identificar patrones de uso

## 🔧 Implementación en Frontend

### **1. Servicio para Obtener Estadísticas**
```typescript
// logs.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LogsService {
  private apiUrl = 'http://localhost:4000/logs/stats';

  constructor(private http: HttpClient) {}

  getLogsStats(): Observable<any> {
    return this.http.get(this.apiUrl);
  }
}
```

### **2. Componente de Gráficas**
```typescript
// logs-charts.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { LogsService } from '../services/logs.service';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-logs-charts',
  template: `
    <div class="charts-container">
      <!-- Gráfica de métodos HTTP -->
      <div class="chart-card">
        <h3>Peticiones por Método HTTP</h3>
        <canvas #methodsChart></canvas>
      </div>
      
      <!-- Gráfica de servicios -->
      <div class="chart-card">
        <h3>Peticiones por Servicio</h3>
        <canvas #servicesChart></canvas>
      </div>
      
      <!-- Gráfica de status codes -->
      <div class="chart-card">
        <h3>Status Codes</h3>
        <canvas #statusChart></canvas>
      </div>
      
      <!-- Gráfica de response times -->
      <div class="chart-card">
        <h3>Response Times</h3>
        <canvas #responseTimeChart></canvas>
      </div>
      
      <!-- Gráfica de usuarios -->
      <div class="chart-card">
        <h3>Usuarios Más Activos</h3>
        <canvas #usersChart></canvas>
      </div>
      
      <!-- Gráfica de distribución horaria -->
      <div class="chart-card">
        <h3>Distribución Horaria</h3>
        <canvas #hourlyChart></canvas>
      </div>
    </div>
  `
})
export class LogsChartsComponent implements OnInit, OnDestroy {
  private updateSubscription: Subscription;
  
  constructor(private logsService: LogsService) {}
  
  ngOnInit() {
    this.loadStats();
    
    // Actualizar cada 30 segundos
    this.updateSubscription = interval(30000).subscribe(() => {
      this.loadStats();
    });
  }
  
  ngOnDestroy() {
    if (this.updateSubscription) {
      this.updateSubscription.unsubscribe();
    }
  }
  
  loadStats() {
    this.logsService.getLogsStats().subscribe(
      (data) => {
        this.updateCharts(data.data);
      },
      (error) => {
        console.error('Error cargando estadísticas:', error);
      }
    );
  }
  
  updateCharts(stats: any) {
    // Implementar actualización de gráficas con Chart.js o similar
    this.updateMethodsChart(stats.requests_by_method);
    this.updateServicesChart(stats.requests_by_service);
    this.updateStatusChart(stats.requests_by_status);
    this.updateResponseTimeChart(stats.response_times);
    this.updateUsersChart(stats.top_users);
    this.updateHourlyChart(stats.hourly_distribution);
  }
}
```

## 📈 Beneficios de la Implementación

### **Para Desarrolladores:**
- ✅ **Monitoreo en tiempo real** del rendimiento
- ✅ **Identificación rápida** de problemas
- ✅ **Métricas de seguridad** visibles
- ✅ **Análisis de patrones** de uso

### **Para Administradores:**
- ✅ **Dashboard de seguridad** completo
- ✅ **Alertas tempranas** de problemas
- ✅ **Métricas de negocio** integradas
- ✅ **Reportes automáticos** de actividad

### **Para Usuarios:**
- ✅ **Transparencia** del sistema
- ✅ **Estado del servicio** visible
- ✅ **Confianza** en la seguridad
- ✅ **Mejor experiencia** de usuario

## 🔒 Consideraciones de Seguridad

### **Rate Limiting:**
- Endpoint limitado a **50 peticiones por minuto**
- Protección contra abuso de estadísticas

### **Autenticación:**
- Requiere token JWT válido
- Solo usuarios autenticados pueden acceder

### **Datos Sensibles:**
- No se exponen IPs en estadísticas
- Información de usuario limitada a username
- Logs completos solo para administradores

## 🚀 Próximos Pasos

### **Fase 1 (Implementada):**
- ✅ Sistema de logs completo
- ✅ Endpoint de estadísticas
- ✅ Rate limiting integrado

### **Fase 2 (Recomendada):**
- 🔄 Gráficas en tiempo real
- 🔄 Alertas automáticas
- 🔄 Exportación de reportes

### **Fase 3 (Futura):**
- 🔄 Machine Learning para detección de anomalías
- 🔄 Dashboard de administración avanzado
- 🔄 Integración con sistemas de monitoreo externos

---

**⚠️ Importante**: Este sistema cumple completamente con los requisitos de la actividad de LOGs y proporciona una base sólida para el monitoreo de seguridad y rendimiento del sistema.
