import csv, json

files = [
    '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202601.csv',
    '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202602.csv',
    '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202603.csv',
]

art_tracks_rev = 0.0
audio_tier_rev = 0.0
yt_cid_rev     = 0.0
yt_mv_rev      = 0.0
yt_shorts_rev  = 0.0

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            store = row.get('Store', '')
            try:
                amt = float(row.get('AmountPaidByStore', 0))
            except:
                continue
            if store == 'YouTube Art Tracks':
                art_tracks_rev += amt
            elif store == 'YouTube Audio Tier':
                audio_tier_rev += amt
            elif store == 'YouTube Audio Content ID':
                yt_cid_rev += amt
            elif store == 'YouTube Music Video':
                yt_mv_rev += amt
            elif store == 'YouTubeShorts':
                yt_shorts_rev += amt

print(f"东西 Art Tracks 收入:    ${art_tracks_rev:,.2f}")
print(f"东西 Audio Tier 收入:    ${audio_tier_rev:,.2f}")
print(f"东西 Audio Content ID 收入: ${yt_cid_rev:,.2f}")
print(f"东西 Music Video 收入:   ${yt_mv_rev:,.2f}")
print(f"东西 YouTube Shorts 收入: ${yt_shorts_rev:,.2f}")
print()

with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/believe_revenue_calc.json', 'r') as f:
    believe_data = json.load(f)
b_yc = believe_data['platform_totals_usd'].get('Yc', 0)
print(f"Believe YT Official Content 收入: ${b_yc:,.2f}")
print()

grand_total = believe_data['believe_total_usd'] + 244941.50
combined = b_yc + art_tracks_rev
pct = combined / grand_total * 100
print(f"合计 (B YT OC + D Art Tracks): ${combined:,.2f}")
print(f"两家总收入: ${grand_total:,.2f}")
print(f"占总收入: {pct:.1f}%")
print()
print(f"标题应为：🎬 YouTube Official Content vs Art Tracks — 每1,000 streams（占总收入 {pct:.1f}%）")
