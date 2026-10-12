"""Original-console application build against the pinned CHGame sources.

Application mechanics adapted from the maintained CHGame WeAct PlatformIO
port (Apache-2.0). Board selection, chip defines and packaging are Rev0-only.
The dependency core, variants and libraries remain unmodified.
"""
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

from SCons.Script import Builder, Default, DefaultEnvironment
from SCons.Tool import createObjBuilders

env = DefaultEnvironment()

builder = Path(env.PioPlatform().get_dir()) / "builder"
sys.path.insert(0, str(builder))
from rev0_profile import BOARD_PATH, TARGET, TARGET_ID, application, find_repo, words

if env.GetProjectOption("board") != TARGET:
    raise ValueError("Loaded platform profile does not match the selected board; check the local platform link")

project = Path(env.subst("$PROJECT_DIR"))
if sys.version_info < (3, 10):
    raise ValueError("Run PlatformIO with Python 3.10 or newer for the CHGame Python host")
repo = find_repo(project)
board_root = repo / BOARD_PATH
core = board_root / "cores/arduino"
system = board_root / "system/CH32X035"
image_kind = env.GetProjectOption("custom_chgame_image", "app")
if image_kind != "app":
    raise ValueError("This platform builds Rev0 game applications only")

toolchain = Path(env.PioPlatform().get_package_dir("toolchain-riscv"))
prefix = "riscv-none-embed-"
compiler_bin = toolchain / "bin"
if not any((compiler_bin / (prefix + "gcc" + ext)).is_file() for ext in ("", ".exe")):
    raise ValueError("This port requires the pinned WCH GCC 8 riscv-none-embed toolchain")
env.PrependENVPath("PATH", str(compiler_bin))
env.Replace(
    CC=prefix + "gcc", CXX=prefix + "g++", AS=prefix + "gcc",
    AR=prefix + "gcc-ar", RANLIB=prefix + "gcc-ranlib",
    OBJCOPY=prefix + "objcopy", SIZE=prefix + "size", GDB=prefix + "gdb",
    PROGNAME="firmware", PROGSUFFIX=".elf", ARFLAGS=["rcs"],
    SIZEPROGREGEXP=r"^(?:\.init|\.vector|\.text|\.fini|\.rodata|\.data|\.ramfunc|\.preinit_array|\.init_array|\.fini_array)\s+([0-9]+).*",
    SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit|\.ramfunc)\s+([0-9]+).*",
    SIZECHECKCMD="$SIZE -A $SOURCES", SIZEPRINTCMD="$SIZE -B -d $SOURCES",
)
common = ["-march=rv32imacxw", "-mabi=ilp32", "-msmall-data-limit=8", "-msave-restore",
          "-ffunction-sections", "-fdata-sections", "-fno-common"]
env.Append(CCFLAGS=common, ASFLAGS=common,
           LINKFLAGS=common + ["-nostartfiles", "-Wl,--gc-sections", "-Wl,-Map,$BUILD_DIR/firmware.map"])
env.Replace(ASCOM="$AS -x assembler-with-cpp $ASFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS -c -o $TARGET $SOURCE")

app = application(repo, project, env.GetProjectOption)
props = app["board"]
variant = board_root / "variants" / props["build.variant"]
sketch_key = hashlib.sha256(str(app["sketch"].resolve()).encode()).hexdigest()[:16]
includes = [variant, variant.parent, core, core / "ch32/usb", core / "avr", core / "ch32", core / "ch32/lib",
            system / "USER", system / "SRC/Core", system / "SRC/Debug",
            system / "SRC/Startup", system / "SRC/Peripheral/inc", system / "SRC/Peripheral/src"]
env.Replace(PROJECT_SRC_DIR=str(app["sketch"]), PROJECTSRC_DIR=str(app["sketch"]),
            BUILD_SRC_DIR="$BUILD_DIR/sketch-" + sketch_key,
            LDSCRIPT_PATH=str(system / "SRC/Ld" / props["build.ldscript"]), LINK="$CXX")
if app["external_sketch"]:
    # Match Arduino: root sketch units and src/, without PC tests or shims.
    env.Replace(SRC_FILTER=["+<*.ino>", "+<*.c>", "+<*.cpp>", "+<*.cc>",
                           "+<*.cxx>", "+<*.S>", "+<*.s>", "+<src/>"])
env.BoardConfig().update("upload.maximum_size", int(props["upload.maximum_size"]))
env.BoardConfig().update("upload.maximum_ram_size", int(props["upload.maximum_data_size"]))
env.Append(CPPPATH=[str(p) for p in includes],
           CPPDEFINES=[("ARDUINO", 10819), "ARDUINO_ARCH_CH32", props["build.series"], props["build.chip"],
                       ("VARIANT_H", env.StringifyMacro(props["build.variant_h"]))],
           CFLAGS=["-std=gnu99"],
           CXXFLAGS=["-std=gnu++14", "-fno-threadsafe-statics", "-fno-rtti", "-fno-exceptions",
                     "-fno-use-cxa-atexit", "-fpermissive"],
           CCFLAGS=words(props["build.flags.optimize"]) + ["-g", "-fsigned-char"],
           ASFLAGS=words(props["build.flags.optimize"]),
           LINKFLAGS=["-fsigned-char"] + words(props["build.flags.optimize"])
                     + words(props.get("build.flags.ltolink", ""))
                     + words(props["build.flags.ldflags"]),
           LIBS=words(props.get("build.ch_extra_lib", "").replace("-l", ""))
                + words(props.get("build.math_lib_gcc", "").replace("-l", "")) + ["c"])
for key in ("build.flags.clock", "build.flags.debug", "build.flags.periph", "build.usb_flags", "build.flags.board"):
    env.MergeFlags(props.get(key, ""))
for define in app["defines"]:
    env.MergeFlags("-D" + define)
env["CHGAME_APP"] = app
env["CHGAME_CORE"] = str(core)
env["CHGAME_VARIANT"] = str(variant)

env["CHGAME_IMAGE_KIND"] = image_kind
env["CHGAME_REPO"] = str(repo)

# Use one object for .S; the lower-case suffix is not a GNU assembly source.
static_obj, shared_obj = createObjBuilders(env)
for obj in (static_obj, shared_obj):
    obj.add_action(".S", "$ASCOM")

env.Append(BUILDERS={"ElfToBin": Builder(action=env.VerboseAction(
    "$OBJCOPY -O binary $SOURCES $TARGET", "Creating $TARGET"), suffix=".bin")})


def upstream_host():
    host = repo / "platform/bootloader/host/py"
    sys.path.insert(0, str(host))
    return host


def prepare_image(source, target, env):
    # This runs only after a user-requested build, never during apply/check.
    binary = Path(str(target[0]))
    data = binary.read_bytes()
    upstream_host()
    build = {"board": TARGET, "target_id": TARGET_ID, "image_kind": image_kind,
             "flash_bytes": len(data), "hardware_tested": False,
             "build_type": env.GetBuildType()}
    from chgame_upload import chg
    limit = int(app["board"]["upload.maximum_size"]) - app["save_pages"] * 256
    if (len(data) + 3) // 4 * 4 > limit:
        raise ValueError("Application exceeds its " + str(limit) + " byte budget with save pages")
    package = binary.with_suffix(".chg")
    package.write_bytes(chg.pack(data, chg.default_title(app["name"]), device=TARGET))
    build.update(name=app["name"], flash_budget=limit, save_pages=app["save_pages"],
                 options=app["options"], defines=app["defines"], app_origin=0x3000)
    binary.with_name("chgame-build.json").write_text(json.dumps(build, indent=2) + "\n")
    if app["external_sketch"] and env.GetProjectOption("custom_chgame_export", "yes") == "yes":
        kind = "debug" if "debug" in env.GetBuildType() else "release"
        out = app["sketch"] / "build" / TARGET / kind
        out.mkdir(parents=True, exist_ok=True)
        stem = app["name"] + ".ino"
        for artifact, suffix in ((binary, ".bin"), (package, ".chg"),
                                 (binary.with_suffix(".elf"), ".elf")):
            shutil.copy2(artifact, out / (stem + suffix))


def upload(source, target, env):
    host = upstream_host()
    child_env = dict(os.environ)
    child_env["PYTHONPATH"] = str(host) + os.pathsep + child_env.get("PYTHONPATH", "")
    command = [sys.executable, "-m", "chgame_upload"]
    command += ["flash", str(source[0]), "--device", TARGET, "--run"]
    if env.get("UPLOAD_PORT"):
        command += ["--port", env.subst("$UPLOAD_PORT")]
    return subprocess.call(command, env=child_env)


program = env.BuildProgram()
binary = env.ElfToBin("$BUILD_DIR/firmware", program)
env.AddPostAction(binary, prepare_image)
env.Depends(binary, "checkprogsize")
env.AddPlatformTarget("size", program, env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"),
                      title="Size", description="Display Rev0 application size")
env.AddPlatformTarget("upload", binary, env.VerboseAction(upload, "Uploading CHGame Rev0 application"),
                      title="Upload", description="CHGame USB application upload (Rev0 only)")
Default(binary)
