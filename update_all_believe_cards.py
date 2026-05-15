#!/usr/bin/env python3
"""
解析 Believe 1-3月 CSV 文件，重新计算各平台总收入，更新 index.html 中的所有卡片
"""
import csv
import json
import re
from collections import defaultdict

# Believe CSV 文件路径
CSV_FILES = [
    '/Users/olivia/Downloads/202601 Believe.csv',
    '/Users/olivia/Downloads/202602 Believe.csv',
    '/Users/olivia/Downloads/202603 Believe.csv',
]

# 地区映射
COUNTRY_MAP = {
    'united states': 'US', 'usa': 'US', 'us': 'US',
    'united kingdom': 'GB', 'uk': 'GB', 'great britain': 'GB',
    'japan': 'JP',
    'korea': 'KR', 'korea, republic of': 'KR', 'korea republic of': 'KR',
    'republic of korea': 'KR', 'south korea': 'KR',
    'taiwan': 'TW', 'taiwan, province of china': 'TW',
    'thailand': 'TH',
    'indonesia': 'ID',
    'viet nam': 'VN', 'vietnam': 'VN',
    'hong kong': 'HK', 'hong kong sar': 'HK',
    'singapore': 'SG',
    'malaysia': 'MY',
    'china': 'CN', 'china mainland': 'CN', 'mainland china': 'CN',
}

# Platform 映射（分别统计 Official Content 和 UGC）
PLATFORM_MAP = {
    'Spotify': 'Sp',
    'Apple Music': 'Ap',
    'Apple iTunes': 'Ap',
    'YouTube Official Content': 'Yc_official',  # Official Content 单独统计
    'YouTube UGC': 'Yc_ugc',                  # UGC 单独统计
    'YouTube Audio Tier': 'Ym',
    'YouTube Music Video': 'Yv',
    'YouTube Shorts': 'Sh',
    'TikTok': 'Tk',
    'Facebook / Instagram': 'Fb',
    'Facebook': 'Fb',
    'Instagram': 'Fb',
    'Boomplay': 'Bp',
    'YouTube': 'Yt',
    'YouTube Music': 'Ym',
}

def parse_csv_file(filepath):
    """解析单个 CSV 文件，返回汇总数据"""
    print(f"\n正在解析: {filepath}")
    
    agg = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))  # {region: {platform: [gross_eur, qty]}}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # CSV 是分号分隔的
        reader = csv.reader(f, delimiter=';')
        
        # 读取表头
        headers = next(reader)
        print(f"表头: {headers[:5]}...")  # 只打印前5个
        
        # 找到关键列的索引
        idx_platform = headers.index('Platform')
        idx_country = headers.index('Country / Region')
        idx_quantity = headers.index('Quantity')
        idx_gross = headers.index('Gross Revenue')
        
        row_count = 0
        for row in reader:
            row_count += 1
            if row_count % 100000 == 0:
                print(f"  已处理 {row_count} 行...")
            
            if len(row) <= max(idx_platform, idx_country, idx_quantity, idx_gross):
                continue
                
            platform = row[idx_platform]
            country = row[idx_country]
            qty = row[idx_quantity]
            gross = row[idx_gross]
            
            if not platform or not country:
                continue
            
            country_key = country.strip().lower()
            region = COUNTRY_MAP.get(country_key)
            if not region:
                continue
            
            platform_key = PLATFORM_MAP.get(platform.strip())
            if not platform_key:
                continue
            
            try:
                q = float(qty) if qty else 0.0
                g = float(gross) if gross else 0.0
                if q > 0:
                    agg[region][platform_key][0] += g  # gross revenue EUR
                    agg[region][platform_key][1] += q  # quantity
            except (TypeError, ValueError):
                pass
        
        print(f"总处理行数: {row_count}")
    
    return agg

# 汇总所有文件的数据
print("=" * 60)
print("开始解析 Believe 1-3月数据")
print("=" * 60)

all_agg = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))

for csv_file in CSV_FILES:
    agg = parse_csv_file(csv_file)
    
    # 合并到 all_agg
    for region in agg:
        for platform in agg[region]:
            all_agg[region][platform][0] += agg[region][platform][0]
            all_agg[region][platform][1] += agg[region][platform][1]

# 计算各平台总收入（所有地区合计）
print("\n" + "=" * 60)
print("Believe 各平台总收入（EUR）→ USD")
print("汇率: 1 EUR = 1.085 USD")
print("=" * 60)

# 汇总所有地区的数据
platform_totals_eur = defaultdict(lambda: [0.0, 0.0])
for region in all_agg:
    for pk in all_agg[region]:
        platform_totals_eur[pk][0] += all_agg[region][pk][0]
        platform_totals_eur[pk][1] += all_agg[region][pk][1]

# 计算 USD 总收入
platform_totals_usd = {}
believe_total_usd = 0.0

PLATFORM_NAMES = {
    'Sp': 'Spotify',
    'Ap': 'Apple Music',
    'Yc': 'YouTube Official Content',
    'Ym': 'YouTube Audio Tier',
    'Yv': 'YouTube Music Video',
    'Sh': 'YouTube Shorts',
    'Tk': 'TikTok',
    'Fb': 'Facebook/Instagram',
    'Bp': 'Boomplay',
    'Yt': 'YouTube',
}

for pk in sorted(platform_totals_eur.keys(), key=lambda x: platform_totals_eur[x][0], reverse=True):
    total_gross_eur, total_qty = platform_totals_eur[pk]
    total_gross_usd = total_gross_eur * 1.085
    platform_totals_usd[pk] = total_gross_usd
    believe_total_usd += total_gross_usd
    
    name = PLATFORM_NAMES.get(pk, pk)
    print(f"{name}:")
    print(f"  EUR {total_gross_eur:,.2f} → USD ${total_gross_usd:,.2f}")
    print(f"  Quantity: {total_qty:,.0f}")
    pct = (total_gross_usd / believe_total_usd * 100) if believe_total_usd > 0 else 0
    print(f"  占比: {pct:.1f}%")
    print()

print("=" * 60)
print(f"Believe 总收入: USD ${believe_total_usd:,.2f}")
print(f"            ≈ RMB ¥{believe_total_usd * 7.2:,.2f}")
print("=" * 60)

# 计算各平台收入占比
print("\n各平台收入占比:")
for pk in sorted(platform_totals_usd.keys(), key=lambda x: platform_totals_usd[x], reverse=True):
    pct = platform_totals_usd[pk] / believe_total_usd * 100 if believe_total_usd > 0 else 0
    name = PLATFORM_NAMES.get(pk, pk)
    print(f"  {name}: {pct:.1f}%")

# 读取当前 index.html
html_path = '/Users/olivia/WorkBuddy/2026-05-13-task-4/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("\n" + "=" * 60)
print("需要更新的 KPI 卡片数据")
print("=" * 60)

# 输出更新后的 KPI 卡片 HTML
kpi_updates = {}

# Believe 总收入
kpi_updates['believe_total'] = {
    'usd': believe_total_usd,
    'rmb': believe_total_usd * 7.2,
}

# Believe YouTube Official Content
yc_usd = platform_totals_usd.get('Yc', 0)
kpi_updates['believe_youtube'] = {
    'usd': yc_usd,
    'pct': yc_usd / believe_total_usd * 100 if believe_total_usd > 0 else 0,
}

# Believe Spotify
sp_usd = platform_totals_usd.get('Sp', 0)
kpi_updates['believe_spotify'] = {
    'usd': sp_usd,
    'pct': sp_usd / believe_total_usd * 100 if believe_total_usd > 0 else 0,
}

# Believe Apple Music
ap_usd = platform_totals_usd.get('Ap', 0)
kpi_updates['believe_apple'] = {
    'usd': ap_usd,
    'pct': ap_usd / believe_total_usd * 100 if believe_total_usd > 0 else 0,
}

print("\n1. Believe 总收入:")
print(f"   USD ${kpi_updates['believe_total']['usd']:,.0f}")
print(f"   ≈ RMB ¥{kpi_updates['believe_total']['rmb']:,.0f}")

print("\n2. Believe YouTube Official Content:")
print(f"   USD ${kpi_updates['believe_youtube']['usd']:,.0f}")
print(f"   占收入 {kpi_updates['believe_youtube']['pct']:.1f}%")

print("\n3. Believe Spotify:")
print(f"   USD ${kpi_updates['believe_spotify']['usd']:,.0f}")
print(f"   占收入 {kpi_updates['believe_spotify']['pct']:.1f}%")

print("\n4. Believe Apple Music:")
print(f"   USD ${kpi_updates['believe_apple']['usd']:,.0f}")
print(f"   占收入 {kpi_updates['believe_apple']['pct']:.1f}%")

# 生成更新后的 HTML 片段
print("\n" + "=" * 60)
print("更新后的 KPI 卡片 HTML")
print("=" * 60)

# Believe 总收入卡片
believe_total_html = f'''<div class="kpi-card believe">
      <div class="kpi-label">Believe · 总收入</div>
      <div class="kpi-value" style="color:var(--believe)">${believe_total_usd:,.0f}</div>
      <div class="kpi-sub">≈ ¥{believe_total_usd * 7.2:,.0f}</div>
    </div>'''

# Believe YouTube Official Content 卡片
yc_html = f'''<div class="kpi-card believe">
      <div class="kpi-label">Believe · YouTube Official Content</div>
      <div class="kpi-value" style="color:var(--believe)">${yc_usd:,.0f}</div>
      <div class="kpi-sub">≈ ¥{yc_usd * 7.2:,.0f} · 占收入 {yc_usd / believe_total_usd * 100:.1f}%</div>
    </div>'''

# Believe Spotify 卡片
sp_html = f'''<div class="kpi-card believe">
      <div class="kpi-label">Believe · Spotify</div>
      <div class="kpi-value" style="color:var(--believe)">${sp_usd:,.0f}</div>
      <div class="kpi-sub">≈ ¥{sp_usd * 7.2:,.0f} · 占收入 {sp_usd / believe_total_usd * 100:.1f}%</div>
    </div>'''

# Believe Apple Music 卡片
ap_html = f'''<div class="kpi-card believe">
      <div class="kpi-label">Believe · Apple Music</div>
      <div class="kpi-value" style="color:var(--believe)">${ap_usd:,.0f}</div>
      <div class="kpi-sub">≈ ¥{ap_usd * 7.2:,.0f} · 占收入 {ap_usd / believe_total_usd * 100:.1f}%</div>
    </div>'''

print("\nBelieve 总收入卡片:")
print(believe_total_html)
print("\nBelieve YouTube Official Content 卡片:")
print(yc_html)
print("\nBelieve Spotify 卡片:")
print(sp_html)
print("\nBelieve Apple Music 卡片:")
print(ap_html)

# 保存计算结果到 JSON
output = {
    'believe_total_usd': round(believe_total_usd, 2),
    'believe_total_rmb': round(believe_total_usd * 7.2, 2),
    'platform_totals_usd': {k: round(v, 2) for k, v in platform_totals_usd.items()},
    'platform_pct': {k: round(v / believe_total_usd * 100, 1) if believe_total_usd > 0 else 0 for k, v in platform_totals_usd.items()},
    'kpi_updates': {
        'believe_total': {
            'usd': round(believe_total_usd, 0),
            'rmb': round(believe_total_usd * 7.2, 0),
        },
        'believe_youtube': {
            'usd': round(yc_usd, 0),
            'pct': round(yc_usd / believe_total_usd * 100, 1) if believe_total_usd > 0 else 0,
        },
        'believe_spotify': {
            'usd': round(sp_usd, 0),
            'pct': round(sp_usd / believe_total_usd * 100, 1) if believe_total_usd > 0 else 0,
        },
        'believe_apple': {
            'usd': round(ap_usd, 0),
            'pct': round(ap_usd / believe_total_usd * 100, 1) if believe_total_usd > 0 else 0,
        },
    }
}

output_path = '/Users/olivia/WorkBuddy/2026-05-13-task-4/believe_revenue_calc.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n计算结果已保存到: {output_path}")
print("\n下一步：手动更新 index.html 中的 KPI 卡片 HTML")
