import pandas as pd
import json

regions = ['US', 'TW', 'SG', 'HK', 'MY', 'GB', 'TH', 'VN', 'JP', 'ID', 'KR']
region_names = {
    'US':'United States','TW':'Taiwan','SG':'Singapore','HK':'Hong Kong',
    'MY':'Malaysia','GB':'United Kingdom','TH':'Thailand','VN':'Vietnam',
    'JP':'Japan','ID':'Indonesia','KR':'South Korea'
}
EUR_USD = 1.085

cmap = {'united states':'US','united kingdom':'GB','japan':'JP','korea, republic of':'KR','korea':'KR',
        'taiwan, province of china':'TW','taiwan':'TW','thailand':'TH','indonesia':'ID','viet nam':'VN',
        'hong kong':'HK','singapore':'SG','malaysia':'MY'}

bdfs = []
for f in ['/Users/olivia/Downloads/202601 Believe.csv',
          '/Users/olivia/Downloads/202602 Believe.csv',
          '/Users/olivia/Downloads/202603 Believe.csv']:
    df = pd.read_csv(f, sep=';', low_memory=False)
    bdfs.append(df)
bl = pd.concat(bdfs, ignore_index=True)
bl_sp = bl[bl['Platform'].str.contains('Spotify', case=False, na=False)].copy()
bl_sp['region'] = bl_sp['Country / Region'].str.lower().str.strip().map(cmap)

# Sony = 第二大 label（1588行）
# Premium = 会员，Freemium / Ad Supported = 免费
labels = bl_sp['Label Name'].value_counts()
sony_label = labels.index[1]  # 第二大的 label

print(f"Sony label: {repr(sony_label)}")
sony_sp = bl_sp[bl_sp['Label Name'] == sony_label]
print(f"Sony Spotify rows: {len(sony_sp)}")

# 会员 = Premium
sony_paid = sony_sp[sony_sp['Streaming Subscription Type'] == 'Premium']
# 免费 = Freemium / Ad Supported
sony_free = sony_sp[sony_sp['Streaming Subscription Type'] == 'Freemium / Ad Supported']

results = []
for r in regions:
    rn = region_names[r]

    # Sony 会员
    pr = sony_paid[sony_paid['region'] == r]
    s_p = pr['Gross Revenue'].sum() * EUR_USD / pr['Quantity'].sum() * 1000 if len(pr) > 0 and pr['Quantity'].sum() > 0 else None

    # Sony 免费
    fr = sony_free[sony_free['region'] == r]
    s_f = fr['Gross Revenue'].sum() * EUR_USD / fr['Quantity'].sum() * 1000 if len(fr) > 0 and fr['Quantity'].sum() > 0 else None

    results.append({
        'region': r, 'name': rn,
        'sony_paid': round(s_p, 4) if s_p else None,
        'sony_free': round(s_f, 4) if s_f else None
    })

# 打印结果
print("\n| Region | Name       | Sony Paid | Sony Free |")
print("|--------|------------|-----------|-----------|")
for r in results:
    sp = f"${r['sony_paid']:.4f}" if r['sony_paid'] else "N/A"
    sf = f"${r['sony_free']:.4f}" if r['sony_free'] else "N/A"
    print(f"| {r['region']} | {r['name']:10s} | {sp:9s} | {sf:9s} |")

# 保存 JSON
with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/sony_spotify_result.json', 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\nSaved to sony_spotify_result.json")
