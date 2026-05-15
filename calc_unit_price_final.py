import pandas as pd, numpy as np, glob, re

EUR_USD = 1.085
TARGET = ['US','GB','JP','KR','TW','TH','ID','VN','HK','SG','MY','CN']

# =============================================
# 口径说明（重要！）
# =============================================
# Believe 分成前单价：
#   公式 = Gross Revenue (EUR) × 1.085 / Quantity × 1000
#   方法 = 加权平均：Σ(Gross Revenue × 1.085) / Σ(Quantity) × 1000
#
# 东西（东西音乐）分成前单价：
#   公式 = AmountPaidByStore (USD) / Quantity × 1000
#   方法 = 加权平均：Σ(AmountPaidByStore) / Σ(Quantity) × 1000
#   注意：用 AmountPaidByStore（分成前），不用 CustomerAmount（分成后）
#
# bYv（Believe YouTube Music Video）来源：
#   来自 believe music video.xlsx，Platform = YouTube Music Video
#   公式 = Unit Price (EUR) × 1.085 × 1000
#   方法 = 按 quantity 加权平均：Σ(Unit Price × Quantity) / Σ(Quantity) × 1.085 × 1000
#   注意：Excel 只有 Unit Price（单价）和 Quantity，没有 Revenue 列
#
# YouTube 子平台映射：
#   Believe：OfficialContent+UGC → ContentID，AudioTier → Music/Art Tracks，Shorts → Shorts
#   东西：AudioContentID → ContentID，ArtTracks → Music，AudioTier → Music，Shorts → Shorts
#
# CN（中国大陆）：东西无 Spotify/Believe 无 Spotify/Believe 无 YouTube 音乐
# =============================================

# ============================
# BELIEVE CSV: bSp, bAp, bYm, bYc, bSh
# ============================
bel_files = sorted(glob.glob('/Users/olivia/Downloads/20260[123] Believe.csv'))
bel = pd.concat([pd.read_csv(f, sep=';', low_memory=False) for f in bel_files], ignore_index=True)
bel['qty'] = pd.to_numeric(bel['Quantity'], errors='coerce').fillna(0)
bel['rev_usd'] = pd.to_numeric(bel['Gross Revenue'], errors='coerce').fillna(0) * EUR_USD

country_map = {
    'united states':'US','united kingdom':'GB','japan':'JP',
    'korea, republic of':'KR','korea':'KR','south korea':'KR',
    'taiwan, province of china':'TW','taiwan':'TW',
    'thailand':'TH','indonesia':'ID','viet nam':'VN',
    'india':'IN','hong kong':'HK','singapore':'SG','malaysia':'MY','china mainland':'CN',
}
bel['cc'] = bel['Country / Region'].map(lambda x: country_map.get(str(x).lower().strip()))

plat_map = {
    'YouTube Official Content':'YTOfficial',
    'YouTube UGC':'YTUGC',
    'YouTube Audio Tier':'YTAudioTier',
    'YouTube Shorts':'YTShorts',
    'Spotify':'Spotify',
}
for p in bel['Platform'].dropna().unique():
    if 'apple' in str(p).lower():
        plat_map[p] = 'AppleMusic'
bel['plat'] = bel['Platform'].map(plat_map)

def wavg_1000(df):
    q = df['qty'].sum(); r = df['rev_usd'].sum()
    return round(r/q*1000, 4) if q > 0 else None

# ============================
# BELIEVE bYv from music video.xlsx
# ============================
ytex = pd.read_excel('/Users/olivia/Desktop/believe music video.xlsx')
ytex['qty'] = pd.to_numeric(ytex['Quantity'], errors='coerce').fillna(0)
ytex['up_eur'] = pd.to_numeric(ytex['Unit Price'], errors='coerce').fillna(0)
yc_map = {'united states':'US','united kingdom':'GB','japan':'JP','korea':'KR',
          'taiwan':'TW','thailand':'TH','indonesia':'ID','viet nam':'VN',
          'hong kong':'HK','singapore':'SG','malaysia':'MY','china':'CN'}
ytex['cc'] = ytex['Country / Region'].str.lower().str.strip().map(yc_map)
ytex = ytex[ytex['qty'] > 0]

def bYv_wavg(df):
    tq = df['qty'].sum()
    tr = (df['up_eur'] * df['qty']).sum()
    if tq == 0: return None
    return round(tr / tq * EUR_USD * 1000, 4)

# ============================
# BELIEVE 结果汇总
# ============================
bel_results = {}
for region in TARGET:
    rd = bel[(bel['cc']==region) & bel['plat'].notna() & (bel['qty']>0)]
    sp = wavg_1000(rd[rd['plat']=='Spotify'])
    ap = wavg_1000(rd[rd['plat']=='AppleMusic'])
    ym = wavg_1000(rd[rd['plat']=='YTAudioTier'])
    yc = wavg_1000(rd[rd['plat'].isin(['YTOfficial','YTUGC'])])
    sh = wavg_1000(rd[rd['plat']=='YTShorts'])
    yv_rd = ytex[ytex['cc']==region]
    yv = bYv_wavg(yv_rd) if len(yv_rd) > 0 else None
    bel_results[region] = {'bSp':sp,'bAp':ap,'bYm':ym,'bYv':yv,'bYc':yc,'bSh':sh}

# ============================
# 东西 CSV: dSp, dAp, dYmAt, dYmAr, dYcAr, dYv, dSh
# ============================
dx_files = sorted(glob.glob('/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_20260[123].csv'))
dx = pd.concat([pd.read_csv(f, low_memory=False, encoding='latin1') for f in dx_files], ignore_index=True)
dx['qty'] = pd.to_numeric(dx['Quantity'], errors='coerce').fillna(0)
dx['rev'] = pd.to_numeric(dx['AmountPaidByStore'], errors='coerce').fillna(0)  # 分成前 USD

dx['s_lower'] = dx['Store'].str.lower().str.strip()

def get_plat2(s):
    s = str(s).lower()
    if 'spotify' in s: return 'Spotify'
    if 'apple' in s: return 'AppleMusic'
    if 'shorts' in s: return 'YTShorts'
    if 'audio tier' in s: return 'YTAudioTier'
    if 'audio content' in s: return 'YTContentID'
    if 'art tracks' in s: return 'YTArtTracks'
    if 'youtube' in s: return 'YTMusicVideo'
    return None

dx['plat2'] = dx['s_lower'].apply(get_plat2)
dx2 = dx[dx['plat2'].notna() & (dx['qty']>0)].copy()

def wavg_dx(df):
    q = df['qty'].sum(); r = df['rev'].sum()
    return round(r/q*1000, 4) if q > 0 else None

dx_results = {}
for region in TARGET:
    rd = dx2[dx2['Territories']==region]
    sp  = wavg_dx(rd[rd['plat2']=='Spotify'])
    ap  = wavg_dx(rd[rd['plat2']=='AppleMusic'])
    at  = wavg_dx(rd[rd['plat2']=='YTAudioTier'])
    ar  = wavg_dx(rd[rd['plat2']=='YTArtTracks'])
    cid = wavg_dx(rd[rd['plat2']=='YTContentID'])
    yv  = wavg_dx(rd[rd['plat2']=='YTMusicVideo'])
    sh  = wavg_dx(rd[rd['plat2']=='YTShorts'])
    dx_results[region] = {
        'dSp':sp,'dAp':ap,'dYmAt':at,'dYmAr':ar,
        'dYcAr':cid,'dYv':yv,'dSh':sh
    }

# ============================
# 打印完整结果
# ============================
print(f'{"Region":<4}  {"bSp":>8} {"bAp":>8} {"bYm":>8} {"bYv":>8} {"bYc":>8} {"bSh":>8} || {"dSp":>8} {"dAp":>8} {"dYmAt":>8} {"dYmAr":>8} {"dYcAr":>8} {"dYv":>8} {"dSh":>8}')
for region in TARGET:
    br = bel_results[region]
    dr = dx_results[region]
    def fv(v): return f'{v:.4f}' if v is not None else 'null'
    print(f'{region:<4}  {fv(br["bSp"]):>8} {fv(br["bAp"]):>8} {fv(br["bYm"]):>8} {fv(br["bYv"]):>8} {fv(br["bYc"]):>8} {fv(br["bSh"]):>8} || '
          f'{fv(dr["dSp"]):>8} {fv(dr["dAp"]):>8} {fv(dr["dYmAt"]):>8} {fv(dr["dYmAr"]):>8} {fv(dr["dYcAr"]):>8} {fv(dr["dYv"]):>8} {fv(dr["dSh"])}')
