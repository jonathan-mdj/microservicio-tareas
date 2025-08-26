# Sistema de Gestión de Tareas con Angular

## 📋 Descripción

Sistema completo de gestión de tareas desarrollado con Angular 19 y PrimeNG, que incluye:

- **Vista Kanban** para gestión visual de tareas
- **CRUD completo** de tareas (Crear, Leer, Actualizar, Eliminar)
- **Gestión de usuarios y roles** (solo para administradores)
- **Sistema de autenticación** con JWT
- **Interfaz moderna y responsive**

## 🚀 Características Principales

### ✅ Funcionalidades Implementadas

#### **Gestión de Tareas**
- ✅ Crear nuevas tareas con nombre, descripción, fecha límite y estado
- ✅ Editar tareas existentes
- ✅ Eliminar tareas (soft delete)
- ✅ Cambiar estado de tareas (En Progreso, En Revisión, Completada, Pausada)
- ✅ Vista Kanban con columnas organizadas por estado
- ✅ Filtros por estado y usuario
- ✅ Resumen estadístico de tareas

#### **Gestión de Usuarios y Roles**
- ✅ Lista de usuarios del sistema
- ✅ Asignación de roles (Admin, Usuario, Manager)
- ✅ Vista de tabla con paginación
- ✅ Cambio de roles con confirmación

#### **Sistema de Autenticación**
- ✅ Login con email/username y contraseña
- ✅ Registro de nuevos usuarios
- ✅ Tokens JWT con expiración
- ✅ Protección de rutas con guards
- ✅ Interceptor para agregar tokens automáticamente

#### **Interfaz de Usuario**
- ✅ Diseño moderno con gradientes y efectos visuales
- ✅ Responsive design para móviles y tablets
- ✅ Componentes PrimeNG para UI consistente
- ✅ Animaciones y transiciones suaves
- ✅ Notificaciones toast y confirmaciones

## 🛠️ Tecnologías Utilizadas

- **Angular 19** - Framework principal
- **PrimeNG 19** - Componentes de UI
- **PrimeIcons** - Iconografía
- **TypeScript** - Lenguaje de programación
- **CSS3** - Estilos y animaciones
- **RxJS** - Programación reactiva

## 📦 Instalación y Configuración

### Prerrequisitos
- Node.js 18+ 
- npm o yarn
- Angular CLI 19+

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd Front/gui
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Configurar el backend**
   - Asegúrate de que el backend esté ejecutándose en `http://localhost:4000`
   - Verifica que los servicios de autenticación y tareas estén activos

4. **Ejecutar el proyecto**
```bash
ng serve
```

5. **Acceder a la aplicación**
   - Abrir `http://localhost:4200` en el navegador

## 🏗️ Estructura del Proyecto

```
Front/gui/src/app/
├── core/
│   ├── guards/
│   │   └── auth.guard.ts          # Guards de autenticación
│   ├── interceptors/
│   │   └── auth.interceptor.ts    # Interceptor para JWT
│   └── services/
│       ├── auth.service.ts        # Servicio de autenticación
│       ├── task.service.ts        # Servicio de tareas
│       └── user.service.ts        # Servicio de usuarios
├── pages/
│   ├── auth/
│   │   ├── login/                 # Componente de login
│   │   └── register/              # Componente de registro
│   └── task/
│       ├── task.component.ts      # Componente principal de tareas
│       ├── task.component.html    # Template de tareas
│       └── task.component.css     # Estilos de tareas
└── app.component.ts               # Componente raíz
```

## 🎯 Uso del Sistema

### **1. Autenticación**
- Accede a `http://localhost:4200`
- Regístrate como nuevo usuario o inicia sesión
- El sistema redirigirá automáticamente a la gestión de tareas

### **2. Gestión de Tareas**

#### **Vista Kanban**
- Las tareas se organizan en columnas por estado
- Arrastra tareas entre columnas para cambiar estado
- Usa los filtros para ver tareas específicas
- El resumen muestra estadísticas en tiempo real

#### **Crear Nueva Tarea**
1. Haz clic en "Nueva Tarea"
2. Completa el formulario:
   - **Nombre**: Obligatorio (mínimo 3 caracteres)
   - **Descripción**: Opcional
   - **Fecha límite**: Opcional
   - **Estado**: Por defecto "En Progreso"
3. Haz clic en "Guardar"

#### **Editar Tarea**
1. Haz clic en el ícono de editar en cualquier tarjeta de tarea
2. Modifica los campos necesarios
3. Guarda los cambios

#### **Cambiar Estado**
- Usa el dropdown en cada tarjeta de tarea
- O arrastra la tarjeta entre columnas

### **3. Gestión de Usuarios (Solo Admin)**

#### **Ver Usuarios**
- Accede a la pestaña "Gestión de Usuarios"
- Verás una tabla con todos los usuarios registrados

#### **Cambiar Rol**
1. Haz clic en "Cambiar Rol" para cualquier usuario
2. Selecciona el nuevo rol del dropdown
3. Confirma el cambio

## 🎨 Características de Diseño

### **Paleta de Colores**
- **Primario**: Gradiente azul-morado (#667eea → #764ba2)
- **Estados de tareas**:
  - En Progreso: Azul (#2196F3)
  - En Revisión: Naranja (#FF9800)
  - Completada: Verde (#4CAF50)
  - Pausada: Gris (#9E9E9E)

### **Responsive Design**
- **Desktop**: Vista completa con todas las columnas
- **Tablet**: Columnas apiladas verticalmente
- **Mobile**: Interfaz optimizada para pantallas pequeñas

### **Animaciones**
- Fade-in para tarjetas de tareas
- Hover effects en botones y tarjetas
- Transiciones suaves en cambios de estado

## 🔧 Configuración Avanzada

### **Variables de Entorno**
Crea un archivo `.env` en la raíz del proyecto:
```env
API_URL=http://localhost:4000
```

### **Personalización de Estilos**
Los estilos están organizados en:
- `styles.css` - Estilos globales y overrides de PrimeNG
- `app.component.css` - Estilos de navegación
- `task.component.css` - Estilos específicos de tareas

### **Configuración de PrimeNG**
El tema actual es `lara-light-blue`. Para cambiar:
1. Modifica el import en `styles.css`
2. Opciones disponibles: `lara-light-blue`, `lara-light-indigo`, `lara-light-purple`, etc.

## 🐛 Solución de Problemas

### **Error de CORS**
- Verifica que el backend tenga CORS configurado para `http://localhost:4200`
- Asegúrate de que el API Gateway esté ejecutándose

### **Error de Autenticación**
- Verifica que el token JWT no haya expirado
- Revisa la consola del navegador para errores específicos
- Intenta hacer logout y login nuevamente

### **Tareas no se cargan**
- Verifica la conexión con el backend
- Revisa que el servicio de tareas esté activo en puerto 5003
- Comprueba los logs del backend

## 📱 Compatibilidad

- **Navegadores**: Chrome, Firefox, Safari, Edge (versiones modernas)
- **Dispositivos**: Desktop, Tablet, Mobile
- **Sistemas Operativos**: Windows, macOS, Linux

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Revisa la documentación del backend
- Consulta los logs de la aplicación
- Abre un issue en el repositorio

---

**Desarrollado con ❤️ usando Angular y PrimeNG**
