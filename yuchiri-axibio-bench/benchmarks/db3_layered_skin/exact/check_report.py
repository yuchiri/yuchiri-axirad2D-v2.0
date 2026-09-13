# -*- coding: utf-8 -*-
"""Check a submitted report against the DB-3 acceptance criterion.
제출된 보고서를 DB-3 합격 기준과 대조한다.

STANDALONE. numpy only. It does not run any solver; it reads a JSON report and
the reference values, and says whether the report passes and why.
독립 실행. numpy 만 쓴다. 솔버를 돌리지 않는다. JSON 보고서와 참조값을 읽어
합격 여부와 그 이유를 말한다.

    python3 check_report.py ../results/yuchiri-axirad2D_v2.0.json

The rule (SPEC section 4): acceptance is by ORDER OF CONVERGENCE, not by a fixed
tolerance. A fixed tolerance is an unjustified constant — it depends on the mesh,
the element order and the problem scale, none of which the suite controls. The
only hard failure is p < 1, which means the code is not converging at all.

규칙(SPEC 4장) — 합격은 고정 허용오차가 아니라 수렴 차수로 판정한다. 고정
허용오차는 근거 없는 상수다. 강제 실패는 p < 1 뿐이며, 그것은 아예 수렴하지
않는다는 뜻이다.
"""
from __future__ import annotations
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(HERE), "reference_values.json")

HARD_MIN_ORDER = 1.0        # below this the code is not converging at all
RADIAL_LIMIT = 1e-9         # the exact solution has no radial dependence
ENERGY_LIMIT = 1e-8         # energy balance, relative


def check(report_path, ref_path=REF, verbose=True):
    rep = json.load(open(report_path, encoding="utf-8"))
    ref = json.load(open(ref_path, encoding="utf-8"))
    ok, notes = True, []

    def say(s):
        if verbose:
            print(s)

    say("report : %s  v%s" % (rep.get("code_name"), rep.get("code_version")))
    say("norm   : %s" % rep.get("norm"))
    say("meshes : %s" % rep.get("mesh_source"))
    if not rep.get("norm"):
        ok = False
        notes.append("the norm used is not named; the expected order depends on it")
    # A report with no cases must not pass.  Silence is not agreement.
    # 사례가 없는 보고서는 통과시키지 않는다. 침묵은 동의가 아니다.
    cases = rep.get("cases", [])
    if not cases:
        ok = False
        notes.append("the report contains no cases at all")
    seen = {c.get("case") for c in cases}
    missing = sorted(set(ref["cases"]) - seen)
    if missing:
        ok = False
        notes.append("cases required by the reference are missing: %s"
                     % ", ".join(missing))
    say("")
    say("  case      T_s exact [K]   T_s reported     diff [K]    "
        "finest error   order p   radial [K]   energy")
    for case in cases:
        tag = case["case"]
        if tag not in ref["cases"]:
            ok = False
            notes.append("case '%s' is not in the reference" % tag)
            continue
        t_ref = ref["cases"][tag]["T_surface_K"]
        finest = case["meshes"][-1]
        d = finest["T_surface_computed_K"] - t_ref
        p = finest.get("observed_order")
        rv = finest.get("radial_variation_K", float("nan"))
        en = finest.get("energy_residual_relative", float("nan"))
        flag = []
        if p is None:
            ok = False
            flag.append("no order reported")
        elif p < HARD_MIN_ORDER:
            ok = False
            flag.append("NOT CONVERGING (p < 1)")
        if rv > RADIAL_LIMIT:
            ok = False
            flag.append("spurious radial variation")
        if en > ENERGY_LIMIT:
            ok = False
            flag.append("energy balance")
        say("  %-9s %14.10f  %14.10f  %+9.2e  %11.3e  %7s  %10.1e  %8.1e %s"
            % (tag, t_ref, finest["T_surface_computed_K"], d,
               finest["error_Linf_nodal_K"],
               "-" if p is None else "%.2f" % p, rv, en,
               "  <-- " + ", ".join(flag) if flag else ""))
        # monotone refinement is expected; report it but do not fail on it
        errs = [m["error_Linf_nodal_K"] for m in case["meshes"]]
        if not all(b < a for a, b in zip(errs, errs[1:])):
            notes.append("case '%s': the error does not fall monotonically "
                         "under refinement" % tag)
    say("")
    if notes:
        say("Notes / 참고")
        for n in notes:
            say("  - " + n)
        say("")
    say("RESULT: %s" % ("PASS / 합격" if ok else "FAIL / 불합격"))
    say("")
    say("Reminder: this is verification, not validation. Passing says the code "
        "solves the")
    say("stated equations correctly. It says nothing about whether those "
        "equations describe")
    say("real tissue.  검증이지 확인이 아니다.")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="DB-3 report checker")
    ap.add_argument("report", help="path to a report JSON")
    ap.add_argument("--reference", default=REF)
    a = ap.parse_args(argv)
    return 0 if check(a.report, a.reference) else 1


if __name__ == "__main__":
    sys.exit(main())
