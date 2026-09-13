# -*- coding: utf-8 -*-
"""[EN] Command-line entry point.

    python -m axirad2d.cli case.toml [-o outdir]
    mpirun -n 4 python -m axirad2d.cli case.toml     # analysis.parallel = "mpi"

Only rank 0 writes output files and prints the summary.

[KO] 명령행 실행기.

    python -m axirad2d.cli case.toml [-o outdir]
    mpirun -n 4 python -m axirad2d.cli case.toml        # analysis.parallel = "mpi"
"""
from __future__ import annotations
import argparse
import os
import sys
from . import problemio, solve


def _rank() -> int:
    """MPI 랭크. mpi4py 가 없거나 직렬 실행이면 0.

    출력과 파일 쓰기는 랭크 0 만 수행한다 (USER_GUIDE 9.2절).
    모든 랭크가 같은 경로에 쓰면 경쟁 상태가 된다.
    """
    try:
        from mpi4py import MPI
        if MPI.Is_initialized():
            return MPI.COMM_WORLD.Get_rank()
    except Exception:
        pass
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="axirad2d")
    ap.add_argument("case", help="문제 TOML 파일")
    ap.add_argument("-o", "--outdir", default=None, help="출력 디렉터리")
    a = ap.parse_args(argv)

    # 입력 오류는 깔끔한 메시지로 끝낸다. 격자를 읽지도 못한 단계에서는
    # 남길 진단이 없으므로 파일을 만들지 않는다.
    try:
        p = problemio.read_problem(a.case)
    except (problemio.InputError, FileNotFoundError, OSError) as exc:
        if _rank() == 0:
            print("[입력 오류 / input error] %s" % exc)
        return 2
    outdir = a.outdir or os.path.join(os.path.dirname(os.path.abspath(a.case)), "out")
    rep = {"schema_version": problemio.SCHEMA,
           "mesh_file": p["raw"]["mesh_file"],
           "mesh_hash": p["mesh_hash"],
           "materials": sorted(p["materials"]),
           "bcs": [{k: v for k, v in b.items()} for b in p["bcs"]],
           "node_count": p["mesh"].nn, "element_count": p["mesh"].ne}
    et = p["mesh"].etype
    rep["element_types"] = {int(t): int((et == t).sum()) for t in sorted(set(et.tolist()))}
    rep["material_elements"] = {m: int((p["mesh"].emat == m).sum())
                                for m in sorted(set(map(str, p["mesh"].emat)))}
    try:
        T, S, B, rep, detail = solve.solve_steady(
            p["mesh"], p["materials"], p["bcs"], p["radiation"], p["solver"],
            rep, blood=p.get("blood"))
    except Exception as exc:
        rep["fatal"] = "%s: %s" % (type(exc).__name__, exc)
        if _rank() == 0:
            problemio.write_results(
                outdir, p["mesh"], __import__("numpy").zeros(p["mesh"].nn),
                None, None, rep)
            print(problemio.summary_text(rep))
            print("\n[중단] %s" % rep["fatal"])
            print("진단은 %s/diagnostics.json 에 남겼다." % outdir)
        return 2
    if _rank() == 0:
        problemio.write_results(outdir, p["mesh"], T, S, B, rep,
                                detail=bool(p["output"].get("detail", False)),
                                extra=detail)
        print(problemio.summary_text(rep))
        print("결과 -> %s" % outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
