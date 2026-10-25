"""Таблица было/стало громкости звуков: было — как сводил старый код (уровень файла + gain_db − 7 под голосом) к p95 голоса;
стало — замер нового reel.py (reel_report.json, sounds[].vs_voice_db)."""
import json, sys
sys.path.insert(0, "/home/user/Generator_Stickman/scripts")
import reel
B = "/tmp/claude-0/-home-user-Generator-Stickman/7605bd81-268a-5536-b1b7-f9696ca784cb/scratchpad/before"
VP = {"03_lenivyi": -5.0, "04_noch": -4.9, "05_ustal": -4.6}          # p95 голоса, тот же замер
OLD_RISER_GAIN = -3
out = []
for r in ("03_lenivyi", "04_noch", "05_ustal"):
    old = json.load(open(f"{B}/{r}/reel_report.json"))["sounds"]
    new = json.load(open(f"/home/user/Generator_Stickman/videos/{r}/reel/reel_report.json"))["sounds"]
    out.append(f"\n### {r}\n| t, с | звук | роль | было, дБ к голосу | стало | цель роли |\n|---|---|---|---|---|---|")
    for o, n in zip(sorted(old, key=lambda x: x["peak"]), sorted(new, key=lambda x: x["peak"])):
        was = reel.SFX[o["name"]][2] + o["gain_db"] - 7.0 - VP[r]
        out.append(f"| {n['peak']:.2f} | {n['name']}{' (переход)' if n['soft'] else ''} | {n['role']} | {was:+.1f} | {n['vs_voice_db']:+.1f} | {n['target_db']:+.1f} |")
print("\n".join(out))
