from abc import ABC, abstractmethod

try:
    from langchain.agents import AgentExecutor
except ImportError:  # LangChain 1.x no longer exports AgentExecutor here
    class AgentExecutor:  # type: ignore[no-redef]
        pass


class BaseAgent(ABC):
    def __init__(self, name: str, tools: list):
        self.name = name
        self.tools = tools
        self.is_running = False

    @abstractmethod
    async def execute(self, task: dict) -> dict:
        """Ejecutar tarea principal del agente"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verificar estado del agente"""
        pass

    async def start(self):
        """Iniciar agente"""
        self.is_running = True

    async def stop(self):
        """Detener agente"""
        self.is_running = False
