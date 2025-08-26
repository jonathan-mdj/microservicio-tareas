//app.routes.ts
import { Routes } from '@angular/router';
import { AuthGuard, AdminGuard, GuestGuard } from './core/guards/auth.guard';

export const routes: Routes = [
   // Ruta por defecto
   { path: '', redirectTo: '/auth/login', pathMatch: 'full' },
   
   // Rutas de autenticación (solo para usuarios no autenticados)
   {
       path: 'auth',
       canActivate: [GuestGuard],
       loadChildren: () => import('./pages/auth/auth.routes').then(m => m.AUTH_ROUTES)
   },
   
   // Dashboard (requiere autenticación)
   {
       path: 'dashboard',
       canActivate: [AuthGuard],
       loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent)
   },

   // Rutas de tareas (requiere autenticación)
   {
       path: 'tasks',
       canActivate: [AuthGuard],
       loadChildren: () => import('./pages/task/task.routes').then(m => m.TASK_ROUTES)
   },
   // Rutas de administración (solo para administradores)
   {
       path: 'admin',
       canActivate: [AuthGuard, AdminGuard],
       children: [
                       { path: '', redirectTo: 'tasks', pathMatch: 'full' },
                          {
                   path: 'graficas',
                   loadComponent: () => import('./pages/admin/user-management/user-management.component').then(m => m.GraficasComponent)
               },
           {
               path: 'roles',
               loadComponent: () => import('./pages/admin/role-management/role-management.component').then(m => m.RoleManagementComponent)
           },
           {
               path: 'system-info',
               loadComponent: () => import('./pages/admin/system-info/system-info.component').then(m => m.SystemInfoComponent)
           }
       ]
   },
   
   // Perfil de usuario
  /* {
       path: 'profile',
       canActivate: [AuthGuard],
       loadComponent: () => import('./pages/profile/profile.component').then(m => m.ProfileComponent)
   },  */
   
   // Página de error 404
   {
       path: '**',
       loadComponent: () => import('./pages/not-found/not-found.component').then(m => m.NotFoundComponent)
   },
];