"""Ember Hollow's settings for the shared CHGame tools."""
SAVE_PAGES = 2
TESTS = {"test_ember": dict(sources=["tools/tests/test_game.cpp", "Game.cpp", "src/assets/Assets.cpp"],
                           extra_flags=["-Wall", "-Wextra"])}
ECHO = ("STATE",)
SIM_TESTS = ["tools/tests/sim_save.py"]

