import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { ChartModule } from 'primeng/chart';
import { DropdownModule } from 'primeng/dropdown';
import { CalendarModule } from 'primeng/calendar';
import { FormsModule } from '@angular/forms';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { LogService, LogStats, LogEntry } from '../../../core/services/log.service';

@Component({
  selector: 'app-graficas',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    ButtonModule,
    ChartModule,
    DropdownModule,
    CalendarModule,
    FormsModule,
    ProgressSpinnerModule
  ],
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.css'
})
export class GraficasComponent implements OnInit {
  logs: LogEntry[] = [];
  logStats: LogStats | null = null;
  isLoading = false;
  
  // Filtros
  selectedService: string = '';
  selectedStatus: string = '';
  dateRange: Date[] = [];
  
  // Datos para gráficas
  serviceChartData: any;
  statusChartData: any;
  timeChartData: any;
  responseTimeChartData: any;
  
  // Opciones de gráficas
  chartOptions: any;

  constructor(private logService: LogService) {
    this.initializeChartOptions();
  }

  ngOnInit(): void {
    this.loadLogs();
  }

  initializeChartOptions(): void {
    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: '#495057'
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: '#495057'
          },
          grid: {
            color: '#ebedef'
          }
        },
        y: {
          ticks: {
            color: '#495057'
          },
          grid: {
            color: '#ebedef'
          }
        }
      }
    };
  }

  loadLogs(): void {
    this.isLoading = true;
    
    // Cargar estadísticas reales desde el API Gateway
    this.logService.getLogStats().subscribe({
      next: (response) => {
        if (response.success && response.data) {
          // Usar datos reales del API Gateway
          this.logStats = response.data;
          
          // Generar logs recientes simulados (por ahora)
          this.logService.getRecentLogs().subscribe(logs => {
            this.logs = logs;
            this.updateCharts();
            this.isLoading = false;
          });
        } else {
          // Fallback a datos simulados si hay error
          this.generateMockLogs();
          this.calculateStats();
          this.updateCharts();
          this.isLoading = false;
        }
      },
      error: (error) => {
        console.error('Error cargando logs del API Gateway:', error);
        // Fallback a datos simulados en caso de error
        this.generateMockLogs();
        this.calculateStats();
        this.updateCharts();
        this.isLoading = false;
      }
    });
  }

  generateMockLogs(): void {
    const services = ['auth-service', 'user-service', 'task-service', 'api-gateway'];
    const methods = ['GET', 'POST', 'PUT', 'DELETE'];
    const statusCodes = [200, 201, 400, 401, 403, 404, 500];
    const users = ['admin', 'user1', 'user2', 'manager1'];
    
    this.logs = [];
    
    for (let i = 0; i < 100; i++) {
      const timestamp = new Date();
      timestamp.setHours(timestamp.getHours() - Math.random() * 24);
      
      this.logs.push({
        id: i + 1,
        timestamp: timestamp.toISOString(),
        service: services[Math.floor(Math.random() * services.length)],
        endpoint: `/api/v1/${Math.random() > 0.5 ? 'users' : 'tasks'}`,
        method: methods[Math.floor(Math.random() * methods.length)],
        status_code: statusCodes[Math.floor(Math.random() * statusCodes.length)],
        response_time: Math.random() * 2000 + 100, // 100ms a 2100ms
        user: users[Math.floor(Math.random() * users.length)],
        ip_address: `192.168.1.${Math.floor(Math.random() * 255)}`
      });
    }
    
    // Ordenar por timestamp descendente
    this.logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

  calculateStats(): void {
    if (this.logs.length === 0) return;

    const totalRequests = this.logs.length;
    const totalResponseTime = this.logs.reduce((sum, log) => sum + log.response_time, 0);
    const averageResponseTime = totalResponseTime / totalRequests;
    
    const successfulRequests = this.logs.filter(log => log.status_code >= 200 && log.status_code < 300).length;
    const successRate = (successfulRequests / totalRequests) * 100;
    
    const requestsByService: { [key: string]: number } = {};
    const requestsByStatus: { [key: string]: number } = {};
    const requestsByHour: { [key: string]: number } = {};
    
    this.logs.forEach(log => {
      // Contar por servicio
      requestsByService[log.service] = (requestsByService[log.service] || 0) + 1;
      
      // Contar por status
      const statusGroup = this.getStatusGroup(log.status_code);
      requestsByStatus[statusGroup] = (requestsByStatus[statusGroup] || 0) + 1;
      
      // Contar por hora
      const hour = new Date(log.timestamp).getHours();
      const hourKey = `${hour}:00`;
      requestsByHour[hourKey] = (requestsByHour[hourKey] || 0) + 1;
    });
    
    this.logStats = {
      total_requests: totalRequests,
      average_response_time: averageResponseTime,
      success_rate: successRate,
      requests_by_service: requestsByService,
      requests_by_status: requestsByStatus,
      requests_by_method: {}, // Se llenará con datos reales
      response_times: {}, // Se llenará con datos reales
      top_users: {}, // Se llenará con datos reales
      hourly_distribution: requestsByHour
    };
  }

  getStatusGroup(statusCode: number): string {
    if (statusCode >= 200 && statusCode < 300) return 'Éxito (2xx)';
    if (statusCode >= 400 && statusCode < 500) return 'Error Cliente (4xx)';
    if (statusCode >= 500) return 'Error Servidor (5xx)';
    return 'Otros';
  }

  updateCharts(): void {
    if (!this.logStats) return;
    
    // Gráfica de servicios
    this.serviceChartData = {
      labels: Object.keys(this.logStats.requests_by_service),
      datasets: [{
        data: Object.values(this.logStats.requests_by_service),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
        borderWidth: 2
      }]
    };
    
    // Gráfica de códigos de estado
    this.statusChartData = {
      labels: Object.keys(this.logStats.requests_by_status),
      datasets: [{
        data: Object.values(this.logStats.requests_by_status),
        backgroundColor: ['#4BC0C0', '#FF6384', '#FFCE56', '#36A2EB'],
        borderWidth: 2
      }]
    };
    
    // Gráfica de tiempo por hora
    this.timeChartData = {
      labels: Object.keys(this.logStats.hourly_distribution),
      datasets: [{
        label: 'Peticiones por Hora',
        data: Object.values(this.logStats.hourly_distribution),
        borderColor: '#36A2EB',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        tension: 0.4,
        fill: true
      }]
    };
    
    // Gráfica de tiempo de respuesta
    const responseTimeData = this.logs.slice(0, 20).map(log => log.response_time);
    const responseTimeLabels = this.logs.slice(0, 20).map(log => 
      new Date(log.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    );
    
    this.responseTimeChartData = {
      labels: responseTimeLabels,
      datasets: [{
        label: 'Tiempo de Respuesta (ms)',
        data: responseTimeData,
        borderColor: '#FF6384',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        tension: 0.4,
        fill: false
      }]
    };
  }

  applyFilters(): void {
    // Implementar filtros si es necesario
    this.calculateStats();
    this.updateCharts();
  }

  clearFilters(): void {
    this.selectedService = '';
    this.selectedStatus = '';
    this.dateRange = [];
    this.applyFilters();
  }

  refreshData(): void {
    this.loadLogs();
  }

  getStatusColor(statusCode: number): string {
    if (statusCode >= 200 && statusCode < 300) return '#28a745';
    if (statusCode >= 400 && statusCode < 500) return '#ffc107';
    if (statusCode >= 500) return '#dc3545';
    return '#6c757d';
  }

  formatResponseTime(time: number): string {
    if (time < 1000) return `${time.toFixed(0)}ms`;
    return `${(time / 1000).toFixed(2)}s`;
  }
}
