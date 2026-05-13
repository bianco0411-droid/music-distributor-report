#!/usr/bin/env python3
"""
东西音乐 2026年1-3月 完整分析脚本（新CSV格式）
- 所有行全部纳入统计（不使用采样）
- 输出：单价对比、收入结构、YouTube CID占比
"""

import pandas as pd
import json
import sys
from collections import defaultdict

# ============================================================
# 1. 平台标准化映射
# ============================================================
def map_platform(store):
    """将原始Store映射为标准平台名称（YouTube统一口径）"""
    store = str(store).strip()
    
    # YouTube Music = Art Tracks + Audio Tier
    if store in ('YouTube Art Tracks', 'YouTube Audio Tier'):
        return 'YouTube Music'
    # YouTube Shorts
    elif store == 'YouTubeShorts':
        return 'YouTube Shorts'
    # YouTube Content ID = Audio Content ID + MCN (UGC equivalent)
    elif store in ('YouTube Audio Content ID', 'YouTubeMCN'):
        return 'YouTube Content ID'
    # Official Video = YouTube Music Video
    elif store == 'YouTube Music Video':
        return 'Official Video'
    elif store == 'Spotify':
        return 'Spotify'
    elif store in ('Apple Music', 'Apple iTunes', 'Apple Match'):
        return 'Apple Music'
    elif store == 'TikTok':
        return 'TikTok'
    elif store == 'Facebook':
        return 'Facebook'
    elif store in ('Amazon Unlimited', 'Amazon Prime', 'Amazon Ads'):
        return 'Amazon'
    elif store == 'Melon':
        return 'Melon'
    elif store == 'Deezer':
        return 'Deezer'
    elif store in ('SoundCloud', 'Audiomack', 'Anghami', 'Flo', 'Tidal', 'Pandora', 'iHeart',
                   'VEVO', 'Trebel', 'AWA', 'Snap', 'Omusic', 'KKbox', 'MOOV',
                   'SoundtrackYourBrand', 'Yandex'):
        return 'Other Streaming'
    else:
        return 'Other'


def map_service_type(service):
    """将Service映射为计费类型"""
    service = str(service).strip()
    ad_keywords = ['Ad-', 'ad-', 'Advertisement', 'Free', 'FREE', 'free', 
                   'UGC', 'Reels', 'FB_', 'IG_', 'Shorts', 'ADS', 'STORY', 'NOTE']
    
    sub_keywords = ['Subscri', 'Premium', 'Premium', 'Family', 'Individual', 
                    'Student', 'Monthly', 'Annual', 'Streaming', 'OnDemand', 
                    'HiRes', 'STREAM', 'DOWNLOAD', 'Deezer', 'Melon', 'AWA',
                    'Apple One', 'Apple Match', 'Amazon', 'Tidal', 'Pandora',
                    'SoundCloud', 'Audiomack', 'Spotify', 'YouTube Music',
                    'YouTube Premium', 'YouTube.com', 'VEVO']
    
    # Check for ad-supported first
    for kw in ad_keywords:
        if kw in service:
            return 'Ad-Supported'
    
    # Then subscription
    for kw in sub_keywords:
        if kw in service:
            return 'Subscription'
    
    # Default based on known patterns
    if 'YouTube' in service or 'Apple' in service:
        if 'Free' in service:
            return 'Ad-Supported'
        else:
            return 'Subscription'
    
    return 'Other'


# ============================================================
# 2. 地区映射（12个目标地区）
# ============================================================
TARGET_REGIONS = ['US', 'UK', 'JP', 'KR', 'TW', 'TH', 'ID', 'VN', 'IN', 'HK', 'SG', 'MY']

def get_region(territory):
    """将Territories映射到标准地区代码"""
    territory = str(territory).strip().upper()
    
    mapping = {
        'US': 'US', 'USA': 'US',
        'GB': 'UK', 'UNITED KINGDOM': 'UK', 'GREAT BRITAIN': 'UK',
        'JP': 'JP', 'JAPAN': 'JP',
        'KR': 'KR', 'SOUTH KOREA': 'KR', 'KOREA': 'KR',
        'TW': 'TW', 'TAIWAN': 'TW',
        'TH': 'TH', 'THAILAND': 'TH',
        'ID': 'ID', 'INDONESIA': 'ID',
        'VN': 'VN', 'VIETNAM': 'VN',
        'IN': 'IN', 'INDIA': 'IN',
        'HK': 'HK', 'HONG KONG': 'HK',
        'SG': 'SG', 'SINGAPORE': 'SG',
        'MY': 'MY', 'MALAYSIA': 'MY',
    }
    
    return mapping.get(territory, 'Other')


# ============================================================
# 3. 核心数据收集（分块处理大文件）
# ============================================================
print("开始读取数据...")

files = {
    '202601': '/Users/olivia/Downloads/2026-05-08/202601.csv',
    '202602': '/Users/olivia/Downloads/2026-05-08/202602.csv',
    '202603': '/Users/olivia/Downloads/2026-05-08/202603.csv',
}

# 全局累加器
total_quantity = defaultdict(int)          # platform × region → quantity
total_revenue = defaultdict(float)         # platform × region → revenue (USD)
platform_revenue = defaultdict(float)      # platform → total revenue
platform_quantity = defaultdict(int)       # platform → total quantity
region_revenue = defaultdict(float)        # region → total revenue
region_quantity = defaultdict(int)         # region → total quantity
service_type_revenue = defaultdict(lambda: defaultdict(float))  # platform → service_type → revenue
grand_total_revenue = 0.0
grand_total_quantity = 0
all_stores = set()
all_services = set()

for month, path in files.items():
    print(f"  处理 {month}...")
    row_count = 0
    
    for chunk in pd.read_csv(path, encoding='utf-8', chunksize=500000,
                             usecols=['Store', 'Service', 'Territories', 'Quantity', 'AmountPaidByStore']):
        # 移除无效行
        chunk = chunk.dropna(subset=['Quantity', 'AmountPaidByStore'])
        chunk['Quantity'] = pd.to_numeric(chunk['Quantity'], errors='coerce').fillna(0)
        chunk['AmountPaidByStore'] = pd.to_numeric(chunk['AmountPaidByStore'], errors='coerce').fillna(0)
        
        # 映射
        chunk['platform'] = chunk['Store'].apply(map_platform)
        chunk['region'] = chunk['Territories'].apply(get_region)
        chunk['service_type'] = chunk['Service'].apply(map_service_type)
        
        # 全局统计
        all_stores.update(chunk['Store'].unique())
        all_services.update(chunk['Service'].unique())
        
        # 按 platform × region 聚合
        grouped = chunk.groupby(['platform', 'region'], sort=False)
        
        for (plat, reg), grp in grouped:
            q = int(grp['Quantity'].sum())
            r = float(grp['AmountPaidByStore'].sum())
            total_quantity[(plat, reg)] += q
            total_revenue[(plat, reg)] += r
        
        # 全局平台级
        for plat, grp in chunk.groupby('platform', sort=False):
            platform_revenue[plat] += float(grp['AmountPaidByStore'].sum())
            platform_quantity[plat] += int(grp['Quantity'].sum())

        # 全局地区级
        for reg, grp in chunk.groupby('region', sort=False):
            region_revenue[reg] += float(grp['AmountPaidByStore'].sum())
            region_quantity[reg] += int(grp['Quantity'].sum())

        # 服务类型 × 平台
        for (plat, stype), grp in chunk.groupby(['platform', 'service_type'], sort=False):
            service_type_revenue[plat][stype] += float(grp['AmountPaidByStore'].sum())

        # 总计
        grand_total_revenue += float(chunk['AmountPaidByStore'].sum())
        grand_total_quantity += int(chunk['Quantity'].sum())
        row_count += len(chunk)
    
    print(f"    {month}: {row_count:,} 行处理完成")

print(f"\n总计: {grand_total_quantity:,} streams, ${grand_total_revenue:,.2f} USD")

# ============================================================
# 4. 构建单价表（/1000 streams）
# ============================================================
print("\n构建单价表...")

# 全局单价
global_unit_price = {}
for plat in platform_revenue:
    q = platform_quantity[plat]
    r = platform_revenue[plat]
    if q > 0:
        global_unit_price[plat] = round(r / q * 1000, 4)

# 按地区单价（仅12个目标地区）
region_platform_unit = {}
for (plat, reg), q in total_quantity.items():
    if reg in TARGET_REGIONS or reg != 'Other':
        if q > 0:
            r = total_revenue[(plat, reg)]
            region_platform_unit[(plat, reg)] = round(r / q * 1000, 4)

# ============================================================
# 5. YouTube CID 专项
# ============================================================
yt_cid_revenue = platform_revenue.get('YouTube Content ID', 0)
yt_cid_pct = yt_cid_revenue / grand_total_revenue * 100 if grand_total_revenue > 0 else 0
tiktok_revenue = platform_revenue.get('TikTok', 0)
tiktok_q = platform_quantity.get('TikTok', 0)
tiktok_unit = tiktok_revenue / tiktok_q * 1000 if tiktok_q > 0 else 0

# ============================================================
# 6. 整理输出数据
# ============================================================
print("整理输出数据...")

# 平台收入排序
platforms_sorted = sorted(platform_revenue.keys(), key=lambda x: platform_revenue[x], reverse=True)

platform_summary = []
for plat in platforms_sorted:
    r = platform_revenue[plat]
    q = platform_quantity[plat]
    pct = r / grand_total_revenue * 100 if grand_total_revenue > 0 else 0
    unit = global_unit_price.get(plat, 0)
    
    # 服务类型拆分
    ad_rev = service_type_revenue[plat].get('Ad-Supported', 0)
    sub_rev = service_type_revenue[plat].get('Subscription', 0)
    other_rev = service_type_revenue[plat].get('Other', 0)
    
    platform_summary.append({
        'platform': plat,
        'revenue': round(r, 2),
        'quantity': q,
        'unit_price': unit,
        'pct': round(pct, 2),
        'ad_revenue': round(ad_rev, 2),
        'sub_revenue': round(sub_rev, 2),
        'other_revenue': round(other_rev, 2),
    })

# 地区收入
regions_sorted = sorted(region_revenue.keys(), key=lambda x: region_revenue[x], reverse=True)
region_summary = []
for reg in regions_sorted:
    if reg in TARGET_REGIONS or reg == 'Other':
        r = region_revenue[reg]
        q = region_quantity[reg]
        pct = r / grand_total_revenue * 100 if grand_total_revenue > 0 else 0
        unit = r / q * 1000 if q > 0 else 0
        region_summary.append({
            'region': reg,
            'revenue': round(r, 2),
            'quantity': q,
            'unit_price': round(unit, 4),
            'pct': round(pct, 2),
        })

# 12地区 × 平台单价矩阵
main_platforms = ['Spotify', 'Apple Music', 'YouTube Music', 'YouTube Content ID', 
                   'Official Video', 'YouTube Shorts', 'TikTok', 'Facebook']
region_platform_matrix = {}
for reg in TARGET_REGIONS:
    row = {}
    for plat in main_platforms:
        key = (plat, reg)
        if key in region_platform_unit:
            row[plat] = region_platform_unit[key]
        else:
            row[plat] = 0
    region_platform_matrix[reg] = row

# ============================================================
# 7. 保存JSON
# ============================================================
output = {
    'grand_total_revenue': round(grand_total_revenue, 2),
    'grand_total_quantity': grand_total_quantity,
    'platform_summary': platform_summary,
    'region_summary': region_summary,
    'region_platform_matrix': region_platform_matrix,
    'main_platforms': main_platforms,
    'yt_cid_revenue': round(yt_cid_revenue, 2),
    'yt_cid_pct': round(yt_cid_pct, 2),
    'tiktok_revenue': round(tiktok_revenue, 2),
    'tiktok_unit_price': round(tiktok_unit, 4),
    'tiktok_quantity': tiktok_q,
    'all_stores': sorted(all_stores),
    'all_services_count': len(all_services),
}

with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_new_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"数据已保存到 dongxi_new_analysis.json")
print(f"  总收入: ${grand_total_revenue:,.2f}")
print(f"  总streams: {grand_total_quantity:,}")
print(f"  YouTube CID占比: {yt_cid_pct:.1f}%")
print(f"  TikTok单价: ${tiktok_unit:.4f}/千次")
