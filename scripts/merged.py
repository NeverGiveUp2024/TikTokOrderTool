# scripts/merged.py

def run():
    import pandas as pd
    from pathlib import Path

    # ======================================
    # 配置
    # ======================================
    cleaned_dir = Path("cleaned_orders")
    merged_dir = Path("merged_orders")
    merged_dir.mkdir(exist_ok=True)

    # ======================================
    # 遍历所有清洗后的订单
    # ======================================
    for file in cleaned_dir.glob("cleaned_*.xlsx"):

        print(f"处理：{file.name}")

        df = pd.read_excel(file)

        required_columns = [
            '达人用户名',
            '创建时间',
            '产品名称',
            '下单件数'
        ]

        if not all(col in df.columns for col in required_columns):
            print(f"跳过文件：{file.name}")
            continue

        # ======================================
        # 分组汇总
        # ======================================
        grouped = (
            df.groupby(
                ['达人用户名', '创建时间', '产品名称'],
                as_index=False
            )
            .agg({
                '下单件数': 'sum',
                'SKU ID': 'first',
                '标准佣金率': 'first',
                '店铺': 'first',
                '内容形式': 'first',
                '订单状态': 'first',
                '负责人': 'first'
            })
        )

        # ======================================
        # 字段顺序
        # ======================================
        grouped = grouped[
            [
                '达人用户名',
                '创建时间',
                '下单件数',
                'SKU ID',
                '产品名称',
                '标准佣金率',
                '店铺',
                '内容形式',
                '订单状态',
                '负责人'
            ]
        ]

        # ======================================
        # 排序
        # ======================================
        grouped = grouped.sort_values(
            by=['达人用户名', '创建时间', '产品名称']
        )

        # ======================================
        # 文件命名
        # cleaned_跨7.xlsx -> merged_跨7.xlsx
        # ======================================
        store_name = file.stem.replace("cleaned_", "")
        output_file = merged_dir / f"merged_{store_name}.xlsx"

        grouped.to_excel(output_file, index=False)
        print(f"完成 -> {output_file}")

    print("\n全部合并完成")