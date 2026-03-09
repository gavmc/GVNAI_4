from fastapi import FastAPI, UploadFile, File
import asyncio
import uvicorn
import os

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
        "command": payload["command"],
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "exit_code": process.returncode,
    }

@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    paths = []

    for file in files:
        path = os.path.join(os.getenv("UPLOAD_PATH"), file.filename)
        contents = await file.read()
        with open(path, "wb") as f:
            f.write(contents)
        paths.append(path)
    return {"paths": paths}

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)