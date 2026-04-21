import json, os, sys

DATASET_PATH = 'dataset/qa_pairs.json'
PDF_DIR      = 'dataset/pdfs'
REQUIRED     = {'id', 'pdf', 'question', 'ideal_answer', 'source_page', 'source_text'}

with open(DATASET_PATH) as f:
    pairs = json.load(f)

ids    = set()
errors = []

for i, p in enumerate(pairs):
    missing = REQUIRED - set(p.keys())
    if missing:
        errors.append(f'[{i}] id={p.get("id","?")} — missing fields: {missing}')
    if p.get('id') in ids:
        errors.append(f'[{i}] Duplicate id: {p["id"]}')
    ids.add(p.get('id'))
    pdf_path = os.path.join(PDF_DIR, str(p.get('pdf', '')))
    if not os.path.exists(pdf_path):
        errors.append(f'[{i}] PDF not found: {pdf_path}')
    if not isinstance(p.get('source_page'), int):
        errors.append(f'[{i}] source_page must be an integer, got: {p.get("source_page")}')

if errors:
    print(f'\nFound {len(errors)} error(s):')
    for e in errors:
        print(f'  {e}')
    sys.exit(1)
else:
    pdfs = len(set(p['pdf'] for p in pairs))
    print(f'Dataset OK — {len(pairs)} pairs across {pdfs} PDF(s). Ready for evaluation.')
