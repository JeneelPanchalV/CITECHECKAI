import pandas as pd

df = pd.read_csv('results/ragas_scores.csv')
metrics = ['faithfulness', 'answer_relevancy', 'context_precision']

print('=' * 55)
print('DOCGUARD AI — RAGAS EVALUATION RESULTS')
print('=' * 55)

print('\n--- Overall (mean +/- std) ---')
for m in metrics:
    print(f'{m:<25}  {df[m].mean():.3f}  +-  {df[m].std():.3f}')

print('\n--- Guard analysis ---')
total   = len(df)
ok      = (df['guard_status'] == 'OK').sum()
refused = total - ok
print(f'Total questions   : {total}')
print(f'Answered (OK)     : {ok}   ({100*ok/total:.1f}%)')
print(f'Refused by guard  : {refused}   ({100*refused/total:.1f}%)')

print('\n--- Per-PDF breakdown ---')
per_pdf = df.groupby('pdf')[metrics].mean().round(3)
print(per_pdf.to_string())

print('\n--- Lowest faithfulness questions (bottom 5) ---')
low = df.nsmallest(5, 'faithfulness')[['id', 'question', 'faithfulness', 'guard_status']]
for _, row in low.iterrows():
    print(f'  [{row["id"]}] faith={row["faithfulness"]:.3f}  guard={row["guard_status"]}')
    print(f'           {row["question"][:65]}...')

print('\n' + '=' * 55)
