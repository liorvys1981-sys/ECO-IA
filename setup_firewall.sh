#!/usr/bin/env bash
# =============================================================================
# ECO-IA – UFW Firewall Configuration
# =============================================================================
set -euo pipefail

[[ "$EUID" -ne 0 ]] && { echo "Run as root."; exit 1; }

echo "Configuring UFW firewall for ECO-IA…"

# Reset to defaults
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# SSH (change port if using non-standard)
ufw allow 22/tcp comment "SSH"

# HTTP/HTTPS
ufw allow 80/tcp  comment "HTTP"
ufw allow 443/tcp comment "HTTPS"

# ECO-IA API (internal access only – use Nginx in prod)
ufw allow 8000/tcp comment "ECO-IA API"

# Monitoring (restrict to trusted IPs in production)
ufw allow 9090/tcp comment "Prometheus"
ufw allow 3000/tcp comment "Grafana"

# Rate limiting for SSH
ufw limit 22/tcp comment "SSH rate limit"

# Enable
ufw --force enable
ufw status verbose

echo "✅ Firewall configured."
