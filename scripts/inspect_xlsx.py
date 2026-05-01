import pandas as pd
import sys

# Force UTF-8 stdout on Windows consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

path = sys.argv[1]
df = pd.read_excel(path)
print('PATH', path)
print('COLUMNS', df.columns.tolist())
print(df.head(3).to_string(index=False))
