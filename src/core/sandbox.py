from docker.client import DockerClient
import docker
from datetime import datetime
import httpx
import asyncio

_client: DockerClient | None = None

def get_client():
    global _client

    if not _client:
        _client = docker.from_env()
        return _client
    
    return _client
        


class SandboxSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.container = None
        self.last_used = datetime.now()

    async def start(self):
        client = get_client()
        self.container = client.containers.run(
            image="sandbox-executor",
            detach=True,
            network="gvnai-sandbox",
            name=f"sandbox-{self.session_id}",
            mem_limit="512m",
            cpu_period=100_000,
            cpu_quota=50_000,
            pids_limit=64,
            read_only=False,
            environment={"UPLOAD_PATH": "/sandbox_files"},
            tmpfs={"/tmp": "size=50m"}
        )
        await self._check_ready()

    async def _check_ready(self):
        async with httpx.AsyncClient() as http:
            for _ in range(20):
                try:
                    await http.get(f"http://sandbox-{self.session_id}:8000/health", timeout=1)
                    return
                except Exception:
                    await asyncio.sleep(0.25)

        raise RuntimeError(f"Sandbox {self.session_id} failed to start")
    
    async def exec(self, command: str) -> dict:
        self.last_used = datetime.now()
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                f"http://sandbox-{self.session_id}:8000/exec",
                json={"command": command},
                timeout=30,
            )
            return resp.json()
        
    async def upload(self, files: list[tuple[str, bytes]]) -> list[str]:

        async with httpx.AsyncClient() as http:
            resp = await http.post(
                f"http://sandbox-{self.session_id}:8000/upload",
                files=[("files", (filename, contents)) for filename, contents in files],
                timeout=30,
            )
            return resp.json()["paths"]
        
    async def destroy(self):
        if self.container:
            self.container.stop()
            self.container.remove()
            self.container = None


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, SandboxSession] = {}
        
    async def get_or_create(self, session_id: str) -> SandboxSession:
        if session_id not in self.sessions:
            session = SandboxSession(session_id)
            await session.start()
            self.sessions[session_id] = session
        
        return self.sessions[session_id]
    
    async def close_session(self, session_id: str):
        session = self.sessions.pop(session_id, None)
        if session:
            await session.destroy()

    async def close_all(self):
        for session in list(self.sessions.values()):
            await session.destroy()
        self.sessions.clear()


session_manager = SessionManager()