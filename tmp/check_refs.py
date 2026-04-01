import yaml, re, sys
data = open('docs/openapi.yaml', encoding='utf-8').read()
refs = set(re.findall(r"\$ref:\s*['\"]#/components/schemas/(\w+)['\"]", data))
parsed = yaml.safe_load(data)
schemas = set(parsed.get('components', {}).get('schemas', {}).keys())
missing = refs - schemas
unused = schemas - refs
if missing:
    print(f'BROKEN refs: {missing}')
    sys.exit(1)
else:
    print('All schema refs valid')
if unused:
    print(f'Unreferenced schemas (OK for top-level): {unused}')
