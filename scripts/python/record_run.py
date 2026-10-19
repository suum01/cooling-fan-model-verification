"""Record content hashes of the executed source, vectors, model and evidence."""
import hashlib
import json
import platform
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def record():
    hashes={}
    for folder in ('scripts','tests','models'):
        for path in sorted((ROOT/folder).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.slxc','.pyc'):
                hashes[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    evidence={}
    for path in sorted((ROOT/'results').rglob('*')):
        if path.is_file() and path.suffix in ('.csv','.png'):
            evidence[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    result={'python':platform.python_version(),
            'source_state':'Implementation files identified by SHA-256; see containing Git commit for repository revision.',
            'source_sha256':hashes,'evidence_sha256':evidence}
    (ROOT/'results/reproducibility.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'Recorded {len(hashes)} source/data hashes and {len(evidence)} evidence hashes')


if __name__=='__main__':
    record()
