"""Render authored test events as reviewable Markdown tables."""
from prepare_tests import ROOT, CASES

PURPOSES = [
    '초기 상태에서 중간 온도', 'ON 경계 직전', 'ON 경계 일치', 'ON 경계 직후',
    'OFF 경계 직후 ON 유지', 'OFF 경계 일치', 'OFF 경계 직전', '중간 온도 OFF 유지',
    '중간 온도 ON 유지', '온도 상승·하강 전환', '시작부터 센서 오류', '저온에서 오류',
    '중간 온도에서 오류', '고온에서 오류', '오류 지속 중 온도 변화', '저온 정상 복구',
    '중간 온도 정상 복구', '고온 정상 복구', '팬 ON 주기 갱신', '팬 OFF 주기 갱신',
    '센서 오류 주기 반영', '센서 복구 주기 반영', '반복 주기 갱신',
]
LINKS = [
    '002,007,010','007,010','005,010','005,010','005,007,010','005,006,010',
    '005,006,010','006,007,010','005,007,010','005,006,007,010','002,008,009',
    '006,008,009,010','007,008,009,010','005,008,009,010','008,009',
    '006,008,009,010,011','007,008,009,010,011','005,008,009,010,011',
    '003,004,005,006,010','003,004,005,006,010',
    '003,004,006,008,009,010','003,004,006,008,009,010,011',
    '003,004,005,006,010',
]


def write():
    lines = ['# 냉각팬 제어 테스트 명세서', '', '버전: v0.1 | 합의일: 2026-10-20', '',
             '## 공통 조건', '',
             '- 각 테스트는 초기화 후 독립 실행한다. 첫 입력은 t=0, 이후 표의 시각(ms)에 적용한다.',
             '- 센서 1=정상, 0=오류. 팬·고장 1=ON, 0=OFF.',
             '- 기대 출력은 해당 시각의 평가 후 값이며 다음 표 행까지 유지한다.',
             '- 50ms 등 비평가 시점에서는 입력만 변경되고 출력은 유지한다.',
             '- 마지막 이벤트 뒤 100ms까지 10ms 간격으로 출력과 시간을 확인한다.',
             '- CSV는 prepare_tests.py의 명시적 기대값을 확장한다. 모델 출력으로 기대값을 생성하지 않는다.',
             '- REQ-001의 평가 전 초기화는 별도 설정 검사·설계 리뷰로 확인한다.', '']
    for (test_id, events), purpose, reqs in zip(CASES, PURPOSES, LINKS):
        lines += [f'## {test_id}: {purpose}', '',
                  '관련 요구사항: ' + ', '.join('REQ-' + r for r in reqs.split(',')), '',
                  '| 시각(ms) | 온도(℃) | 센서 정상 | 기대 팬 | 기대 고장 |',
                  '|---|---|---|---|---|']
        lines += ['| ' + ' | '.join(map(str,e)) + ' |' for e in events]
        lines += ['']
    (ROOT/'docs/05-test-specification.md').write_text('\n'.join(lines),encoding='utf-8')
    lines = ['# 요구사항 추적성 표', '', '버전: v0.1', '',
             '결과는 results/actual/summary.csv와 docs/07-verification-report.md에서 확인한다.', '',
             '| 요구사항 | 구현 요소 | 검증 근거 |', '|---|---|---|']
    elements = ['PreviousFan 초기값 / 고장 표시 무상태 설계','입력 첫 샘플 t=0',
                'TemperatureSample / SensorSample / PreviousFan','샘플링된 입력에 의한 출력 유지',
                'AtOrAboveOn / OnOrLower','AtOrBelowOff / OffOrHold','PreviousFan / OffOrHold',
                'SensorOverride','Fault','Fault','SensorOverride → PreviousFan 피드백']
    for i, element in enumerate(elements,1):
        num=f'{i:03}'
        tests=[c[0] for c, links in zip(CASES,LINKS) if num in links.split(',')]
        evidence=', '.join(tests)
        if i==1: evidence='STATIC-INIT: 설정 검사 및 고장 표시 초기화 설계 리뷰 (동적 출력으로 직접 관찰하지 않음)'
        lines.append(f'| REQ-{num} | {element} | {evidence} |')
    lines += ['', 'ASM-001~003은 입력 계약이다. 유효한 온도와 센서 상태 조합을 테스트에 사용한다.',
              '테스트가 연결되어 있다는 사실만으로 요구사항 충족을 판정하지 않는다. 실행 결과와 정적 근거를 함께 검토한다.', '']
    (ROOT/'docs/06-traceability.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__ == '__main__':
    write()
