//user.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  created_at: string;
}

export interface Role {
  id: number;
  nombre: string;
  created_at: string;
}

export interface UserResponse {
  users: User[];
  count: number;
}

export interface RoleResponse {
  roles: Role[];
  count: number;
}

export interface UpdateUserRoleRequest {
  user_id: number;
  role_id: number;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  role_id: number;
}

export interface UpdateUserRequest {
  username?: string;
  email?: string;
  password?: string;
  role_id?: number;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly API_URL = environment.apiUrl;

  constructor(private readonly http: HttpClient) {}

  /**
   * Obtener todos los usuarios
   */
  getUsers(): Observable<UserResponse> {
    return this.http.get<UserResponse>(`${this.API_URL}/user/users`).pipe(
      catchError(error => {
        console.error('Error obteniendo usuarios:', error);
        // Retornar datos vacíos en caso de error
        return of({ users: [], count: 0 });
      })
    );
  }

  /**
   * Obtener todos los roles disponibles
   */
  getRoles(): Observable<RoleResponse> {
    return this.http.get<RoleResponse>(`${this.API_URL}/user/roles`).pipe(
      catchError(error => {
        console.error('Error obteniendo roles:', error);
        // Retornar roles por defecto en caso de error
        return of({
          roles: [
            { id: 1, nombre: 'Admin', created_at: new Date().toISOString() },
            { id: 2, nombre: 'Usuario', created_at: new Date().toISOString() },
            { id: 3, nombre: 'Manager', created_at: new Date().toISOString() }
          ],
          count: 3
        });
      })
    );
  }

  /**
   * Crear un nuevo usuario
   */
  createUser(userData: CreateUserRequest): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/user/users`, userData).pipe(
      catchError(error => {
        console.error('Error creando usuario:', error);
        throw error;
      })
    );
  }

  /**
   * Actualizar un usuario existente
   */
  updateUser(id: number, userData: UpdateUserRequest): Observable<any> {
    return this.http.put<any>(`${this.API_URL}/user/users/${id}`, userData).pipe(
      catchError(error => {
        console.error('Error actualizando usuario:', error);
        throw error;
      })
    );
  }

  /**
   * Actualizar el rol de un usuario
   */
  updateUserRole(request: UpdateUserRoleRequest): Observable<any> {
    // Usar el endpoint de actualización de usuario con solo el campo role_id
    const updateData = { role_id: request.role_id };
    return this.http.put<any>(`${this.API_URL}/user/users/${request.user_id}`, updateData).pipe(
      catchError(error => {
        console.error('Error actualizando rol:', error);
        throw error;
      })
    );
  }

  /**
   * Obtener información de un usuario específico
   */
  getUserById(id: number): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/user/users/${id}`).pipe(
      catchError(error => {
        console.error('Error obteniendo usuario:', error);
        throw error;
      })
    );
  }

  /**
   * Eliminar un usuario (soft delete)
   */
  deleteUser(id: number): Observable<any> {
    return this.http.delete<any>(`${this.API_URL}/user/users/${id}`).pipe(
      catchError(error => {
        console.error('Error eliminando usuario:', error);
        throw error;
      })
    );
  }
} 