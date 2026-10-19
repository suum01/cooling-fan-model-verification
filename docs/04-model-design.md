# 냉각팬 제어 모델 설계서

버전: v0.1 | 합의일: 2026-10-20

## 구조

```text
temperature → 100ms 입력 샘플링 → 정상 온도 제어 → 센서 오류 처리 → fan_cmd
                                      ↑                           │
                                      └── 이전 팬 상태 ← 상태 저장 ┘
sensor_valid → 100ms 입력 샘플링 → 고장 표시 생성 → fault_flag
```

1. 이전 상태를 읽는다.
2. 온도 ≥95℃이면 ON, ≤90℃이면 OFF, 그 사이이면 이전 상태로 정상 명령을 계산한다.
3. 센서 오류이면 정상 명령보다 우선하여 ON을 출력한다.
4. 오류 처리가 끝난 **최종 팬 명령**을 저장한다.

센서가 오류에서 정상으로 복구되었을 때 93℃라면 저장된 ON을 유지한다.

## 시간·자료형

- 초기 팬 상태 OFF. 초기 고장 표시는 OFF이며 별도 고장 이력 상태는 두지 않는다.
- t=0부터 0.1초 주기로 평가, 사이에는 출력 유지.
- 온도 double, 센서·팬·고장·저장 상태 Boolean.
- ON 임계값 95℃, OFF 임계값 90℃. 이름을 가진 모델 파라미터로 관리.

## 구현 블록

| 블록 이름 | Simulink 블록 | 역할 |
|---|---|---|
| TemperatureSample, SensorSample | Zero-Order Hold | 100ms 입력 샘플링 |
| AtOrAboveOn, AtOrBelowOff | Compare To Constant | ≥95, ≤90 판단 |
| OffOrHold, OnOrLower | Switch | OFF/이전 상태/ON 선택 |
| SensorOverride | Switch | 정상 명령 또는 오류 시 ON 선택 |
| PreviousFan | Unit Delay | 최종 팬 명령 저장, 초기값 false, 100ms |
| Fault | Logical Operator (NOT) | 샘플링된 sensor_valid의 반전 |
| True, False | Constant | Boolean 상수 |

Unit Delay는 현재 출력의 피드백을 한 제어 주기 지연하여 대수 루프를 피한다. 센서 입력을 먼저 샘플링하므로 오류와 복구도 평가 시점에 반영된다.

## 테스트 관찰

테스트용 To Workspace 블록 두 개로 출력을 10ms 간격으로 기록한다. 시뮬레이션은 fixed-step discrete, 10ms 기본 간격으로 실행한다. 이는 관찰 환경 설정이며 제어 로직의 100ms 주기와 구분한다.

## 구현·초기화 점검

REQ-001의 팬 초기화는 PreviousFan의 false 설정으로 확인한다. fault_flag는 상태를 갖지 않으며 첫 평가에서 센서 입력으로 결정한다. 따라서 초기 고장 표시 OFF는 사전 초기값 개념이며 독립적인 시뮬레이션 출력 샘플로 노출되지 않는다. 자동 설정 검사와 설계 리뷰 결과를 동적 결과와 구분해 남긴다.
