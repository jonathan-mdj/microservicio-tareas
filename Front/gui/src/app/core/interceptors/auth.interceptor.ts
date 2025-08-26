//auth.interceptor.ts
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(
    private readonly authService: AuthService,
    private readonly router: Router
  ) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Obtener token del servicio de autenticación
    const token = this.authService.getToken();
    
    // Clonar la request y añadir el token si existe
    let authRequest = request;
    if (token) {
      authRequest = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    // Continuar con la request y manejar errores
    return next.handle(authRequest).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Error en interceptor:', error);
        
        // Log adicional para debug
        console.log('Status:', error.status);
        console.log('URL:', error.url);
        console.log('Error body:', error.error);
        
        // Si es error 401 (No autorizado), cerrar sesión
        if (error.status === 401) {
          console.log('Token expirado o inválido, cerrando sesión...');
          this.authService.logout();
        }
        
        // Si es error 403 (Forbidden), mostrar mensaje
        if (error.status === 403) {
          console.log('Acceso denegado - Permisos insuficientes');
          // Aquí puedes mostrar un mensaje toast o modal
        }
        
        // Si es error 400 (Bad Request), logear detalles para debug
        if (error.status === 400) {
          console.log('Error 400 - Bad Request');
          console.log('Request URL:', error.url);
          console.log('Request body:', error.error);
        }
        
        // Si es error de conexión (0 o 500+), mostrar mensaje
        if (error.status === 0 || error.status >= 500) {
          console.log('Error de conexión con el servidor');
          // Aquí puedes mostrar un mensaje de error de conexión
        }
        
        return throwError(() => error);
      })
    );
  }
}