"""
重新生成 DATA 对象：
- 去掉 bYc（OC+UGC 合并），改为 bYcOc 和 bYcUgc
- 修正 bYv 的用途（只用于 Music Video，不用于 Official Content）
- 以 Believe xlsx 实际 Platform 名称为准，不预设映射
"""
import openpyxl
import csv
from collections import defaultdict

EUR_TO_USD = 1.085

# ========== 1. Believe 分地区分 Platform 单价 ==========
wb = openpyxl.load_workbook('/Users/olivia/Desktop/2026Q1 Believe.xlsx', data_only=True)
ws = wb.active
headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
plat_idx = headers.index('Platform')
country_idx = headers.index('Country / Region')
qty_idx = headers.index('Quantity')
gross_idx = headers.index('Gross Revenue')

COUNTRY_MAP = {
    'united states': 'US', 'united kingdom': 'GB', 'japan': 'JP',
    'korea, republic of': 'KR', 'taiwan, province of china': 'TW',
    'thailand': 'TH', 'indonesia': 'ID', 'viet nam': 'VN',
    'hong kong': 'HK', 'singapore': 'SG', 'malaysia': 'MY', 'china': 'CN',
}

# believe_data[region][platform] = {rev, qty}
believe_data = defaultdict(lambda: defaultdict(lambda: {'rev': 0.0, 'qty': 0.0}))
believe_total = defaultdict(lambda: {'rev': 0.0, 'qty': 0.0})  # 合计

for row in ws.iter_rows(min_row=2, values_only=True):
    plat = row[plat_idx]
    country = row[country_idx]
    qty = row[qty_idx]
    gross = row[gross_idx]
    if not plat or not country or qty is None or gross is None:
        continue
    region = COUNTRY_MAP.get(str(country).strip().lower())
    if not region:
        continue
    try:
        qty_f = float(qty)
        rev_f = float(gross) * EUR_TO_USD
    except (ValueError, TypeError):
        continue
    believe_data[region][plat]['rev'] += rev_f
    belief_data[region][plat]['qty'] += qty_f
    believe_total[plat]['rev'] += rev_f
    believe_total[plat]['qty'] += qty_f

def up(rev, qty):
    return rev / qty * 1000 if qty > 0 else None

# ========== 2. 东西 分地区分 Store 单价 ==========
dongxi_data = defaultdict(lambda: defaultdict(lambda: {'rev': 0.0, 'qty': 0.0}))

for f in ['/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202601.csv',
          '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202602.csv',
          '/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202603.csv']:
    try:
        with open(f, encoding='utf-8-sig') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                store = row.get('Store', '')
                region = row.get('Territories', '').strip()
                try:
                    rev = float(row.get('AmountPaidByStore', 0))
                    qty = float(row.get('Quantity', 0))
                except (ValueError, TypeError):
                    rev, qty = 0, 0
                dongxi_data[region][store]['rev'] += rev
                dongxi_data[region][store]['qty'] += qty
    except FileNotFoundError:
        pass

# ========== 3. 对照实际名称，不合并 ==========
# Believe Platform → 东西 Store（以实际名称为准）
# Official Content vs Art Tracks：Believe YouTube Official Content ↔ 东西 YouTube Art Tracks
# UGC vs Audio Content ID：Believe YouTube UGC ↔ 东西 YouTube Audio Content ID
# Audio Tier：Believe YouTube Audio Tier ↔ 东西 YouTube Audio Tier
# Music Video：Believe YouTube Music Video ↔ 东西 YouTube Music Video
# Shorts：Believe YouTube Shorts ↔ 东西 YouTubeShorts

REGIONS = ['US', 'GB', 'JP', 'KR', 'TW', 'TH', 'ID', 'VN', 'HK', 'SG', 'MY']

# 计算各地区 DATA 值
# 需要保留的原有字段：bSp, dSp, bAp, dAp, bYm, dYmAt, dYmAr, bYv, dYv, bSh, dSh, sSp, sAp, sYm, sTk
# 新增：bYcOc（Official Content 单价），bYcUgc（UGC 单价）
# 删除：bYc（原来的合并值）

print('开始生成 DATA 对象...')

# 先输出到文件
with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/data_new.js', 'w', encoding='utf-8') as f:
    f.write('const DATA = {\n')
    f.write('  // 口径说明\n')
    f.write('  // Believe 单价：Gross Revenue (EUR) × 1.085 / Quantity × 1000（加权平均）\n')
    f.write('  // 东西单价：AmountPaidByStore (USD) / Quantity × 1000（加权平均）\n')
    f.write('  // bYcOc = Believe YouTube Official Content（不合并 UGC）\n')
    f.write('  // bYcUgc = Believe YouTube UGC（不合并 Official Content）\n')
    
    for region in REGIONS:
        rd = dict(believe_data[region])
        dd = dict(dongxi_data.get(region, {}))
        
        # Believe
        bSp = up(rd.get('Spotify', {}).get('rev',0), rd.get('Spotify', {}).get('qty',0))
        bAp = up(rd.get('Apple Music', {}).get('rev',0), rd.get('Apple Music', {}).get('qty',0))
        bYm = up(rd.get('YouTube Audio Tier', {}).get('rev',0), rd.get('YouTube Audio Tier', {}).get('qty',0))
        bYcOc = up(rd.get('YouTube Official Content', {}).get('rev',0), rd.get('YouTube Official Content', {}).get('qty',0))
        bYcUgc = up(rd.get('YouTube UGC', {}).get('rev',0), rd.get('YouTube UGC', {}).get('qty',0))
        bYv = up(rd.get('YouTube Music Video', {}).get('rev',0), rd.get('YouTube Music Video', {}).get('qty',0))
        bSh = up(rd.get('YouTube Shorts', {}).get('rev',0), rd.get('YouTube Shorts', {}).get('qty',0))
        
        # 东西
        dSp = up(dd.get('Spotify', {}).get('rev',0), dd.get('Spotify', {}).get('qty',0))
        dAp = up(dd.get('Apple Music', {}).get('rev',0), dd.get('Apple Music', {}).get('qty',0))
        dYmAt = up(dd.get('YouTube Audio Tier', {}).get('rev',0), dd.get('YouTube Audio Tier', {}).get('qty',0))
        dYmAr = up(dd.get('YouTube Art Tracks', {}).get('rev',0), dd.get('YouTube Art Tracks', {}).get('qty',0))
        dYcAr = up(dd.get('YouTube Audio Content ID', {}).get('rev',0), dd.get('YouTube Audio Content ID', {}).get('qty',0))
        dYv = up(dd.get('YouTube Music Video', {}).get('rev',0), dd.get('YouTube Music Video', {}).get('qty',0))
        dSh = up(dd.get('YouTubeShorts', {}).get('rev',0), dd.get('YouTubeShorts', {}).get('qty',0))
        
        # Sony 数据（保留原值，这里先用 None 占位——需要从原 HTML 读取）
        # 暂时写 None，后面再从原 DATA 里抄
        sSp = None
        sAp = None
        sYm = None
        sTk = None
        
        def js_val(v):
            return f'{v:.4f}' if v is not None else 'null'
        
        f.write(f'  {region}: ' + '{')
        f.write(f'bSp:{js_val(bSp)}, dSp:{js_val(dSp)}, ')
        f.write(f'bAp:{js_val(bAp)}, dAp:{js_val(dAp)}, ')
        f.write(f'bYm:{js_val(bYm)}, dYmAt:{js_val(dYmAt)}, dYmAr:{js_val(dYmAr)}, ')
        f.write(f'bYcOc:{js_val(bYcOc)}, bYcUgc:{js_val(bYcUgc)}, ')  # 新增：分开
        f.write(f'dYcAr:{js_val(dYcAr)}, ')
        f.write(f'bYv:{js_val(bYv)}, dYv:{js_val(dYv)}, ')
        f.write(f'bSh:{js_val(bSh)}, dSh:{js_val(dSh)}, ')
        f.write(f'sSp:{js_val(sSp)}, sAp:{js_val(sAp)}, sYm:{js_val(sYm)}, sTk:{js_val(sTk)}')
        f.write('},\n')
    
    # CN（只有 东西 有部分数据，Believe 无）
    f.write(f'  CN: ' + '{')
    f.write('bAp:2.8433, dAp:3.2152, dYmAr:0.0, dYv:0.0, dYcAr:0.0, bSh:0.0067, sAp:21.175, sYm:null, sTk:null')
    f.write('},\n')
    
    f.write('};\n')

print('DATA 对象已导出到 data_new.js')
print('注意：Sony 数据（sSp/sAp/sYm/sTk）暂为 null，需要从原 HTML 中手动补全。')
