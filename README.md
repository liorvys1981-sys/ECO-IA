# 🌱 ECO-IA

Sistema multi-agente orientado a operación autónoma, monetización de servicios, observabilidad y seguridad. ECO-IA combina una API REST en FastAPI, agentes especializados, colas con Redis/Celery, persistencia en PostgreSQL y monitoreo con Prometheus/Grafana.

## Descripción del proyecto

ECO-IA centraliza varias capacidades en una sola plataforma:

- **Orquestación de agentes** para coordinar tareas del sistema
- **Monetización** con planes, clientes y facturación Stripe
- **Operación DevOps** con backups, healing y automatización
- **Optimización de recursos** y escalado basado en carga
- **Seguridad** con auditoría, firewall y detección de intrusiones
- **Analytics** con reportes y detección de anomalías

## Arquitectura del sistema

### Componentes principales

- **FastAPI** expone la API REST y la documentación Swagger/OpenAPI
- **PostgreSQL** almacena entidades de negocio y métricas persistentes
- **Redis** funciona como caché y broker/backend de Celery
- **Celery worker** procesa tareas asíncronas
- **Prometheus + Grafana** proveen monitoreo y visualización
- **Nginx** sirve como reverse proxy

### Arquitectura multi-agente

```text
                    ┌─────────────────────┐
                    │   🧠 ORQUESTADOR    │
                    │   Coordina todo     │
                    └──────┬──────────────┘
                           │ MessageBus / Redis
          ┌────────┬───────┼───────┬────────┬────────┐
          ▼        ▼       ▼       ▼        ▼
       💰 Monet  🔧 Dev  🌿 Res  🛡️ Sec  📊 Ana
```

### Layout del repositorio

```text
ECO-IA/
├── README.md
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.agent
├── requirements.txt
├── settings.py
├── main.py
├── orchestrator.py
├── agent_base.py
├── communication.py
├── celery_app.py
├── billing.py
├── clients.py
├── pricing.py
├── optimizer.py
├── scaler.py
├── cleaner.py
├── firewall.py
├── intrusion_detector.py
├── dashboard.py
├── predictor.py
├── reporter.py
├── prometheus.yml
├── nginx.conf
├── backup.sh
├── install.sh
├── health_check.sh
├── test_agents.py
└── test_api.py
```

## Requisitos previos

Antes de instalar ECO-IA, asegúrate de tener:

- **Python 3.12+**
- **Docker**
- **Docker Compose**
- **Git**
- Acceso a credenciales para:
  - OpenAI u Ollama
  - Stripe
  - PostgreSQL
  - Redis
  - SMTP opcional

## Guía de instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/liorvys1981-sys/ECO-IA.git
cd ECO-IA
```

### 2. Crear entorno virtual local

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 4. Preparar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las variables listadas abajo.

### 5. Levantar la plataforma con Docker Compose

```bash
docker compose up -d --build
```

### 6. Verificar estado

```bash
docker compose ps
curl http://localhost:8000/health
```

## Configuración de variables de entorno

Variables más importantes para ejecutar el sistema:

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DEBUG` | Modo debug | `false` |
| `ENVIRONMENT` | Entorno | `production` |
| `API_HOST` | Host de la API | `0.0.0.0` |
| `API_PORT` | Puerto de la API | `8000` |
| `API_WORKERS` | Workers Uvicorn | `4` |
| `ECO_IA_API_KEY` | API key pública de consumo | `change-me` |
| `ECO_IA_ADMIN_KEY` | API key administrativa | `change-me-admin` |
| `CORS_ORIGINS` | Orígenes permitidos | `*` |
| `DATABASE_URL` | Conexión PostgreSQL | `******postgres:5432/eco_ia` |
| `REDIS_URL` | Conexión Redis | `redis://redis:6379/0` |
| `LLM_PROVIDER` | Proveedor LLM | `openai` |
| `LLM_MODEL` | Modelo LLM | `gpt-4o-mini` |
| `OPENAI_API_KEY` | Clave OpenAI | `sk-...` |
| `OLLAMA_BASE_URL` | URL de Ollama | `http://localhost:11434` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Webhook de Stripe | `whsec_...` |
| `STRIPE_PUBLISHABLE_KEY` | Clave pública Stripe | `pk_live_...` |
| `SMTP_HOST` | Host SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP | `587` |
| `SMTP_USER` | Usuario SMTP | `user@example.com` |
| `SMTP_PASSWORD` | Password SMTP | `secret` |
| `ALERT_EMAILS` | Correos de alertas | `ops@example.com,admin@example.com` |
| `PROMETHEUS_PORT` | Puerto Prometheus | `9090` |
| `GRAFANA_PORT` | Puerto Grafana | `3000` |

## Cómo ejecutar el sistema

### Ejecución con Docker Compose

```bash
docker compose up -d --build
```

### Detener servicios

```bash
docker compose down
```

### Ver logs

```bash
docker compose logs -f eco-ia-api
docker compose logs -f eco-ia-worker
```

### Ejecutar API localmente

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Ejecutar worker localmente

```bash
python -m celery -A celery_app worker --loglevel=info
```

## Descripción de cada agente

### 🧠 Orquestador

Coordina a los agentes, registra su estado, programa tareas periódicas y genera decisiones o reportes ejecutivos.

### 💰 Monetización

Gestiona clientes, planes, pricing dinámico y facturación con Stripe.

### 🔧 DevOps

Automatiza backups, recuperación de servicios y tareas operativas del despliegue.

### 🌿 Recursos

Recoge métricas del sistema, evalúa presión de CPU/RAM y ejecuta escalado y limpieza.

### 🛡️ Seguridad

Administra reglas de firewall, analiza intentos de intrusión y ejecuta auditorías de seguridad.

### 📊 Analytics

Agrega métricas, detecta anomalías y genera reportes para operación y negocio.

## API endpoints disponibles

### Públicos

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Estado general del sistema |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/openapi.json` | Esquema OpenAPI |
| `GET` | `/dashboard` | Dashboard HTML |

### Servicios

Requieren header `X-API-Key`.

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/services/hosting/plans` | Lista de planes |
| `GET` | `/api/v1/services/hosting/status` | Estado del hosting |
| `POST` | `/api/v1/services/data/process` | Procesamiento de datos |

### Administración

Requieren header `X-Admin-Key`.

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/admin/health` | Salud del sistema y agentes |
| `GET` | `/api/v1/admin/metrics` | Métricas de recursos |
| `GET` | `/api/v1/admin/agents` | Inventario de agentes |
| `GET` | `/api/v1/admin/scheduler/tasks` | Tareas programadas |

### Webhooks

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/v1/webhooks/stripe` | Recepción de eventos Stripe |

## Monitoreo

Servicios expuestos por defecto:

- **API:** `http://localhost:8000`
- **Swagger:** `http://localhost:8000/docs`
- **Prometheus:** `http://localhost:9090`
- **Grafana:** `http://localhost:3000`

## Validación local

Comandos útiles:

```bash
python -m pytest -q
python -m ruff check .
```

## Contribución

1. Haz fork del repositorio
2. Crea una rama para tu cambio
3. Realiza cambios pequeños y enfocados
4. Ejecuta validaciones locales antes de abrir tu PR
5. Documenta cambios funcionales en el README o documentación relacionada
6. Abre un Pull Request con contexto claro

## Licencia

MIT
