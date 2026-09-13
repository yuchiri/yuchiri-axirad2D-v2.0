#!/usr/bin/env bash
set -e
export PYTHONPATH=src:examples:examples/coaxial_enclosure:examples/bm2_bm5:examples/db3
echo "== 격자 생성 =="; python3 examples/coaxial_enclosure/build_mesh.py
echo; echo "== 검증 시험 =="; python3 -m pytest tests -q
echo; echo "== 벤치마크 =="; python3 -m axirad2d.cli examples/coaxial_enclosure/case.toml
echo; echo "== 해석해 대조 =="; python3 examples/coaxial_enclosure/reference.py
