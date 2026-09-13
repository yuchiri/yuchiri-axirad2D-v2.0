# -*- coding: utf-8 -*-
"""[EN] Check that the outputs shipped with this repository regenerate exactly.

Copies the committed outputs aside, recomputes them, and compares. Everything is
compared bit for bit except two wall-clock timing fields, which cannot be
reproducible and are named explicitly below.

    export PYTHONPATH=src:examples:examples/coaxial_enclosure:examples/bm2_bm5
    python3 tools/check_reproducibility.py

[KO] 저장소에 들어 있는 출력이 그대로 재생성되는지 확인한다.

커밋된 출력을 옆에 치워 두고 다시 계산해 비교한다. 아래에 명시한 벽시계 시간
두 항목을 빼면 전부 비트 단위로 비교한다. 그 둘은 원리적으로 재현될 수 없다.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Wall-clock fields: these measure how long the machine took, so they differ
# between runs by construction. Nothing else in diagnostics.json may differ.
# 벽시계 항목 — 기계가 얼마나 걸렸는지를 재므로 실행마다 다르다. 진단의 나머지는
# 어느 것도 달라지면 안 된다.
TIMING_KEYS = ("time_radiation_s", "time_total_s")

CASES = [("examples/coaxial_enclosure/case.toml", "examples/coaxial_enclosure/out"),
         ("examples/bm2_bm5/case_bm2.toml", "examples/bm2_bm5/out_bm2"),
         ("examples/bm2_bm5/case_bm5.toml", "examples/bm2_bm5/out_bm5")]

MESHES = ["examples/coaxial_enclosure/coaxial_enclosure.mesh.npz",
          "examples/bm2_bm5/bm2.mesh.npz", "examples/bm2_bm5/bm5.mesh.npz",
          "examples/db3/db3_r1.mesh.npz", "examples/db3/db3_r2.mesh.npz",
          "examples/db3/db3_r4.mesh.npz"]

BUILDERS = ["examples/coaxial_enclosure/build_mesh.py",
            "examples/bm2_bm5/build_meshes.py",
            "examples/db3/db3_problem.py"]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(args):
    env = dict(os.environ)
    env["PYTHONPATH"] = ":".join(
        os.path.join(ROOT, p) for p in
        ("src", "examples", "examples/coaxial_enclosure",
         "examples/bm2_bm5", "examples/db3"))
    r = subprocess.run([sys.executable] + args, cwd=ROOT, env=env,
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-1500:])
        print(r.stderr[-1500:])
        raise SystemExit("command failed: %s" % " ".join(args))


def main():
    keep = tempfile.mkdtemp(prefix="repro_")
    for rel in MESHES:
        shutil.copy(os.path.join(ROOT, rel), os.path.join(keep, os.path.basename(rel)))
    for _, out in CASES:
        shutil.copytree(os.path.join(ROOT, out),
                        os.path.join(keep, out.replace("/", "_")))

    print("recomputing / 다시 계산")
    for b in BUILDERS:
        run([b])
    for case, out in CASES:
        run(["-m", "axirad2d.cli", case, "-o", out])

    ok = True
    print()
    print("meshes / 격자")
    for rel in MESHES:
        same = sha(os.path.join(ROOT, rel)) == sha(os.path.join(keep, os.path.basename(rel)))
        ok &= same
        print("  %-46s %s" % (os.path.basename(rel), "identical" if same else "DIFFERS"))

    print()
    print("outputs / 출력")
    for _, out in CASES:
        old = os.path.join(keep, out.replace("/", "_"))
        a = np.load(os.path.join(ROOT, out, "results.npz"))
        b = np.load(os.path.join(old, "results.npz"))
        npz = sorted(a.files) == sorted(b.files) and all(
            np.array_equal(a[k], b[k]) for k in a.files)
        csv = (sha(os.path.join(ROOT, out, "temperature.csv"))
               == sha(os.path.join(old, "temperature.csv")))
        da = json.load(open(os.path.join(ROOT, out, "diagnostics.json"), encoding="utf-8"))
        db = json.load(open(os.path.join(old, "diagnostics.json"), encoding="utf-8"))
        diff = sorted(k for k in set(da) | set(db)
                      if k not in TIMING_KEYS and da.get(k) != db.get(k))
        ok &= npz and csv and not diff
        print("  %-34s results.npz %-9s temperature.csv %-9s diagnostics %s"
              % (out, "identical" if npz else "DIFFERS",
                 "identical" if csv else "DIFFERS",
                 "identical" if not diff else "DIFFERS: %s" % diff))

    shutil.rmtree(keep, ignore_errors=True)
    print()
    print("Ignored by design / 의도적으로 제외: %s — wall clock" % ", ".join(TIMING_KEYS))
    print("RESULT: %s" % ("REPRODUCIBLE / 재현됨" if ok else "NOT REPRODUCIBLE / 재현되지 않음"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
