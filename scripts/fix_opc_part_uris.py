import os, json

file1 = r'D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis_native.Report\StaticResources\RegisteredResources\Delhi-NCR Environmental Dark Navy'
file2 = r'D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis_native.Report\StaticResources\RegisteredResources\Delhi-NCR Environmental Dark Navy.json'

if os.path.exists(file1):
    os.remove(file1)
    print(f'Removed: {file1}')
else:
    print(f'Not found: {file1}')

if os.path.exists(file2):
    os.remove(file2)
    print(f'Removed: {file2}')
else:
    print(f'Not found: {file2}')

report_json_path = r'D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis_native.Report\definition\report.json'
with open(report_json_path, 'r', encoding='utf-8') as fp:
    report_json = json.load(fp)

# Update RegisteredResources path
for pkg in report_json.get('resourcePackages', []):
    if pkg.get('name') == 'RegisteredResources':
        for item in pkg.get('items', []):
            if item.get('name') == 'Delhi-NCR Environmental Dark Navy':
                old_path = item.get('path')
                item['path'] = 'theme_navy_environmental.json'
                print(f'Updated item path from "{old_path}" to "{item["path"]}"')

with open(report_json_path, 'w', encoding='utf-8') as fp:
    json.dump(report_json, fp, indent=2)

print('Updated report.json successfully!')
