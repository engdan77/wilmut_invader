# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pygame",
# ]
# ///
import sys
import os


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


def get_namespace_from_source(file='game.py', python2=False):
    source_dir = os.path.dirname(__file__)
    game_file = os.path.join(source_dir, 'game.py')
    source_code = open(game_file).read()
    if python2:
        source_code = py2to3(source_code)
    ns = {}
    exec(source_code, ns)
    return ns


def start():
    """Why all this? (Experimentation)
    ... attempt to make source compatible with Python2 to support OnionOS
    ... as well as Python3 using asyncio to support pygbag"""
    try:
        print('Changing into game directory')
        os.chdir('src/wilmut_invader')
    except FileNotFoundError:
        pass
    python_version = int(sys.version.split('.').pop(0))
    if python_version == 3:
        print('Starting Python 3 version')
        import asyncio
        ns = get_namespace_from_source('game.py', python2=False)
        asyncio.run(ns['game_loop']())
    else:
        print('Starting Python 2 version')
        ns = get_namespace_from_source('game.py', python2=True)
        ns['game_loop']()


if __name__ == '__main__':
    start()

