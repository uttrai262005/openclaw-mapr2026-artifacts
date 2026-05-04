from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.metrics import cohen_kappa_score

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'output' / 'raw'
OUT_XLSX = ROOT / 'output' / 'mapr_analysis_tables.xlsx'
OUT_JSON = ROOT / 'output' / 'mapr_analysis_summary.json'

ASSIGNMENTS = ['BT1', 'BT2', 'BT3', 'BT4']
MODELS = ['gpt52_single', 'gpt54', 'gpt4o', 'gpt54mini']
MODEL_LABELS = {
    'gpt52_single': 'GPT-5.2 (single-agent)',
    'gpt54': 'GPT-5.4',
    'gpt4o': 'GPT-4o',
    'gpt54mini': 'GPT-5.4-mini',
}


def qwk_int(a, b):
    ai = np.round(np.asarray(a, dtype=float) * 2).astype('float')
    bi = np.round(np.asarray(b, dtype=float) * 2).astype('float')
    m = np.isfinite(ai) & np.isfinite(bi)
    if m.sum() == 0:
        return np.nan
    return float(cohen_kappa_score(ai[m].astype(int), bi[m].astype(int), weights='quadratic'))


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


def bootstrap_ci(metric_fn, x, y, B=3000, seed=42):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m]
    y = y[m]
    n = len(x)
    if n == 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        idx = rng.integers(0, n, size=n)
        vals.append(metric_fn(x[idx], y[idx]))
    return (float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5)))


def read_human_subset():
    path = SRC / 'human_subset' / 'mau_cham_tay.xlsx'
    xls = pd.ExcelFile(path)
    out = {}
    colmaps = {
        'BT1': {'id': 'MSSV', 'gpt52_single': 'Tổng_P1(/10)', 'gpt52_multi': 'Tổng_P2(/10)', 'human1': 'Điểm_tay_người1', 'human2': 'Điểm_tay_người2'},
        'BT2': {'id': 'MSSV', 'gpt52_single': 'Tổng_P1(/10)', 'gpt52_multi': 'Tổng_P2(/10)', 'human1': 'Điểm_tay_người1', 'human2': 'Điểm_tay_người2'},
        'BT3': {'id': 'MSSV', 'gpt52_single': 'Tổng_P1(/10)', 'gpt52_multi': 'Tổng_P2(/10)', 'human1': 'Điểm_tay_người1', 'human2': 'Điểm_tay_người2'},
        'BT4': {'id': 'MSSV', 'gpt52_single': 'Tổng_P1(/10)', 'gpt52_multi': 'Tổng_P2(/10)', 'human1': 'Điểm_tay_người1', 'human2': 'Điểm_tay_người2'},
    }
    for bt in ASSIGNMENTS:
        df = pd.read_excel(path, sheet_name=bt)
        m = colmaps[bt]
        sdf = pd.DataFrame({
            'student': df[m['id']].astype(str).str.replace('.0', '', regex=False).str.strip(),
            'gpt52_single': pd.to_numeric(df[m['gpt52_single']], errors='coerce'),
            'gpt52_multi': pd.to_numeric(df[m['gpt52_multi']], errors='coerce'),
            'human1': pd.to_numeric(df[m['human1']], errors='coerce'),
            'human2': pd.to_numeric(df[m['human2']], errors='coerce'),
        })
        sdf['GT'] = (sdf['human1'] + sdf['human2']) / 2
        out[bt] = sdf
    return out


def load_total_table(path: Path, preferred_total_col: str | None = None) -> pd.DataFrame:
    df = pd.read_excel(path)
    if preferred_total_col and preferred_total_col in df.columns:
        total_col = preferred_total_col
    else:
        cols = {str(c).lower(): c for c in df.columns}
        student_col = cols.get('student') or cols.get('mssv')
        total_col = cols.get('total') or cols.get('tổng(/10)') or cols.get('tổng_p1(/10)') or cols.get('p1_total')
        if not total_col:
            candidates = [c for c in df.columns if 'total' in str(c).lower() or 'tổng' in str(c).lower()]
            for cand in candidates:
                s = str(cand).lower()
                if 'p2' in s:
                    total_col = cand
                    break
            if not total_col and candidates:
                total_col = candidates[0]
    cols = {str(c).lower(): c for c in df.columns}
    student_col = cols.get('student') or cols.get('mssv')
    if not student_col:
        raise ValueError(f'Missing student column in {path}')
    if not total_col:
        raise ValueError(f'Missing total column in {path}; columns={list(df.columns)}')
    out = pd.DataFrame({
        'student': df[student_col].astype(str).str.replace('.0', '', regex=False).str.strip(),
        'total': pd.to_numeric(df[total_col], errors='coerce')
    })
    return out.drop_duplicates(subset=['student'])


def load_sources():
    return {
        'gpt52_single_full': {bt: load_total_table(SRC / 'gpt52_single_full' / f'ket_qua_{bt}_clean.xlsx') for bt in ASSIGNMENTS},
        'gpt52_multi_full': {bt: load_total_table(SRC / 'gpt52_multi_full' / f'ket_qua_{bt}_phase2.xlsx', preferred_total_col='Tổng_P2(/10)') for bt in ASSIGNMENTS},
        'gpt4o_full': {bt: load_total_table(SRC / 'gpt4o_full' / f'ket_qua_{bt}_gpt4o.xlsx', preferred_total_col='total') for bt in ASSIGNMENTS},
        'gpt54mini_full': {bt: load_total_table(SRC / 'gpt54mini_full' / f'ket_qua_{bt}_gpt_5_4_mini.xlsx', preferred_total_col='total') for bt in ASSIGNMENTS},
        'gpt54_subset': {bt: load_total_table(SRC / 'gpt54_subset' / f'ket_qua_mau_cham_tay_{bt}_gpt_5_4.xlsx', preferred_total_col='total') for bt in ASSIGNMENTS},
    }


def build_subset_tables(human_subset, sources):
    merged = {}
    for bt in ASSIGNMENTS:
        base = human_subset[bt].copy()
        base = base.merge(sources['gpt54_subset'][bt].rename(columns={'total': 'gpt54'}), on='student', how='left')
        base = base.merge(sources['gpt4o_full'][bt].rename(columns={'total': 'gpt4o'}), on='student', how='left')
        base = base.merge(sources['gpt54mini_full'][bt].rename(columns={'total': 'gpt54mini'}), on='student', how='left')
        base = base.merge(sources['gpt52_single_full'][bt].rename(columns={'total': 'gpt52_single_full'}), on='student', how='left')
        base = base.merge(sources['gpt52_multi_full'][bt].rename(columns={'total': 'gpt52_multi_full'}), on='student', how='left')
        merged[bt] = base
    return merged


def compute_summary(subset_tables):
    rows = []
    ci_rows = []
    bias_rows = []
    multi_rows = []
    for i, bt in enumerate(ASSIGNMENTS, start=1):
        df = subset_tables[bt]
        gt = df['GT']
        human_qwk = qwk_int(df['human1'], df['human2'])
        human_ci = bootstrap_ci(qwk_int, df['human1'], df['human2'], seed=100 + i)
        bias = {'BT': bt, 'Mean_GT': float(np.nanmean(gt))}
        row = {'BT': bt, 'Human_QWK': human_qwk}
        ci_row = {'BT': bt, 'Human_QWK': human_qwk, 'Human_QWK_CI95_low': human_ci[0], 'Human_QWK_CI95_high': human_ci[1]}
        for j, model in enumerate(MODELS, start=1):
            vals = df[model]
            row[f'{model}_QWK'] = qwk_int(vals, gt)
            row[f'{model}_MAE'] = mae(vals, gt)
            row[f'{model}_Pearson_r'] = pearson(vals, gt)
            qwk_ci = bootstrap_ci(qwk_int, vals, gt, seed=1000 + i * 10 + j)
            mae_ci = bootstrap_ci(mae, vals, gt, seed=2000 + i * 10 + j)
            ci_row[f'{model}_QWK'] = row[f'{model}_QWK']
            ci_row[f'{model}_QWK_CI95_low'] = qwk_ci[0]
            ci_row[f'{model}_QWK_CI95_high'] = qwk_ci[1]
            ci_row[f'{model}_MAE'] = row[f'{model}_MAE']
            ci_row[f'{model}_MAE_CI95_low'] = mae_ci[0]
            ci_row[f'{model}_MAE_CI95_high'] = mae_ci[1]
            ci_row[f'{model}_Pearson_r'] = row[f'{model}_Pearson_r']
            bias[f'{model}_Bias'] = float(np.nanmean(vals - gt))
        rows.append(row)
        ci_rows.append(ci_row)
        bias_rows.append(bias)
        multi_rows.append({
            'BT': bt,
            'Single_Agent_QWK': row['gpt52_single_QWK'],
            'Multi_Agent_QWK': qwk_int(df['gpt52_multi'], gt),
            'Multi_Agent_MAE': mae(df['gpt52_multi'], gt),
            'Multi_Agent_Pearson_r': pearson(df['gpt52_multi'], gt),
        })
    return pd.DataFrame(rows), pd.DataFrame(ci_rows), pd.DataFrame(bias_rows), pd.DataFrame(multi_rows)


def compute_full_deltas(sources):
    rows = []
    for bt in ASSIGNMENTS:
        p1 = sources['gpt52_single_full'][bt].rename(columns={'total': 'p1'})
        p2 = sources['gpt52_multi_full'][bt].rename(columns={'total': 'p2'})
        m = p1.merge(p2, on='student', how='inner')
        delta = pd.to_numeric(m['p2'], errors='coerce') - pd.to_numeric(m['p1'], errors='coerce')
        rows.append({
            'BT': bt,
            'N_full': int(len(m)),
            'mean_P2_minus_P1': float(np.nanmean(delta)),
            'median_P2_minus_P1': float(np.nanmedian(delta)),
        })
    return pd.DataFrame(rows)


def main():
    human_subset = read_human_subset()
    sources = load_sources()
    subset_tables = build_subset_tables(human_subset, sources)
    summary, ci, bias, multi = compute_summary(subset_tables)
    full_delta = compute_full_deltas(sources)

    OUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUT_XLSX, engine='openpyxl') as writer:
        summary.to_excel(writer, sheet_name='summary', index=False)
        ci.to_excel(writer, sheet_name='ci_metrics', index=False)
        bias.to_excel(writer, sheet_name='bias_table', index=False)
        multi.to_excel(writer, sheet_name='multiagent_subset', index=False)
        full_delta.to_excel(writer, sheet_name='full_dataset_delta', index=False)
        for bt, df in subset_tables.items():
            df.to_excel(writer, sheet_name=f'subset_{bt}', index=False)

    payload = {
        'summary_rows': summary.to_dict(orient='records'),
        'bias_rows': bias.to_dict(orient='records'),
        'multiagent_rows': multi.to_dict(orient='records'),
        'full_delta_rows': full_delta.to_dict(orient='records'),
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved: {OUT_XLSX}')
    print(f'Saved: {OUT_JSON}')


if __name__ == '__main__':
    main()
