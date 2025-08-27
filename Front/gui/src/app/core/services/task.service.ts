//task.services.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../../environments/environment';

export interface Task {
  id?: number;
  name: string;
  description?: string;
  deadline?: string;
  status: 'In Progress' | 'Revision' | 'Completed' | 'Paused';
  created_at?: string;
  updated_at?: string;
  created_by?: number;
  created_by_username?: string;
  is_alive?: boolean;
}

export interface TaskResponse {
  tasks: Task[];
  count: number;
  status?: string;
}

export interface TaskDetailResponse {
  task: Task;
}

export interface ApiResponse {
  message: string;
  error?: string;
  task?: Task;
}

export interface SystemInfo {
  sistema: string;
  usuario_actual: string;
  estadisticas: {
    total_usuarios: number;
    total_roles: number;
    total_permisos: number;
    total_tareas: number;
    tareas_por_status: { [key: string]: number };
  };
}

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private readonly API_URL = environment.apiUrl; // Ahora apunta al API Gateway

  constructor(
    private readonly http: HttpClient,
    private readonly authService: AuthService
  ) {}

  /**
   * Obtener todas las tareas del usuario
   */
  getTasks(): Observable<TaskResponse> {
    return this.http.get<TaskResponse>(`${this.API_URL}/tasks`);
  }

  /**
   * Obtener una tarea específica por ID
   */
  getTask(id: number): Observable<TaskDetailResponse> {
    return this.http.get<TaskDetailResponse>(`${this.API_URL}/task/${id}`);
  }
  /**
   * Crear una nueva tarea
   */
  createTask(task: Omit<Task, 'id'>): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.API_URL}/task`, task);
  }

  /**
   * Actualizar una tarea existente
   */
  updateTask(id: number, task: Partial<Task>): Observable<ApiResponse> {
    return this.http.put<ApiResponse>(`${this.API_URL}/task/${id}`, task);
  }

  /**
   * Eliminar una tarea (soft delete)
   */
  deleteTask(id: number): Observable<ApiResponse> {
    return this.http.delete<ApiResponse>(`${this.API_URL}/task/${id}`);
  }

  /**
   * Obtener tareas por status
   */
  getTasksByStatus(status: string): Observable<TaskResponse> {
    const statusMap: { [key: string]: string } = {
      'In Progress': 'in_progress',
      'Revision': 'revision',
      'Completed': 'completed',
      'Paused': 'paused'
    };
    
    const urlStatus = statusMap[status] || status.toLowerCase().replace(' ', '_');
    
    return this.http.get<TaskResponse>(`${this.API_URL}/tasks/status/${urlStatus}`);
  }

  /**
   * Obtener información del sistema
   */
  getSystemInfo(): Observable<SystemInfo> {
    return this.http.get<SystemInfo>(`${this.API_URL}/info`);
  }

  /**
   * Obtener estadísticas de tareas
   
  getTaskStats(): Observable<any> {
    return this.getSystemInfo();
  }
    */

  /**
   * Cambiar status de una tarea
  updateTaskStatus(id: number, status: Task['status']): Observable<ApiResponse> {
    return this.updateTask(id, { status });
  }
    */

  /**
   * Marcar tarea como completada
   
  completeTask(id: number): Observable<ApiResponse> {
    return this.updateTaskStatus(id, 'Completed');
  }
    */

  /**
   * Pausar tarea
   
  pauseTask(id: number): Observable<ApiResponse> {
    return this.updateTaskStatus(id, 'Paused');
  }
    */

  /**
   * Reanudar tarea
   
  resumeTask(id: number): Observable<ApiResponse> {
    return this.updateTaskStatus(id, 'In Progress');
  }
    */

  /**
   * Enviar tarea a revisión
   
  sendToRevision(id: number): Observable<ApiResponse> {
    return this.updateTaskStatus(id, 'Revision');
  }
    */

  /**
   * Validar formato de fecha
   */
  validateDateFormat(dateString: string): boolean {
    const regex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;
    return regex.test(dateString);
  }

  /**
   * Formatear fecha para el backend
   */
  formatDateForBackend(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
}