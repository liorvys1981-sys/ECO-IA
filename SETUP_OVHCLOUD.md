# 🚀 ECO-IA — Guía de Instalación en OVHcloud US

## Servidor
- **Provider:** OVHcloud US
- **Modelo:** b3-8 (8GB RAM, 3 vCores, 48GB SSD)
- **OS:** Ubuntu 24.04 LTS
- **IP:** 135.148.232.10
- **Región:** Virginia (US-EAST-VA-1)
- **SSH Key:** caco_eco_ia

---

## Paso 1 — Conectar al servidor

```bash
ssh ubuntu@135.148.232.10
```

---

## Paso 2 — Clonar el repositorio

```bash
git clone https://github.com/liorvys1981-sys/ECO-IA.git /opt/eco-ia
cd /opt/eco-ia
```

---

## Paso 3 — Ejecutar instalación automática

```bash
sudo bash scripts/install.sh
```

El script hace automáticamente:
1. Actualiza el sistema (apt update/upgrade)
2. Instala dependencias (curl, git, python3, etc.)
3. Instala Docker CE + Docker Compose
4. Crea el usuario `ecouser`
5. Configura Python virtual environment
6. Configura UFW Firewall
7. Configura Fail2Ban
8. Crea el archivo `.env` desde `.env.example`
9. Instala el servicio systemd `eco-ia`
10. Configura backups horarios (cron)

---

## Paso 4 — Configurar variables de entorno

```bash
nano /opt/eco-ia/.env
```

Variables críticas a completar:

```bash
# Generar con: openssl rand -hex 32
ECO_IA_API_KEY=TU_KEY_AQUI
ECO_IA_ADMIN_KEY=TU_ADMIN_KEY_AQUI

# PostgreSQL
POSTGRES_PASSWORD=password_fuerte_aqui

# OpenAI
OPENAI_API_KEY=sk-tu-clave-openai

# Stripe
STRIPE_SECRET_KEY=sk_live_tu-clave-stripe
STRIPE_PUBLISHABLE_KEY=pk_live_tu-clave-stripe
STRIPE_WEBHOOK_SECRET=whsec_tu-secreto

# Email alertas
SMTP_HOST=smtp.gmail.com
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
ALERT_EMAILS=liogg35@gmail.com

# Grafana
GF_SECURITY_ADMIN_PASSWORD=password_grafana
```

---

## Paso 5 — Arrancar el sistema

```bash
systemctl start eco-ia
systemctl status eco-ia
```

---

## Paso 6 — Verificar estado

```bash
bash /opt/eco-ia/scripts/health_check.sh
```

---

## Accesos

| Servicio | URL |
|----------|-----|
| **API** | http://135.148.232.10:8000 |
| **API Docs** | http://135.148.232.10:8000/docs |
| **Grafana** | http://135.148.232.10:3000 |
| **Prometheus** | http://135.148.232.10:9090 |

---

## Comandos útiles

```bash
# Ver logs de todos los contenedores
docker compose -f /opt/eco-ia/docker/docker-compose.yml logs -f

# Ver solo la API
docker compose -f /opt/eco-ia/docker/docker-compose.yml logs -f eco-ia-api

# Estado de contenedores
docker compose -f /opt/eco-ia/docker/docker-compose.yml ps

# Reiniciar todo
systemctl restart eco-ia

# Parar todo
systemctl stop eco-ia

# Actualizar desde GitHub
cd /opt/eco-ia && git pull && \
  docker compose -f docker/docker-compose.yml up -d --build
```

---

## Puertos abiertos (UFW)

| Puerto | Protocolo | Servicio |
|--------|-----------|---------|
| 22 | TCP | SSH |
| 80 | TCP | HTTP / Nginx |
| 443 | TCP | HTTPS |
| 8000 | TCP | ECO-IA API |
| 3000 | TCP | Grafana |
| 9090 | TCP | Prometheus |
