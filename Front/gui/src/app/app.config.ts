//app.config.ts
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi, withFetch } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from './core/interceptors/auth.interceptor';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withInterceptorsFromDi(), withFetch()),
    provideAnimations(), // Esto es crucial para PrimeNG
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    },
    // Configuración para PrimeNG
    {
      provide: 'PRIMENG_CONFIG',
      useValue: {
        ripple: true,
        inputStyle: 'outlined',
        zIndex: {
          modal: 1100,
          overlay: 1000,
          menu: 1000,
          tooltip: 1100
        }
      }
    }
  ]
};