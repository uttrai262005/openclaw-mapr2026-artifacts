import os
import re
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / 'output' / 'mau_cham_tay.xlsx'

PHASE1 = {
    'BT1': ROOT / 'OpenClaw_Grading_Phase1' / '03_Ket_qua_AI' / 'ket_qua_BT1_clean.xlsx',
    'BT2': ROOT / 'OpenClaw_Grading_Phase1' / '03_Ket_qua_AI' / 'ket_qua_BT2_clean.xlsx',
    'BT3': ROOT / 'OpenClaw_Grading_Phase1' / '03_Ket_qua_AI' / 'ket_qua_BT3_clean_nckh.xlsx',
    'BT4': ROOT / 'OpenClaw_Grading_Phase1' / '03_Ket_qua_AI' / 'ket_qua_BT4_clean_nckh.xlsx',
}

PHASE2 = {
    'BT1': ROOT / 'OpenClaw_Grading_Phase2' / '03_Ket_qua_AI' / 'ket_qua_BT1_phase2_full.xlsx',
    'BT2': ROOT / 'OpenClaw_Grading_Phase2' / '03_Ket_qua_AI' / 'ket_qua_BT2_phase2_full.xlsx',
    'BT3': ROOT / 'OpenClaw_Grading_Phase2' / '03_Ket_qua_AI' / 'ket_qua_BT3_phase2_full.xlsx',
    'BT4': ROOT / 'OpenClaw_Grading_Phase2' / '03_Ket_qua_AI' / 'ket_qua_BT4_phase2_full.xlsx',
}

SAMPLE_SIZES = {
    'low': 8,
    'mid': 14,
    'high': 8,
}

RANDOM_STATE = 20260329


def find_col(cols, patterns):
    cols_list = list(cols)
    for pat in patterns:
        rx = re.compile(pat, re.IGNORECASE)
        for c in cols_list:
            if rx.search(str(c)):
                return c
    return None


def load_bt(bt: str) -> pd.DataFrame:
    p1 = PHASE1[bt]
    p2 = PHASE2[bt]
    if not p1.exists():
        raise FileNotFoundError(p1)
    if not p2.exists():
        raise FileNotFoundError(p2)

    df1 = pd.read_excel(p1)
    mssv1 = find_col(df1.columns, [r'^MSSV$'])
    total1 = find_col(df1.columns, [r'^Tổng\(/10\)$', r'^Tong\(/10\)$', r'Tổng'])
    if not mssv1 or not total1:
        raise ValueError(f'{bt}: cannot find MSSV/total in Phase1. cols={df1.columns.tolist()}')
    df1 = df1[[mssv1, total1]].rename(columns={mssv1: 'MSSV', total1: 'Tổng_P1(/10)'})

    df2 = pd.read_excel(p2)
    mssv2 = find_col(df2.columns, [r'^MSSV$'])
    total2 = find_col(df2.columns, [r'Tổng[_ ]?P2\(/10\)', r'Tổng_P2', r'Tong[_ ]?P2\(/10\)'])
    if not mssv2 or not total2:
        raise ValueError(f'{bt}: cannot find MSSV/Tổng_P2 in Phase2. cols={df2.columns.tolist()}')
    df2 = df2[[mssv2, total2]].rename(columns={mssv2: 'MSSV', total2: 'Tổng_P2(/10)'})

    # Normalize MSSV as string to avoid merge issues
    df1['MSSV'] = df1['MSSV'].astype(str)
    df2['MSSV'] = df2['MSSV'].astype(str)

    df = df1.merge(df2, on='MSSV', how='left')
    return df


def stratified_sample(df: pd.DataFrame) -> pd.DataFrame:
    """Target 30 rows: 8 low(<5), 14 mid(5–7.5), 8 high(>7.5).

    If a band doesn't have enough rows (common for some BTs), we *top-up*:
    - low shortage: take the lowest remaining Tổng_P1
    - high shortage: take the highest remaining Tổng_P1

    This keeps the sample size fixed at 30 while staying as close as possible
    to the intended strata.
    """
    df = df.copy()
    df['Tổng_P1(/10)'] = pd.to_numeric(df['Tổng_P1(/10)'], errors='coerce')
    df['Tổng_P2(/10)'] = pd.to_numeric(df['Tổng_P2(/10)'], errors='coerce')

    df = df.dropna(subset=['Tổng_P1(/10)'])

    low_pool = df[df['Tổng_P1(/10)'] < 5]
    mid_pool = df[(df['Tổng_P1(/10)'] >= 5) & (df['Tổng_P1(/10)'] <= 7.5)]
    high_pool = df[df['Tổng_P1(/10)'] > 7.5]

    # Start with true-band samples
    low_n = min(SAMPLE_SIZES['low'], len(low_pool))
    high_n = min(SAMPLE_SIZES['high'], len(high_pool))

    low = low_pool.sample(n=low_n, random_state=RANDOM_STATE) if low_n else low_pool.head(0)
    high = high_pool.sample(n=high_n, random_state=RANDOM_STATE) if high_n else high_pool.head(0)

    picked = set(low['MSSV']).union(set(high['MSSV']))
    remaining = df[~df['MSSV'].isin(picked)].copy()

    # Top-up low shortage from the lowest remaining
    low_short = SAMPLE_SIZES['low'] - len(low)
    if low_short > 0 and len(remaining) > 0:
        extra_low = remaining.sort_values(['Tổng_P1(/10)', 'MSSV']).head(low_short)
        low = pd.concat([low, extra_low], ignore_index=True)
        picked = set(low['MSSV']).union(set(high['MSSV']))
        remaining = df[~df['MSSV'].isin(picked)].copy()

    # Top-up high shortage from the highest remaining
    high_short = SAMPLE_SIZES['high'] - len(high)
    if high_short > 0 and len(remaining) > 0:
        extra_high = remaining.sort_values(['Tổng_P1(/10)', 'MSSV'], ascending=[False, True]).head(high_short)
        high = pd.concat([high, extra_high], ignore_index=True)
        picked = set(low['MSSV']).union(set(high['MSSV']))
        remaining = df[~df['MSSV'].isin(picked)].copy()

    # Mid: sample from the remaining (prefer true mid band first)
    mid_need = SAMPLE_SIZES['mid']
    mid_candidates = remaining.copy()
    # prioritize rows in intended mid band
    mid_first = mid_candidates[(mid_candidates['Tổng_P1(/10)'] >= 5) & (mid_candidates['Tổng_P1(/10)'] <= 7.5)]
    mid_rest = mid_candidates.drop(index=mid_first.index)

    if len(mid_first) >= mid_need:
        mid = mid_first.sample(n=mid_need, random_state=RANDOM_STATE)
    else:
        mid = mid_first
        still = mid_need - len(mid)
        if still > 0 and len(mid_rest) > 0:
            mid2 = mid_rest.sample(n=min(still, len(mid_rest)), random_state=RANDOM_STATE)
            mid = pd.concat([mid, mid2], ignore_index=True)

    # Final assembly & ordering
    low = low.copy(); mid = mid.copy(); high = high.copy()
    low['_band'] = 0
    mid['_band'] = 1
    high['_band'] = 2
    sampled = pd.concat([low, mid, high], ignore_index=True)

    # Ensure exactly 30 (in case of duplicates/edge cases)
    sampled = sampled.drop_duplicates(subset=['MSSV']).head(30)

    sampled = sampled.sort_values(['_band', 'Tổng_P1(/10)', 'MSSV'], ascending=[True, True, True]).drop(columns=['_band'])

    sampled['Điểm_tay_người1'] = ''
    sampled['Điểm_tay_người2'] = ''
    sampled = sampled[['MSSV', 'Tổng_P1(/10)', 'Tổng_P2(/10)', 'Điểm_tay_người1', 'Điểm_tay_người2']]
    return sampled


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(OUT_PATH, engine='openpyxl') as writer:
        for bt in ['BT1', 'BT2', 'BT3', 'BT4']:
            df = load_bt(bt)
            samp = stratified_sample(df)
            samp.to_excel(writer, sheet_name=bt, index=False)

    print(str(OUT_PATH))


if __name__ == '__main__':
    main()
