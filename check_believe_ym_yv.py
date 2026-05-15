import json

with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/believe_revenue_calc.json', 'r') as f:
    d = json.load(f)

print('Believe platform_totals_usd:')
for k, v in d['platform_totals_usd'].items():
    print(f"  {k}: ${v:,.2f}")

print(f"\nBelieve total: ${d['believe_total_usd']:,.2f}")

# 直接看原始believe CSV数据，确认Ym和Yv是否有收入
import csv
ym_rev = 0.0
yv_rev = 0.0

with open('/Users/olivia/Downloads/202601~603 Believe.csv', 'r', encoding='utf-8') as fh:
    reader = csv.DictReader(fh, delimiter=';')
    for row in reader:
        platform = row.get('Platform', '')
        try:
            amt = float(row.get('Gross Revenue', 0))
        except:
            continue
        if platform == 'YouTube Audio Tier':
            ym_rev += amt
        elif platform == 'YouTube Music Video':
            yv_rev += amt

print(f"\n直接从Believe CSV计算:")
print(f"  YouTube Audio Tier (Ym) 收入: ${ym_rev:,.2f}")
print(f"  YouTube Music Video (Yv) 收入: ${yv_rev:,.2f}")

# 换算成USD
print(f"\n换算USD (÷1.085):")
print(f"  Ym: ${ym_rev/1.085:,.2f}")
print(f"  Yv: ${yv_rev/1.085:,.2f}")
