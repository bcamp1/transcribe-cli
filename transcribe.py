#!/usr/bin/env python3

import typer
import subprocess
import os
from pathlib import Path

transcribe_path = Path("~/transcribe")
ENV_VAR_NAME = "TRANSCRIBE_PATH"

app = typer.Typer()

def panic(message: str):
    print(message)
    exit(1)

def execute_command_safe(command: str):
    print("Running Command: " + command)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        panic("Error: The above command failed")
        return ""

def get_filename_from_url(url: str, video: bool = False):
    title = execute_command_safe("yt-dlp --get-title " + url)
    filename = title.lower().strip().replace(' ', '-')
    if video:
        filename += ".mp4"
    else:
        filename += ".mp3"
    print(filename)
    return filename

def get_filename_from_search(search_str: str, video: bool = False):
    filename = search_str.lower().strip().replace(' ', '-')
    if video:
        filename += ".mp4"
    else:
        filename += ".mp3"
    return filename

def download_url(url: str, output_fname: str):
    extension = output_fname.split('.')[1]
    if extension == "mp3":
        include_video = False
    elif extension == "mp4":
        include_video = True
    else:
        include_video = False
        panic("Invalid extension type: " + extension)

    full_path = transcribe_path / "sources" / output_fname

    yt_dlp_options = "-o " + str(full_path)

    if include_video:
        yt_dlp_options += " -t mp4"
    else:
        yt_dlp_options += " -t mp3"

    yt_dlp_cmd = f'yt-dlp {yt_dlp_options} "{url}"'
    print(execute_command_safe(yt_dlp_cmd))

def get_url_from_search(search_str: str):
    search_cmd = f'yt-dlp "ytsearch1:{search_str}" --get-id'
    id = execute_command_safe(search_cmd).strip()
    url = "https://www.youtube.com/watch?v=" + id
    print(url)
    return url

@app.command()
def fetch(search_str: str, video: bool = False):
    print("Finding URL from search term...")
    url = get_url_from_search(search_str)
    output_fname = get_filename_from_search(search_str, video=video)     
    print("Downloading " + url)
    download_url(url, output_fname)

@app.command()
def fetch_url(url: str, video: bool = False):
    output_fname = get_filename_from_url(url, video=video)     
    print("Downloading " + url)
    download_url(url, output_fname)

@app.command()
def open(name: str):
    print("Open " + name)

if __name__ == "__main__":
    # Get path from environment variable
    env_path = os.environ.get(ENV_VAR_NAME)
    if env_path is not None:
        transcribe_path = Path(env_path)
    print("Using path " + str(transcribe_path))
    execute_command_safe("mkdir -p " + str(transcribe_path))
    app()


