// environment-check.ts
// Este archivo verifica qué environment se está usando
// NOTA: Angular automáticamente selecciona el archivo correcto según la configuración de build

import { environment } from '../environments/environment';

export function logEnvironmentInfo() {
  console.log('🔍 ===== VERIFICACIÓN DE ENVIRONMENT =====');
  console.log('📁 Archivo usado:', environment.buildConfig || 'unknown');
  console.log('🌐 API URL:', environment.apiUrl);
  console.log('⚙️ Production:', environment.production);
  console.log('🏗️ Build Config:', environment.buildConfig);
  console.log('⏰ Build Time:', environment.buildTime);
  console.log('==========================================');
  
  // Verificar que se esté usando el environment correcto
  if (environment.production && environment.apiUrl.includes('localhost')) {
    console.error('🚨 ERROR: Se está usando environment de DESARROLLO en PRODUCCIÓN');
  } else if (!environment.production && environment.apiUrl.includes('onrender.com')) {
    console.error('🚨 ERROR: Se está usando environment de PRODUCCIÓN en DESARROLLO');
  } else {
    console.log('✅ Environment configurado correctamente');
  }
}
