 // environment.prod.ts - PRODUCCIÓN FORZADA
// Este archivo SIEMPRE se usa en producción, sin importar la configuración

export const environment = {
  production: true,
  apiUrl: 'https://microservicio-backend.onrender.com',
  // Forzar el uso de producción
  isProduction: true,
  // Log para verificar que se está usando este archivo
  buildTime: new Date().toISOString(),
  buildConfig: 'production',
  // FORZAR URL de producción
  forceProductionUrl: true
};

// Verificación adicional
if (environment.apiUrl.includes('localhost')) {
  throw new Error('🚨 CRÍTICO: environment.prod.ts contiene localhost!');
}
