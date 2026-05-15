#!/usr/bin/env python3
"""替换 index.html 中的 DATA 对象"""
import re

with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 新的 DATA 对象文本
NEW_DATA = """const DATA = {
  // 口径说明
  // Believe 单价：Gross Revenue (EUR) × 1.085 / Quantity × 1000（加权平均）
  // 东西单价：AmountPaidByStore (USD) / Quantity × 1000（加权平均）
  // bYv 来源：music video.xlsx Unit Price (EUR) × 1.085 × 1000（按 quantity 加权平均）
  // YT Music Video 口径：东西 dYv=YouTube(不含子分类)，bYv=YouTube Music Video
  // Sony 单价：Roy. Price (RMB) × 1000（算术平均）。表格中主显示$（RMB÷7.25），副显示≈¥（原始RMB×1000）
  US: {bSp:3.1903, dSp:3.5229, bAp:5.3956, dAp:4.4246, bYm:2.2686, dYmAt:2.5000, dYmAr:8.4011, bYv:6.9589, dYv:7.0181, bYc:7.2989, dYcAr:2.6736, bSh:0.0067, dSh:0.1771, sSp:28.2638, sAp:60.1275, sYm:null, sTk:51.7250},
  GB: {bSp:3.3018, dSp:3.8657, bAp:8.3536, dAp:10.4151, bYm:2.2046, dYmAt:2.4255, dYmAr:8.9137, bYv:6.2866, dYv:5.9933, bYc:8.878, dYcAr:2.1389, bSh:0.0067, dSh:0.0828, sSp:32.0096, sAp:74.2448, sYm:null, sTk:43.6333},
  JP: {bSp:1.2971, dSp:1.6849, bAp:3.8468, dAp:5.0595, bYm:2.3167, dYmAt:1.9123, dYmAr:5.0883, bYv:3.7565, dYv:4.0550, bYc:3.8776, dYcAr:1.3493, bSh:0.0067, dSh:0.0278, sSp:28.6273, sAp:51.5300, sYm:null, sTk:0.0100},
  KR: {bSp:1.4582, dSp:1.9649, bAp:3.6846, dAp:4.1088, bYm:2.0949, dYmAt:2.2995, dYmAr:5.3784, bYv:2.6276, dYv:3.5842, bYc:2.9775, dYcAr:0.6916, bSh:0.0067, dSh:0.0259, sSp:20.9524, sAp:30.4100, sYm:null, sTk:32.0000},
  TW: {bSp:1.025, dSp:1.1295, bAp:3.2324, dAp:3.8847, bYm:1.1492, dYmAt:1.2654, dYmAr:3.6433, bYv:2.6236, dYv:2.8197, bYc:2.6015, dYcAr:1.1778, bSh:0.0067, dSh:0.0191, sSp:9.3110, sAp:31.6395, sYm:9.6923, sTk:33.2625},
  TH: {bSp:0.3413, dSp:0.7549, bAp:2.7724, dAp:3.4703, bYm:1.2652, dYmAt:1.3941, dYmAr:1.5071, bYv:0.8363, dYv:1.2083, bYc:1.4167, dYcAr:0.5022, bSh:0.0067, dSh:0.0088, sSp:10.2714, sAp:22.2870, sYm:null, sTk:11.5000},
  ID: {bSp:0.1316, dSp:0.4906, bAp:1.7865, dAp:2.1739, bYm:0.8793, dYmAt:0.9675, dYmAr:1.3672, bYv:0.9263, dYv:0.9695, bYc:0.4801, dYcAr:0.1075, bSh:0.0067, dSh:0.0032, sSp:2.0333, sAp:16.9714, sYm:null, sTk:null},
  VN: {bSp:0.3026, dSp:0.4382, bAp:1.872, dAp:2.2665, dYmAr:0.6711, bYv:0.7021, dYv:0.685, bYc:0.3268, dYcAr:0.1335, bSh:0.0067, dSh:0.0071, sSp:8.6200, sAp:21.4357, sYm:null, sTk:7.6000},
  HK: {bSp:1.8331, dSp:2.3707, bAp:5.3651, dAp:6.4423, dYmAt:1.2794, dYmAr:5.7108, bYv:4.4256, dYv:4.1506, bYc:4.7429, dYcAr:1.5761, bSh:0.0067, dSh:0.0225, sSp:21.8020, sAp:45.3027, sYm:null, sTk:null},
  SG: {bSp:2.446, dSp:2.8156, bAp:7.3019, dAp:8.7171, bYm:1.8492, dYmAt:2.0371, dYmAr:6.963, bYv:4.7665, dYv:4.661, bYc:5.3803, dYcAr:1.9382, bSh:0.0067, dSh:0.0314, sSp:16.2352, sAp:63.6667, sYm:null, sTk:20.6000},
  MY: {bSp:0.7057, dSp:1.0059, bAp:3.1351, dAp:3.9002, bYm:1.1381, dYmAt:1.2616, dYmAr:2.0249, bYv:1.7693, dYv:1.722, bYc:1.5767, dYcAr:0.8007, bSh:0.0067, dSh:0.0103, sSp:7.3478, sAp:26.1222, sYm:null, sTk:null},
  CN: {bAp:2.8433, dAp:3.2152, dYmAr:0.0, dYv:0.0, dYcAr:0.0, bSh:0.0067, sAp:21.175, sYm:null, sTk:null},
};"""

# 用正则替换 DATA 对象（从 const DATA = { 到 };）
pattern = r'const DATA = \{[^;]*\};'
new_content = re.sub(pattern, NEW_DATA, content, flags=re.DOTALL)

with open('/Users/olivia/WorkBuddy/2026-05-13-task-4/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("DATA 对象已更新！")
print("更新内容：")
print("  1. 所有地区的 Believe 数据已用 2026Q1 Excel 重新计算")
print("  2. KR（韩国）补全了缺失的 bSp/bAp/bYm/bYv/bYc/bSh")
print("  3. bYc 等值已修正（US: 8.4155→7.2989, GB: 11.1682→8.878 等）")
