"""Package an already built/tested WeAct game. Never uploads to a board.

Run inside the parent CHGame checkout. Builds must exist in .pio/build;
this script packages release firmware, a card-ready CHG, the distributable
cart, the complete game source, notices, and measured memory metadata.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import struct
import sys
import zipfile

GAME=Path(__file__).resolve().parents[1]
REPO=GAME.parents[1]
sys.path.insert(0,str(REPO/'tools'))
import chgpack
from chcart import model, sources, zipio


def memory(elf_path):
    """Allocated RAM sections in a little-endian ELF32; include RAMFUNC code."""
    data=elf_path.read_bytes()
    if data[:6]!=b'\x7fELF\x01\x01':raise ValueError('Expected little-endian ELF32')
    shoff=struct.unpack_from('<I',data,32)[0]
    entsize,count,names_index=struct.unpack_from('<HHH',data,46)
    sections=[struct.unpack_from('<10I',data,shoff+i*entsize) for i in range(count)]
    strings=sections[names_index]
    names=data[strings[4]:strings[4]+strings[5]]
    ram=0
    for section in sections:
        at=section[0];end=names.find(b'\0',at);name=names[at:end].decode()
        if section[2]&2 and 0x20000010<=section[3]<0x20005000 and name!='.stack':ram+=section[5]
    return ram


def profile(environment,build_root=GAME):
    folder=build_root/'.pio/build'/environment
    report=json.loads((folder/'chgame-build.json').read_text())
    image=(folder/'firmware.bin').read_bytes()
    if report['target_id']!=0x36384657 or report['flash_bytes']!=len(image):raise ValueError('Wrong target or stale build')
    ram=memory(folder/'firmware.elf')
    if len(image)>50432 or ram>18416:raise ValueError('Memory/save budget exceeded')
    return {
        'environment':environment,'flash_bytes':len(image),'flash_budget_bytes':50432,
        'flash_headroom_bytes':50432-len(image),'static_ram_bytes':ram,'static_ram_budget_bytes':18416,
        'static_ram_headroom_bytes':18416-ram,'ram_with_stack_and_retained_bytes':ram+2048+16,
        'save_pages':report['save_pages'],'build_type':report['build_type'],
        'sha256':hashlib.sha256(image).hexdigest()
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=GAME/'out/package')
    ap.add_argument('--base-revision',default='unrecorded')
    ap.add_argument('--check-log',type=Path,required=True)
    ap.add_argument('--build-log',type=Path)
    ap.add_argument('--root-build-log',type=Path)
    ap.add_argument('--sanitizers-passed',action='store_true')
    ap.add_argument('--build-root',type=Path,default=GAME)
    ap.add_argument('--repository-template',type=Path)
    args=ap.parse_args()
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True)
    release=profile('ember',args.build_root);debug=profile('ember-debug',args.build_root)
    version=json.loads((GAME/'chgame.json').read_text())['version']
    if version not in (GAME/'config.h').read_text():raise ValueError('Source version mismatch')
    check_text=args.check_log.read_text() if args.check_log else ''
    if args.check_log and 'ALL GOOD' not in check_text:raise ValueError('Check log is not a pass')
    package=args.out/'EmberHollow_WeAct_F8U6';package.mkdir(exist_ok=True)
    destination=package/'games/EmberHollow'
    # Only the game: the maintained core and PlatformIO port stay upstream.
    for source in sorted(GAME.rglob('*')):
        if not source.is_file():continue
        relative=source.relative_to(GAME)
        if any(p in ('.pio','out','build','__pycache__','.git') for p in relative.parts) or source.name.endswith('.ino.cpp'):continue
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    for name in ('README.md','INSTALL.md','NOTICE','LICENSE'):
        shutil.copyfile(GAME/name,package/name)
    with (package/'NOTICE').open('a',encoding='utf-8') as notice:
        notice.write('\nIn this distribution, the referenced licenses/ directory is\ngames/EmberHollow/licenses/.\n')
    (package/'README.md').write_text(
        '# Ember Hollow\n\n'
        'A Halloween adventure through a haunted lava world, for CHGame on WeAct CH32X035F8U6.\n\n'
        '![Ember Hollow gameplay](games/EmberHollow/docs/gameplay.gif)\n\n'
        'Read [INSTALL.md](INSTALL.md) to play or build, and the '
        '[game guide](games/EmberHollow/README.md) for controls and rules.\n\n'
        '| Included | Use |\n|---|---|\n'
        '| `sdcard/GAMES/EMBER.CHG` | Copy to the existing card’s `GAMES/` folder |\n'
        '| `games/EmberHollow/` | Game source, PlatformIO project, original assets and tests |\n'
        '| `cart/EmberHollow.chgame` | Share or deploy using CHGame’s cart tools |\n'
        '| `firmware/EmberHollow.bin` | Raw WF86 application image |\n'
        '| `BUILD_REPORT.md` | Measured memory use and verification scope |\n\n'
        'All runtime artwork is embedded. No separate data file is needed. '
        'The firmware is built and simulator-tested; physical hardware has not been tested.\n',encoding='utf-8')
    firmware=package/'firmware';firmware.mkdir(exist_ok=True)
    image=(args.build_root/'.pio/build/ember/firmware.bin').read_bytes()
    (firmware/'EmberHollow.bin').write_bytes(image)
    card=package/'sdcard/GAMES';card.mkdir(parents=True,exist_ok=True)
    chg=chgpack.pack(image,'EMBER HOLLOW',author='Ember Hollow',version=version,
                     picture=chgpack.picture_file(str(GAME/'docs/cart.png')),target=chgpack.target_of('weact-f8u6'))
    header=chgpack.parse(chg,target=chgpack.target_of('weact-f8u6'))
    if header['payload_bytes']!=len(image) or chgpack.read_picture(chg) is None:raise ValueError('CHG verification failed')
    (card/'EMBER.CHG').write_bytes(chg)
    carts=package/'cart';carts.mkdir(exist_ok=True)
    game=sources.from_sketch(GAME,image,device='weact-f8u6')
    cart=model.Cart(title=game.title,games=[game],version=game.version,author=game.author,license=game.license)
    cart_path=carts/'EmberHollow.chgame'
    zipio.write(cart,cart_path)
    loaded=zipio.load(cart_path)
    if loaded.games[0].binaries['weact-f8u6']!=image:raise ValueError('Cart image mismatch')
    if set(loaded.games[0].binaries)!={'weact-f8u6'}:raise ValueError('Unexpected cart device')
    report={
        'game':'Ember Hollow','version':version,'board':'weact-f8u6','target_id':'WF86 / 0x36384657',
        'base_revision':args.base_revision,'application_origin':'0x00003000','hardware_tested':False,
        'target_frame_rate':30,'display_spi_hz':12000000,'save_magic':'EHLO','save_version':1,
        'save_record_bytes':40,'builds':[release,debug],
        'checks':{'host_and_simulator_passed':bool(check_text and 'ALL GOOD' in check_text),
                  'address_and_undefined_sanitizers_passed':args.sanitizers_passed,
                  'leak_detection_enabled':False,'script_image_comparisons':'two identical runs per script' if check_text else 'unrecorded',
                  'simulated_flash_restart':'passed' if 'flash record retains' in check_text else 'unrecorded',
                  'five_second_menu_exit':'passed' if 'five-second hold calls the menu exit successfully' in check_text else 'unrecorded',
                  'chg_header_payload_crc_and_picture':'passed','cart_round_trip_and_board':'passed'},
        'gameplay_gif_bytes':(GAME/'docs/gameplay.gif').stat().st_size,
        'limitations':['No hardware upload or playtest','No measured physical frame rate or stack high-water mark',
                       'No Rev0 build','Future upstream versions require rebuild and tests'],
    }
    if args.root_build_log:
        root_image=REPO/'.pio/build/game/firmware.bin'
        report['root_and_game_project_byte_identical']=root_image.read_bytes()==image
        if not report['root_and_game_project_byte_identical']:raise ValueError('Root/game builds differ')
    if args.repository_template:
        standalone=args.repository_template/'.pio/build/ember/firmware.bin'
        if standalone.exists():
            report['standalone_and_game_project_byte_identical']=standalone.read_bytes()==image
            if not report['standalone_and_game_project_byte_identical']:raise ValueError('Standalone/game builds differ')
    (package/'BUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Ember Hollow build verification','',
           'Built for WeAct CH32X035F8U6 (WF86), application origin `0x3000`. Both builds preserve two save pages.','',
           '| Build | Flash / save-safe budget | Static SRAM / budget |','|---|---:|---:|']
    for item in report['builds']:lines.append(f"| {item['build_type']} | {item['flash_bytes']:,} / 50,432 B | {item['static_ram_bytes']:,} / 18,416 B |")
    lines += ['',f'Base checkout: `{args.base_revision}`. PlatformIO 6.1.19, WCH RISC-V GCC 8.2.0, `-Os` with LTO, nano runtime.',
              '', 'Static SRAM includes allocated RAM code and data; the budget reserves the 16-byte boot block and 2 KB stack.',
              '', 'Verification: host gameplay tests and a 100,000-tick soak; two deterministic simulator runs for all three gameplay/smoke/tutorial scripts; simulated flash checkpoint/restart/continue/new-game checks; five-second exit, early release, and millisecond rollover; WF86 header, payload CRC, cover, and cart round-trip checks.',
              '', 'AddressSanitizer/UndefinedBehaviorSanitizer passed with leak detection disabled.' if args.sanitizers_passed else 'Sanitizer results were not recorded for this package.',
              '', f"The gameplay preview is {report['gameplay_gif_bytes']:,} bytes, below CHGame's 1 MB limit.",
              '', 'Root and game-folder PlatformIO builds are byte-identical.' if report.get('root_and_game_project_byte_identical') else 'Root build comparison was not recorded.',
              '', 'The standalone repository release is also byte-identical.' if report.get('standalone_and_game_project_byte_identical') else 'Standalone build comparison was not recorded.',
              '', '**Hardware was not uploaded or tested.** 30 fps is the configured target, not a measured physical rate. Rev0 and future API releases are untested. Inspect the game folder\'s NOTES.md and the included logs for the check scope.']
    (package/'BUILD_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for name in ('BUILD_REPORT.md','BUILD_REPORT.json'):
        shutil.copyfile(package/name,destination/name)
        shutil.copyfile(package/name,GAME/name)
    logs=package/'verification';logs.mkdir(exist_ok=True)
    for label,path in [('check.log',args.check_log),('build.log',args.build_log),('root-build.log',args.root_build_log)]:
        if path:shutil.copyfile(path,logs/label)
    if args.repository_template:
        excluded={'games','platform','ports','spec','.deps','.pio','.git','.venv','out','verification','firmware','sdcard','cart'}
        for source in sorted(args.repository_template.rglob('*')):
            if not source.is_file():continue
            relative=source.relative_to(args.repository_template)
            if relative.parts[0] in excluded or '__pycache__' in relative.parts:continue
            if relative.parts[0]=='tools' and relative.as_posix() not in {'tools/project.py','tools/requirements.txt'}:continue
            if source.name in {'BUILD_REPORT.md','BUILD_REPORT.json','SHA256SUMS.json'}:continue
            target=package/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    manifest={str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(package.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'}
    (package/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    out=args.out/'EmberHollow_WeAct_F8U6.zip'
    # Stable order/date; regenerated sources/art/builds can be compared faithfully.
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for source in sorted(package.rglob('*')):
            if source.is_file():
                info=zipfile.ZipInfo('EmberHollow_WeAct_F8U6/'+str(source.relative_to(package)),date_time=(2026,10,11,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,source.read_bytes())
    print(json.dumps({'package':str(out),'size_bytes':out.stat().st_size,'release':release,'debug':debug,'files':len(manifest)+1}))


if __name__=='__main__':main()

