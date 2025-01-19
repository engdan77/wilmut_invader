# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fpdf2",
#     "mistletoe",
#     "typer",
# ]
# ///
import re
import string
from pathlib import Path

import typer
from mistletoe import markdown
from fpdf import FPDF
import shutil

SHORTCUT_TEMPLATE = """#!/bin/sh
# Python Ports Script Template

# main configuration :
GameName="$game_name"
GameDir="$normalized_name"
GameExecutable="$main_python_file"
GameDataFile=""

# additional configuration
KillAudioserver=1
PerformanceMode=0

# specific to this port :
Arguments=""
unset LD_PRELOAD

# running command line :
/mnt/SDCARD/Emu/PORTS/launch_python2.sh "$$GameName" "$$GameDir" "$$GameExecutable" "$$Arguments" "$$GameDataFile" "$$KillAudioserver" "$$PerformanceMode"
"""

app = typer.Typer()


def normalize_name(name: str) -> str:
    return re.sub(r'[^a-z0-9\s.]', '', name.lower()).replace(' ', '_')


def create_pdf(input_markdown: Path, output_pdf: Path):
    html = markdown(input_markdown.read_text())
    pdf = FPDF()
    pdf.add_page()
    pdf.write_html(html)
    pdf.output(output_pdf.as_posix())


def copy_source_files(source_dir: Path, target_dir: Path, game_name: str):
    game_folder = normalize_name(game_name)
    game_source_target_path = Path(target_dir / f'Roms/PORTS/Games/{game_folder}').expanduser()
    game_source_target_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir.expanduser(), game_source_target_path.as_posix(), dirs_exist_ok=True)
    cache_dir = (game_source_target_path / '__pycache__').expanduser().as_posix()
    shutil.rmtree(cache_dir, ignore_errors=True)


def copy_img(target_dir: Path, png_file: Path, game_name: str, ext: str = 'png'):
    imgs_path = Path(target_dir / 'Roms/PORTS/Imgs').expanduser()
    imgs_path.mkdir(parents=True, exist_ok=True)
    Path(imgs_path / f'{normalize_name(game_name)}.{ext}').write_bytes(
        png_file.read_bytes()
    )


def create_manual(target_dir: Path, source_md: Path, game_name: str):
    html = markdown(source_md.read_text().encode('ascii', 'ignore').decode('utf-8'))
    pdf = FPDF()
    pdf.add_page()
    pdf.write_html(html)
    name = normalize_name(game_name)
    manual_path = Path(target_dir / 'Roms/PORTS/Manuals').expanduser()
    manual_path.mkdir(parents=True, exist_ok=True)
    pdf.output(Path(manual_path / f'{name}.pdf').as_posix())


def create_shortcut(
    target_dir: Path, game_name: str, main_python_file: str = 'main.py'
):
    name = normalize_name(game_name)
    shortcuts_dir = Path(target_dir / 'Roms/PORTS/Shortcuts/Actions').expanduser()
    shortcuts_dir.mkdir(parents=True, exist_ok=True)
    shortcut_file = shortcuts_dir / f'{name}.notfound'
    data = string.Template(SHORTCUT_TEMPLATE).substitute(
        game_name=game_name,
        normalized_name=normalize_name(game_name),
        main_python_file=main_python_file,
    )
    print(f'Writing: {data}')
    shortcut_file.write_text(data)


@app.command()
def build_port(
    target_dir: Path,
    game_name: str = 'Wilmut Invader',
    source_files_path: Path = typer.Option(
        Path(__file__).parent, help='Path to the source code'
    ),
    image_file: Path = typer.Option(
        Path(__file__).parent / '../../assets/screen.png',
        help='PNG with 256x360 resolution',
    ),
    readme_file: Path = typer.Option(
        Path(__file__).parent / '../../README.md', help='The README.md'
    ),
    main_python_file: str = typer.Option(
        'main.py', help='The main python file to start'
    ),
):
    """Build a OnionOS port of this game"""
    copy_source_files(source_files_path, target_dir, game_name=game_name)
    copy_img(target_dir, image_file, game_name)
    create_manual(target_dir, readme_file, game_name)
    create_shortcut(target_dir, game_name, main_python_file)


if __name__ == '__main__':
    app()
