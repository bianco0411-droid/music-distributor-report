import pandas as pd
import os

out_dir = "/Users/olivia/WorkBuddy/2026-05-13-task-4/"
os.makedirs(out_dir, exist_ok=True)

for fname, mon in [("202601东西.xlsx","01"), ("202602东西.xlsx","02"), ("202603东西.xlsx","03")]:
    path = f"/Users/olivia/Downloads/{fname}"
    xl = pd.ExcelFile(path)
    all_dfs = []
    for sh in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sh)
        df['_sheet'] = sh
        all_dfs.append(df)
    merged = pd.concat(all_dfs, ignore_index=True)
    out_path = f"{out_dir}dongxi_2026{mon}.csv"
    merged.to_csv(out_path, index=False)
    print(f"Saved {out_path}: {len(merged)} rows")

print("ALL DONE")
