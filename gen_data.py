#!/usr/bin/env python3
"""生成更新后的 DATA 对象（保留 d* 和 s*，更新 b*）"""
import json

# 从 Excel 解析出的 Believe 数据（USD / 1000 streams）
BELIEVE = {
    "AU": {"Ap": 3.9738, "Sh": 0.0067, "Sp": 2.7186, "Tk": 1.0265, "Yc": 7.7292, "Ym": 1.7588, "Yv": 8.1769},
    "BR": {"Ap": 4.4851, "Sh": 0.0067, "Sp": 1.1962, "Tk": 0.998,  "Yc": 1.3235, "Ym": 0.8636, "Yv": 1.698},
    "CA": {"Ap": 4.4352, "Sh": 0.0067, "Sp": 2.1152, "Tk": 1.0056, "Yc": 6.0874, "Ym": 1.5226, "Yv": 4.5462},
    "CN": {"Ap": 2.8433},
    "DE": {"Ap": 6.2268, "Sh": 0.0067, "Sp": 3.1405, "Tk": 1.1103, "Yc": 5.8409, "Ym": 1.9143, "Yv": 5.4746},
    "FR": {"Ap": 5.5173, "Sh": 0.0067, "Sp": 2.3428, "Tk": 1.1063, "Yc": 4.0189, "Ym": 1.9145, "Yv": 3.3463},
    "GB": {"Ap": 8.3536, "Sh": 0.0067, "Sp": 3.3018, "Tk": 1.1259, "Yc": 8.878,  "Ym": 2.2046, "Yv": 6.2866},
    "HK": {"Ap": 5.3651, "Sh": 0.0067, "Sp": 1.8331, "Tk": 1.1047, "Yc": 4.7429, "Yv": 4.4256},
    "ID": {"Ap": 1.7865, "Sh": 0.0067, "Sp": 0.1316, "Tk": 1.0767, "Yc": 0.4801, "Ym": 0.8793, "Yv": 0.9263},
    "JP": {"Ap": 3.8468, "Sh": 0.0067, "Sp": 1.2971, "Tk": 1.0748, "Yc": 3.8776, "Ym": 2.3167, "Yv": 3.7565},
    "KR": {"Ap": 3.6846, "Sh": 0.0067, "Sp": 1.4582, "Tk": 1.1545, "Yc": 2.9775, "Ym": 2.0949, "Yv": 2.6276},
    "MX": {"Ap": 2.1469, "Sh": 0.0067, "Sp": 1.1881, "Tk": 0.9939, "Yc": 1.2257, "Ym": 1.2928, "Yv": 1.0508},
    "MY": {"Ap": 3.1351, "Sh": 0.0067, "Sp": 0.7057, "Tk": 1.1091, "Yc": 1.5767, "Ym": 1.1381, "Yv": 1.7693},
    "SG": {"Ap": 7.3019, "Sh": 0.0067, "Sp": 2.446,  "Tk": 1.1243, "Yc": 5.3803, "Ym": 1.8492, "Yv": 4.7665},
    "TH": {"Ap": 2.7724, "Sh": 0.0067, "Sp": 0.3413, "Tk": 1.194,  "Yc": 1.4167, "Ym": 1.2652, "Yv": 0.8363},
    "TW": {"Ap": 3.2324, "Sh": 0.0067, "Sp": 1.025,  "Tk": 1.1239, "Yc": 2.6015, "Ym": 1.1492, "Yv": 2.6236},
    "US": {"Ap": 5.3956, "Sh": 0.0067, "Sp": 3.1903, "Tk": 1.0283, "Yc": 7.2989, "Ym": 2.2686, "Yv": 6.9589},
    "VN": {"Ap": 1.872,  "Sh": 0.0067, "Sp": 0.3026, "Tk": 1.1116, "Yc": 0.3268, "Yv": 0.7021},
}

# 当前 DATA 中的 d* 和 s*（从 index.html 保留）
DONGXI_SONY = {
    "US": {"dSp": 3.5229, "dAp": 4.4246, "dYmAt": 2.5, "dYmAr": 8.4011, "dYv": 7.0181, "dYcAr": 2.6736, "dSh": 0.1771, "sSp": 28.2638, "sAp": 60.1275, "sYm": None, "sTk": 51.725},
    "GB": {"dSp": 3.8657, "dAp": 10.4151, "dYmAt": 2.4255, "dYmAr": 8.9137, "dYv": 5.9933, "dYcAr": 2.1389, "dSh": 0.0828, "sSp": 32.0096, "sAp": 74.2448, "sYm": None, "sTk": 43.6333},
    "JP": {"dSp": 1.6849, "dAp": 5.0595, "dYmAt": 1.9123, "dYmAr": 5.0883, "dYv": 4.055, "dYcAr": 1.3493, "dSh": 0.0278, "sSp": 28.6273, "sAp": 51.53, "sYm": None, "sTk": 0.01},
    "KR": {"dSp": 1.9649, "dAp": 4.1088, "dYmAt": 2.2995, "dYmAr": 5.3784, "dYv": 3.5842, "dYcAr": 0.6916, "dSh": 0.0259, "sSp": 20.9524, "sAp": 30.41, "sYm": None, "sTk": 32.0},
    "TW": {"dSp": 1.1295, "dAp": 3.8847, "dYmAt": 1.2654, "dYmAr": 3.6433, "dYv": 2.8197, "dYcAr": 1.1778, "dSh": 0.0191, "sSp": 9.311, "sAp": 31.6395, "sYm": 9.6923, "sTk": 33.2625},
    "TH": {"dSp": 0.7549, "dAp": 3.4703, "dYmAt": 1.3941, "dYmAr": 1.5071, "dYv": 1.2083, "dYcAr": 0.5022, "dSh": 0.0088, "sSp": 10.2714, "sAp": 22.287, "sYm": None, "sTk": 11.5},
    "ID": {"dSp": 0.4906, "dAp": 2.1739, "dYmAt": 0.9675, "dYmAr": 1.3672, "dYv": 0.9695, "dYcAr": 0.1075, "dSh": 0.0032, "sSp": 2.0333, "sAp": 16.9714, "sYm": None, "sTk": None},
    "VN": {"dSp": 0.4382, "dAp": 2.2665, "dYmAr": 0.6711, "dYv": 0.685, "dYcAr": 0.1335, "dSh": 0.0071, "sSp": 8.62, "sAp": 21.4357, "sYm": None, "sTk": 7.6},
    "HK": {"dSp": 2.3707, "dAp": 6.4423, "dYmAt": 1.2794, "dYmAr": 5.7108, "dYv": 4.1506, "dYcAr": 1.5761, "dSh": 0.0225, "sSp": 21.802, "sAp": 45.3027, "sYm": None, "sTk": None},
    "SG": {"dSp": 2.8156, "dAp": 8.7171, "dYmAt": 2.0371, "dYmAr": 6.963, "dYv": 4.661, "dYcAr": 1.9382, "dSh": 0.0314, "sSp": 16.2352, "sAp": 63.6667, "sYm": None, "sTk": 20.6},
    "MY": {"dSp": 1.0059, "dAp": 3.9002, "dYmAt": 1.2616, "dYmAr": 2.0249, "dYv": 1.722, "dYcAr": 0.8007, "dSh": 0.0103, "sSp": 7.3478, "sAp": 26.1222, "sYm": None, "sTk": None},
    "CN": {"dAp": 3.2152, "dYmAr": 0.0, "dYv": 0.0, "dYcAr": 0.0, "dSh": 0.0067, "sAp": 21.175, "sYm": None, "sTk": None},
}

# b* key 映射：BELIEVE 里的 key → DATA 里的 key
B_MAP = {
    "Sp": "bSp", "Ap": "bAp", "Ym": "bYm", "Yv": "bYv", "Yc": "bYc", "Sh": "bSh", "Tk": "bTk"
}

ALL_REGIONS = sorted(set(list(BELIEVE.keys()) + list(DONGXI_SONY.keys())))

print("const DATA = {")
for r in ALL_REGIONS:
    b = BELIEVE.get(r, {})
    d = DONGXI_SONY.get(r, {})
    entries = []
    # b* fields
    for bk, dvk in B_MAP.items():
        v = b.get(bk)
        if v is not None:
            entries.append(f"{dvk}:{v}")
    # d* fields
    for dk in ["dSp", "dAp", "dYmAt", "dYmAr", "dYv", "dYcAr", "dSh"]:
        v = d.get(dk)
        if v is not None:
            entries.append(f"{dk}:{v}")
    # s* fields
    for sk in ["sSp", "sAp", "sYm", "sTk"]:
        v = d.get(sk)
        if v is not None:
            entries.append(f"{sk}:{v}")
    
    if entries:
        print(f"  {r}: {{{', '.join(entries)}}},")
print("};")
