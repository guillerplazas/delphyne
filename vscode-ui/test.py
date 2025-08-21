import why3py, subprocess, pathlib, sys
print("why3py location:", pathlib.Path(why3py.__file__).resolve())
subprocess.run(["why3", "--version"], check=True)
print("Everything linked ✔")