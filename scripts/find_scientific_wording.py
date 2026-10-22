import subprocess, os, re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
output = subprocess.check_output(f'git -C "{PROJECT_ROOT}" ls-files', shell=True).decode('utf-8')
files = output.splitlines()

findings = []
patterns = [
    (re.compile(r'(sensor\s+saturation|physical\s+sensor\s+ceiling|detector\s+saturation)', re.IGNORECASE), 'Sensor Saturation Claim'),
    (re.compile(r'(causal\s+counterfactual|definitive\s+counterfactual|clean\s+counterfactual|causal\s+decomposition|causal\s+finding)', re.IGNORECASE), 'Overstated Causal Counterfactual')
]

for f in files:
    if f.endswith(('.pbix', '.png', '.jpg', '.parquet', '.zip')):
        continue
    full_path = PROJECT_ROOT / f
    if not os.path.exists(full_path):
        continue
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
        for line_no, line in enumerate(fp, 1):
            for pat, label in patterns:
                if pat.search(line):
                    findings.append((f, line_no, label, line.strip()))

print(f'Total occurrences found: {len(findings)}')
for f, l, label, text in findings:
    print(f'{f}:{l} [{label}] -> {text[:110]}')
