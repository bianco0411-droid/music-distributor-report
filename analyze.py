"""
完整的Believe vs 东西发行商对比分析脚本
"""
import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. 读取并整合数据
# ============================================================

# --- Believe CSV (分号分隔) ---
print("Loading Believe data...")
believe_files = [
    "/Users/olivia/Downloads/202601 Believe.csv",
    "/Users/olivia/Downloads/202602 Believe.csv",
    "/Users/olivia/Downloads/202603 Believe.csv",
]
bel_dfs = []
for f in believe_files:
    df = pd.read_csv(f, sep=';', low_memory=False)
    bel_dfs.append(df)
bel = pd.concat(bel_dfs, ignore_index=True)
print(f"  Believe rows: {len(bel):,}")
print(f"  Columns: {bel.columns.tolist()}")

# --- 东西 CSV (逗号分隔) ---
print("\nLoading 东西 data...")
dz_files = [
    "/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202601.csv",
    "/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202602.csv",
    "/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202603.csv",
]
dz_dfs = []
for f in dz_files:
    df = pd.read_csv(f, low_memory=False)
    dz_dfs.append(df)
dz = pd.concat(dz_dfs, ignore_index=True)
print(f"  东西 rows: {len(dz):,}")
print(f"  Columns: {dz.columns.tolist()}")

# ============================================================
# 2. Believe: EUR->USD (用固定汇率 1 EUR = 1.085 USD, 2026Q1 avg)
EUR_USD = 1.085

# 统一字段名
bel['platform'] = bel['Platform']
bel['country'] = bel['Country / Region'].str.strip().str.lower()
bel['quantity'] = pd.to_numeric(bel['Quantity'], errors='coerce').fillna(0)
bel['unit_price_eur'] = pd.to_numeric(bel['Unit Price'], errors='coerce').fillna(0)
bel['gross_rev_eur'] = pd.to_numeric(bel['Gross Revenue'], errors='coerce').fillna(0)
bel['net_rev_eur'] = pd.to_numeric(bel['Net Revenue'], errors='coerce').fillna(0)
bel['unit_price_usd'] = bel['unit_price_eur'] * EUR_USD
bel['gross_rev_usd'] = bel['gross_rev_eur'] * EUR_USD
bel['net_rev_usd'] = bel['net_rev_eur'] * EUR_USD
bel['sales_type'] = bel['Sales Type'].str.strip()
bel['streaming_type'] = bel['Streaming Subscription Type'].fillna('').str.strip()

# ============================================================
# 3. 东西: USD已经是USD (验证Currency列)
print("\n东西 Currency unique:", dz['Currency'].unique())
dz['platform'] = dz['Store']
dz['country_code'] = dz['Territories'].fillna('').str.strip().str.upper()
dz['quantity'] = pd.to_numeric(dz['Quantity'], errors='coerce').fillna(0)
dz['unit_price_usd'] = pd.to_numeric(dz['AmountPaidByStore'], errors='coerce').fillna(0) / dz['quantity'].replace(0, np.nan)
dz['gross_rev_usd'] = pd.to_numeric(dz['AmountPaidByStore'], errors='coerce').fillna(0)
dz['customer_amt_usd'] = pd.to_numeric(dz['CustomerAmount'], errors='coerce').fillna(0)

# ============================================================
# 4. Believe: 平台名称标准化
bel_platform_map = {}
for p in bel['platform'].unique():
    pl = str(p).lower()
    if 'youtube music' in pl:
        bel_platform_map[p] = 'YouTube Music'
    elif 'youtube shorts' in pl:
        bel_platform_map[p] = 'YouTube Shorts'
    elif 'youtube ugc' in pl or 'youtube audio' in pl.replace(' ',''):
        bel_platform_map[p] = 'YouTube Content ID'
    elif 'youtube official' in pl:
        bel_platform_map[p] = 'YouTube Official Content'
    elif 'youtube' in pl:
        bel_platform_map[p] = 'YouTube Other'
    elif 'spotify' in pl:
        bel_platform_map[p] = 'Spotify'
    elif 'apple music' in pl or 'apple' in pl:
        bel_platform_map[p] = 'Apple Music'
    elif 'tiktok' in pl:
        bel_platform_map[p] = 'TikTok'
    elif 'facebook' in pl or 'instagram' in pl:
        bel_platform_map[p] = 'Facebook/Instagram'
    elif 'amazon' in pl:
        bel_platform_map[p] = 'Amazon'
    elif 'boomplay' in pl:
        bel_platform_map[p] = 'Boomplay'
    elif 'yandex' in pl:
        bel_platform_map[p] = 'Yandex'
    elif 'nct' in pl or 'netease' in pl:
        bel_platform_map[p] = 'NetEase'
    elif 'deezer' in pl:
        bel_platform_map[p] = 'Deezer'
    else:
        bel_platform_map[p] = 'Other'

bel['platform_std'] = bel['platform'].map(bel_platform_map)
print("\nBelieve platform mapping:")
print(bel['platform_std'].value_counts().head(20))

# 东西平台标准化
dz_platform_map = {}
for p in dz['platform'].unique():
    pl = str(p).lower()
    if 'youtube art tracks' in pl or 'youtube music' in pl:
        dz_platform_map[p] = 'YouTube Music'
    elif 'youtube shorts' in pl:
        dz_platform_map[p] = 'YouTube Shorts'
    elif 'youtube audio content id' in pl or 'youtube content id' in pl or 'youtube ugc' in pl:
        dz_platform_map[p] = 'YouTube Content ID'
    elif 'youtube official' in pl:
        dz_platform_map[p] = 'YouTube Official Content'
    elif 'youtube' in pl:
        dz_platform_map[p] = 'YouTube Other'
    elif 'spotify' in pl:
        dz_platform_map[p] = 'Spotify'
    elif 'apple music' in pl or 'itunes' in pl:
        dz_platform_map[p] = 'Apple Music'
    elif 'tiktok' in pl:
        dz_platform_map[p] = 'TikTok'
    elif 'amazon' in pl:
        dz_platform_map[p] = 'Amazon'
    elif 'facebook' in pl or 'instagram' in pl:
        dz_platform_map[p] = 'Facebook/Instagram'
    elif 'deezer' in pl:
        dz_platform_map[p] = 'Deezer'
    elif 'kkbox' in pl:
        dz_platform_map[p] = 'KKBOX'
    elif 'netease' in pl or 'nct' in pl:
        dz_platform_map[p] = 'NetEase'
    else:
        dz_platform_map[p] = 'Other'

dz['platform_std'] = dz['platform'].map(dz_platform_map)
print("\n东西 platform mapping:")
print(dz['platform_std'].value_counts().head(20))

# ============================================================
# 5. 地区映射 (Believe用国家名称, 东西用ISO2代码)
country_name_to_code = {
    'united states': 'US',
    'united kingdom': 'GB',
    'japan': 'JP',
    'korea': 'KR',
    'korea, republic of': 'KR',
    'south korea': 'KR',
    'republic of korea': 'KR',
    'taiwan': 'TW',
    'taiwan province of china': 'TW',
    'thailand': 'TH',
    'indonesia': 'ID',
    'viet nam': 'VN',
    'vietnam': 'VN',
    'india': 'IN',
    'hong kong': 'HK',
    'singapore': 'SG',
    'malaysia': 'MY',
    'china mainland': 'CN',
    'germany': 'DE',
    'france': 'FR',
    'canada': 'CA',
    'australia': 'AU',
    'brazil': 'BR',
    'mexico': 'MX',
    'philippines': 'PH',
    'cambodia': 'KH',
    'myanmar': 'MM',
}
bel['country_code'] = bel['country'].map(country_name_to_code)

TARGET_REGIONS = ['US','GB','JP','KR','TW','TH','ID','VN','IN','HK','SG','MY']

# ============================================================
# 6. 核心计算函数
def calc_per_1000_streams(df_sub, platform_col='platform_std', rev_col='gross_rev_usd', qty_col='quantity'):
    """计算每1000次播放的收益"""
    df = df_sub[df_sub['quantity'] > 0].copy()
    total_qty = df[qty_col].sum()
    total_rev = df[rev_col].sum()
    if total_qty > 0:
        return (total_rev / total_qty) * 1000
    return np.nan

# ============================================================
# 7. 核心数据对比：按地区按平台计算单价
print("\n" + "="*60)
print("CORE ANALYSIS: Per-platform per-region unit price")
print("="*60)

results = {}

for region in TARGET_REGIONS:
    results[region] = {}
    
    # Believe
    bel_region = bel[bel['country_code'] == region]
    
    for plat in ['YouTube Music', 'YouTube Shorts', 'YouTube Content ID', 'YouTube Official Content', 'Spotify', 'Apple Music']:
        bel_plat = bel_region[bel_region['platform_std'] == plat]
        if len(bel_plat) > 0:
            val = calc_per_1000_streams(bel_plat)
            results[region][f'bel_{plat}'] = val
        else:
            results[region][f'bel_{plat}'] = np.nan
    
    # 东西
    dz_region = dz[dz['country_code'] == region]
    
    for plat in ['YouTube Music', 'YouTube Shorts', 'YouTube Content ID', 'YouTube Official Content', 'Spotify', 'Apple Music']:
        dz_plat = dz_region[dz_region['platform_std'] == plat]
        if len(dz_plat) > 0:
            val = calc_per_1000_streams(dz_plat, rev_col='gross_rev_usd')
            results[region][f'dz_{plat}'] = val
        else:
            results[region][f'dz_{plat}'] = np.nan

# 打印结果摘要
for region in TARGET_REGIONS:
    print(f"\n--- {region} ---")
    for plat in ['Spotify', 'Apple Music', 'YouTube Music', 'YouTube Shorts', 'YouTube Content ID']:
        bv = results[region].get(f'bel_{plat}', np.nan)
        dv = results[region].get(f'dz_{plat}', np.nan)
        bv_str = f"${bv:.4f}" if not np.isnan(bv) else "N/A"
        dv_str = f"${dv:.4f}" if not np.isnan(dv) else "N/A"
        print(f"  {plat:30s} Believe={bv_str:12s} 东西={dv_str}")

# ============================================================
# 8. 收入结构分析
print("\n" + "="*60)
print("REVENUE STRUCTURE ANALYSIS")
print("="*60)

bel_total = bel['gross_rev_usd'].sum()
dz_total = dz['gross_rev_usd'].sum()

print(f"\nBelieve Total Gross Revenue (USD): ${bel_total:,.2f}")
print(f"东西 Total Gross Revenue (USD): ${dz_total:,.2f}")

bel_by_platform = bel.groupby('platform_std')['gross_rev_usd'].sum().sort_values(ascending=False)
dz_by_platform = dz.groupby('platform_std')['gross_rev_usd'].sum().sort_values(ascending=False)

print("\n--- Believe Revenue by Platform ---")
for p, v in bel_by_platform.items():
    pct = v/bel_total*100
    print(f"  {p:35s}: ${v:>10,.2f}  ({pct:.1f}%)")

print("\n--- 东西 Revenue by Platform ---")
for p, v in dz_by_platform.items():
    pct = v/dz_total*100
    print(f"  {p:35s}: ${v:>10,.2f}  ({pct:.1f}%)")

# ============================================================
# 9. 保存结果到JSON供后续HTML渲染使用
output = {
    'eur_usd': EUR_USD,
    'believe_total_usd': bel_total,
    'dz_total_usd': dz_total,
    'region_unit_price': {},
    'believe_revenue_struct': {},
    'dz_revenue_struct': {},
    'believe_by_platform_detail': {},
    'dz_by_platform_detail': {},
}

for region in TARGET_REGIONS:
    output['region_unit_price'][region] = {}
    for plat in ['Spotify', 'Apple Music', 'YouTube Music', 'YouTube Shorts', 'YouTube Content ID', 'YouTube Official Content']:
        bv = results[region].get(f'bel_{plat}', np.nan)
        dv = results[region].get(f'dz_{plat}', np.nan)
        output['region_unit_price'][region][f'believe_{plat}'] = None if np.isnan(bv) else round(bv, 6)
        output['region_unit_price'][region][f'dz_{plat}'] = None if np.isnan(dv) else round(dv, 6)

for p, v in bel_by_platform.items():
    output['believe_revenue_struct'][p] = round(v, 4)
for p, v in dz_by_platform.items():
    output['dz_revenue_struct'][p] = round(v, 4)

# 额外: 量统计
bel_qty_by_plat = bel.groupby('platform_std')['quantity'].sum()
dz_qty_by_plat = dz.groupby('platform_std')['quantity'].sum()
for p, v in bel_qty_by_plat.items():
    output['believe_by_platform_detail'][p] = {'qty': int(v), 'rev': round(float(bel_by_platform.get(p, 0)), 4)}
for p, v in dz_qty_by_plat.items():
    output['dz_by_platform_detail'][p] = {'qty': int(v), 'rev': round(float(dz_by_platform.get(p, 0)), 4)}

# YouTube CID占比
bel_yt_cid = bel_by_platform.get('YouTube Content ID', 0) + bel_by_platform.get('YouTube Official Content', 0)
dz_yt_cid = dz_by_platform.get('YouTube Content ID', 0) + dz_by_platform.get('YouTube Official Content', 0)
output['believe_yt_cid_pct'] = round(bel_yt_cid / bel_total * 100, 2)
output['dz_yt_cid_pct'] = round(dz_yt_cid / dz_total * 100, 2)
print(f"\nBelieve YouTube CID占总收入比例: {output['believe_yt_cid_pct']:.2f}%")
print(f"东西 YouTube CID占总收入比例: {output['dz_yt_cid_pct']:.2f}%")

# ============================================================
# 10. 按地区看总收入分布
print("\n--- Believe Revenue by Region (Top 15) ---")
bel_by_region = bel.groupby('country_code')['gross_rev_usd'].sum().sort_values(ascending=False).head(15)
print(bel_by_region.to_string())

print("\n--- 东西 Revenue by Region (Top 15) ---")
dz_by_region = dz.groupby('country_code')['gross_rev_usd'].sum().sort_values(ascending=False).head(15)
print(dz_by_region.to_string())

output['believe_by_region'] = {k: round(float(v),4) for k,v in bel_by_region.items()}
output['dz_by_region'] = {k: round(float(v),4) for k,v in dz_by_region.items()}

# ============================================================
# 11. 全局平均单价（across all regions）
print("\n--- Global Average Unit Price per 1000 streams ---")
for plat in ['Spotify', 'Apple Music', 'YouTube Music', 'YouTube Shorts', 'YouTube Content ID', 'YouTube Official Content']:
    bel_plat = bel[bel['platform_std'] == plat]
    dz_plat = dz[dz['platform_std'] == plat]
    bv = calc_per_1000_streams(bel_plat)
    dv = calc_per_1000_streams(dz_plat)
    bv_str = f"${bv:.4f}" if not np.isnan(bv) else "N/A"
    dv_str = f"${dv:.4f}" if not np.isnan(dv) else "N/A"
    output[f'global_believe_{plat}'] = None if np.isnan(bv) else round(bv, 6)
    output[f'global_dz_{plat}'] = None if np.isnan(dv) else round(dv, 6)
    print(f"  {plat:35s} Believe={bv_str:14s} 东西={dv_str}")

# ============================================================
# 12. TikTok analysis
print("\n--- TikTok Detail ---")
bel_tiktok = bel[bel['platform_std'] == 'TikTok']
dz_tiktok = dz[dz['platform_std'] == 'TikTok']
print(f"Believe TikTok rows: {len(bel_tiktok)}, revenue: ${bel_tiktok['gross_rev_usd'].sum():.4f}")
print(f"东西 TikTok rows: {len(dz_tiktok)}, revenue: ${dz_tiktok['gross_rev_usd'].sum():.4f}")
if len(bel_tiktok) > 0:
    print(f"  Believe TikTok Sales Types: {bel_tiktok['sales_type'].value_counts().to_dict()}")
    bel_tik_per1000 = calc_per_1000_streams(bel_tiktok)
    output['global_believe_TikTok_per1000'] = None if np.isnan(bel_tik_per1000) else round(bel_tik_per1000, 6)

if len(dz_tiktok) > 0:
    dz_tik_per1000 = calc_per_1000_streams(dz_tiktok)
    output['global_dz_TikTok_per1000'] = None if np.isnan(dz_tik_per1000) else round(dz_tik_per1000, 6)

# ============================================================
# Save JSON
import json
with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/analysis_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("\nSaved analysis_data.json")
