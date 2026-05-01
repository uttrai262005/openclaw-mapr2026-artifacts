import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr

in_path = Path('output/mau_cham_tay.xlsx')
out_path = Path('output/bang_metrics_paper.xlsx')

xls = pd.ExcelFile(in_path)
expected = ['BT1','BT2','BT3','BT4']
missing = [s for s in expected if s not in xls.sheet_names]
if missing:
    raise SystemExit(f'Missing sheets: {missing}. Found: {xls.sheet_names}')

def qwk_int(a, b):
    ai = np.round(np.asarray(a, dtype=float) * 2).astype('float')
    bi = np.round(np.asarray(b, dtype=float) * 2).astype('float')
    m = np.isfinite(ai) & np.isfinite(bi)
    if m.sum() == 0:
        return np.nan
    return cohen_kappa_score(ai[m].astype(int), bi[m].astype(int), weights='quadratic')

def mae(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() == 0:
        return np.nan
    return float(np.mean(np.abs(a[m] - b[m])))

def pearson(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 2:
        return np.nan
    return float(pearsonr(a[m], b[m]).statistic)

colmap = {
    'BT1': {'P1': 7, 'P2': 8, 'Ng1': 9, 'Ng2': 10},
    'BT2': {'P1': 2, 'P2': 3, 'Ng1': 4, 'Ng2': 5},
    'BT3': {'P1': 2, 'P2': 3, 'Ng1': 4, 'Ng2': 5},
    'BT4': {'P1': 2, 'P2': 3, 'Ng1': 4, 'Ng2': 5},
}

rows = []
out_path.parent.mkdir(parents=True, exist_ok=True)

with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
    for sheet in expected:
        df = pd.read_excel(in_path, sheet_name=sheet)
        m = colmap[sheet]

        def series_at(col_1idx):
            idx = col_1idx - 1
            if idx < 0 or idx >= df.shape[1]:
                raise ValueError(f'{sheet}: expected col {col_1idx} but only {df.shape[1]} cols')
            return df.iloc[:, idx]

        P1 = series_at(m['P1'])
        P2 = series_at(m['P2'])
        Ng1 = series_at(m['Ng1'])
        Ng2 = series_at(m['Ng2'])
        GT = (Ng1 + Ng2) / 2

        res = {
            'BT': sheet,
            'Inter_rater_QWK': qwk_int(Ng1, Ng2),
            'P1_vs_GT_QWK': qwk_int(P1, GT),
            'P1_vs_GT_MAE': mae(P1, GT),
            'P1_vs_GT_Pearson_r': pearson(P1, GT),
            'P2_vs_GT_QWK': qwk_int(P2, GT),
            'P2_vs_GT_MAE': mae(P2, GT),
            'P2_vs_GT_Pearson_r': pearson(P2, GT),
        }
        numeric = [v for k, v in res.items() if k != 'BT']
        res['AVG'] = float(np.nanmean(numeric))
        rows.append(res)

        extracted = pd.DataFrame({'P1': P1, 'P2': P2, 'Ng1': Ng1, 'Ng2': Ng2, 'GT': GT})
        extracted.to_excel(writer, sheet_name=sheet, index=False)

    summary = pd.DataFrame(rows)
    cols = ['BT','Inter_rater_QWK','P1_vs_GT_QWK','P1_vs_GT_MAE','P1_vs_GT_Pearson_r','P2_vs_GT_QWK','P2_vs_GT_MAE','P2_vs_GT_Pearson_r','AVG']
    summary = summary[cols]
    summary.to_excel(writer, sheet_name='metrics', index=False)

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 50)
print(summary.to_string(index=False))
print(f"\nSaved: {out_path.resolve()}")
