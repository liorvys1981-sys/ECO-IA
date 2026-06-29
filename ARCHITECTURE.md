# 🏗️ ECO-IA — Arquitectura Técnica

## Stack completo

```
┌─────────────────────────────────────────────────────────┐
│                 🌐  Internet / Clientes                  │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS :443 / HTTP :80
               ┌──────▼──────┐
               │    Nginx    │  (reverse proxy + rate limit)
               └──────┬──────┘
                      │ :8000
          ┌───────────▼───────────┐
          │    ECO-IA FastAPI     │  Python 3.12
          │    REST API :8000     │  Uvicorn + 4 workers
          └───────────┬───────────┘
                      │
         ┌────────────▼────────────┐
         │   🧠 ORQUESTADOR        │  OrchestratorAgent
         │   LLM: GPT-4o-mini      │  MessageBus async
         └────┬───┬───┬───┬───┬───┘
              │   │   │   │   │
    ┌─────────┤ ┌─┤ ┌─┤ ┌─┤ ┌─┤
    │ 💰 Monet│ │🔧│ │🌿│ │🛡│ │📊│
    └─────────┘ └─┘ └─┘ └─┘ └─┘
              │
    ┌─────────▼──────────────────────────┐
    │         Capa de datos              │
    │  PostgreSQL :5432  Redis :6379     │
    └────────────────────────────────────┘
              │
    ┌─────────▼──────────────────────────┐
    │         Monitoreo                  │
    │  Prometheus :9090  Grafana :3000   │
    │  AlertManager :9093                │
    └────────────────────────────────────┘
```

---

## Componentes

### FastAPI — REST API

- **Framework:** FastAPI 0.115 + Uvicorn 0.34
- **Workers:** 4 procesos Uvicorn
- **Auth:** API Keys con `hmac.compare_digest` (anti-timing)
- **Rate Limit:** 100 req/min por IP (sliding window)
- **CORS:** Configurable vía `CORS_ORIGINS`

### Agentes IA — Multi-Agent System

- **Comunicación:** `MessageBus` async pub/sub en memoria
- **Base:** `AgentBase` ABC con lifecycle hooks
- **Scheduler:** `TaskScheduler` asyncio — tareas periódicas
- **LLM:** `LLMConnector` — OpenAI o Ollama (self-hosted)

### Celery — Task Queue

- **Broker:** Redis
- **Workers:** `eco-ia-worker` (4 concurrencias)
- **Beat:** `eco-ia-beat` (scheduler distribuido)

### Base de datos

- **PostgreSQL 15:** datos persistentes (clientes, facturas, logs)
- **Redis 7:** cache, sesiones, Celery broker

### Monitoreo

- **Prometheus:** métricas de API, sistema, Docker
- **Grafana:** dashboards visuales
- **AlertManager:** alertas por email SMTP

---

## Flujo de una request

```
Cliente
  → Nginx (rate limit, proxy)
    → FastAPI (auth middleware)
      → Route handler
        → Agent / Service
          → LLM / Stripe / DB
        ← Response
      ← JSON
    ← HTTP
  ← Response
```

---

## Seguridad

| Capa | Mecanismo |
|------|-----------|
| Red | UFW firewall (puertos 22, 80, 443, 8000, 3000, 9090) |
| SSH | Fail2Ban + SSH key only |
| API | HMAC API keys, rate limiting 100 req/min |
| Webhooks | HMAC-SHA256 signature verification |
| Firewall dinámico | Auto-block IPs maliciosas (10 intentos) |
| Contenedores | Usuario no-root (`ecouser`) |
| Secrets | `.env` excluido de git, permisos 600 |
| IP validation | Octetos 0-255 + CIDR max /32 |

---

## Servidor OVHcloud b3-8

| Recurso | Especificación |
|---------|---------------|
| CPU | 3 vCores |
| RAM | 8 GB |
| Disco | 48 GB SSD |
| Red | 500 Mbit público |
| OS | Ubuntu 24.04 LTS |
| IP | 135.148.232.10 |
| Región | Virginia US-EAST-VA-1 |

### Distribución de recursos

| Servicio | RAM estimada |
|---------|-------------|
| eco-ia-api (x4) | ~800 MB |
| eco-ia-worker | ~300 MB |
| eco-ia-beat | ~150 MB |
| PostgreSQL | ~512 MB |
| Redis | ~256 MB |
| Prometheus | ~256 MB |
| Grafana | ~256 MB |
| Nginx | ~50 MB |
| **Total** | **~2.6 GB** |
| **Disponible** | **~5.4 GB libre** |

---

## Docker Compose — Servicios

```yaml
services:
  eco-ia-api      # FastAPI REST API
  eco-ia-worker   # Celery worker (tareas async)
  eco-ia-beat     # Celery beat (scheduler)
  postgres        # PostgreSQL 15
  redis           # Redis 7
  nginx           # Reverse proxy
  prometheus      # Métricas
  grafana         # Dashboards
  alertmanager    # Alertas email
  node-exporter   # Métricas del host
```

---

## Variables de entorno críticas

```bash
SERVER_IP=135.148.232.10
ECO_IA_API_KEY=           # openssl rand -hex 32
ECO_IA_ADMIN_KEY=         # openssl rand -hex 32
POSTGRES_PASSWORD=        # password fuerte
OPENAI_API_KEY=           # sk-...
STRIPE_SECRET_KEY=        # sk_live_...
GF_SECURITY_ADMIN_PASSWORD=
```
