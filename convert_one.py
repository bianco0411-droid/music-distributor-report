import pandas as pd, os, sys

month = sys.argv[1]  # e.g. "02"
fname = f"2026{month}东西.xlsx"
path = f"/Users/olivia/Downloads/{fname}"
out_dir = "/Users/olivia/WorkBuddy/2026-05-13-task-4/"
xl = pd.ExcelFile(path)
all_dfs = []
for sh in xl.sheet_names:
    df = pd.read_excel(path, sheet_name=sh)
    df['_sheet'] = sh
    all_dfs.append(df)
merged = pd.concat(all_dfs, ignore_index=True)
out_path = f"{out_dir}dongxi_2026{month}.csv"
merged.to_csv(out_path, index=False)
print(f"Saved {out_path}: {len(merged)} rows")
