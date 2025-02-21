# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pygame",
# ]
# ///
import sys
import os
import traceback
from datetime import datetime
import pygame


def py2to3(code):
    output_lines = []
    lines = code.split('\n')
    for line in lines:
        if 'import asyncio' in line:
            continue
        if 'await asyncio.sleep(0)' in line:
            continue
        if 'async def' in line:
            line = line.replace('async def', 'def')
        if 'await ' in line:
            line = line.replace('await ', '')
        output_lines.append(line)
    return '\n'.join(output_lines)


def get_source_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_namespace_from_source(file='game.py', python2=False):
    source_dir = get_source_dir()
    game_file = os.path.join(source_dir, file)
    source_code = open(game_file).read()
    if python2:
        source_code = py2to3(source_code)
    ns = dict()
    ns['GAME_PATH'] = source_dir
    exec(source_code, ns)
    return ns


def start():
    """Why all this? (Experimentation)
    ... attempt to make source compatible with Python2 to support OnionOS
    ... as well as Python3 using asyncio to support pygbag"""
    try:
        print('Changing into game directory')
        os.chdir('src/wilmut_invader')
    except OSError:
        pass
    python_version = int(sys.version.split('.').pop(0))
    source_dir = get_source_dir()
    crash_fn = source_dir + '/crash_report.log'
    if os.path.exists(crash_fn):
        os.unlink(crash_fn)
    if python_version == 3:
        print('Starting Python 3 version')
        import asyncio
        from pathlib import Path
        ns = get_namespace_from_source('game.py', python2=False)
        print('Game path after import: ' + ns['GAME_PATH'])
        for _ in range(2):
            try:
                asyncio.run(ns['game_loop']())
                break
            except FileNotFoundError as e:
                # In such case run as a package rather than a module/script
                print(e)
                ns['GAME_PATH'] = Path(__file__).parent.as_posix()
    else:
        print('Starting Python 2 version')
        ns = get_namespace_from_source('game.py', python2=True)
        try:
            ns['game_loop']()
        except Exception as err:
            pygame_version = pygame.version.ver
            error_class = err.__class__.__name__
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]
            print('Writing crash report to ' + crash_fn + ' ...')
            with open(crash_fn, 'w') as f:
                now = datetime.now()
                for line in (str(now), 'error: ' + error_class, detail, 'line: ' + str(line_number), 'pygame: ' + pygame_version):
                    f.write(line + '\n')


if __name__ == '__main__':
    start()

