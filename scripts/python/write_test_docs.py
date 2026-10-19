"""Render authored test events as reviewable Markdown tables."""
from prepare_tests import ROOT, CASES

PURPOSES = [
    '�ʱ� ���¿��� �߰� �µ�', 'ON ��� ����', 'ON ��� ��ġ', 'ON ��� ����',
    'OFF ��� ���� ON ����', 'OFF ��� ��ġ', 'OFF ��� ����', '�߰� �µ� OFF ����',
    '�߰� �µ� ON ����', '�µ� ��¡��ϰ� ��ȯ', '���ۺ��� ���� ����', '���¿��� ����',
    '�߰� �µ����� ����', '���¿��� ����', '���� ���� �� �µ� ��ȭ', '���� ���� ����',
    '�߰� �µ� ���� ����', '���� ���� ����', '�� ON �ֱ� ����', '�� OFF �ֱ� ����',
    '���� ���� �ֱ� �ݿ�', '���� ���� �ֱ� �ݿ�', '�ݺ� �ֱ� ����',
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
    lines = ['# �ð��� ���� �׽�Ʈ ������', '', '����: v0.1 | ������: 2026-10-20', '',
             '## ���� ����', '',
             '- �� �׽�Ʈ�� �ʱ�ȭ �� ���� �����Ѵ�. ù �Է��� t=0, ���� ǥ�� �ð�(ms)�� �����Ѵ�.',
             '- ���� 1=����, 0=����. �ҡ����� 1=ON, 0=OFF.',
             '- ��� ����� �ش� �ð��� �� �� ���̸� ���� ǥ ����� �����Ѵ�.',
             '- 50ms �� ���� ���������� �Է¸� ����ǰ� ����� �����Ѵ�.',
             '- ������ �̺�Ʈ �� 100ms���� 10ms �������� ��°� �ð��� Ȯ���Ѵ�.',
             '- CSV�� prepare_tests.py�� ������ ��밪�� Ȯ���Ѵ�. �� ������� ��밪�� �������� �ʴ´�.',
             '- REQ-001�� �� �� �ʱ�ȭ�� ���� ���� �˻硤���� ����� Ȯ���Ѵ�.', '']
    for (test_id, events), purpose, reqs in zip(CASES, PURPOSES, LINKS):
        lines += [f'## {test_id}: {purpose}', '',
                  '���� �䱸����: ' + ', '.join('REQ-' + r for r in reqs.split(',')), '',
                  '| �ð�(ms) | �µ�(��) | ���� ���� | ��� �� | ��� ���� |',
                  '|---|---|---|---|---|']
        lines += ['| ' + ' | '.join(map(str,e)) + ' |' for e in events]
        lines += ['']
    (ROOT/'docs/05-test-specification.md').write_text('\n'.join(lines),encoding='utf-8')
    lines = ['# �䱸���� ������ ǥ', '', '����: v0.1', '',
             '����� results/actual/summary.csv�� docs/07-verification-report.md���� Ȯ���Ѵ�.', '',
             '| �䱸���� | ���� ��� | ���� �ٰ� |', '|---|---|---|']
    elements = ['PreviousFan �ʱⰪ / ���� ǥ�� ������ ����','�Է� ù ���� t=0',
                'TemperatureSample / SensorSample / PreviousFan','���ø��� �Է¿� ���� ��� ����',
                'AtOrAboveOn / OnOrLower','AtOrBelowOff / OffOrHold','PreviousFan / OffOrHold',
                'SensorOverride','Fault','Fault','SensorOverride �� PreviousFan �ǵ��']
    for i, element in enumerate(elements,1):
        num=f'{i:03}'
        tests=[c[0] for c, links in zip(CASES,LINKS) if num in links.split(',')]
        evidence=', '.join(tests)
        if i==1: evidence='STATIC-INIT: ���� �˻� �� ���� ǥ�� �ʱ�ȭ ���� ���� (���� ������� ���� �������� ����)'
        lines.append(f'| REQ-{num} | {element} | {evidence} |')
    lines += ['', 'ASM-001~003�� �Է� ����̴�. ��ȿ�� �µ��� ���� ���� ������ �׽�Ʈ�� ����Ѵ�.',
              '�׽�Ʈ�� ����Ǿ� �ִٴ� ��Ǹ����� �䱸���� ������ �������� �ʴ´�. ���� ����� ���� �ٰŸ� �Բ� �����Ѵ�.', '']
    (ROOT/'docs/06-traceability.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__ == '__main__':
    write()
