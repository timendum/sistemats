from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {"packages": [], "excludes": ["tkinter", "tlc", "unittest"]}

base = "Console"

executables = [Executable("invia.py", base=base, targetName="invia_fatture")]

setup(
    name="InviaFatture",
    version="1.0",
    description="",
    options={"build_exe": build_options},
    executables=executables,
)
