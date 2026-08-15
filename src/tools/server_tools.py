"""Operational helpers exposed to agents."""

from agents.devops import AutoHealer, BackupManager, Deployer


class ServerTools:
    """Facade over server-side operations used by agents."""

    def __init__(self, compose_file: str = "docker-compose.yml") -> None:
        self.deployer = Deployer(compose_file=compose_file)
        self.backups = BackupManager()
        self.healer = AutoHealer()

    def deploy_service(self, service: str) -> dict:
        return self.deployer.deploy_service(service)

    def backup_now(self, label: str = "manual") -> dict:
        return self.backups.run_backup(label=label)


__all__ = ["ServerTools"]
