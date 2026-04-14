from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import uuid
import zipfile

app = FastAPI()

# Serve static web files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.post("/download")
async def download_videos(links: str = Form(...)):
    # Split links by new line
    urls = [u.strip() for u in links.split("\n") if u.strip()]

    # Create download folder
    folder = f"downloads_{uuid.uuid4()}"
    os.makedirs(folder, exist_ok=True)

    downloaded_files = []

    # yt-dlp options
    ydl_opts = {
        "outtmpl": f"{folder}/%(title)s.%(ext)s",
        "format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "ignoreerrors": True
    }

    # Download each URL
    for url in urls:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if os.path.exists(filename):
                    downloaded_files.append(filename)
        except Exception as e:
            print("Error downloading:", url, e)

    # Create ZIP file
    zip_path = f"{folder}.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, os.path.basename(file))

    return FileResponse(zip_path, media_type="application/zip", filename="videos.zip")