# Tradelog — Documentación de Arquitectura y Desarrollo

## 1. Visión General
**Tradelog** es una aplicación web fullstack en Django diseñada para coleccionistas y comerciantes de TCG (One Piece Card Game). Permite gestionar compras y ventas, múltiples ítems con cantidades y precios, datos de contactos (WhatsApp, Instagram, email), ubicaciones físicas con geocodificación y mapas interactivos, seguimiento de retiros/entregas/envíos mediante una agenda/checklist diaria, y catálogo de cartas con imágenes oficiales en caché.

---

## 2. Stack Tecnológico

| Componente | Tecnología |
|---|---|
| **Lenguaje / Gestor** | Python 3.10+ gestionado con `uv` |
| **Framework Backend** | Django 5.x |
| **Base de Datos** | SQLite (desarrollo y producción inicial) |
| **Servidor WSGI Prod** | Gunicorn + WhiteNoise (archivos estáticos) |
| **Frontend / UI** | Django Templates + Bootstrap 5 (Tema personalizado EVA-01 Modo Oscuro) |
| **Interactividad Frontend** | HTMX 2.x, Tom-Select (búsqueda y autocompletado en selects), Leaflet.js (mapas) |
| **Mapas y Geocodificación**| OpenStreetMap + Nominatim API (con sesgo a Chile `countrycodes=cl`) |
| **Contenedorización** | Docker + Docker Compose (solo para deploy) |

---

## 3. Estructura del Proyecto

```
tradelog/
├── agents_docs/                ← Documentación viva para asistentes y desarrolladores
│   └── plan.md
├── catalog/                    ← Catálogo compartido de cartas TCG
│   ├── management/commands/    ← Comando `import_cards` para carga masiva CSV
│   ├── models.py               ← Modelo Card con versiones (NORMAL, FOIL, ALT_ART, SP, PRE)
│   └── views.py                ← Proxy y caché local de imágenes oficiales
├── contacts/                   ← Libreta de contactos privada por usuario
├── locations/                  ← Ubicaciones y direcciones privadas con geocodificación
├── transactions/               ← Compras, ventas, ítems, moneda, checklists y estados
├── tradelog/                   ← Configuración raíz del proyecto
│   ├── settings/
│   │   ├── base.py             ← Configuración compartida, WhiteNoise, i18n
│   │   ├── dev.py              ← Modo desarrollo (DEBUG=True, SQLite)
│   │   └── prod.py             ← Modo producción (DEBUG=False, decouple/env)
│   ├── forms.py                ← Formularios de autenticación estilizados
│   ├── urls.py                 ← Enrutamiento principal y cuentas
│   └── views.py                ← Landing page pública y Dashboard con mapa diario
├── templates/                  ← Plantillas HTML organizadas por app
├── media/card_cache/           ← Caché en disco de imágenes de cartas
├── Dockerfile                  ← Build para producción
├── docker-compose.yml          ← Orquestación de deploy
├── pyproject.toml              ← Dependencias del proyecto gestionadas con uv
├── uv.lock                     ← Lockfile de dependencias
└── manage.py
```

---

## 4. Principios de Arquitectura y Datos

1. **Aislamiento Multi-usuario:**
   - Modelos privados: `Purchase`, `Sale`, `Contact`, `Location` pertenecen a un `owner` (`User`). Cada usuario autenticado únicamente consulta, edita y opera sobre sus propios registros.
   - Modelo compartido: `Card` pertenece al catálogo general compartido entre todos los usuarios.
2. **Fechas diferenciadas y Logística:**
   - `date`: Fecha en que se concreta el acuerdo comercial.
   - `fulfillment_date`: Fecha programada para retiro, entrega o despacho por envío. El dashboard y el mapa del día filtran por esta fecha.
   - `is_shipping`: Booleano que alterna dinámicamente la UI entre logística presencial y despacho por encomienda.
3. **Imágenes y Seguridad CORS/CORP:**
   - Las imágenes oficiales se descargan mediante un proxy interno del backend (`/catalog/cards/<id>/image/`) y se almacenan en `media/card_cache/` para evitar bloqueos `Cross-Origin-Resource-Policy: same-site` en el navegador del cliente.
4. **Flujo de Creación Dinámica (HTMX):**
   - Los formularios de transacción permiten crear contactos, lugares y cartas en modales flotantes sin abandonar el formulario actual, inyectando el nuevo ID automáticamente en el selector Tom-Select activo.

---

## 5. Comandos de Operación Habituales

```powershell
# Ejecutar servidor de desarrollo local
uv run python manage.py runserver

# Aplicar migraciones
uv run python manage.py makemigrations
uv run python manage.py migrate

# Verificación de integridad del sistema
uv run python manage.py check

# Importar cartas desde CSV
uv run python manage.py import_cards ruta/a/archivo.csv [--image-suffix _p1] [--update]

# Crear superusuario
uv run python manage.py createsuperuser
```

---

## 6. Próximos Pasos (Roadmap)
- Pipeline de CI/CD con GitHub Actions para testing y despliegue automatizado.
- Migración opcional a PostgreSQL cuando aumente el volumen de transacciones concurrentes.
- Reportes financieros avanzados (utilidades, márgenes por carta y valor total de inventario).
- Los items de cartas pueden crearse manualmente desde el admin o via script de importación (futuro).
