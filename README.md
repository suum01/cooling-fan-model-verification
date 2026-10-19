# CoolingFan-Controller

## Simulink 기반 냉각팬 제어 모델 검증 및 테스트 자동화

온도·센서 상태에 따라 팬 명령을 결정하는 기본 블록 모델과 요구사항 기반 검증 프로젝트입니다. 정상 모델의 23개 동적 테스트를 수행하고, 3종의 의도적 결함을 테스트로 검출했습니다.

## 제어 규칙

| 조건 | 팬 명령 | 고장 표시 |
|---|---|---|
| 센서 오류 | ON | ON |
| 정상·95℃ 이상 | ON | OFF |
| 정상·90℃ 이하 | OFF | OFF |
| 정상·90℃ 초과 95℃ 미만 | 이전 명령 유지 | OFF |

팬 초기 상태는 OFF입니다. 초기화 후 t=0에서 첫 평가를 수행하고 이후 100ms마다 갱신합니다. 오류 처리까지 끝난 최종 명령을 저장하므로 93℃에서 센서가 복구되면 팬 ON을 유지합니다.

## 모델 구조

![Simulink 모델](results/figures/model.png)

| 블록 | 선택 이유 |
|---|---|
| Zero-Order Hold | 입력을 100ms마다 샘플링 |
| Compare To Constant | 95℃ 이상, 90℃ 이하 경계 명시 |
| Switch | 온도 구간과 센서 오류 우선순위 선택 |
| Unit Delay | 최종 팬 상태를 한 제어 주기 저장 |
| NOT | 센서 정상 여부를 고장 표시로 변환 |

## 문서

1. [프로젝트 계획서](docs/01-project-plan.md)
2. [요구사항 정의서](docs/02-requirements.md)
3. [검증 계획서](docs/03-verification-plan.md)
4. [모델 설계서](docs/04-model-design.md)
5. [23개 테스트 명세](docs/05-test-specification.md)
6. [요구사항 추적성](docs/06-traceability.md)
7. [검증 결과 보고서](docs/07-verification-report.md)

## 실행 환경

- 검증 환경: MATLAB R2023a Update 8, Simulink, Python 3.11
- Python은 표준 라이브러리만 사용합니다. pip 설치가 필요하지 않습니다.
- Simulink Test, Coverage, Check, Stateflow, Coder는 실행 필수 제품이 아닙니다.
- 저장소 루트에서 아래 명령을 실행합니다. MATLAB 배치 실행은 PATH에 matlab이 등록되어 있어야 합니다.

### 1. 테스트 데이터 준비

```text
python scripts/python/prepare_tests.py
python scripts/python/write_test_docs.py
```

기대 결과는 요구사항에서 수동 도출한 이벤트 표를 확장한 값입니다. 모델 출력이나 동일 제어 알고리즘으로 기대값을 생성하지 않습니다.

### 2. 모델 설정 검사와 정상 모델 실행

```text
matlab -batch "addpath('scripts/matlab'); check_model; run_tests;"
python scripts/python/check_results.py
```

`models/cooling_fan.slx`를 열어 모델을 확인할 수 있습니다. 파일이 없으면 build_model.m이 기본 블록으로 생성합니다. 기존 파일이 있으면 수동 편집 내용을 보존하기 위해 재생성하지 않고 불러옵니다. 모델 생성 코드를 변경한 경우 기존 모델과 비교하여 갱신해야 합니다.

모델은 100ms 주기로 제어하고 테스트 출력은 10ms 간격으로 관찰합니다. 결과는 `results/actual/`에 저장됩니다. 새 실행 시작 시 해당 실행 폴더의 기존 테스트 CSV를 제거하여 오래된 결과가 재사용되지 않도록 합니다.

### 3. 의도적 결함 검출

```text
matlab -batch "addpath('scripts/matlab'); run_tests('on_strict'); run_tests('wrong_feedback'); run_tests('no_override');"
python scripts/python/check_mutations.py
```

결함은 메모리에서만 삽입하며 정상 .slx 파일에 저장하지 않습니다. 결함 모델의 일부 테스트가 FAIL인 것이 예상 결과입니다. check_mutations.py는 지정한 테스트에서 실제 팬 출력 불일치를 검출하면 종료 코드 0을 반환합니다.

### 4. 판정 도구 검사와 재현 정보 기록

```text
python -m unittest discover -s tests -p test_result_checker.py
python scripts/python/record_run.py
```

소스·모델·입력·기대값과 결과의 SHA-256을 `results/reproducibility.json`에 기록합니다. 실행 시 MATLAB/Simulink 제품 버전과 UTC 시각도 별도로 남깁니다.

## 구성

| 경로 | 내용 |
|---|---|
| docs/ | 합의한 요구사항, 설계, 검증 문서 |
| models/ | Simulink 모델 |
| scripts/matlab/ | 모델 생성, 설정 검사, 시뮬레이션 |
| scripts/python/ | 입력·명세 생성, 결과 판정, 결함 검출 확인 |
| tests/ | 독립 테스트 23개, 기대값, 판정 도구 테스트 |
| results/ | 실제 출력, 요약, 환경, 구조 이미지 |

## 범위와 한계

실제 냉각 성능·ECU·센서 진단은 포함하지 않습니다. 온도 값의 유효성은 외부 입력 계약이며, 센서가 정상일 때 유효한 유한 실수를 전달한다고 가정합니다. 평가 사이에 발생했다가 사라지는 오류를 기억하지 않습니다.

모델 설정 검사와 설계 리뷰를 정적 근거로 사용했습니다. MISRA 검사, 형식 검증, 모델 구조 커버리지 측정은 수행하지 않았습니다. 결과는 ISO 26262 인증이나 MISRA 준수를 의미하지 않습니다.

초기 고장 표시 OFF는 첫 평가 전의 개념적 초기 상태이며 출력 샘플로 별도 노출되지 않습니다. REQ-001의 근거와 동적 테스트 결과를 구분하여 [결과 보고서](docs/07-verification-report.md)에 기록합니다.
