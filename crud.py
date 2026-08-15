"""CRUD operations for ECO-IA models."""
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from database.models import (
    AgentEvent,
    APIUsage,
    Client,
    Invoice,
    PlanEnum,
    SecurityAlert,
    SystemMetric,
)

# ── Clients ─────────────────────────────────────────────────────────────


def create_client(db: Session, name: str, email: str, plan: str = "basic",
                  stripe_customer_id: str | None = None) -> Client:
    client = Client(name=name, email=email, plan=PlanEnum(plan),
                    stripe_customer_id=stripe_customer_id)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client(db: Session, client_id: uuid.UUID) -> Client | None:
    return db.query(Client).filter(Client.id == client_id).first()


def get_client_by_email(db: Session, email: str) -> Client | None:
    return db.query(Client).filter(Client.email == email).first()


def get_clients(
        db: Session,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100) -> list[Client]:
    q = db.query(Client)
    if active_only:
        q = q.filter(Client.is_active)
    return q.offset(skip).limit(limit).all()


def update_client_plan(
        db: Session,
        client_id: uuid.UUID,
        new_plan: str) -> Client | None:
    client = get_client(db, client_id)
    if client:
        client.plan = PlanEnum(new_plan)
        client.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(client)
    return client


def deactivate_client(db: Session, client_id: uuid.UUID) -> bool:
    client = get_client(db, client_id)
    if client:
        client.is_active = False
        client.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False


# ── Invoices ────────────────────────────────────────────────────────────

def create_invoice(
        db: Session,
        client_id: uuid.UUID,
        amount_cents: int,
        description: str,
        stripe_invoice_id: str | None = None) -> Invoice:
    inv = Invoice(client_id=client_id, amount_cents=amount_cents,
                  description=description, stripe_invoice_id=stripe_invoice_id)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def get_invoices(db: Session, client_id: uuid.UUID | None = None,
                 limit: int = 50) -> list[Invoice]:
    q = db.query(Invoice)
    if client_id:
        q = q.filter(Invoice.client_id == client_id)
    return q.order_by(Invoice.created_at.desc()).limit(limit).all()


def mark_invoice_paid(db: Session, invoice_id: uuid.UUID) -> Invoice | None:
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if inv:
        inv.status = "paid"
        inv.paid_at = datetime.utcnow()
        db.commit()
        db.refresh(inv)
    return inv


# ── API Usage ───────────────────────────────────────────────────────────

def record_api_usage(db: Session, client_id: uuid.UUID, endpoint: str,
                     tokens_used: int = 0, cost_usd: float = 0.0,
                     model: str | None = None) -> APIUsage:
    usage = APIUsage(client_id=client_id, endpoint=endpoint,
                     tokens_used=tokens_used, cost_usd=cost_usd, model=model)
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage


# ── System Metrics ──────────────────────────────────────────────────────

def record_metric(
        db: Session,
        cpu: float,
        ram: float,
        disk: float,
        active_clients: int = 0,
        revenue: float = 0.0) -> SystemMetric:
    metric = SystemMetric(
        cpu_percent=cpu,
        ram_percent=ram,
        disk_percent=disk,
        active_clients=active_clients,
        monthly_revenue=revenue)
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def get_recent_metrics(db: Session, limit: int = 100) -> list[SystemMetric]:
    return db.query(SystemMetric).order_by(
        SystemMetric.recorded_at.desc()).limit(limit).all()


# ── Security Alerts ─────────────────────────────────────────────────────

def create_alert(
        db: Session,
        alert_type: str,
        source_ip: str | None = None,
        severity: str = "medium",
        description: str | None = None) -> SecurityAlert:
    alert = SecurityAlert(alert_type=alert_type, source_ip=source_ip,
                          severity=severity, description=description)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session, resolved: bool = False,
               limit: int = 50) -> list[SecurityAlert]:
    return db.query(SecurityAlert).filter(
        SecurityAlert.resolved == resolved
    ).order_by(SecurityAlert.created_at.desc()).limit(limit).all()


# ── Agent Events ────────────────────────────────────────────────────────

def log_agent_event(
        db: Session,
        agent_name: str,
        event_type: str,
        payload: str | None = None,
        success: bool = True) -> AgentEvent:
    event = AgentEvent(agent_name=agent_name, event_type=event_type,
                       payload=payload, success=success)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
