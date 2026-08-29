# Tradelog 🎴

> **Plataforma web para el registro, seguimiento y gestión de compras, ventas y logística de cartas coleccionables TCG (One Piece Card Game).**

---

## ✨ Características Principales

- **Gestión Integral de Transacciones:** Registro detallado de compras y ventas con soporte multi-ítem, cantidades, precios unitarios y subtotales.
- **Soporte Multi-moneda:** Operaciones en **CLP** (formateado como enteros con separador de miles), **USD** y **ARS**.
- **Logística & Fechas Diferenciadas:**
  - Fecha de acuerdo comercial vs. Fecha de retiro, entrega o envío.
  - Alternancia dinámica para entregas presenciales o despachos por encomienda (🚚).
- **Agenda Diaria & Checklist:** Dashboard con selector de fecha para visualizar la lista de tareas del día y marcar compras/ventas como concretadas en tiempo real sin recargar la página (AJAX).
- **Mapa Interactivo de Recorridos:** Integración con **Leaflet.js** y **OpenStreetMap** que geocodifica automáticamente las ubicaciones del día y muestra pines diferenciados (pendientes vs. concretados).
- **Libreta de Contactos & Ubicaciones:** Información de compradores y vendedores (WhatsApp con enlace directo, Instagram, correo) y ubicaciones físicas con buscador por dirección/calle/metro.
- **Catálogo con Caché Local de Imágenes:** Las imágenes oficiales se descargan y almacenan localmente mediante un proxy interno del backend, evitando restricciones de CORS/CORP en navegadores.
- **Modales Rápidos (HTMX):** Creación fluida de cartas, contactos y lugares sin salir del formulario de compra/venta.
- **Aislamiento Multi-usuario:** Cada usuario gestiona su propia información privada (compras, ventas, contactos y lugares), compartiendo únicamente el catálogo general de cartas.
- **Modo Oscuro Personalizado:** Interfaz moderna estilizada con paleta **EVA-01** (púrpura profundo, verde neón y lavanda de alto contraste).

---

## 🛠️ Requisitos & Stack Tecnológico

- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)** (gestor ultra-rápido de paquetes y entornos Python)
- **Django 5.x**
- **Bootstrap 5**, **HTMX 2.x**, **Tom-Select**, **Leaflet.js**
- **Docker & Docker Compose** (para despliegue)

---

## 🚀 Inicio Rápido en Desarrollo Local

### 1. Clonar el repositorio
`ash
git clone https://github.com/TU_USUARIO/tradelog.git
cd tradelog
`

### 2. Sincronizar dependencias con uv
`ash
uv sync
`

### 3. Aplicar migraciones
`ash
uv run python manage.py migrate
`

### 4. Crear superusuario inicial
`ash
uv run python manage.py createsuperuser
`

### 5. Iniciar el servidor de desarrollo
`ash
uv run python manage.py runserver
`
Visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en tu navegador.

---

## 📥 Importación Masiva de Cartas

Puedes importar lotes de cartas directamente desde archivos CSV:

`ash
uv run python manage.py import_cards ruta/a/cartas.csv [--image-suffix _p1] [--update]
`

**Formato esperado del CSV:**
`csv
code,name,version,notes
OP01-001,Roronoa Zoro,NORMAL,
OP01-002,Trafalgar Law,FOIL,
OP01-003,Monkey D. Luffy,ALT_ART,Arte alternativo
`
*Versiones soportadas:* NORMAL, FOIL, ALT_ART, SP, PRE.

---

## 🐳 Despliegue con Docker & Docker Compose

Para producción o servidores remotos:

1. Copiar y configurar las variables de entorno:
   `ash
   cp .env.example .env
   # Editar .env con tu SECRET_KEY y ALLOWED_HOSTS
   `

2. Construir e iniciar los contenedores:
   `ash
   docker compose up -d --build
   `

3. Aplicar migraciones y crear superusuario en el contenedor:
   `ash
   docker compose exec web uv run python manage.py migrate
   docker compose exec web uv run python manage.py createsuperuser
   `

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
