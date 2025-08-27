// environment.ts - DESARROLLO LOCAL
// Este archivo se usa SOLO cuando se hace build con --configuration development

export const environment = {
  production: false,
  apiUrl: 'http://localhost:4000',
  // Forzar el uso de desarrollo
  isProduction: false,
  // Log para verificar que se está usando este archivo
  buildTime: new Date().toISOString(),
  buildConfig: 'development'
};
