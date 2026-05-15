import openpyxl
import csv
from collections import defaultdict

EUR_TO_USD = 1.085

# ========== 1. Believe 数据 ==========
wb = openpyxl.load_workbook('/Users/olivia/Desktop/2026Q1 Believe.xlsx', data_only=True)
ws = wb.active
headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
platform_idx = headers.index('Platform')
gross_idx = headers.index('Gross Revenue')

believe_rev = defaultdict(float)
for row in ws.iter_rows(min_row=2, values_only=True):
    p = row[platform_idx]
    g = row[gross_idx]
    if p and g is not None:
        try:
            believe_rev[p] += float(g) * EUR_TO_USD
        except:
            pass

# ========== 2. 东西数据 ==========
dongxi_rev = defaultdict(float)
for f in ['/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202601.csv',
          '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202602.csv',
          '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202603.csv']:
    with open(f, encoding='utf-8-sig') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            s = row.get('Store', '')
            try:
                r = float(row.get('AmountPaidByStore', 0))
            except:
                r = 0
            dongxi_rev[s] += r

# ========== 3. 以报表实际名称为准，不合并 ==========
# Believe Platform 名称 → 东西 Store 名称（不合并 UGC/OC）
comparisons = [
    ('Spotify',               'Spotify',              'Spotify'),
    ('Apple Music',           'Apple Music',          'Apple Music'),
    ('YouTube Official Content', 'YouTube Official Content', 'YouTube Art Tracks'),
    ('YouTube UGC',            'YouTube UGC',           'YouTube Audio Content ID'),
    ('YouTube Audio Tier',    'YouTube Audio Tier',    'YouTube Audio Tier'),
    ('YouTube Music Video',   'YouTube Music Video',   'YouTube Music Video'),
    ('YouTube Shorts',       'YouTube Shorts',       'YouTubeShorts'),
    ('Facebook / Instagram', 'Facebook / Instagram',  'Facebook'),
    ('TikTok',               'TikTok',               'TikTok'),
]

total_all = sum(believe_rev.values()) + sum(dongxi_rev.values())

print(f'Believe 总收入: {sum(believe_rev.values()):,.2f} USD')
print(f'东西总收入:   {sum(dongxi_rev.values()):,.2f} USD')
print(f'合计:         {total_all:,.2f} USD')
print()
print(f'{"对比板块":42s} {"Believe(USD)":>16s} {"东西(USD)":>16s} {"合计":>16s} {"占总收入%":>10s} {"东西%":>8s} {"Believe%":>10s}')
print('-' * 130)

results = {}
for name, b_plat, d_store in comparisons:
    b = believe_rev.get(b_plat, 0.0)
    d = dongxi_rev.get(d_store, 0.0)
    combined = b + d
    pct_total = combined / total_all * 100 if total_all else 0
    pct_d = d / combined * 100 if combined else 0
    pct_b = b / combined * 100 if combined else 0
    print(f'{name:42s} {b:>16,.2f} {d:>16,.2f} {combined:>16,.2f} {pct_total:>9.1f}% {pct_d:>7.1f}% {pct_b:>9.1f}%')
    results[name] = {
        'b_plat': b_plat,
        'd_store': d_store,
        'b': b,
        'd': d,
        'combined': combined,
        'pct_total': pct_total,
        'pct_d': pct_d,
        'pct_b': pct_b,
    }

# ========== 4. 更新 HTML ==========
with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 平台标题映射：HTML 中的 emoji 标题 → results key
# 需要先清理所有现有的百分比后缀，再写入新的
import re

# 清理所有平台标题里的旧百分比
# 匹配模式：emoji + "— 每1,000 xxx" + 可能出现的旧百分比
# 然后替换为：emoji + "— 每1,000 xxx" + 新百分比

platform_configs = [
    ('🟢 Spotify',                        'Spotify',               '🟢 Spotify — 每1,000 streams'),
    ('🍎 Apple Music',                    'Apple Music',           '🍎 Apple Music — 每1,000 streams'),
    ('▶️ YouTube Audio Tier',             'YouTube Audio Tier',    '▶️ YouTube Audio Tier — 每1,000 streams'),
    ('🎬 YouTube Content ID',            'YouTube UGC',           '🎬 YouTube Content ID — 每1,000 streams'),
    ('🎬 YouTube Official Content vs Art Tracks', 'YouTube Official Content', '🎬 YouTube Official Content vs Art Tracks — 每1,000 streams'),
    ('🎵 YouTube Music Video',           'YouTube Music Video',   '🎵 YouTube Music Video — 每1,000 streams'),
    ('🩳 YouTube Shorts',               'YouTube Shorts',       '🩳 YouTube Shorts — 每1,000 shorts'),
]

# 先清理所有旧百分比
for emoji_name, _, _ in platform_configs:
    # 去掉已有的百分比后缀（可能有多个叠加）
    pattern = re.escape(emoji_name) + r' — 每1,000 (?:streams|shorts)(?:（占总收入 [\d.]+%，其中东西占[\d.]+%，Believe占[\d.]+%）)*'
    # 先找到完整的 h3 内容
    pass

# 更简单的方法：直接替换整个 h3 行
# 读取所有行，找到包含 emoji 的行，替换整行
lines = html.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    matched = False
    for emoji_name, res_key, base_text in platform_configs:
        if emoji_name in line and '每1,000' in line:
            r = results[res_key]
            new_h3 = f'  <h3 style="font-size:14px;color:var(--muted);margin-bottom:8px;margin-top:20px;">{emoji_name} — 每1,000{" shorts" if "Shorts" in emoji_name else " streams"}（占总收入 {r["pct_total"]:.1f}%，其中东西占{r["pct_d"]:.1f}%，Believe占{r["pct_b"]:.1f}%）</h3>'
            new_lines.append(new_h3)
            matched = True
            break
    if not matched:
        new_lines.append(line)
    i += 1

html = '\n'.join(new_lines)

with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print()
print('HTML 已更新！')
print()
print('注意：')
print('- YouTube Official Content vs Art Tracks：Believe 只用 Official Content（不再合并 UGC）')
print('- YouTube Content ID 板块：实际上对应 Believe YouTube UGC vs 东西 YouTube Audio Content ID')
print('- 如果你希望调整板块名称或拆分方式，告诉我。')
