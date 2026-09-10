# 💰 ECO-IA — Guía de Monetización con Stripe

## Flujo de ingresos

```
Cliente → API ECO-IA → Stripe → BillingManager → Base de datos
```

---

## Configuración Stripe

### 1. Obtener claves API

Ve a [dashboard.stripe.com](https://dashboard.stripe.com) → Developers → API keys

```bash
# En .env
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx
```

### 2. Crear productos en Stripe

```bash
# Plan Basic — $9.99/mes
stripe products create --name="ECO-IA Basic"
stripe prices create --product=prod_xxx --unit-amount=999 --currency=usd --recurring[interval]=month

# Plan Pro — $49.99/mes
stripe products create --name="ECO-IA Pro"
stripe prices create --product=prod_xxx --unit-amount=4999 --currency=usd --recurring[interval]=month

# Plan Enterprise — $199.99/mes
stripe products create --name="ECO-IA Enterprise"
stripe prices create --product=prod_xxx --unit-amount=19999 --currency=usd --recurring[interval]=month
```

### 3. Configurar webhook

En Stripe Dashboard → Webhooks → Add endpoint:
- URL: `http://135.148.232.10:8000/api/v1/webhooks/stripe`
- Eventos: `customer.subscription.created`, `customer.subscription.deleted`, `invoice.payment_succeeded`, `invoice.payment_failed`

---

## API de facturación

### Crear cliente
```bash
curl -X POST http://135.148.232.10:8000/api/v1/services/ai/complete \
  -H "X-API-Key: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hola ECO-IA", "max_tokens": 100}'
```

### Ver planes disponibles
```bash
curl http://135.148.232.10:8000/api/v1/services/hosting/plans \
  -H "X-API-Key: TU_API_KEY"
```

---

## Planes y precios

| Plan | Precio | API Calls | Storage | Soporte |
|------|--------|-----------|---------|---------|
| **Basic** | $9.99/mes | 10,000 | 10 GB | Comunidad |
| **Pro** | $49.99/mes | 100,000 | 100 GB | Email |
| **Enterprise** | $199.99/mes | 1,000,000 | 1 TB | Dedicado |

### Pricing dinámico (surge)

Cuando el servidor está bajo alta carga, los precios suben automáticamente:

| Carga CPU | Multiplicador |
|-----------|--------------|
| < 50% | 1.0x (normal) |
| 50-75% | 1.1x |
| 75-90% | 1.25x |
| > 90% | 1.5x (peak) |

---

## Precios IP OVHcloud US

Los precios de infraestructura IP ahora se reflejan para **EE.UU.** en **USD** mediante el catálogo `GE-A8CCF`.

### Cloud

| Producto | Precio mensual |
|----------|----------------|
| Floating IPv4 | $3.50 |
| Floating IPv6 | $1.50 |
| Primary IPv4 | $0.60 |
| Primary IPv6 | Gratis |

### Servidores dedicados

| Producto | Precio mensual | Configuración |
|----------|----------------|---------------|
| Primary IPv4 | $1.90 | - |
| Additional single IP | $1.90 | $6.00 |
| IP subnet /29 | $16.00 | $39.00 |
| IP subnet /28 | $31.00 | $67.00 |
| IP subnet /27 | $61.00 | $121.00 |
| IP subnet /26 | $121.00 | $221.00 |
| IP subnet /25 | $242.00 | $299.00 |
| IP subnet /24 | $484.00 | $732.00 |

### API

```bash
curl http://135.148.232.10:8000/api/v1/services/hosting/ip-pricing \
  -H "X-API-Key: TU_API_KEY"
```

---

## Upselling automático

El agente de monetización detecta oportunidades automáticamente:

- Cliente en **Basic** con gasto > $50/mes → sugiere **Pro**
- Cliente en **Pro** con gasto > $200/mes → sugiere **Enterprise**

```python
opps = client_manager.detect_upsell_opportunities()
# [{'client_id': '...', 'suggested_plan': 'pro', 'reason': 'High monthly spend'}]
```

---

## Revenue proyectado

| Clientes | Plan | MRR |
|----------|------|-----|
| 10 | Basic | $99.90 |
| 5 | Pro | $249.95 |
| 2 | Enterprise | $399.98 |
| **Total** | | **$749.83/mes** |

Con 100 clientes mixtos: ~$3,000-8,000 MRR
