import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TaskService } from '../../../core/services/task.service';

@Component({
  selector: 'app-system-info',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    ButtonModule,
    ProgressSpinnerModule
  ],
  templateUrl: './system-info.component.html',
  styleUrl: './system-info.component.css'
})
export class SystemInfoComponent implements OnInit {
  systemInfo: any = null;
  isLoading = false;
  error = '';

  constructor(private taskService: TaskService) {}

  ngOnInit(): void {
    this.loadSystemInfo();
  }

  loadSystemInfo(): void {
    this.isLoading = true;
    this.error = '';
    
    this.taskService.getSystemInfo().subscribe({
      next: (response: any) => {
        this.systemInfo = response;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('Error cargando información del sistema:', error);
        this.error = 'Error al cargar la información del sistema';
        this.isLoading = false;
      }
    });
  }

  refreshSystemInfo(): void {
    this.loadSystemInfo();
  }

  getTaskStatuses(): Array<{label: string, count: number}> {
    if (!this.systemInfo?.estadisticas?.tareas_por_status) {
      return [];
    }
    
    const statusMap: { [key: string]: string } = {
      'In Progress': 'En Progreso',
      'Revision': 'En Revisión',
      'Completed': 'Completadas',
      'Paused': 'Pausadas'
    };
    
    return Object.entries(this.systemInfo.estadisticas.tareas_por_status).map(([status, count]) => ({
      label: statusMap[status] || status,
      count: count as number
    }));
  }
}
