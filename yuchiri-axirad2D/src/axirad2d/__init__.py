# -*- coding: utf-8 -*-
"""yuchiri-axirad2D — a general-purpose 2D axisymmetric conduction-radiation FEM solver.

[EN] Takes geometry, mesh and material properties as input and computes the
temperature field.  Surface radiation is solved by Monte Carlo ray tracing for
Gebhart absorption factors, fully coupled to conduction through Newton's method.
Copyright (c) 2026 Yoo Cheol WON.  MIT License.

[KO] 범용 2차원 축대칭 전도-복사 유한요소 코드.
형상, 격자, 물성을 입력으로 받아 온도 분포를 계산한다.
"""
__version__ = "2.0.0"
__spec_version__ = "v1.1"
