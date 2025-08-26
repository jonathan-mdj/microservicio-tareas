//auth.guard.ts
import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { map, take } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    
    return this.authService.isAuthenticated$.pipe(
      take(1),
      map(isAuthenticated => {
        if (isAuthenticated) {
          // Verificar si la ruta requiere un rol específico
          const requiredRole = route.data?.['role'];
          if (requiredRole) {
            const user = this.authService.getCurrentUser();
            if (!user || user.role_id !== requiredRole) {
              console.log('Acceso denegado - Rol insuficiente');
              this.router.navigate(['/tasks']); // Redirigir a tareas
              return false;
            }
          }
          return true;
        } else {
          console.log('Usuario no autenticado, redirigiendo al login');
          this.router.navigate(['/auth/login'], { 
            queryParams: { returnUrl: state.url }
          });
          return false;
        }
      })
    );
  }
}

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): boolean {
    if (this.authService.isAuthenticated() && this.authService.isAdmin()) {
      return true;
    } else {
      console.log('Acceso denegado - Se requieren permisos de administrador');
      this.router.navigate(['/tasks']);
      return false;
    }
  }
}

@Injectable({
  providedIn: 'root'
})
export class GuestGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): boolean {
    if (!this.authService.isAuthenticated()) {
      return true;
    } else {
      console.log('Usuario ya autenticado, redirigiendo a tareas');
      this.router.navigate(['/tasks']);
      return false;
    }
  }
}