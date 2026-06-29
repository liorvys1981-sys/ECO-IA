# 🤖 ECO-IA — Documentación de Agentes

## Arquitectura Multi-Agente

```
                    ┌─────────────────────┐
                    │   🧠 ORQUESTADOR    │
                    │   Coordina todo     │
                    └──────┬──────────────┘
                           │ MessageBus
          ┌────────┬───────┼───────┬────────┐
          ▼        ▼       ▼       ▼        ▼
       💰 Monet  🔧 Dev  🌿 Res  🛡️ Sec  📊 Ana
```

---

## 🧠 Orquestador (`agents/orchestrator/`)

**Clase:** `OrchestratorAgent`

El agente maestro. Coordina a todos los demás agentes, toma decisiones usando LLM y genera reportes ejecutivos.

### Responsabilidades
- Registrar y monitorear el estado de cada agente
- Enrutar tareas al agente correcto
- Tomar decisiones de alto nivel con OpenAI/Ollama
- Generar reportes ejecutivos cada hora
- Manejar alertas de otros agentes

### Tareas programadas
| Tarea | Intervalo | Descripción |
|-------|-----------|-------------|
| `health_check` | 60s | Ping a todos los agentes |
| `executive_report` | 3600s | Reporte ejecutivo con LLM |

### Configuración (`config.yaml`)
```yaml
heartbeat_interval: 30
health_check_interval: 60
report_interval: 3600
llm:
  provider: openai
  model: gpt-4o-mini
```

---

## 💰 Monetización (`agents/monetization/`)

Gestiona clientes, facturación Stripe y pricing dinámico.

### Módulos

**`PricingEngine`** — Precios dinámicos según demanda
```python
engine = PricingEngine()
price = engine.get_price('pro', usage_pct=80)  # surge pricing
plans = engine.list_plans()  # basic/pro/enterprise
```

| Plan | Precio base | API calls/mes | Storage |
|------|-------------|---------------|---------|
| Basic | $9.99 | 10,000 | 10 GB |
| Pro | $49.99 | 100,000 | 100 GB |
| Enterprise | $199.99 | 1,000,000 | 1 TB |

**`ClientManager`** — CRUD de clientes
```python
cm = ClientManager()
client = cm.create_client('Nombre', 'email@domain.com', 'pro')
cm.upgrade_plan(client.client_id, 'enterprise')
opps = cm.detect_upsell_opportunities()
```

**`BillingManager`** — Stripe integration
```python
bm = BillingManager()
customer = await bm.create_customer('email@domain.com', 'Nombre')
subscription = await bm.create_subscription(customer['id'], 'price_xxx')
invoice = await bm.create_invoice(customer['id'], 4999, 'Pro plan')
```

---

## 🔧 DevOps (`agents/devops/`)

Deploy automático, auto-healing y backups.

### Módulos

**`AutoHealer`** — Monitorea y reinicia servicios Docker caídos
```python
healer = AutoHealer(
    services=['eco-ia-api', 'eco-ia-worker', 'eco-ia-postgres'],
    check_interval=60,
    max_restart_attempts=3
)
await healer.start()
```

**`Deployer`** — Gestiona deploys Docker Compose
```python
deployer = Deployer(compose_file='docker/docker-compose.yml')
deployer.deploy_service('eco-ia-api')
deployer.apply_security_updates()
status = deployer.get_service_status()
```

**`BackupManager`** — Backups a storage remoto vía rsync
```python
bm = BackupManager(
    local_paths=['/opt/eco-ia/data', '/opt/eco-ia/config'],
    retention_days=30
)
result = bm.run_backup(label='daily')
```

---

## 🌿 Recursos (`agents/resources/`)

Optimización de CPU/RAM, escalado y limpieza.

### Módulos

**`ResourceOptimizer`** — Métricas en tiempo real
```python
opt = ResourceOptimizer(cpu_threshold=85.0, ram_threshold=90.0)
metrics = opt.get_metrics()
# {'cpu_percent': 45.2, 'ram_percent': 62.1, 'disk_percent': 23.5, ...}
analysis = opt.analyse()
# {'status': 'healthy', 'recommendations': [...]}
```

**`AutoScaler`** — Escala réplicas Docker según carga
```python
scaler = AutoScaler(
    min_replicas=1, max_replicas=10,
    scale_up_cpu_threshold=70.0,
    scale_down_cpu_threshold=30.0
)
scaler.evaluate_and_scale('eco-ia-api', cpu_percent=82.0)
```

**`Cleaner`** — Limpieza automática de logs y artefactos Docker
```python
cleaner = Cleaner(max_log_age_days=7, max_log_size_mb=100.0)
cleaner.run_all()  # logs + temp + docker prune
```

---

## 🛡️ Seguridad (`agents/security/`)

Firewall dinámico, detección de intrusiones y auditorías.

### Módulos

**`FirewallManager`** — Control de UFW
```python
fw = FirewallManager()
fw.block_ip('1.2.3.4', reason='brute force')
fw.allow_port(8000, 'tcp')
fw.get_status()
```

**`IntrusionDetector`** — Análisis de `/var/log/auth.log`
```python
detector = IntrusionDetector(brute_force_threshold=10)
threats = detector.analyse_auth_log()
suspicious = detector.get_suspicious_ips()
```

**`SecurityAuditor`** — Auditorías periódicas
```python
auditor = SecurityAuditor()
report = auditor.run_full_audit()
# checks: puertos abiertos, logins fallidos, sudo usage, world-writable files
```

---

## 📊 Analytics (`agents/analytics/`)

Reportes diarios, predicción de anomalías y dashboard.

### Módulos

**`Predictor`** — Detección de anomalías con z-score
```python
predictor = Predictor(window_size=20, z_score_threshold=2.5)
predictor.record('cpu', 45.2)
is_anomaly, z_score = predictor.is_anomaly('cpu', 95.0)
next_val = predictor.predict_next('cpu')
```

**`DashboardData`** — Agrega métricas para Grafana
```python
dashboard = DashboardData()
snapshot = dashboard.snapshot(
    resources={'cpu_percent': 30, 'ram_percent': 40},
    monetization={'active_clients': 5, 'monthly_revenue_usd': 499.95},
    security={'total_alerts': 0, 'high_severity': 0}
)
kpis = dashboard.get_kpis()
# system_health: 'healthy' | 'warning' | 'critical'
```

**`Reporter`** — Reportes por email SMTP
```python
reporter = Reporter(
    smtp_host='smtp.gmail.com',
    smtp_user='tu@gmail.com',
    to_emails=['liogg35@gmail.com']
)
reporter.send_daily_report_email(data)
```

---

## MessageBus — Comunicación entre agentes

```python
bus = MessageBus()

# Suscribir
await bus.subscribe('security', handle_message)

# Publicar a un agente específico
await bus.publish(Message(
    sender='orchestrator',
    target='security',
    content={'type': 'audit_request'}
))

# Broadcast a todos
await bus.publish(Message('orchestrator', '*', {'type': 'health_ping'}))
```
