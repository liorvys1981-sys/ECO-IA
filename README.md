# 🌱 ECO-IA

Sistema base para un servidor **99.9% autónomo** basado en agentes IA, orientado a auto-operación, monetización y sostenibilidad.

## Arquitectura

ECO-IA está organizado alrededor de 6 agentes:

- 🧠 **Orquestador**: coordina agentes, prioridades y decisiones.
- 💰 **Monetización**: clientes, pricing dinámico y Stripe.
- 🔧 **DevOps**: deployments, auto-healing y backups.
- 🌿 **Recursos**: CPU/RAM/disco, limpieza y auto-scaling.
- 🛡️ **Seguridad**: firewall, auditoría y detección de amenazas.
- 📊 **Analytics**: reportes, KPIs y predicción de anomalías.

La base actual mantiene la implementación existente y además expone la estructura solicitada en `src/`, `config/`, `scripts/`, `monitoring/` y `tests/`.

## Estructura

```text
ECO-IA/
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── agents_config.yaml
│   └── nginx.conf
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── master_agent.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── monetization_agent.py
│   │   ├── devops_agent.py
│   │   ├── resources_agent.py
│   │   ├── security_agent.py
│   │   └── analytics_agent.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── payments/
│   │   │   ├── __init__.py
│   │   │   └── stripe_service.py
│   │   └── database/
│   │       ├── __init__.py
│   │       └── models.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── server_tools.py
│   │   ├── monitoring_tools.py
│   │   └── notification_tools.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── scripts/
│   ├── setup.sh
│   ├── start.sh
│   ├── backup.sh
│   ├── health_check.sh
│   └── setup_firewall.sh
├── monitoring/
│   ├── prometheus.yml
│   ├── alertmanager/
│   │   └── config.yml
│   └── grafana/
│       └── dashboards/
│           └── overview.json
└── tests/
    ├── __init__.py
    └── test_agents.py
```

## Stack tecnológico

- Python 3.11+
- FastAPI
- LangChain
- PostgreSQL
- Redis
- Docker + Docker Compose
- Prometheus + Grafana
- Stripe

## Requisitos previos

- Python 3.11 o superior
- Docker y Docker Compose
- Redis
- PostgreSQL
- Credenciales válidas para OpenAI/Ollama y Stripe si se quieren activar esas integraciones

## Instalación

1. Clona el repositorio.
2. Copia variables de entorno:

   ```bash
   cp .env.example .env
   ```

3. Instala dependencias Python:

   ```bash
   pip install -r requirements.txt
   pip install ruff
   ```

4. Ajusta `.env` con tus credenciales y endpoints.
5. Levanta la plataforma:

   ```bash
   bash scripts/start.sh
   ```

Para aprovisionamiento completo del servidor:

```bash
sudo bash scripts/setup.sh
```

## Variables de entorno

Las principales variables viven en `.env.example`:

- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `SMTP_*`
- `PROMETHEUS_PORT`
- `GRAFANA_PORT`

## Ejecución

- API principal: `python -m uvicorn api.main:app --reload`
- Entrada compatible solicitada: `python -m uvicorn src.main:app --reload`
- Docker Compose: `docker compose up -d`

Swagger/OpenAPI queda disponible en `/docs`.

## API disponible

Endpoints principales:

- `GET /`
- `GET /health`
- `GET /api/v1/services/hosting/plans`
- `GET /api/v1/services/hosting/ip-pricing`
- `GET /api/v1/services/hosting/status`
- `POST /api/v1/services/data/process`

## Comunicación entre agentes

La implementación existente usa `MessageBus` para coordinación interna y Redis sigue formando parte del stack operativo para cola/mensajería del sistema.

## Logging centralizado

- Configuración base en `src/utils/logger.py`
- Logs operativos en agentes, API y tareas programadas

## Scripts

- `scripts/setup.sh`: aprovisionamiento inicial
- `scripts/start.sh`: inicio del stack
- `scripts/backup.sh`: ejecución de backup
- `scripts/health_check.sh`: chequeo rápido de salud

## Tests

```bash
python -m pytest
python -m ruff check .
```

## Contribución

1. Crea una rama de trabajo.
2. Mantén la estructura anterior al agregar módulos nuevos.
3. Ejecuta tests y lint antes de enviar cambios.
4. Documenta cualquier endpoint, agente o variable nueva.
