// environment.prod.ts - PRODUCCIÓN
// Este archivo se usa SOLO cuando se hace build con --configuration production

export const environment = {
  production: true,
  apiUrl: 'https://microservicio-backend.onrender.com',
  // Forzar el uso de producción
  isProduction: true,
  // Log para verificar que se está usando este archivo
  buildTime: new Date().toISOString(),
  buildConfig: 'production'
};
