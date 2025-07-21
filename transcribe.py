#!/usr/bin/python3

import typer
import subprocess
import os
from pathlib import Path
import questionary

ENV_VAR_NAME = "TRANSCRIBE_PATH"

transcribe_path = Path("/")
transcribe_path_sources = Path("/")
transcribe_path_projects = Path("/")

app = typer.Typer()

def panic(message: str):
    print(message)
    exit(1)

def execute_command_safe(command: str, silent: bool = False):
    if not silent:
        print("Running Command: " + command)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() + '\n' + result.stderr.strip()
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

    full_path = transcribe_path_sources / output_fname

    yt_dlp_options = "-o " + str(full_path)

    if include_video:
        yt_dlp_options += " -t mp4"
    else:
        yt_dlp_options += " -t mp3"

    yt_dlp_cmd = f'yt-dlp {yt_dlp_options} "{url}"'
    print(execute_command_safe(yt_dlp_cmd))

def open_transcribe_at_relative(path: str):
    open_transcribe_at_absolute(transcribe_path_sources / path)

def open_transcribe_at_absolute(path: Path):
    execute_command_safe('open -a Transcribe! "' + str(path) + '" &')

def get_url_from_search(search_str: str):
    search_cmd = f'yt-dlp "ytsearch1:{search_str}" --get-id'
    id = execute_command_safe(search_cmd).strip()
    url = "https://www.youtube.com/watch?v=" + id
    print(url)
    return url

@app.command()
def fetch(search_str: str, video: bool = False, open: bool = False):
    print("Finding URL from search term...")
    url = get_url_from_search(search_str)
    output_fname = get_filename_from_search(search_str, video=video)     
    print("Downloading " + url)
    download_url(url, output_fname)
    if open:
        open_transcribe_at_relative(output_fname)

@app.command()
def fetch_url(url: str, video: bool = False, open: bool = False):
    output_fname = get_filename_from_url(url, video=video)     
    print("Downloading " + url)
    download_url(url, output_fname)
    if open:
        open_transcribe_at_relative(output_fname)

@app.command()
def open():
    global transcribe_path_sources
    selected = choose_from_dir(transcribe_path_sources, "Select file to open:")
    full_path = transcribe_path_sources / selected
    open_transcribe_at_absolute(full_path)

@app.command()
def rm():
    global transcribe_path_sources
    selected = choose_from_dir(transcribe_path_sources, "Select file to remove:")
    full_path = transcribe_path_sources / selected
    execute_command_safe('rm "' + str(full_path) + '"')

def ls_dir(dir: Path):
    files = [f for f in dir.iterdir() if f.is_file()]
    return files

def choose_from_dir(dir: Path, message: str):
    ls_files = ls_dir(dir)
    names = [str(f.name) for f in ls_files]
    allowed_extensions = ["mp3", "mp4", "xsc"]
    
    vetted_names = []
    for n in names:
        try:
            ext = n.split(".")[1]
            if ext in allowed_extensions:
                vetted_names.append(n)
        except Exception:
            pass

    selected = questionary.select(message, choices=vetted_names).ask()
    print("You selected:", selected)
    return selected

def set_transcribe_path(path: Path):
    global transcribe_path
    global transcribe_path_sources
    global transcribe_path_projects
    transcribe_path = path
    transcribe_path_sources = transcribe_path / "sources"
    transcribe_path_projects = transcribe_path / "projects"
    execute_command_safe("mkdir -p " + str(transcribe_path), silent=True)
    execute_command_safe("mkdir -p " + str(transcribe_path_sources), silent=True)
    execute_command_safe("mkdir -p " + str(transcribe_path_projects), silent=True)

if __name__ == "__main__":
    # Get path from environment variable
    env_path = os.environ.get(ENV_VAR_NAME)
    if env_path is not None:
        new_path = Path(env_path)
    else:
        new_path = Path("/Users/bransoncamp/transcribe")
    
    set_transcribe_path(new_path)
    print("Using path " + str(transcribe_path))
    app()

