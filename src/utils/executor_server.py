from fastapi import FastAPI
import asyncio, uvicorn

app = FastAPI()

@app.post("/exec")
async def exec_command(payload: dict):
    process = await asyncio.create_subprocess_shell(
        payload["command"],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    return {
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "exit_code": process.returncode,
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)