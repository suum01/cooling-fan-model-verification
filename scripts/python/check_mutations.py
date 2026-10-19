"""A mutant is detected only if a designated behavioral test rejects it."""
from check_results import ROOT, check, read_rows

TARGETS={'on_strict':'TC-003','wrong_feedback':'TC-017','no_override':'TC-012'}


def main():
    lines=['# ���� ���� ���', '',
           '���� �𵨰� �и��� �޸𸮻��� �����̸� ���� ������ .slx�� �������� �ʴ´�.', '',
           '| ���� | ��ǥ �׽�Ʈ | ��� | ���� �׽�Ʈ �� |', '|---|---|---|---|']
    all_detected=True
    for variant,target in TARGETS.items():
        folder=ROOT/'results/mutations'/variant
        check(folder)
        rows=read_rows(folder/'summary.csv')
        missing=any(not (folder/f'{r["test_id"]}.csv').exists() for r in rows)
        detected=not missing and any(r['test_id']==target and r['status']=='FAIL'
                                    and 'fan_cmd expected' in r['detail'] for r in rows)
        all_detected &= detected
        failures=sum(r['status']=='FAIL' for r in rows)
        lines.append(f'| {variant} | {target} | {"����" if detected else "��Ȯ��"} | {failures} |')
    (ROOT/'results/mutation-summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return all_detected


if __name__=='__main__':
    raise SystemExit(0 if main() else 1)
