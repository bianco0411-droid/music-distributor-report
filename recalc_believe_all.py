import csv, json, glob

files = glob.glob('/Users/olivia/Downloads/*Believe*.csv')
print('找到文件:', files)

# Believe CSV是分号分隔，EUR计价
platform_rev_eur = {}

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh, delimiter=';')
        for row in reader:
            platform = row.get('Platform', '').strip()
            try:
                amt = float(row.get('Gross Revenue', 0))
            except:
                continue
            platform_rev_eur[platform] = platform_rev_eur.get(platform, 0.0) + amt

print('\nBelieve 各平台收入 (EUR):')
for k,v in sorted(platform_rev_eur.items(), key=lambda x: -x[1]):
    print(f"  {k}: €{v:,.2f}")

# 换算USD (÷1.085)
print('\nBelieve 各平台收入 (USD, ÷1.085):')
platform_rev_usd = {}
for k,v in platform_rev_eur.items():
    usd = v / 1.085
    platform_rev_usd[k] = usd
    print(f"  {k}: ${usd:,.2f}")

total_usd = sum(platform_rev_usd.values())
print(f"\nBelieve 总收入(USD): ${total_usd:,.2f}")

# 输出映射：用于更新believe_revenue_calc.json
mapping = {
    'Spotify': 'Sp',
    'Apple Music': 'Ap',
    'YouTube Official Content': 'Yc',
    'YouTube UGC': 'Yc',   # UGC也属于Yc
    'YouTube Audio Tier': 'Ym',
    'YouTube Music Video': 'Yv',
    'YouTube Shorts': 'Sh',
    'Facebook/Instagram': 'Fb',
    'TikTok': 'Tk',
}
print('\n映射到DATA键:')
mapped = {}
for plat, key in mapping.items():
    rev = sum(v for k,v in platform_rev_usd.items() if plat in k)
    mapped[key] = mapped.get(key, 0) + rev
for k,v in mapped.items():
    print(f"  {k}: ${v:,.2f}")
