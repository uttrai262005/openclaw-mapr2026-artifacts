import pandas as pd
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

p = r'output/mau_cham_tay.xlsx'
xl = pd.ExcelFile(p)
print('sheets', xl.sheet_names)
for sh in xl.sheet_names:
    df = pd.read_excel(p, sheet_name=sh)
    low = (df['Tổng_P1(/10)'] < 5).sum()
    mid = ((df['Tổng_P1(/10)'] >= 5) & (df['Tổng_P1(/10)'] <= 7.5)).sum()
    high = (df['Tổng_P1(/10)'] > 7.5).sum()
    print(sh, 'rows', len(df), 'low/mid/high', (low, mid, high))
