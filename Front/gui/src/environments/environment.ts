// environment.ts - DETECCIÓN AUTOMÁTICA
// Este archivo detecta automáticamente si está en producción o desarrollo

// Detectar si estamos en producción
const isProduction = window.location.hostname !== 'localhost' && 
                    window.location.hostname !== '127.0.0.1' &&
                    !window.location.hostname.includes('localhost');

// Detectar si estamos en Vercel
const isVercel = window.location.hostname.includes('vercel.app') || 
                 window.location.hostname.includes('onrender.com');

export const environment = {
  production: isProduction || isVercel,
  apiUrl: (isProduction || isVercel) 
    ? 'https://microservicio-backend.onrender.com' 
    : 'http://localhost:4000',
  // Detección automática
  isProduction: isProduction || isVercel,
  // Log para verificar que se está usando este archivo
  buildTime: new Date().toISOString(),
  buildConfig: (isProduction || isVercel) ? 'production' : 'development',
  // Información de detección
  detectedHostname: window.location.hostname,
  isVercel: isVercel,
  isLocalhost: !isProduction && !isVercel
};
