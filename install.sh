#!/usr/bin/env bash
# =============================================================================
# ECO-IA — Installation Script
# OVHcloud US b3-8 | Ubuntu 24.04 LTS | 8GB RAM | IP: 135.148.232.10
# Usage: sudo bash scripts/install.sh
# =============================================================================
set -euo pipefail

ECO_IA_DIR="/opt/eco-ia"
ECO_IA_USER="ecouser"
SERVER_IP="135.148.232.10"
REPO_URL="https://github.com/liorvys1981-sys/ECO-IA.git"
LOG_FILE="/var/log/eco-ia-install.log"

RED="\033[0;31m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; BOLD="\033[1m"; NC="\033[0m"
info()  { echo -e "${GREEN}[INFO]${NC}  $*" | tee -a "$LOG_FILE"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE"; exit 1; }
step()  { echo -e "\n${BOLD}${GREEN}▶ $*${NC}" | tee -a "$LOG_FILE"; }

[[ "$EUID" -ne 0 ]] && error "Run as root: sudo bash scripts/install.sh"
mkdir -p "$(dirname $LOG_FILE)"; touch "$LOG_FILE"

echo -e "${GREEN}${BOLD}"
cat << 'BANNER'
  ╔══════════════════════════════════════════════════════╗
  ║   🌱 ECO-IA — OVHcloud US b3-8 | Ubuntu 24.04      ║
  ║   8GB RAM | 3 vCores | IP: 135.148.232.10           ║
  ╚══════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

step "1/10 — System update"
apt-get update -qq && apt-get upgrade -y -qq

step "2/10 — System dependencies"
apt-get install -y -qq \
    curl wget git vim tmux \
    python3 python3-venv python3-pip \
    postgresql-client redis-tools \
    rsync openssh-client \
    ufw fail2ban \
    htop iotop net-tools \
    ca-certificates gnupg lsb-release unzip

step "3/10 — Docker CE"
if ! command -v docker &>/dev/null; then
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable --now docker
    info "Docker installed: $(docker --version)"
else
    info "Docker already present: $(docker --version)"
fi

step "4/10 — App user '$ECO_IA_USER'"
if ! id "$ECO_IA_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$ECO_IA_USER"
    usermod -aG docker "$ECO_IA_USER"
    info "User '$ECO_IA_USER' created"
fi

step "5/10 — ECO-IA repository"
if [[ -d "$ECO_IA_DIR/.git" ]]; then
    sudo -u "$ECO_IA_USER" git -C "$ECO_IA_DIR" pull --ff-only
else
    git clone "$REPO_URL" "$ECO_IA_DIR"
    chown -R "$ECO_IA_USER:$ECO_IA_USER" "$ECO_IA_DIR"
fi

step "6/10 — Python virtual environment"
sudo -u "$ECO_IA_USER" python3 -m venv "$ECO_IA_DIR/.venv"
sudo -u "$ECO_IA_USER" "$ECO_IA_DIR/.venv/bin/pip" install -q --upgrade pip
sudo -u "$ECO_IA_USER" "$ECO_IA_DIR/.venv/bin/pip" install -q -r "$ECO_IA_DIR/requirements.txt"

step "7/10 — UFW Firewall"
bash "$ECO_IA_DIR/scripts/setup_firewall.sh"

step "8/10 — Fail2Ban"
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
systemctl enable --now fail2ban

step "9/10 — Environment file"
if [[ ! -f "$ECO_IA_DIR/.env" ]]; then
    cp "$ECO_IA_DIR/.env.example" "$ECO_IA_DIR/.env"
    chown "$ECO_IA_USER:$ECO_IA_USER" "$ECO_IA_DIR/.env"
    chmod 600 "$ECO_IA_DIR/.env"
    warn "⚠  Edit $ECO_IA_DIR/.env before starting!"
fi

step "10/10 — Systemd service"
cat > /etc/systemd/system/eco-ia.service << SVCEOF
[Unit]
Description=ECO-IA Autonomous System — OVHcloud b3-8
After=network.target docker.service
Requires=docker.service

[Service]
Type=forking
User=$ECO_IA_USER
WorkingDirectory=$ECO_IA_DIR
ExecStart=/usr/bin/docker compose -f $ECO_IA_DIR/docker/docker-compose.yml up -d
ExecStop=/usr/bin/docker compose -f $ECO_IA_DIR/docker/docker-compose.yml down
ExecReload=/usr/bin/docker compose -f $ECO_IA_DIR/docker/docker-compose.yml restart
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable eco-ia

(crontab -u "$ECO_IA_USER" -l 2>/dev/null; \
 echo "0 * * * * $ECO_IA_DIR/scripts/backup.sh >> /var/log/eco-ia-backup.log 2>&1") \
    | sort -u | crontab -u "$ECO_IA_USER" -

echo -e "${GREEN}${BOLD}"
cat << 'SUCCESS'
  ╔═══════════════════════════════════════════════════════════╗
  ║  ✅  ECO-IA INSTALLED — OVHcloud US b3-8                 ║
  ╠═══════════════════════════════════════════════════════════╣
  ║  1. nano /opt/eco-ia/.env  → add your API keys          ║
  ║  2. systemctl start eco-ia → start all containers       ║
  ║  3. bash /opt/eco-ia/scripts/health_check.sh            ║
  ║                                                           ║
  ║  API:        http://135.148.232.10:8000                   ║
  ║  API Docs:   http://135.148.232.10:8000/docs              ║
  ║  Grafana:    http://135.148.232.10:3000                   ║
  ║  Prometheus: http://135.148.232.10:9090                   ║
  ╚═══════════════════════════════════════════════════════════╝
SUCCESS
echo -e "${NC}"
