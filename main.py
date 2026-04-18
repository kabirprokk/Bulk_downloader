from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
import yt_dlp
import os
import uuid
import zipfile

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/download")
async def download_videos(links: str = Form(...)):
    urls = [u.strip() for u in links.split("\n") if u.strip()]

    folder = f"downloads_{uuid.uuid4()}"
    os.makedirs(folder, exist_ok=True)

    downloaded_files = []

    ydl_opts = {
        "outtmpl": f"{folder}/%(title)s.%(ext)s",
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "ignoreerrors": True
    }

    for url in urls:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    filename = ydl.prepare_filename(info)
                    if os.path.exists(filename):
                        downloaded_files.append(filename)
        except Exception as e:
            print("Error:", e)

    zip_path = f"{folder}.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, os.path.basename(file))

    return FileResponse(zip_path, media_type="application/zip", filename="videos.zip")
