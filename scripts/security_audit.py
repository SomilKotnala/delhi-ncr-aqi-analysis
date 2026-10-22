import subprocess, os, re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
output = subprocess.check_output(f'git -C "{PROJECT_ROOT}" ls-files', shell=True).decode('utf-8')
files = output.splitlines()

findings = []

user_path_pattern = re.compile(r'C:[/\\]Users[/\\][A-Za-z0-9_]+', re.IGNORECASE)
pwd_pattern = re.compile(r'(password\s*[:=]\s*["\']?[^"\'\s,;]+|pwd\s*[:=]\s*["\']?[^"\'\s,;]+)', re.IGNORECASE)
secret_pattern = re.compile(r'(secret|token|api_key|bearer)\s*[:=]\s*["\']?[A-Za-z0-9_\-\.]{8,}', re.IGNORECASE)

for f in files:
    full_path = PROJECT_ROOT / f
    if not full_path.exists():
        continue
    # skip binary files
    if f.endswith(('.pbix', '.png', '.jpg', '.parquet', '.zip')):
        continue
    
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
            for line_no, line in enumerate(fp, 1):
                # Check user paths
                for m in user_path_pattern.finditer(line):
                    findings.append((f, line_no, 'User Path', m.group(0), line.strip()[:100]))
                # Check passwords
                for m in pwd_pattern.finditer(line):
                    findings.append((f, line_no, 'Password Pattern', m.group(0), line.strip()[:100]))
                # Check secrets
                for m in secret_pattern.finditer(line):
                    findings.append((f, line_no, 'Secret Pattern', m.group(0), line.strip()[:100]))
    except Exception as e:
        print(f'Error reading {f}: {e}')

print(f'Total findings: {len(findings)}')
by_type = {}
for f, l, t, m, sample in findings:
    by_type.setdefault(t, []).append((f, l, m, sample))

for t, items in by_type.items():
    print(f'\n--- {t} ({len(items)} occurrences) ---')
    for f, l, m, sample in items[:25]:
        print(f'  {f}:{l} [{m}] -> {sample}')
    if len(items) > 25:
        print(f'  ... and {len(items) - 25} more')
