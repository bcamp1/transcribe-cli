#!/usr/bin/env python3

import typer
import subprocess

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

@app.command()
def get_filename_from_url(url: str, video: bool = False):
    title = execute_command_safe("yt-dlp --get-title " + url)
    filename = title.lower().strip().replace(' ', '-')
    if video:
        filename += ".mp4"
    else:
        filename += ".mp3"
    print(filename)
    return filename

@app.command()
def download_url(url: str, output_fname: str):
    extension = output_fname.split('.')[1]
    if extension == "mp3":
        include_video = False
    elif extension == "mp4":
        include_video = True
    else:
        include_video = False
        panic("Invalid extension type: " + extension)

    yt_dlp_options = "-o " + output_fname

    if include_video:
        yt_dlp_options += " -t mp4"
    else:
        yt_dlp_options += " -t mp3"

    yt_dlp_cmd = f'yt-dlp {yt_dlp_options} "{url}"'
    print(execute_command_safe(yt_dlp_cmd))

@app.command()
def find(name: str):
    print(f"Hello {name}")

@app.command()
def download(url: str):
    pass

@app.command()
def open(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")

if __name__ == "__main__":
    app()

"""
def get_youtube_title(url: str):
    yt = YouTube(url)
    return yt.title

def main(item: str, video: bool = False, output: str = "default"):
    item_is_link = item.startswith('http')
    output_fname = ""

    if item_is_link:
        # Get URL information
        #title = get_youtube_title(item)
        title = "Hi"
        output_fname = title.lower().strip().replace(' ', '-') if output == "default" else output
    else:
        output_fname = item.lower().strip().replace(' ', '-') if output == "default" else output

    if video:
        output_fname += ".mp4"
    else:
        output_fname += ".mp3"

    youtube_link = ''
    if item_is_link:
        youtube_link = item
    else:
        print("Searching for best-fit video link...")
        fuzzy_cmd = f'yt-dlp "ytsearch1:{item}" --get-id'
        try:
            result = subprocess.run(fuzzy_cmd, shell=True, capture_output=True, text=True)
            youtube_code = result.stdout.strip()
            youtube_link = 'https://www.youtube.com/watch?v=' + youtube_code
        except subprocess.CalledProcessError:
            print("Error: fuzzy finder command failed")
            exit(1)


    print("Downloading " + ("video" if video else "audo") + " from " + youtube_link + "...")

    yt_dlp_options = "-o " + output_fname

    if video:
        yt_dlp_options += " -t mp4"
    else:
        yt_dlp_options += " -t mp3"

    yt_dlp_cmd = f'yt-dlp {yt_dlp_options} "{youtube_link}"'
    print(yt_dlp_cmd)
    try:
        result = subprocess.run(yt_dlp_cmd, shell=True, capture_output=True, text=True)
        print("Done!")
    except subprocess.CalledProcessError:
        print("Error: yt-dlp command failed")
        exit(1)


if __name__ == "__main__":
    typer.run(main)
"""

