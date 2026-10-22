import os, json, glob

report_dir = r'D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis_native.Report'
model_dir = r'D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis_native.SemanticModel'

print('=== 1. AUDITING ALL FILES ON DISK FOR OPC URI COMPLIANCE ===')
for root, dirs, files in os.walk(report_dir):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, report_dir).replace('\\', '/')
        part_uri = '/Report/' + rel
        if ' ' in part_uri or any(ord(c) > 127 for c in part_uri):
            print(f'ILLEGAL FILE PART URI: {rel} -> {part_uri}')

for root, dirs, files in os.walk(model_dir):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, model_dir).replace('\\', '/')
        part_uri = '/DataModel/' + rel
        if ' ' in part_uri or any(ord(c) > 127 for c in part_uri):
            print(f'ILLEGAL MODEL PART URI: {rel} -> {part_uri}')

print('\n=== 2. AUDITING JSON PROPERTIES FOR RESOURCE PATHS WITH SPACES ===')
suspect_keys = {'path', 'url', 'uri', 'imagePath', 'resourcePackage', 'file', 'fileName'}

for f in glob.glob(os.path.join(report_dir, '**', '*.json'), recursive=True):
    rel = os.path.relpath(f, report_dir).replace('\\', '/')
    with open(f, 'r', encoding='utf-8') as fp:
        try:
            data = json.load(fp)
        except Exception as e:
            print(f'JSON SYNTAX ERROR in {rel}: {e}')
            continue
            
    def check_obj(d, path=''):
        if isinstance(d, dict):
            for k, v in d.items():
                if k in suspect_keys:
                    if isinstance(v, str) and (' ' in v or any(ord(c) > 127 for c in v)):
                        print(f'SUSPECT PROPERTY: {rel} -> {path}.{k} = "{v}"')
                check_obj(v, f'{path}.{k}')
        elif isinstance(d, list):
            for i, item in enumerate(d):
                check_obj(item, f'{path}[{i}]')
                
    check_obj(data)

print('\n=== AUDIT COMPLETE ===')
