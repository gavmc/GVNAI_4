import docker
from docker.client import DockerClient

_client: DockerClient | None = None

def get_client():
    global _client

    if not _client:
        _client = docker.get_env()
        return _client
    
    return _client
        