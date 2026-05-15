import pandas as pd

regions = ['US', 'TW', 'SG', 'HK', 'MY', 'GB', 'TH', 'VN', 'JP', 'ID', 'KR']
region_names = {
    'US':'United States','TW':'Taiwan','SG':'Singapore','HK':'Hong Kong',
    'MY':'Malaysia','GB':'United Kingdom','TH':'Thailand','VN':'Vietnam',
    'JP':'Japan','ID':'Indonesia','KR':'South Korea'
}
EUR_USD = 1.085

# ========== 东西 Spotify ==========
dfs = []
for f in ['/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202601.csv',
          '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202602.csv',
          '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202603.csv']:
    df = pd.read_csv(f, low_memory=False)
    dfs.append(df)
dx = pd.concat(dfs, ignore_index=True)
dx_sp = dx[dx['Store'].str.contains('Spotify', na=False)]
dx_sub = dx_sp[dx_sp['Service'].isin(['P', 'FAM6', 'DUO'])]
dx_free = dx_sp[dx_sp['Service'] == 'A']

# ========== Believe Spotify ==========
bdfs = []
for f in ['/Users/olivia/Downloads/202601 Believe.csv',
          '/Users/olivia/Downloads/202602 Believe.csv',
          '/Users/olivia/Downloads/202603 Believe.csv']:
    df = pd.read_csv(f, sep=';', low_memory=False)
    bdfs.append(df)
bl = pd.concat(bdfs, ignore_index=True)
bl_sp = bl[bl['Platform'].str.contains('Spotify', case=False, na=False)].copy()
cmap = {'united states':'US','united kingdom':'GB','japan':'JP','korea, republic of':'KR','korea':'KR',
        'taiwan, province of china':'TW','taiwan':'TW','thailand':'TH','indonesia':'ID','viet nam':'VN',
        'hong kong':'HK','singapore':'SG','malaysia':'MY'}
bl_sp['region'] = bl_sp['Country / Region'].str.lower().str.strip().map(cmap)
bl_free = bl_sp[bl_sp['Streaming Subscription Type'] == 'Freemium / Ad Supported']
bl_prem = bl_sp[bl_sp['Streaming Subscription Type'] == 'Premium']

results = []
for r in regions:
    rn = region_names[r]

    # 东西 会员
    sub = dx_sub[dx_sub['Territories'] == r]
    dx_p = sub['AmountPaidByStore'].sum() / sub['Quantity'].sum() * 1000 if len(sub) > 0 and sub['Quantity'].sum() > 0 else None

    # 东西 免费
    fr = dx_free[dx_free['Territories'] == r]
    dx_f = fr['AmountPaidByStore'].sum() / fr['Quantity'].sum() * 1000 if len(fr) > 0 and fr['Quantity'].sum() > 0 else None

    # Believe 免费
    bfr = bl_free[bl_free['region'] == r]
    bl_f = bfr['Gross Revenue'].sum() * EUR_USD / bfr['Quantity'].sum() * 1000 if len(bfr) > 0 and bfr['Quantity'].sum() > 0 else None

    # Believe 会员
    bpr = bl_prem[bl_prem['region'] == r]
    bl_p = bpr['Gross Revenue'].sum() * EUR_USD / bpr['Quantity'].sum() * 1000 if len(bpr) > 0 and bpr['Quantity'].sum() > 0 else None

    results.append({'Region': r, 'Name': rn,
                     'DX_Sub': dx_p, 'DX_Free': dx_f,
                     'BL_Free': bl_f, 'BL_Sub': bl_p})

df = pd.DataFrame(results)
print(df.to_string(index=False))
print()

# Markdown table
print("| 地区 | 名称 | 东西会员 | 东西免费 | Believe免费 | Believe会员 |")
print("|------|------|---------|---------|------------|------------|")
for _, row in df.iterrows():
    dx_s = f"${row['DX_Sub']:.4f}" if row['DX_Sub'] else "N/A"
    dx_fr = f"${row['DX_Free']:.4f}" if row['DX_Free'] else "N/A"
    bl_fr = f"${row['BL_Free']:.4f}" if row['BL_Free'] else "N/A"
    bl_s = f"${row['BL_Sub']:.4f}" if row['BL_Sub'] else "N/A"
    print(f"| {row['Region']} | {row['Name']} | {dx_s} | {dx_fr} | {bl_fr} | {bl_s} |")
