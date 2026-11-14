"""python3 look.py s05 6.7,7.0,... — кадры + лист /tmp/a58b/look_<id>.jpg (сжатый 0.25)."""
import subprocess, sys, glob, os
sid, ts = sys.argv[1], sys.argv[2]
H = os.path.dirname(os.path.abspath(__file__))
out = subprocess.check_output(["python3", os.path.join(H, "make.py"), sid, "--sheet", ts]).decode()
files = out.split("sheet ")[-1].split()
subprocess.check_call(["python3", os.path.join(H, "sheet.py"), f"/tmp/a58b/look_{sid}.jpg", *files, "--w", sys.argv[3] if len(sys.argv) > 3 else "300"])
print(f"/tmp/a58b/look_{sid}.jpg")
