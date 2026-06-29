# 🌱 ECO-IA — Autonomous AI-Agent Server System

> Servidor **99.9% autónomo** con 6 Agentes IA que **se autoabastece**, **genera ingresos** y es **sostenible**.
> Deployado en **OVHcloud US b3-8** | IP: `135.148.232.10` | Ubuntu 24.04

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 ¿Qué es ECO-IA?

Sistema multi-agente de IA que trabaja 24/7 para:

1. 🔧 **Autoabastecerse** — monitoreo, auto-recuperación, backups
2. 💰 **Generar ingresos** — API de IA + hosting cobrado con Stripe
3. 🌿 **Ser sostenible** — optimización de recursos, escalado automático

---

## 🏗️ Los 6 Agentes

| Agente | Función |
|--------|---------|
| 🧠 **Orquestador** | Coordina todo, usa LLM para decisiones, reportes ejecutivos |
| 💰 **Monetización** | Clientes, facturación Stripe, pricing dinámico |
| 🔧 **DevOps** | Deploy automático, auto-healing, backups |
| 🌿 **Recursos** | Optimiza CPU/RAM, limpieza, auto-scaling |
| 🛡️ **Seguridad** | Firewall UFW, detección de intrusiones, auditorías |
| 📊 **Analytics** | Reportes diarios, predicción de anomalías |

---

## 🚀 Deploy (1 comando)

```bash
# En ubuntu@ecoia — OVHcloud US
git clone https://github.com/liorvys1981-sys/ECO-IA.git /opt/eco-ia
sudo bash /opt/eco-ia/scripts/install.sh
```

### Post-instalación:

```bash
nano /opt/eco-ia/.env          # 1. Agregar API keys
systemctl start eco-ia         # 2. Arrancar contenedores
bash /opt/eco-ia/scripts/health_check.sh  # 3. Verificar
```

---

## 🌐 Endpoints

| Servicio | URL |
|----------|-----|
| **API** | http://135.148.232.10:8000 |
| **API Docs** | http://135.148.232.10:8000/docs |
| **Grafana** | http://135.148.232.10:3000 |
| **Prometheus** | http://135.148.232.10:9090 |

---

## 📂 Estructura

```
ECO-IA/
├── agents/
│   ├── orchestrator/    # 🧠 OrchestratorAgent
│   ├── monetization/    # 💰 BillingManager, ClientManager, PricingEngine
│   ├── devops/          # 🔧 AutoHealer, BackupManager, Deployer
│   ├── resources/       # 🌿 ResourceOptimizer, AutoScaler, Cleaner
│   ├── security/        # 🛡️ SecurityAuditor, FirewallManager, IntrusionDetector
│   └── analytics/       # 📊 DashboardData, Predictor, Reporter
├── core/                # MessageBus, TaskScheduler, LLMConnector, AgentBase
├── api/                 # FastAPI + middleware + routes
├── config/              # settings.py, agents.yaml, nginx.conf
├── docker/              # Dockerfile + docker-compose.yml
├── monitoring/          # Prometheus + AlertManager
├── scripts/             # install.sh, health_check.sh, backup.sh
├── tests/               # test_agents.py + test_api.py
├── .env.example         # Template OVHcloud
└── requirements.txt
```

---

## 🐳 Docker

```bash
# Arrancar todo
docker compose -f docker/docker-compose.yml up -d

# Estado
docker compose -f docker/docker-compose.yml ps

# Logs
docker compose -f docker/docker-compose.yml logs -f eco-ia-api

# Parar
docker compose -f docker/docker-compose.yml down
```

---

## 🧪 Tests

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=.
```

---

## 🖥️ Servidor

- **Provider:** OVHcloud US
- **Modelo:** b3-8 (8GB RAM, 3 vCores, 48GB SSD)
- **OS:** Ubuntu 24.04 LTS
- **IP:** 135.148.232.10
- **Región:** Virginia (US-EAST-VA-1)
- **SSH Key:** caco_eco_ia

---

## 📄 Licencia

MIT — libre para uso personal y comercial.
