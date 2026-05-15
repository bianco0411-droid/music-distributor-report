import csv, json, glob

# 1. 重新计算 Believe 各平台收入 (USD)
files = glob.glob('/Users/olivia/Downloads/*Believe*.csv')
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

# 换算USD
platform_rev_usd = {k: v/1.085 for k,v in platform_rev_eur.items()}
believe_total = sum(platform_rev_usd.values())

# 映射到DATA键
b_map = {}
mapping = {
    'Spotify': 'Sp',
    'Apple Music': 'Ap',
    'YouTube Official Content': 'Yc',
    'YouTube UGC': 'Yc',
    'YouTube Audio Tier': 'Ym',
    'YouTube Music Video': 'Yv',
    'YouTube Shorts': 'Sh',
    'Facebook / Instagram': 'Fb',
    'TikTok': 'Tk',
}
for plat, key in mapping.items():
    rev = sum(v for k,v in platform_rev_usd.items() if plat in k)
    b_map[key] = b_map.get(key, 0.0) + rev

print('=== Believe 各平台收入 (USD) ===')
for k,v in b_map.items():
    print(f"  {k}: ${v:,.2f}")
print(f"Believe 总收入: ${believe_total:,.2f}")

# 2. 东西各平台收入
with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_new_analysis.json', 'r') as f:
    dongxi_data = json.load(f)
dongxi_total = dongxi_data['grand_total_revenue']
d_platform = {item['platform']: item for item in dongxi_data.get('platform_summary', [])}

print(f"\n=== 东西 各平台收入 (USD) ===")
d_map = {}
for item in dongxi_data.get('platform_summary', []):
    d_map[item['platform']] = item.get('revenue', 0)
for k,v in d_map.items():
    print(f"  {k}: ${v:,.2f}")
print(f"东西 总收入: ${dongxi_total:,.2f}")

# 3. 计算各平台标题占比
grand_total = believe_total + dongxi_total
print(f"\n两家总收入: ${grand_total:,.2f}")
print(f"\n=== 各平台标题占比 ===")

platforms = [
    ('Spotify',           'Sp', 'Spotify'),
    ('Apple Music',       'Ap', 'Apple Music'),
    ('YouTube Content ID','Yc', 'YouTube Content ID'),
    ('YouTube Audio Tier','Ym', 'YouTube Music'),
    ('YouTube Music Video','Yv', 'YouTube Music Video'),
    ('YouTube Shorts',    'Sh', 'YouTube Shorts'),
    ('Facebook/Instagram','Fb', 'Facebook'),
    ('TikTok',           'Tk', 'TikTok'),
]

for label, b_key, d_key in platforms:
    b_rev = b_map.get(b_key, 0)
    d_item = d_platform.get(d_key, {})
    d_rev = d_item.get('revenue', 0) if isinstance(d_item, dict) else 0
    
    combined = b_rev + d_rev
    total_pct = combined / grand_total * 100 if grand_total else 0
    
    b_pct = b_rev / combined * 100 if combined else 0
    d_pct = d_rev / combined * 100 if combined else 0
    
    print(f"{label}: 占总收入{total_pct:.1f}%, 东西{d_pct:.1f}%, Believe{b_pct:.1f}%")

# 4. YouTube Official Content vs Art Tracks
b_yc = b_map.get('Yc', 0)
# 东西 Art Tracks - 从CSV重算
art_tracks_rev = 0.0
dx_files = [
    '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202601.csv',
    '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202602.csv',
    '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202603.csv',
]
for f in dx_files:
    with open(f, 'r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row.get('Store', '') == 'YouTube Art Tracks':
                try:
                    art_tracks_rev += float(row.get('AmountPaidByStore', 0))
                except: pass

combined_oc_at = b_yc + art_tracks_rev
pct_oc_at = combined_oc_at / grand_total * 100 if grand_total else 0
b_pct2 = b_yc / combined_oc_at * 100 if combined_oc_at else 0
d_pct2 = art_tracks_rev / combined_oc_at * 100 if combined_oc_at else 0

print(f"\nYouTube Official Content vs Art Tracks:")
print(f"  Believe YC: ${b_yc:,.2f}, 东西ArtTracks: ${art_tracks_rev:,.2f}")
print(f"  占总收入{pct_oc_at:.1f}%, 东西{d_pct2:.1f}%, Believe{b_pct2:.1f}%")
