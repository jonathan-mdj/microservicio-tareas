//task.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { DatePickerModule } from 'primeng/datepicker';
import { SelectModule } from 'primeng/select';
import { DialogModule } from 'primeng/dialog';
import { TableModule } from 'primeng/table';
import { MessageModule } from 'primeng/message';
import { MessagesModule } from 'primeng/messages';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ConfirmationService, MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { SelectButtonModule } from 'primeng/selectbutton';
import { TooltipModule } from 'primeng/tooltip';

import { TaskService, Task } from '../../core/services/task.service';
import { UserService, User, Role } from '../../core/services/user.service';
import { AuthService } from '../../core/services/auth.service';

interface Message {
  severity?: string;
  summary?: string;
  detail?: string;
  id?: any;
}

interface KanbanColumn {
  status: Task['status'];
  title: string;
  tasks: Task[];
  color: string;
}

@Component({
  selector: 'app-task',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    CardModule,
    ButtonModule,
    InputTextModule,
    TextareaModule,
    DatePickerModule,
    SelectModule,
    DialogModule,
    TableModule,
    MessageModule,
    MessagesModule,
    ConfirmDialogModule,
    ToastModule,
    SelectButtonModule,
    TooltipModule
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './task.component.html',
  styleUrl: './task.component.css'
})
export class TaskComponent implements OnInit {
  // Tareas
  tasks: Task[] = [];
  filteredTasks: Task[] = [];
  selectedTask: Task | null = null;
  taskDialogVisible = false;
  isEditing = false;
  
  // Usuarios y roles
  users: User[] = [];
  roles: Role[] = [];
  selectedUser: User | null = null;
  userRoleDialogVisible = false;
  
  // Formularios
  taskForm: FormGroup;
  userRoleForm: FormGroup;
  
  // Estados
  isLoading = false;
  messages: Message[] = [];
  
  // Fecha actual para comparaciones
  currentDate = new Date();
  
  // Kanban
  kanbanColumns: KanbanColumn[] = [
    { status: 'In Progress', title: 'En Progreso', tasks: [], color: '#2196F3' },
    { status: 'Revision', title: 'En Revisión', tasks: [], color: '#FF9800' },
    { status: 'Completed', title: 'Completadas', tasks: [], color: '#4CAF50' },
    { status: 'Paused', title: 'Pausadas', tasks: [], color: '#9E9E9E' }
  ];
  
  // Filtros
  statusFilter: string = 'all';
  userFilter: number | null = null;
  
  // Tabs
  activeTabIndex = 0;

  constructor(
    private taskService: TaskService,
    private userService: UserService,
    public authService: AuthService,
    private fb: FormBuilder,
    private confirmationService: ConfirmationService,
    private messageService: MessageService
  ) {
    this.taskForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      description: [''],
      deadline: [null, [this.deadlineValidator()]],
      status: ['In Progress', Validators.required]
    });

    this.userRoleForm = this.fb.group({
      user_id: [null, Validators.required],
      role_id: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    
    // Cargar tareas
    this.taskService.getTasks().subscribe({
      next: (response) => {
        this.tasks = response.tasks;
        this.filteredTasks = [...this.tasks];
        this.updateKanbanColumns();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error cargando tareas:', error);
        this.showMessage('error', 'Error', 'Error al cargar las tareas');
        this.isLoading = false;
      }
    });

    // Cargar usuarios y roles (solo si es admin)
    if (this.authService.isAdmin()) {
      this.loadUsers();
      this.loadRoles();
    }
  }

  loadUsers(): void {
    this.userService.getUsers().subscribe({
      next: (response) => {
        this.users = response.users;
      },
      error: (error) => {
        console.error('Error cargando usuarios:', error);
      }
    });
  }

  loadRoles(): void {
    this.userService.getRoles().subscribe({
      next: (response) => {
        this.roles = response.roles;
      },
      error: (error) => {
        console.error('Error cargando roles:', error);
      }
    });
  }

  updateKanbanColumns(): void {
    this.kanbanColumns.forEach(column => {
      column.tasks = this.filteredTasks.filter(task => task.status === column.status);
    });
  }

  // Métodos de Tareas
  openNewTask(): void {
    this.isEditing = false;
    this.selectedTask = null;
    this.taskForm.reset({
      status: 'In Progress'
    });
    this.taskDialogVisible = true;
  }

  editTask(task: Task): void {
    this.isEditing = true;
    this.selectedTask = task;
    this.taskForm.patchValue({
      name: task.name,
      description: task.description || '',
      deadline: task.deadline ? new Date(task.deadline) : null,
      status: task.status
    });
    this.taskDialogVisible = true;
  }

  saveTask(): void {
    if (this.taskForm.valid) {
      const taskData = this.taskForm.value;
      
      if (taskData.deadline) {
        taskData.deadline = this.taskService.formatDateForBackend(taskData.deadline);
      }

      if (this.isEditing && this.selectedTask) {
        this.taskService.updateTask(this.selectedTask.id!, taskData).subscribe({
          next: (response) => {
            this.showMessage('success', 'Éxito', 'Tarea actualizada correctamente');
            this.taskDialogVisible = false;
            this.loadData();
          },
          error: (error) => {
            this.showMessage('error', 'Error', 'Error al actualizar la tarea');
          }
        });
      } else {
        this.taskService.createTask(taskData).subscribe({
          next: (response) => {
            this.showMessage('success', 'Éxito', 'Tarea creada correctamente');
            this.taskDialogVisible = false;
            this.loadData();
          },
          error: (error) => {
            this.showMessage('error', 'Error', 'Error al crear la tarea');
          }
        });
      }
    }
  }

  deleteTask(task: Task): void {
    this.confirmationService.confirm({
      message: `¿Estás seguro de que quieres eliminar la tarea "${task.name}"?`,
      header: 'Confirmar eliminación',
      icon: 'pi pi-exclamation-triangle',
      accept: () => {
        this.taskService.deleteTask(task.id!).subscribe({
          next: (response) => {
            this.showMessage('success', 'Éxito', 'Tarea eliminada correctamente');
            this.loadData();
          },
          error: (error) => {
            this.showMessage('error', 'Error', 'Error al eliminar la tarea');
          }
        });
      }
    });
  }

  updateTaskStatus(task: Task, newStatus: Task['status']): void {
    this.taskService.updateTask(task.id!, { status: newStatus }).subscribe({
      next: (response) => {
        this.showMessage('success', 'Éxito', 'Estado de tarea actualizado');
        this.loadData();
      },
      error: (error) => {
        this.showMessage('error', 'Error', 'Error al actualizar el estado');
      }
    });
  }

  // Métodos de Usuarios y Roles
  openUserRoleDialog(user: User): void {
    this.selectedUser = user;
    // Necesitamos obtener el role_id basado en el nombre del rol
    const roleId = this.getRoleIdByName(user.role);
    this.userRoleForm.patchValue({
      user_id: user.id,
      role_id: roleId
    });
    this.userRoleDialogVisible = true;
  }

  updateUserRole(): void {
    if (this.userRoleForm.valid) {
      const request = this.userRoleForm.value;
      
      this.userService.updateUserRole(request).subscribe({
        next: (response) => {
          this.showMessage('success', 'Éxito', 'Rol de usuario actualizado correctamente');
          this.userRoleDialogVisible = false;
          this.loadUsers();
        },
        error: (error) => {
          this.showMessage('error', 'Error', 'Error al actualizar el rol');
        }
      });
    }
  }

  // Filtros
  applyFilters(): void {
    this.filteredTasks = this.tasks.filter(task => {
      let matchesStatus = true;
      let matchesUser = true;

      if (this.statusFilter !== 'all') {
        matchesStatus = task.status === this.statusFilter;
      }

      if (this.userFilter) {
        matchesUser = task.created_by === this.userFilter;
      }

      return matchesStatus && matchesUser;
    });

    this.updateKanbanColumns();
  }

  clearFilters(): void {
    this.statusFilter = 'all';
    this.userFilter = null;
    this.filteredTasks = [...this.tasks];
    this.updateKanbanColumns();
  }

  // Utilidades
  showMessage(severity: string, summary: string, detail: string): void {
    this.messageService.add({
      severity,
      summary,
      detail
    });
  }

  getStatusColor(status: Task['status']): string {
    const colors = {
      'In Progress': '#2196F3',
      'Revision': '#FF9800',
      'Completed': '#4CAF50',
      'Paused': '#9E9E9E'
    };
    return colors[status] || '#666';
  }

  getStatusIcon(status: Task['status']): string {
    const icons = {
      'In Progress': 'pi pi-play',
      'Revision': 'pi pi-eye',
      'Completed': 'pi pi-check',
      'Paused': 'pi pi-pause'
    };
    return icons[status] || 'pi pi-circle';
  }

  // Métodos auxiliares para roles
  getRoleColor(role: string): string {
    const colors = {
      'Admin': '#dc3545',     // admin - rojo
      'Usuario': '#28a745',   // user - verde
      'Manager': '#ffc107'    // manager - amarillo
    };
    return colors[role as keyof typeof colors] || '#6c757d';
  }

  getRoleName(role: string): string {
    return role || 'Desconocido';
  }

  getRoleIdByName(roleName: string): number {
    const roleMap = {
      'Admin': 1,
      'Usuario': 2,
      'Manager': 3
    };
    return roleMap[roleName as keyof typeof roleMap] || 2; // Default a Usuario
  }

  // Método para verificar si una fecha está vencida
  isOverdue(dateString: string): boolean {
    if (!dateString) return false;
    const taskDate = new Date(dateString);
    return taskDate < this.currentDate;
  }

  // Getters para el formulario
  get taskName() { return this.taskForm.get('name'); }
  get taskDescription() { return this.taskForm.get('description'); }
  get taskDeadline() { return this.taskForm.get('deadline'); }
  get taskStatus() { return this.taskForm.get('status'); }

  // Métodos para validaciones de fecha
  getDeadlineError(): string | null {
    const deadlineControl = this.taskForm.get('deadline');
    if (deadlineControl?.errors && deadlineControl.touched) {
      if (deadlineControl.errors['pastDate']) {
        return 'La fecha límite no puede ser anterior a la fecha actual';
      }
      if (deadlineControl.errors['noTime']) {
        return 'Debe seleccionar una hora específica';
      }
    }
    return null;
  }

  getDeadlineValue(): string | null {
    const deadlineValue = this.taskForm.get('deadline')?.value;
    if (deadlineValue) {
      // Si es una fecha válida
      if (deadlineValue instanceof Date) {
        return this.formatDate(deadlineValue);
      }
    }
    return null;
  }

  // Método para formatear la fecha
  formatDate(date: Date): string {
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}`;
  }

  // Helper para tabs
  isTabActive(index: number): boolean {
    return this.activeTabIndex === index;
  }

  // Validador personalizado para fecha límite
  deadlineValidator() {
    return (control: any) => {
      const deadline = control.value;
      
      if (!deadline) {
        return null; // No es requerido
      }

      const selectedDate = new Date(deadline);
      const now = new Date();
      
      // Validar que la fecha no sea pasada
      if (selectedDate < now) {
        return { pastDate: true };
      }

      // Validar que tenga hora (no solo fecha)
      const hasTime = deadline.getHours() !== 0 || deadline.getMinutes() !== 0;
      if (!hasTime) {
        return { noTime: true };
      }

      return null;
    };
  }
}
