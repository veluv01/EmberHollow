"""Read the original console's Arduino definition and enforce its ABI."""
import importlib.util
import os
from pathlib import Path
import re
import shlex
import sys

TARGET = 'rev0'
TARGET_ID = 0x35335843
BOARD_PATH = Path('platform/board/arduino/CHGame')


def find_repo(project):
    for path in (Path(project).resolve(), *Path(project).resolve().parents):
        if (path / BOARD_PATH / 'boards.txt').is_file():
            return path
    raise ValueError('Run setup first, or place this game inside a CHGame checkout')


def words(value):
    return shlex.split(value)


def properties(path):
    result = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def board_settings(repo, options):
    props = {key[5:]: value for key, value in properties(repo / BOARD_PATH / 'boards.txt').items()
             if key.startswith('rev0.')}
    expected = {'build.board': 'CHGAME_REV0', 'build.series': 'CH32X035',
                'build.chip': 'CH32X035G8U', 'build.variant': 'CH32X035/CHGame_Rev0',
                'build.variant_h': 'variant_CHGame_Rev0.h', 'build.ldscript': 'link_chgame_app.ld',
                'build.march': 'rv32imacxw', 'build.mabi': 'ilp32',
                'upload.maximum_size': '50944', 'upload.maximum_data_size': '18416'}
    for key, value in expected.items():
        if props.get(key) != value:
            raise ValueError('Rev0 board contract changed: ' + key)
    for menu, choice in options.items():
        key = 'menu.' + menu + '.' + choice
        if key not in props:
            raise ValueError('Unknown Rev0 option: ' + menu + '=' + choice)
        props.update({k[len(key)+1:]: v for k, v in list(props.items()) if k.startswith(key + '.')})
    # Vendor comments use a legacy encoding; the linker directives are ASCII.
    ld = (repo / BOARD_PATH / 'system/CH32X035/SRC/Ld/link_chgame_app.ld').read_bytes().decode('utf-8', errors='replace')
    for region, origin, length in [('FLASH', '0x00003000', '50944'), ('RAM', '0x20000010', '20464')]:
        if not re.search(region + r'\s*\([^)]*\)\s*:\s*ORIGIN\s*=\s*' + origin + r'\s*,\s*LENGTH\s*=\s*' + length, ld):
            raise ValueError('Rev0 memory layout changed; review the adapter')
    return props


def application(repo, project, get_option, environ=None):
    environ = os.environ if environ is None else environ
    name = environ.get('CHGAME_SKETCH', get_option('custom_chgame_sketch', ''))
    sketch = Path(name).expanduser()
    if not sketch.is_absolute():
        sketch = Path(project) / sketch
    sketch = sketch.resolve()
    if not name or not (sketch / (sketch.name + '.ino')).is_file():
        raise ValueError('Select an existing game with custom_chgame_sketch')
    sys.path.insert(0, str(repo / 'tools'))
    spec = importlib.util.spec_from_file_location('ember_rev0_gamecfg', repo / 'tools/gamecfg.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cfg = module.load(sketch)
    opts = {'opt': 'oslto', 'rtlib': 'nano', 'periph': 'game', 'usb': 'uploadonly'}
    if cfg.FQBN:
        parts = cfg.FQBN.split(':', 3)
        if parts[:3] != ['CHGame', 'ch32v', 'rev0']:
            raise ValueError('Sketch FQBN does not target the original CHGame console')
        opts['usb'] = 'serial'
        if len(parts) > 3:
            opts.update(dict(pair.split('=', 1) for pair in parts[3].split(',') if pair))
    for menu in ('opt', 'rtlib', 'usb'):
        choice = get_option('custom_chgame_' + menu, 'auto')
        if choice != 'auto':
            opts[menu] = choice
    pages = get_option('custom_chgame_save_pages', 'auto')
    pages = int(cfg.SAVE_PAGES if pages == 'auto' else pages)
    if pages not in (0, 1, 2):
        raise ValueError('Save-page reservation must be 0, 1, or 2')
    return {'sketch': sketch, 'name': sketch.name, 'board': board_settings(repo, opts),
            'defines': list(cfg.DEFINES), 'save_pages': pages, 'external_sketch': True, 'options': opts}
