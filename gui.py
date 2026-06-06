import PySimpleGUI as sg
import subprocess
import os
import sys
from pathlib import Path

from scripts.cleaned import run as clean_run
from scripts.merged2 import run as merge_run

# ==========================================
# 默认路径
# ==========================================

DEFAULT_ORDERS = "data/orders"
DEFAULT_SKU = "data/sku_mapping.xlsx"
DEFAULT_INFLUENCER = "data/influencer_mapping.xlsx"

DEFAULT_CLEANED = "cleaned_orders"
DEFAULT_MERGED = "merged_orders"

# ==========================================
# GUI主题
# ==========================================

sg.theme("LightBlue2")

# ==========================================
# 界面布局
# ==========================================

layout = [

    [
        sg.Text(
            "达人订单统计工具 v1.0",
            font=("Microsoft YaHei", 18, "bold")
        )
    ],

    [sg.HorizontalSeparator()],

    [
        sg.Text("TK订单目录", size=(15, 1)),
        sg.Input(
            DEFAULT_ORDERS,
            key="orders_folder",
            size=(50, 1)
        ),
        sg.FolderBrowse("选择")
    ],

    [
        sg.Text("SKU映射表", size=(15, 1)),
        sg.Input(
            DEFAULT_SKU,
            key="sku_file",
            size=(50, 1)
        ),
        sg.FileBrowse("选择")
    ],

    [
        sg.Text("达人负责人表", size=(15, 1)),
        sg.Input(
            DEFAULT_INFLUENCER,
            key="influencer_file",
            size=(50, 1)
        ),
        sg.FileBrowse("选择")
    ],

    [sg.HorizontalSeparator()],

    [
        sg.Text("清洗结果目录", size=(15, 1)),
        sg.Input(
            DEFAULT_CLEANED,
            key="cleaned_folder",
            size=(50, 1)
        ),
        sg.FolderBrowse("选择")
    ],

    [
        sg.Text("合并结果目录", size=(15, 1)),
        sg.Input(
            DEFAULT_MERGED,
            key="merged_folder",
            size=(50, 1)
        ),
        sg.FolderBrowse("选择")
    ],

    [sg.HorizontalSeparator()],

    [
        sg.Button(
            "开始处理订单",
            size=(18, 1),
            key="run"
        ),

        sg.Button(
            "打开清洗目录",
            size=(18, 1),
            key="open_cleaned"
        ),

        sg.Button(
            "打开合并目录",
            size=(18, 1),
            key="open_merged"
        )
    ],

    [
        sg.ProgressBar(
            max_value=100,
            orientation="h",
            size=(60, 20),
            key="progress"
        )
    ],

    [
        sg.Multiline(
            size=(100, 20),
            key="log",
            autoscroll=True,
            expand_x=True,
            expand_y=True
        )
    ]
]

window = sg.Window(
    "达人订单统计工具",
    layout,
    size=(900, 700),
    finalize=True
)

# ==========================================
# 日志函数
# ==========================================

def log(msg):
    window["log"].print(msg)

# ==========================================
# 打开目录
# ==========================================

def open_folder(folder):

    if not os.path.exists(folder):
        sg.popup_error(
            "目录不存在",
            folder
        )
        return

    if sys.platform == "win32":
        os.startfile(folder)
    else:
        subprocess.Popen(["open", folder])

# ==========================================
# 主处理函数
# ==========================================

def run_processing(values):

    try:

        window["run"].update(disabled=True)

        log("=" * 50)
        log("开始执行订单处理")
        log("=" * 50)

        # ----------------------------------
        # 设置环境变量
        # ----------------------------------

        os.environ["ORDERS_DIR"] = values["orders_folder"]

        os.environ["SKU_FILE"] = values["sku_file"]

        os.environ["INFLUENCER_FILE"] = values["influencer_file"]

        os.environ["CLEANED_DIR"] = values["cleaned_folder"]

        os.environ["MERGED_DIR"] = values["merged_folder"]

        # ----------------------------------
        # 清洗订单
        # ----------------------------------

        log("正在清洗订单...")

        window["progress"].update(20)

        clean_run()

        window["progress"].update(60)

        log("订单清洗完成")

        # ----------------------------------
        # 合并订单
        # ----------------------------------

        log("正在合并订单...")

        merge_run()

        window["progress"].update(100)

        log("订单合并完成")

        # ----------------------------------
        # 统计文件数
        # ----------------------------------

        cleaned_count = len(
            list(
                Path(values["cleaned_folder"]).glob("*.xlsx")
            )
        )

        merged_count = len(
            list(
                Path(values["merged_folder"]).glob("*.xlsx")
            )
        )

        log("")
        log(f"清洗文件：{cleaned_count} 个")
        log(f"合并文件：{merged_count} 个")
        log("")
        log("全部处理完成")

        sg.popup(
            "处理完成",
            f"清洗文件：{cleaned_count} 个\n"
            f"合并文件：{merged_count} 个"
        )

    except PermissionError:

        sg.popup_error(
            "Excel文件被占用",
            "请关闭所有Excel后重新运行"
        )

        log("错误：Excel文件被占用")

    except Exception as e:

        sg.popup_error(
            "运行失败",
            str(e)
        )

        log(f"错误：{e}")

    finally:

        window["run"].update(disabled=False)

        window["progress"].update(0)

# ==========================================
# 事件循环
# ==========================================

while True:

    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "run":
        run_processing(values)

    elif event == "open_cleaned":
        open_folder(values["cleaned_folder"])

    elif event == "open_merged":
        open_folder(values["merged_folder"])

window.close()