# 요구사항 추적성 표

버전: v0.1

결과는 results/actual/summary.csv와 docs/07-verification-report.md에서 확인한다.

| 요구사항 | 구현 요소 | 검증 근거 |
|---|---|---|
| REQ-001 | PreviousFan 초기값 / 고장 표시 무상태 설계 | STATIC-INIT: 설정 검사 및 고장 표시 초기화 설계 리뷰 (동적 출력으로 직접 관찰하지 않음) |
| REQ-002 | 입력 첫 샘플 t=0 | TC-001, TC-011 |
| REQ-003 | TemperatureSample / SensorSample / PreviousFan | TC-019, TC-020, TC-021, TC-022, TC-023 |
| REQ-004 | 샘플링된 입력에 의한 출력 유지 | TC-019, TC-020, TC-021, TC-022, TC-023 |
| REQ-005 | AtOrAboveOn / OnOrLower | TC-003, TC-004, TC-005, TC-006, TC-007, TC-009, TC-010, TC-014, TC-018, TC-019, TC-020, TC-023 |
| REQ-006 | AtOrBelowOff / OffOrHold | TC-006, TC-007, TC-008, TC-010, TC-012, TC-016, TC-019, TC-020, TC-021, TC-022, TC-023 |
| REQ-007 | PreviousFan / OffOrHold | TC-001, TC-002, TC-005, TC-008, TC-009, TC-010, TC-013, TC-017 |
| REQ-008 | SensorOverride | TC-011, TC-012, TC-013, TC-014, TC-015, TC-016, TC-017, TC-018, TC-021, TC-022 |
| REQ-009 | Fault | TC-011, TC-012, TC-013, TC-014, TC-015, TC-016, TC-017, TC-018, TC-021, TC-022 |
| REQ-010 | Fault | TC-001, TC-002, TC-003, TC-004, TC-005, TC-006, TC-007, TC-008, TC-009, TC-010, TC-012, TC-013, TC-014, TC-016, TC-017, TC-018, TC-019, TC-020, TC-021, TC-022, TC-023 |
| REQ-011 | SensorOverride → PreviousFan 피드백 | TC-016, TC-017, TC-018, TC-022 |

ASM-001~003은 입력 계약이다. 유효한 온도와 센서 상태 조합을 테스트에 사용한다.
테스트가 연결되어 있다는 사실만으로 요구사항 충족을 판정하지 않는다. 실행 결과와 정적 근거를 함께 검토한다.
