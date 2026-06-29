"""ECO-IA global settings — OVHcloud US b3-8 | 135.148.232.10."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# General
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

# OVHcloud Server
SERVER_IP: str = os.getenv("SERVER_IP", "135.148.232.10")
SERVER_REGION: str = os.getenv("SERVER_REGION", "US-EAST-VA-1")

# API
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
ECO_IA_API_KEY: str = os.getenv("ECO_IA_API_KEY", "change-me-in-production")
ECO_IA_ADMIN_KEY: str = os.getenv("ECO_IA_ADMIN_KEY", "change-me-in-production-admin")
CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://eco_ia:eco_ia_password@localhost:5432/eco_ia")
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# LLM
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Stripe
STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# Email
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAILS: list = [e for e in os.getenv("ALERT_EMAILS", "").split(",") if e]

# Backup storage (OVHcloud Object Storage or rsync target)
BACKUP_HOST: str = os.getenv("BACKUP_HOST", os.getenv("HETZNER_STORAGE_BOX_HOST", ""))
BACKUP_USER: str = os.getenv("BACKUP_USER", os.getenv("HETZNER_STORAGE_BOX_USER", ""))
# Legacy aliases
HETZNER_STORAGE_BOX_HOST: str = BACKUP_HOST
HETZNER_STORAGE_BOX_USER: str = BACKUP_USER
HETZNER_API_TOKEN: str = os.getenv("HETZNER_API_TOKEN", "")

# Monitoring
PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
GRAFANA_PORT: int = int(os.getenv("GRAFANA_PORT", "3000"))

# DevOps
COMPOSE_FILE: str = os.getenv("COMPOSE_FILE", str(BASE_DIR / "docker" / "docker-compose.yml"))
BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

# Security
MAX_BRUTE_FORCE_ATTEMPTS: int = int(os.getenv("MAX_BRUTE_FORCE_ATTEMPTS", "10"))
AUTO_BLOCK_INTRUDERS: bool = os.getenv("AUTO_BLOCK_INTRUDERS", "true").lower() == "true"
