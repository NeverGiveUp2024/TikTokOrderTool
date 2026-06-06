# scripts/cleaned.py

def run():
    import pandas as pd
    from pathlib import Path
    import os

    # ==========================================
    # 配置
    # ==========================================
    orders_dir = Path(os.getenv("ORDERS_DIR", "data/orders"))
    sku_mapping_file = Path(os.getenv("SKU_FILE", "data/sku_mapping.xlsx"))
    influencer_mapping_file = Path(os.getenv("INFLUENCER_FILE", "data/influencer_mapping.xlsx"))
    output_dir = Path(os.getenv("CLEANED_DIR", "cleaned_orders"))
    output_dir.mkdir(exist_ok=True)

    # ==========================================
    # 读取 SKU 映射表
    # ==========================================
    sku_df = pd.read_excel(sku_mapping_file, dtype=str).fillna("")
    sku_map_dict = {
        f"{row['Store']}_{str(row['SKU_ID'])[-4:]}": row["Product_Name"]
        for _, row in sku_df.iterrows()
    }

    # ==========================================
    # 读取达人负责人映射表
    # ==========================================
    influencer_df = pd.read_excel(influencer_mapping_file, dtype=str).fillna("未匹配负责人")
    influencer_df = influencer_df.rename(
        columns={influencer_df.columns[0]: "达人用户名", influencer_df.columns[1]: "负责人"}
    )

    # 收集未匹配SKU
    all_unmatched = []

    # ==========================================
    # 遍历订单文件
    # ==========================================
    for order_file in orders_dir.glob("*.xlsx"):
        store_name = order_file.stem
        print(f"\n开始处理：{store_name}")

        df = pd.read_excel(order_file, dtype={"SKU ID": str, "达人用户名": str})
        df["店铺"] = store_name

        # 保留需要列
        columns_to_keep = [
            "达人用户名",
            "创建时间",
            "下单件数",
            "SKU ID",
            "标准佣金率",
            "店铺",
            "内容形式",
            "订单状态",
        ]
        df = df[columns_to_keep]

        # SKU 后四位
        df["SKU后四位"] = df["SKU ID"].astype(str).str[-4:]

        # 产品名称映射
        df["产品名称"] = df.apply(
            lambda x: sku_map_dict.get(f"{x['店铺']}_{x['SKU后四位']}", "未匹配SKU"), axis=1
        )
        df.insert(df.columns.get_loc("SKU ID") + 1, "产品名称", df.pop("产品名称"))

        # 记录未匹配 SKU
        unmatched = df[df["产品名称"] == "未匹配SKU"]
        if len(unmatched) > 0:
            all_unmatched.append(unmatched[["店铺", "SKU ID", "SKU后四位"]])

        # 订单状态过滤
        df = df[df["订单状态"].isin(["待确认", "已结算"])]

        # 内容形式过滤
        df["内容形式"] = df["内容形式"].astype(str).str.strip()
        df = df[df["内容形式"].isin(["视频", "商品橱窗", "直播"])]

        # 标准佣金率过滤
        df["标准佣金率"] = df["标准佣金率"].astype(str).str.strip()
        df = df[df["标准佣金率"].str.contains("%", na=False)]

        # 创建时间处理
        df["创建时间"] = pd.to_datetime(df["创建时间"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["创建时间"])
        df["创建时间"] = (
            df["创建时间"].dt.year.astype(str)
            + "/"
            + df["创建时间"].dt.month.astype(str)
            + "/"
            + df["创建时间"].dt.day.astype(str)
        )

        # 排序：按达人用户名 + 创建时间升序
        df = df.sort_values(by=["达人用户名", "创建时间", "产品名称"]).reset_index(drop=True)

        # 添加负责人列
        df = df.merge(influencer_df, on="达人用户名", how="left")
        df["负责人"] = df["负责人"].fillna("未匹配负责人")

        # 删除辅助列
        df = df.drop(columns=["SKU后四位"])

        # 保存清洗结果
        output_path = output_dir / f"cleaned_{store_name}.xlsx"
        df.to_excel(output_path, index=False)
        print(f"完成：{store_name} ({len(df)}条)")

    # 输出未匹配 SKU
    if all_unmatched:
        unmatched_df = (
            pd.concat(all_unmatched)
            .drop_duplicates()
            .sort_values(by=["店铺", "SKU后四位"])
            .reset_index(drop=True)
        )
        unmatched_path = output_dir / "unmatched_skus.xlsx"
        unmatched_df.to_excel(unmatched_path, index=False)
        print(f"\n发现 {len(unmatched_df)} 个未匹配SKU，已输出 → {unmatched_path}")
    else:
        print("\n所有SKU均已匹配")