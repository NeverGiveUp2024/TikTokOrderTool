from scripts.cleaned import run as clean_run
from scripts.merged2 import run as merge_run
import sys

if __name__ == "__main__":
    try:
        print("==========")
        print("步骤1：清洗订单")
        print("==========")
        clean_run()
    except PermissionError as e:
        print("❌ 步骤1失败：请检查是否有Excel表格正在打开，关闭后重试。")
        print(f"错误信息：{e}")
        sys.exit(1)
    except Exception as e:
        print("❌ 步骤1出现未知错误")
        print(f"错误信息：{e}")
        sys.exit(1)

    try:
        print("==========")
        print("步骤2：合并订单")
        print("==========")
        merge_run()
    except PermissionError as e:
        print("❌ 步骤2失败：请检查是否有Excel表格正在打开，关闭后重试。")
        print(f"错误信息：{e}")
        sys.exit(1)
    except Exception as e:
        print("❌ 步骤2出现未知错误")
        print(f"错误信息：{e}")
        sys.exit(1)

    print("✅ 全部完成")