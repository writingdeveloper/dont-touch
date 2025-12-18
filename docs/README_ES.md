# Don't Touch 🛡️

**Asistente para la Corrección de Tricotilomanía**

[한국어](README_KO.md) | [English](../README.md) | [日本語](README_JA.md) | [中文](README_ZH.md) | [Русский](README_RU.md)

---

## Introducción

Don't Touch es una aplicación de escritorio diseñada para ayudar a corregir el hábito de tocarse o arrancarse el cabello inconscientemente (Tricotilomanía).

Utilizando tu webcam, rastrea los movimientos de las manos en tiempo real y te alerta cuando tu mano se acerca a tu cara o cabeza, ayudándote a tomar conciencia del hábito.

## Características Principales

- 🎥 **Detección en Tiempo Real** - Rastrea la posición de manos y cara mediante webcam
- 🔔 **Alertas Instantáneas** - Advertencias sonoras y visuales cuando las manos se acercan a la cabeza
- 📊 **Estadísticas y Seguimiento** - Registro y análisis de toques diarios/semanales
- 📅 **Vista de Calendario** - Resumen mensual de hábitos de un vistazo
- 🔥 **Función de Racha** - Seguimiento de días consecutivos sin toques para motivación
- ⚙️ **Configuración Personalizable** - Ajusta sensibilidad, sonidos de alerta, tiempo de espera
- 🌐 **Soporte Multiidioma** - Coreano, inglés, japonés, chino, español, ruso
- 🖥️ **Bandeja del Sistema** - Se ejecuta silenciosamente en segundo plano
- 🔄 **Verificación Automática de Actualizaciones** - Notifica cuando hay una nueva versión disponible
- 📷 **Alternar Vista Previa** - Desactiva la vista previa de la cámara para ahorrar CPU (la detección continúa)

## Descarga e Instalación

### Windows

1. Descarga `DontTouch_Setup_x.x.x.exe` desde la página de [Releases](https://github.com/writingdeveloper/dont-touch/releases)
2. Ejecuta el instalador y sigue el asistente de configuración
3. Inicia desde el Menú de Inicio o el acceso directo del Escritorio

**Características del Instalador:**
- Accesos directos en Escritorio y Menú de Inicio
- Opción de inicio automático con Windows
- Desinstalación fácil desde el Panel de Control
- Notificaciones automáticas de actualizaciones

> ⚠️ **Advertencia de Seguridad de Windows**
>
> Dado que esta aplicación aún no está firmada digitalmente, Windows puede mostrar una advertencia de seguridad:
>
> **Windows SmartScreen:**
> 1. Haz clic en "Más información"
> 2. Haz clic en "Ejecutar de todos modos"
>
> **Windows 11 Smart App Control:**
> - Si Smart App Control está en modo "Evaluación" u "Activado", la aplicación puede ser bloqueada
> - Desactivar temporalmente: Configuración → Privacidad y seguridad → Seguridad de Windows → Control de aplicaciones y navegador → Smart App Control → Desactivado
> - Puedes reactivarlo después de la instalación
>
> 🔐 **Firma de Código Próximamente**: Planeamos implementar la firma de código a través de [SignPath](https://signpath.io) para proyectos de código abierto para eliminar estas advertencias en futuras versiones.

### Requisitos

- Windows 10/11 (64-bit)
- Webcam (integrada o externa)

## Cómo Usar

### Uso Básico

1. **Inicia la aplicación** - Ejecuta desde el Menú de Inicio o acceso directo del Escritorio
2. **Comienza el monitoreo** - Haz clic en el botón "Iniciar"
3. **Trabaja normalmente** - La aplicación monitorea en segundo plano
4. **Recibe alertas** - Recibe notificaciones cuando las manos se acercan a tu cabeza

### Ajustar Configuración

- **Sensibilidad** - Valores más bajos significan detección más sensible
- **Tiempo de Activación** - Tiempo de espera antes de que se active la alerta
- **Tiempo de Espera** - Tiempo entre alertas consecutivas

### Bandeja del Sistema

- Continúa ejecutándose en la bandeja incluso cuando se cierra la ventana
- Haz clic en el icono de la bandeja para abrir/cerrar la ventana
- Clic derecho para acceso rápido al menú

## Ver Estadísticas

- **Gráfico Diario** - Analiza patrones de toques por hora del día
- **Gráfico Semanal** - Ve el estado de toques por día de la semana
- **Calendario** - Visualiza los conteos mensuales de toques
- **Racha** - Verifica días consecutivos sin toques

## Preguntas Frecuentes

### La webcam no funciona
- Verifica si otra aplicación está usando la webcam
- Asegúrate de que los controladores de la webcam estén actualizados
- Verifica que la aplicación tenga permisos de cámara

### La detección es muy sensible / no lo suficiente
- Ajusta la sensibilidad en la configuración
- Intenta aumentar o disminuir el tiempo de activación

### Quiero cambiar el sonido de alerta
- Puedes seleccionar sonidos de alerta o silenciar en la configuración

## Privacidad

- Todos los datos se almacenan **solo localmente**
- Las imágenes de la webcam **nunca se envían a servidores**
- **No requiere conexión a internet** (funciona sin conexión)

## Comentarios y Soporte

- **Reportar Errores**: [GitHub Issues](https://github.com/writingdeveloper/dont-touch/issues)
- **Solicitar Funciones**: [GitHub Issues](https://github.com/writingdeveloper/dont-touch/issues)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](../LICENSE) para más detalles.

---

<p align="center">
  <b>Los hábitos comienzan con la conciencia. ¡Construye hábitos saludables con Don't Touch! 💪</b>
</p>
