import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr

OUT_PATH = Path('output/soict_analysis_tables.xlsx')
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# phase1/phase2 files (full dataset)
P1_FILES = {
    'BT1': Path('output/ket_qua_BT1_clean.xlsx'),
    'BT2': Path('output/ket_qua_BT2_clean.xlsx'),
    'BT3': Path('output/ket_qua_BT3_clean_nckh.xlsx'),
    'BT4': Path('output/ket_qua_BT4_clean_nckh.xlsx'),
}
P2_FILES = {
    'BT1': Path('output/ket_qua_BT1_phase2_full.xlsx'),
    'BT2': Path('output/ket_qua_BT2_phase2_full.xlsx'),
    'BT3': Path('output/ket_qua_BT3_phase2_full.xlsx'),
    'BT4': Path('output/ket_qua_BT4_phase2_full_resume.xlsx'),
}

# human scores exist only in mau_cham_tay.xlsx (30 samples/sheet)
HUMAN_PATH = Path('output/mau_cham_tay.xlsx')
HUMAN_SHEET_MAP = {'BT1': 'BT1', 'BT2': 'BT2', 'BT3': 'BT3', 'BT4': 'BT4'}
# Column names in human file
HUMAN_COLS = {
    'BT1': {'mssv': 'MSSV', 'P1': 'Tổng_P1(/10)', 'P2': 'Tổng_P2(/10)', 'Ng1': 'Điểm_tay_người1', 'Ng2': 'Điểm_tay_người2'},
    'BT2': {'mssv': 'MSSV', 'P1': 'Tổng_P1(/10)', 'P2': 'Tổng_P2(/10)', 'Ng1': 'Điểm_tay_người1', 'Ng2': 'Điểm_tay_người2'},
    'BT3': {'mssv': 'MSSV', 'P1': 'Tổng_P1(/10)', 'P2': 'Tổng_P2(/10)', 'Ng1': 'Điểm_tay_người1', 'Ng2': 'Điểm_tay_người2'},
    'BT4': {'mssv': 'MSSV', 'P1': 'Tổng_P1(/10)', 'P2': 'Tổng_P2(/10)', 'Ng1': 'Điểm_tay_người1', 'Ng2': 'Điểm_tay_người2'},
}

def qwk_int(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() == 0:
        return np.nan
    ai = np.round(a[m] * 2).astype(int)
    bi = np.round(b[m] * 2).astype(int)
    return cohen_kappa_score(ai, bi, weights='quadratic')

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


def signed_error(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() == 0:
        return np.nan
    return float(np.mean(a[m] - b[m]))


def load_phase1(bt):
    df = pd.read_excel(P1_FILES[bt])
    total_col = [c for c in df.columns if 'Tổng(/10)' in c][0]
    tc_cols = [c for c in df.columns if c.startswith('TC')]
    return df[['MSSV'] + tc_cols + [total_col]].rename(columns={total_col: 'Total_P1'})


def load_phase2(bt):
    df = pd.read_excel(P2_FILES[bt])
    tc_cols = [c for c in df.columns if c.startswith('TC')]
    return df[['MSSV'] + tc_cols + ['Tổng_P2(/10)', 'Tổng_P1(/10)', 'Diff(P2-P1)', 'Veto', 'Spread', 'Total_content', 'Total_structure', 'Total_language']].rename(columns={'Tổng_P2(/10)': 'Total_P2', 'Tổng_P1(/10)': 'Total_P1_fromP2'})


def load_human(bt):
    df = pd.read_excel(HUMAN_PATH, sheet_name=HUMAN_SHEET_MAP[bt])
    c = HUMAN_COLS[bt]
    out = df[[c['mssv'], c['P1'], c['P2'], c['Ng1'], c['Ng2']]].copy()
    out.columns = ['MSSV', 'Total_P1_sample', 'Total_P2_sample', 'Ng1', 'Ng2']
    out['GT'] = (out['Ng1'] + out['Ng2']) / 2
    return out


summary_rows = []
all_tc_tables = {}
all_bias_tables = {}

with pd.ExcelWriter(OUT_PATH, engine='openpyxl') as writer:
    for bt in ['BT1','BT2','BT3','BT4']:
        p1 = load_phase1(bt)
        p2 = load_phase2(bt)
        merged = p2.merge(p1, on='MSSV', how='left', suffixes=('', '_p1src'))

        # Basic sanity
        merged['Total_P1'] = merged['Total_P1'].astype(float)
        merged['Total_P2'] = merged['Total_P2'].astype(float)

        # TC-level differences (P2 - P1)
        tc_cols = [c for c in p1.columns if c.startswith('TC')]
        tc_diff = pd.DataFrame({'MSSV': merged['MSSV']})
        for c in tc_cols:
            tc_diff[c] = merged[c].astype(float)
            tc_diff[c + '_P1'] = merged[c + '_p1src'].astype(float)
            tc_diff[c + '_Diff(P2-P1)'] = tc_diff[c] - tc_diff[c + '_P1']

        # Summaries per TC
        tc_summary = []
        for c in tc_cols:
            d = tc_diff[c + '_Diff(P2-P1)']
            tc_summary.append({
                'BT': bt,
                'TC': c,
                'mean_diff(P2-P1)': float(np.nanmean(d)),
                'median_diff(P2-P1)': float(np.nanmedian(d)),
                'std_diff(P2-P1)': float(np.nanstd(d)),
                'pct_P2_gt_P1': float(np.nanmean((d>0).astype(float)))
            })
        tc_summary_df = pd.DataFrame(tc_summary)

        # Bias table for full dataset (P2 vs P1 only)
        bias = {
            'BT': bt,
            'N': int(len(merged)),
            'mean_Total_P1': float(np.nanmean(merged['Total_P1'])),
            'mean_Total_P2': float(np.nanmean(merged['Total_P2'])),
            'mean_diff(P2-P1)': float(np.nanmean(merged['Diff(P2-P1)'])),
            'median_diff(P2-P1)': float(np.nanmedian(merged['Diff(P2-P1)'])),
            'pct_veto': float(np.mean(merged['Veto'].astype(str).str.upper().isin(['Y','YES','TRUE','1']).astype(float))) if 'Veto' in merged else np.nan,
            'mean_spread': float(np.nanmean(merged['Spread'])),
        }

        # Human-sample evaluation (30 samples) for explanation sections
        human = load_human(bt)
        m = merged.merge(human[['MSSV','Ng1','Ng2','GT']], on='MSSV', how='inner')
        # Use totals from merged (computed on full outputs) on same MSSVs
        bias.update({
            'N_human_sample': int(len(m)),
            'Inter_rater_QWK': qwk_int(m['Ng1'], m['Ng2']),
            'P1_vs_GT_QWK': qwk_int(m['Total_P1'], m['GT']),
            'P1_vs_GT_MAE': mae(m['Total_P1'], m['GT']),
            'P1_vs_GT_Pearson_r': pearson(m['Total_P1'], m['GT']),
            'P1_signed_error': signed_error(m['Total_P1'], m['GT']),
            'P2_vs_GT_QWK': qwk_int(m['Total_P2'], m['GT']),
            'P2_vs_GT_MAE': mae(m['Total_P2'], m['GT']),
            'P2_vs_GT_Pearson_r': pearson(m['Total_P2'], m['GT']),
            'P2_signed_error': signed_error(m['Total_P2'], m['GT']),
        })

        summary_rows.append(bias)

        # write sheets
        merged.to_excel(writer, sheet_name=f'{bt}_merged', index=False)
        tc_diff.to_excel(writer, sheet_name=f'{bt}_tc_diff', index=False)
        tc_summary_df.to_excel(writer, sheet_name=f'{bt}_tc_summary', index=False)

    summary = pd.DataFrame(summary_rows)
    summary.to_excel(writer, sheet_name='summary', index=False)

print(f'Saved: {OUT_PATH.resolve()}')
