//register.component.ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { MessageModule } from 'primeng/message';
import { MessagesModule } from 'primeng/messages';
import { CommonModule } from '@angular/common';
import { AuthService, RegisterRequest } from '../../../core/services/auth.service';

interface Message {
  severity?: string;
  summary?: string;
  detail?: string;
  id?: any;
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CardModule,
    ButtonModule,
    InputTextModule,
    PasswordModule,
    MessageModule,
    MessagesModule,
    ReactiveFormsModule,
    CommonModule
  ],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;
  isLoading = false;
  messages: Message[] = [];
  qrBase64: string | null = null;

  constructor(
    private readonly fb: FormBuilder,
    private readonly authService: AuthService,
    private readonly router: Router,
    private readonly route: ActivatedRoute
  ) {
    this.registerForm = this.fb.group({
      username: ['', [
        Validators.required, 
        Validators.minLength(3),
        Validators.maxLength(30),
        Validators.pattern('^[a-zA-Z][a-zA-Z0-9_]*$') // Debe empezar con letra, solo letras, números y guiones bajos
      ]],
      email: ['', [
        Validators.required, 
        Validators.email,
        Validators.maxLength(100),
        Validators.pattern(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/) // Validación de email más estricta
      ]],
      password: ['', [
        Validators.required, 
        Validators.minLength(8),
        Validators.maxLength(50),
        Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
      ]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    this.messages = [];
    
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/tasks']);
    }
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      confirmPassword.setErrors({ passwordMismatch: true });
    } else {
      if (confirmPassword?.errors?.['passwordMismatch']) {
        delete confirmPassword.errors['passwordMismatch'];
        if (Object.keys(confirmPassword.errors).length === 0) {
          confirmPassword.setErrors(null);
        }
      }
    }
    return null;
  }

onSubmit(): void {
  if (this.registerForm.valid) {
    this.isLoading = true;
    this.messages = [];

    const registerData: RegisterRequest = {
      username: this.registerForm.value.username.trim(),
      email: this.registerForm.value.email.trim().toLowerCase(),
      password: this.registerForm.value.password
    };

    // 1. Log de depuración (datos que se enviarán)
    console.groupCollapsed('%c📤 Datos del Formulario', 'color: #4CAF50; font-weight: bold');
    console.table({
      Usuario: registerData.username,
      Email: registerData.email,
      'Long. Contraseña': registerData.password.length
    });
    console.groupEnd();

    // 2. Llamada al servicio
    this.authService.register(registerData).subscribe({
      next: (response) => {
        // 3. Log de éxito
        console.group('%c✅ Registro Exitoso', 'color: #4CAF50; font-weight: bold');
        console.log('Respuesta completa:', response);
        console.groupEnd();
        
        this.handleSuccess(response);
      },
      error: (error) => {
        // 4. Log de error detallado (lo que pediste)
        console.groupCollapsed('%c🛑 Error en el Registro', 'color: #f44336; font-weight: bold');
        console.log('%cTipo de Error:', 'color: #f44336', error.name || 'HttpErrorResponse');
        console.log('%cStatus HTTP:', 'color: #f44336', error.status);
        console.log('%cURL:', 'color: #f44336', error.url || window.location.href);
        console.log('%cMensaje:', 'color: #f44336', error.message);
        
        if (error.error) {
          console.group('%cRespuesta del Servidor:', 'color: #f44336');
          console.log('%cMensaje:', 'color: #f44336', error.error.message || 'No especificado');
          console.log('%cError:', 'color: #f44336', error.error.error || 'No especificado');
          console.log('%cDetalles:', 'color: #f44336', error.error.details || 'No especificado');
          console.log('%cCódigo:', 'color: #f44336', error.error.statusCode || 'No especificado');
          console.log('%cTimestamp:', 'color: #f44336', error.error.timestamp || new Date().toISOString());
          console.groupEnd();
        }
        
        console.log('%cError completo:', 'color: #f44336', error);
        console.groupEnd();

        this.handleError(error);
      },
      complete: () => {
        // 5. Log opcional cuando se completa el observable
        console.debug('Proceso de registro completado');
      }
    });
  } else {
    // 6. Log para errores de validación del formulario
    console.group('%c⚠ Validación Fallida', 'color: #FFC107; font-weight: bold');
    console.table(this.registerForm.errors);
    Object.keys(this.registerForm.controls).forEach(key => {
      const control = this.registerForm.get(key);
      if (control?.errors) {
        console.log(`%cCampo ${key}:`, 'color: #FFC107', control.errors);
      }
    });
    console.groupEnd();

    this.markFormGroupTouched();
    this.showValidationErrors();
  }
}

private handleSuccess(response: any): void {
  this.isLoading = false;
  this.messages = [{
    severity: 'success',
    summary: 'Éxito',
    detail: response.message || 'Registro completado con éxito'
  }];
  this.qrBase64 = response.otp_qr || null;
  // Solo redirigir si no hay QR (por compatibilidad)
  if (!this.qrBase64) {
    setTimeout(() => {
      this.router.navigate(['/auth/login']);
    }, 1500);
  }
}

private handleError(error: any): void {
  this.isLoading = false;
  
  let userMessage = {
    severity: 'error',
    summary: 'Error',
    detail: 'Ocurrió un error durante el registro'
  };

  if (error.status === 0) {
    userMessage.detail = 'No se pudo conectar al servidor. Verifica tu conexión.';
  } else if (error.status === 400) {
    userMessage.detail = error.error?.message || 'Datos inválidos';
    userMessage.severity = 'warn';
  } else if (error.status === 409) {
    userMessage.detail = 'El usuario o email ya existe';
  } else if (error.status >= 500) {
    userMessage.detail = 'Error en el servidor. Intenta más tarde.';
  }

  this.messages = [userMessage];
}



private parse400Error(error: any): Message {
  const serverError = error.error;
  const defaultMsg = 'Datos inválidos';

  if (!serverError) return { severity: 'error', detail: defaultMsg };

  // Caso 1: Error estructurado (API estándar)
  if (serverError.error) {
    return {
      severity: 'warn',
      detail: serverError.error
    };
  }

  // Caso 2: Mensaje directo
  if (serverError.message) {
    return {
      severity: 'warn',
      detail: serverError.message
    };
  }

  // Caso 3: Validación detallada
  if (serverError.details) {
    return {
      severity: 'warn',
      detail: Array.isArray(serverError.details) 
        ? serverError.details.join('. ') 
        : serverError.details
    };
  }

  return { severity: 'error', detail: defaultMsg };
}

  private validateFormData(data: RegisterRequest): boolean {
    // Validaciones adicionales
    if (!data.username || data.username.length < 3) {
      this.messages = [
        { severity: 'error', summary: 'Error', detail: 'El nombre de usuario debe tener al menos 3 caracteres' }
      ];
      return false;
    }

    if (!data.email || !this.isValidEmail(data.email)) {
      this.messages = [
        { severity: 'error', summary: 'Error', detail: 'El email no tiene un formato válido' }
      ];
      return false;
    }

    if (!data.password || data.password.length < 6) {
      this.messages = [
        { severity: 'error', summary: 'Error', detail: 'La contraseña debe tener al menos 6 caracteres' }
      ];
      return false;
    }

    return true;
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  private showValidationErrors(): void {
    const errors: string[] = [];
    
    Object.keys(this.registerForm.controls).forEach(key => {
      const control = this.registerForm.get(key);
      if (control && control.errors) {
        switch (key) {
          case 'username':
            if (control.errors['required']) errors.push('El nombre de usuario es requerido');
            if (control.errors['minlength']) errors.push('El nombre de usuario debe tener al menos 3 caracteres');
            if (control.errors['pattern']) errors.push('El nombre de usuario solo puede contener letras, números y guiones bajos');
            break;
          case 'email':
            if (control.errors['required']) errors.push('El email es requerido');
            if (control.errors['email']) errors.push('El email no tiene un formato válido');
            break;
          case 'password':
            if (control.errors['required']) errors.push('La contraseña es requerida');
            if (control.errors['minlength']) errors.push('La contraseña debe tener al menos 6 caracteres');
            break;
          case 'confirmPassword':
            if (control.errors['required']) errors.push('Debe confirmar la contraseña');
            if (control.errors['passwordMismatch']) errors.push('Las contraseñas no coinciden');
            break;
        }
      }
    });

    this.messages = [
      { 
        severity: 'warn', 
        summary: 'Errores de validación', 
        detail: errors.join('. ') 
      }
    ];
  }

  private markFormGroupTouched(): void {
    Object.keys(this.registerForm.controls).forEach(key => {
      const control = this.registerForm.get(key);
      control?.markAsTouched();
    });
  }

  // Getters para acceder fácilmente a los controles
  get username() {
    return this.registerForm.get('username');
  }

  get email() {
    return this.registerForm.get('email');
  }

  get password() {
    return this.registerForm.get('password');
  }

  get confirmPassword() {
    return this.registerForm.get('confirmPassword');
  }

  goToLogin(): void {
    this.router.navigate(['/auth/login']);
  }
}