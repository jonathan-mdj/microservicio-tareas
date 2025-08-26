import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface LogEntry {
  id: number;
  timestamp: string;
  service: string;
  endpoint: string;
  method: string;
  status_code: number;
  response_time: number;
  user: string;
  ip_address: string;
}

export interface LogStats {
  total_requests: number;
  average_response_time: number;
  success_rate: number;
  requests_by_method: { [key: string]: number };
  requests_by_service: { [key: string]: number };
  requests_by_status: { [key: string]: number };
  response_times: { [key: string]: number };
  top_users: { [key: string]: number };
  hourly_distribution: { [key: string]: number };
}

export interface LogStatsResponse {
  success: boolean;
  data: LogStats;
  timestamp: string;
}

@Injectable({
  providedIn: 'root'
})
export class LogService {
  private apiUrl = environment.apiUrl || 'http://localhost:4000';

  constructor(private http: HttpClient) { }

  /**
   * Obtener estadísticas de logs desde el API Gateway
   */
  getLogStats(): Observable<LogStatsResponse> {
    return this.http.get<LogStatsResponse>(`${this.apiUrl}/logs/stats`);
  }

  /**
   * Obtener logs recientes (simulado por ahora, ya que el API Gateway solo devuelve stats)
   */
  getRecentLogs(): Observable<LogEntry[]> {
    // Por ahora devolvemos logs simulados ya que el API Gateway solo tiene stats
    // En el futuro se podría agregar un endpoint /logs/recent en el API Gateway
    return new Observable(observer => {
      const mockLogs = this.generateMockRecentLogs();
      observer.next(mockLogs);
      observer.complete();
    });
  }

  /**
   * Generar logs recientes simulados para mantener compatibilidad
   */
  private generateMockRecentLogs(): LogEntry[] {
    const services = ['auth_service', 'user_service', 'task_service', 'api_gateway'];
    const methods = ['GET', 'POST', 'PUT', 'DELETE'];
    const statusCodes = [200, 201, 400, 401, 403, 404, 500];
    const users = ['admin', 'user1', 'user2', 'manager1'];
    
    const logs: LogEntry[] = [];
    
    for (let i = 0; i < 20; i++) {
      const timestamp = new Date();
      timestamp.setMinutes(timestamp.getMinutes() - Math.random() * 60);
      
      logs.push({
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
    return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }
}
