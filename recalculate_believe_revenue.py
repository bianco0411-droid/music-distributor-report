#!/usr/bin/env python3
"""
重新计算 Believe 各平台总收入，并更新 index.html 中的 KPI 卡片
"""
import openpyxl
import json
import re
from collections import defaultdict

# 找到 Believe Excel 文件
import glob
import os

downloads = '/Users/olivia/Downloads/'
excel_files = glob.glob(downloads + '*Believe*.xlsx')
believe_file = None
for f in excel_files:
    if '20260101-20260331' in f or 'Q1' in f:
        believe_file = f
        break
if not believe_file and excel_files:
    believe_file = excel_files[0]  # 取第一个

print(f"使用文件: {believe_file}")
print(f"文件大小: {os.path.getsize(believe_file)} bytes")

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

# Platform 映射
PLATFORM_MAP = {
    'Spotify': 'Sp',
    'Apple Music': 'Ap',
    'Apple iTunes': 'Ap',
    'YouTube Official Content': 'Yc',
    'YouTube UGC': 'Yc',
    'YouTube Audio Tier': 'Ym',
    'YouTube Music Video': 'Yv',
    'YouTube Shorts': 'Sh',
    'TikTok': 'Tk',
    'Facebook / Instagram': 'Fb',
    'Facebook': 'Fb',
    'Instagram': 'Fb',
}

print("\n正在加载 Excel 文件...")
wb = openpyxl.load_workbook(believe_file, read_only=True)
ws = wb.active
print(f"Sheet: {ws.title}, 总行数: {ws.max_row}")

# 读取表头
headers = None
for row in ws.iter_rows(min_row=1, max_row=1):
    headers = [cell.value for cell in row]
print("表头:", headers)

idx_platform = headers.index('Platform')
idx_country = headers.index('Country / Region')
idx_quantity = headers.index('Quantity')
idx_gross = headers.index('Gross Revenue')

# 汇总：{region: {platform_key: [total_gross_eur, total_qty]}}
agg = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))

row_count = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    row_count += 1
    if row_count % 100000 == 0:
        print(f"  已处理 {row_count} 行...")
    
    platform = row[idx_platform]
    country = row[idx_country]
    qty = row[idx_quantity]
    gross = row[idx_gross]
    
    if platform is None or country is None:
        continue
    
    country_key = str(country).strip().lower()
    region = COUNTRY_MAP.get(country_key)
    if region is None:
        continue
    
    platform_key = PLATFORM_MAP.get(str(platform).strip())
    if platform_key is None:
        continue
    
    try:
        q = float(qty) if qty is not None else 0.0
        g = float(gross) if gross is not None else 0.0
        if q > 0:
            agg[region][platform_key][0] += g  # gross revenue EUR
            agg[region][platform_key][1] += q  # quantity
    except (TypeError, ValueError):
        pass

wb.close()

print(f"\n总处理行数: {row_count}")

# 计算各平台总收入（所有地区合计）
print("\n=== Believe 各平台总收入（EUR）→ USD ===")
print("汇率: 1 EUR = 1.085 USD\n")

# 汇总所有地区的数据
platform_totals_eur = defaultdict(lambda: [0.0, 0.0])
for region in agg:
    for pk in agg[region]:
        platform_totals_eur[pk][0] += agg[region][pk][0]
        platform_totals_eur[pk][1] += agg[region][pk][1]

# 计算 USD 总收入
platform_totals_usd = {}
believe_total_usd = 0.0

# 平台名称映射（用于输出）
PLATFORM_NAMES = {
    'Sp': 'Spotify',
    'Ap': 'Apple Music',
    'Yc': 'YouTube Official Content',
    'Ym': 'YouTube Audio Tier',
    'Yv': 'YouTube Music Video',
    'Sh': 'YouTube Shorts',
    'Tk': 'TikTok',
    'Fb': 'Facebook/Instagram',
}

for pk in sorted(platform_totals_eur.keys()):
    total_gross_eur, total_qty = platform_totals_eur[pk]
    total_gross_usd = total_gross_eur * 1.085
    platform_totals_usd[pk] = total_gross_usd
    believe_total_usd += total_gross_usd
    
    name = PLATFORM_NAMES.get(pk, pk)
    print(f"{name}: €{total_gross_eur:,.2f} → ${total_gross_usd:,.2f} USD")

print(f"\nBelieve 总收入: ${believe_total_usd:,.2f} USD")
print(f"≈ ¥{believe_total_usd * 7.2:,.2f} RMB")

# 计算各平台收入占比
print("\n=== 各平台收入占比 ===")
for pk in sorted(platform_totals_usd.keys(), key=lambda x: platform_totals_usd[x], reverse=True):
    pct = platform_totals_usd[pk] / believe_total_usd * 100
    name = PLATFORM_NAMES.get(pk, pk)
    print(f"{name}: {pct:.1f}%")

# 读取当前 index.html
html_path = '/Users/olivia/WorkBuddy/2026-05-13-task-4/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("\n=== 需要更新的 KPI 卡片数据 ===")

# 输出更新后的 KPI 卡片 HTML
kpi_data = {
    'believe_total': {
        'usd': believe_total_usd,
        'rmb': believe_total_usd * 7.2,
    },
    'believe_spotify': {
        'usd': platform_totals_usd.get('Sp', 0),
        'pct': platform_totals_usd.get('Sp', 0) / believe_total_usd * 100 if believe_total_usd > 0 else 0,
    },
    'believe_apple': {
        'usd': platform_totals_usd.get('Ap', 0),
        'pct': platform_totals_usd.get('Ap', 0) / believe_total_usd * 100 if believe_total_usd > 0 else 0,
    },
    'believe_youtube': {
        'usd': platform_totals_usd.get('Yc', 0),
        'pct': platform_totals_usd.get('Yc', 0) / believe_total_usd * 100 if believe_total_usd > 0 else 0,
    },
}

print("\nBelieve 总收入:")
print(f"  ${kpi_data['believe_total']['usd']:,.0f}")
print(f"  ≈ ¥{kpi_data['believe_total']['rmb']:,.0f}")

print("\nBelieve YouTube Official Content:")
print(f"  ${kpi_data['believe_youtube']['usd']:,.0f}")
print(f"  占收入 {kpi_data['believe_youtube']['pct']:.1f}%")

print("\nBelieve Spotify:")
print(f"  ${kpi_data['believe_spotify']['usd']:,.0f}")
print(f"  占收入 {kpi_data['believe_spotify']['pct']:.1f}%")

print("\nBelieve Apple Music:")
print(f"  ${kpi_data['believe_apple']['usd']:,.0f}")
print(f"  占收入 {kpi_data['believe_apple']['pct']:.1f}%")

# 保存计算结果到 JSON
output = {
    'believe_total_usd': believe_total_usd,
    'platform_totals_usd': {k: round(v, 2) for k, v in platform_totals_usd.items()},
    'platform_pct': {k: round(v / believe_total_usd * 100, 1) if believe_total_usd > 0 else 0 for k, v in platform_totals_usd.items()},
}

output_path = '/Users/olivia/WorkBuddy/2026-05-13-task-4/believe_revenue_calc.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n计算结果已保存到: {output_path}")
print("\n请手动更新 index.html 中的 KPI 卡片数据。")
