from fastapi import FastAPI, UploadFile, File
import asyncio
import uvicorn
import os

app = FastAPI()

def get_unique_path(directory: str, filename: str) -> str:
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        return path

    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        path = os.path.join(directory, f"{name}_{counter}{ext}")
        if not os.path.exists(path):
            return path
        counter += 1

@app.post("/exec")
async def exec_command(payload: dict):
    process = await asyncio.create_subprocess_shell(
        payload["command"],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
    except asyncio.TimeoutError:
        process.kill()
        return {
            "command": payload["command"],
            "stdout": "",
            "stderr": "Execution timed out",
            "exit_code": -1,
        }
    

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
        path = get_unique_path(os.getenv("UPLOAD_PATH"), file.filename)
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