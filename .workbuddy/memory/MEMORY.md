# 长期记忆

## 报告项目：Believe vs 东西发行商对比分析

项目路径：`/Users/olivia/WorkBuddy/2026-05-13-task-4/`

### Believe CSV 原始数据
- 文件：`/Users/olivia/Downloads/202601~603 Believe.csv`（分号分隔，EUR计价）
- 列名：`Platform` / `Country / Region` / `Quantity` / `Gross Revenue` 等
- 汇率：1 EUR = 1.085 USD（2026Q1均值）

### Believe 地区名称 → 代码映射（原始CSV中的实际写法）
⚠️ **Korea 必须用 `'korea, republic of'`，不是 `'korea'`！**

```python
country_name_to_code = {
    'united states': 'US',
    'united kingdom': 'GB',
    'japan': 'JP',
    'korea, republic of': 'KR',   # ← 必须是这个！
    'korea': 'KR',                 # ← 这个也要保留兜底
    'south korea': 'KR',
    'republic of korea': 'KR',
    'taiwan, province of china': 'TW',
    'taiwan': 'TW',
    'thailand': 'TH',
    'indonesia': 'ID',
    'viet nam': 'VN',
    'india': 'IN',
    'hong kong': 'HK',
    'singapore': 'SG',
    'malaysia': 'MY',
}
```

### 东西 CSV 原始数据
- 文件：`/Users/olivia/WorkBuddy/2026-05-13-task-4/dongxi_202601~603.csv`（逗号分隔，USD计价）
- 列名：`Store` / `Territories`（ISO2代码）/ `Quantity` / `AmountPaidByStore` 等

### YouTube 子平台映射（Olivia 确认版）
- **Believe**：
  - YouTube Official Content → Content ID 单价
  - YouTube UGC → Content ID 单价
  - YouTube Audio Tier → Music/Art Tracks 单价
  - YouTube Shorts → Shorts 单价
- **东西**：
  - YouTube Audio Content ID → Content ID 单价
  - YouTube Art Tracks → Music 单价
  - YouTube Audio Tier → Music 单价
  - YouTube Shorts → Shorts 单价
