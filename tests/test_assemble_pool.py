"""Пул клипов сборщика не ждёт вечно (05.11: пробник L02 висел 40 мин — процесс клипа умер молча, а сборщик ждал
его результат). Завис или сломался — недоделанные клипы идут в новый пул."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import assemble_frames as af  # noqa: E402


def _hang_once(job):
    flag = job["flag"]
    if job["k"] == 1 and not os.path.exists(flag):
        open(flag, "w").close()
        time.sleep(120)                     # первый раз клип «висит»
    return job["k"] * 10


def _die_once(job):
    flag = job["flag"]
    if job["k"] == 0 and not os.path.exists(flag):
        open(flag, "w").close()
        os._exit(1)                         # первый раз процесс клипа умирает
    return job["k"] * 10


def test_stalled_clip_is_rendered_again_instead_of_waiting_forever(tmp_path):
    jobs = [dict(k=k, flag=str(tmp_path / "hang")) for k in range(3)]
    t = time.time()
    out = af.render_all(jobs, 2, render=_hang_once, stall=2)
    assert out == {0: 0, 1: 10, 2: 20} and time.time() - t < 60


def test_dead_worker_does_not_lose_its_clip(tmp_path):
    jobs = [dict(k=k, flag=str(tmp_path / "die")) for k in range(3)]
    assert af.render_all(jobs, 2, render=_die_once, stall=30) == {0: 0, 1: 10, 2: 20}
