"""Compile the current dependency's core and original-console variant."""
from SCons.Script import Import
Import("env")
env.BuildSources("$BUILD_DIR/FrameworkArduino", env["CHGAME_CORE"])
env.BuildSources("$BUILD_DIR/Variant", env["CHGAME_VARIANT"])
