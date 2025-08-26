//task.routes.ts
import { Routes } from '@angular/router';

export const TASK_ROUTES: Routes = [
    {
        path: '',
        loadComponent: () => import('./task.component').then(m => m.TaskComponent)
    }
];