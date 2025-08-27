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
  console.log('🌍 Hostname detectado:', environment.detectedHostname);
  console.log('🚀 Es Vercel:', environment.isVercel);
  console.log('🏠 Es localhost:', environment.isLocalhost);
  console.log('==========================================');
  
  // Verificar que se esté usando el environment correcto
  if (environment.production && environment.apiUrl.includes('localhost')) {
    console.error('🚨 ERROR: Se está usando environment de DESARROLLO en PRODUCCIÓN');
  } else if (!environment.production && environment.apiUrl.includes('onrender.com')) {
    console.error('🚨 ERROR: Se está usando environment de PRODUCCIÓN en DESARROLLO');
  } else {
    console.log('✅ Environment configurado correctamente');
  }
  
  // Verificación adicional para Vercel
  if (environment.isVercel && environment.apiUrl.includes('localhost')) {
    console.error('🚨 CRÍTICO: Vercel está usando localhost!');
  } else if (environment.isVercel) {
    console.log('✅ Vercel configurado correctamente para producción');
  }
}
