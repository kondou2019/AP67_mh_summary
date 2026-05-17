#!/usr/bin/env python3
import io
import json
import subprocess
import tkinter
import tkinter as tk
from dataclasses import asdict
from logging import getLevelName
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import click
from dacite import from_dict

from dialog_reorder_pivot_table import DialogReorderPivotTable
from dialog_tag_config_verify import DialogTagConfigVerify
from src.data_model import (
    Config,
    MhTask,
    ValidationError,
    ValidationErrorBase,
    check_validation_error,
    mhtask_dict_factory,
)
from src.task_build import MhTaskBuild
from src.task_categorize import MhTaskCategorize
from src.task_sort import MhTaskSort
from src.task_utl import format_mht_list

__VERSION__ = "0.1.255"


class MainWindow:
    """!
    @brief メインウィンド
    """

    def __init__(self, *, config_path: Optional[str] = None):
        # 設定ファイルの読み込み
        if config_path is not None:
            with open(config_path, mode="r", encoding="utf-8") as f:
                json_dic = json.load(f)
            config = from_dict(data_class=Config, data=json_dic)
        else:
            config = Config()
        self.config_path_s = config_path
        self.config = config
        self.file_path_s: Optional[str] = None
        # ウィンド作成
        self.MainWindow_load()
        #
        self.mht_list: list[MhTask] = []

    def set_title(self, *, file_name: Optional[str] = None) -> None:
        if file_name is not None:
            self.root.title(f"{file_name} - mh_summary")
        else:
            self.root.title("無題 - mh_summary")
        self.file_path_s = file_name

    def update_problem_textbox(self, validation_error: list[ValidationErrorBase]) -> None:
        """!
        @brief 更新;結果出力
        """
        if len(validation_error) == 0:
            return
        #
        msg_list: list[str] = []
        for err in validation_error:
            if isinstance(err, ValidationError):
                if err.mht is not None and err.mht.location is not None:
                    # 2行出力
                    msg_list.append(f"({err.mht.location.line_no}):{err.mht.get_line()}")
                    msg_list.append(f"\t{getLevelName(err.level)}:{err.message}")
                else:
                    # 1行出力
                    msg_list.append(str(err))
            else:
                msg_list.append(str(err))
        s = "\n".join(msg_list)
        # エラー更新
        self.problem_textbox.delete("1.0", tk.END)
        self.problem_textbox.insert("1.0", s)

    def update_task_textbox(self, text: str, *, file_name: str = "") -> None:
        # logseq 対応
        task_date: Optional[str] = None
        file_path = Path(file_name)
        if file_path.suffix == ".md":
            self.logseq_var.set(True)
            # ファイル名から日付を取得。ex)2023_06_03.md
            filename = file_path.stem
            task_date = filename.replace("_", "/")
        elif len(file_path.suffix):  # その他のファイル形式
            self.logseq_var.set(False)
        # 出力エリアをクリア
        self.task_textbox.delete("1.0", tk.END)
        self.problem_textbox.delete("1.0", tk.END)
        # 読み込み
        build = MhTaskBuild()
        f = io.StringIO(text)
        mht_list = build.task_read(f, file_name=file_name, logseq=self.logseq_var.get())
        if check_validation_error(build.validation_error):
            self.update_problem_textbox(build.validation_error)
            return
        ##
        mht_list = build.task_summary(mht_list)
        if check_validation_error(build.validation_error):
            self.update_problem_textbox(build.validation_error)
            return
        ## バリデーションエラー(I,W)出力
        self.update_problem_textbox(build.validation_error)
        # タグを付与
        categorize = MhTaskCategorize(config=self.config)
        categorize.task_add_tag(mht_list)
        if check_validation_error(categorize.validation_error):
            self.update_problem_textbox(categorize.validation_error)
            return
        ## バリデーションエラー(I,W)出力
        self.update_problem_textbox(categorize.validation_error)
        self.mht_list = mht_list
        # 集計
        header = self.csv_header_var.get()
        f = io.StringIO(newline="")
        categorize.mh_task_print4(mht_list, o_stream=f, header=header, task_date=task_date)
        s = f.getvalue()
        f.close()
        # 結果出力
        self.task_textbox.insert("1.0", s)

    # ===================#
    # GUIイベント,Window #
    # ===================#
    def MainWindow_load(self):
        def create_menu():
            # メニュー
            menu = tkinter.Menu(self.root)
            ## File
            menu_file = tkinter.Menu(menu, tearoff=0)
            menu_file.add_command(label="開く(O)", command=self.on_menu_file_open_click)
            menu_file.add_command(label="再読込(R)", command=self.on_menu_file_reload_click)
            menu_file.add_command(label="開いたファイルをメモ帳で開く...", command=self.on_menu_file_notepad_open_click)
            menu_file.add_separator()
            menu_file.add_command(label="終了(E)", command=self.on_menu_file_exit_click)
            menu.add_cascade(label="ファイル(F)", menu=menu_file)
            ## Tool
            menu_tool = tkinter.Menu(menu, tearoff=0)
            menu_tool.add_command(label="ピボットテーブルの並び替え...", command=self.on_menu_tool_reorder_pivot_click)
            menu_tool.add_command(
                label="開始時間でソートの貼り付け", command=self.on_menu_tool_sort_began_time_paste_click
            )
            menu_tool.add_separator()
            menu_tool.add_command(label="tag_configの検証...", command=self.on_menu_tool_tag_config_verify_click)
            menu_tool.add_separator()
            menu_tool.add_command(label="設定ファイルを開く", command=self.on_menu_tool_open_config_click)
            menu.add_cascade(label="ツール(T)", menu=menu_tool)

            ## Debug
            menu_debug = tkinter.Menu(menu, tearoff=0)
            menu_debug.add_command(label="パース結果の貼り付け", command=self.on_menu_debug_paste_mht_list_click)
            menu_debug.add_command(label="jsonの貼り付け", command=self.on_menu_debug_paste_json_click)
            menu.add_cascade(label="デバッグ(G)", menu=menu_debug)

            ## Help
            menu_help = tkinter.Menu(menu, tearoff=0)
            menu_help.add_command(label="...について(A)", command=self.on_menu_help_about_click)
            menu.add_cascade(label="ヘルプ(H)", menu=menu_help)

            self.root.config(menu=menu)

        self.root = tk.Tk()
        self.set_title()
        self.root.geometry("576x576")

        create_menu()

        # メインフレーム
        # main_frm = ttk.Frame(self)
        # コントロール
        self.frame1 = tk.Frame(self.root)
        self.frame1.pack(fill=tk.X)
        ##
        self.search_button = tk.Button(self.frame1, text="集計", command=self.on_button_exec)
        self.search_button.pack(side=tk.LEFT)  # 設置
        self.search_button = tk.Button(self.frame1, text="結果をコピー", command=self.on_button_copy)
        self.search_button.pack(side=tk.LEFT)  # 設置
        ##
        self.logseq_var = tk.BooleanVar()
        self.logseq_checkbox = tk.Checkbutton(self.frame1, text="Logseq", variable=self.logseq_var)
        self.logseq_checkbox.pack(side=tk.LEFT)
        ##
        self.csv_header_var = tk.BooleanVar()
        self.csv_header_checkbox = tk.Checkbutton(self.frame1, text="CSVヘッダの有無", variable=self.csv_header_var)
        self.csv_header_checkbox.pack(side=tk.LEFT)
        ##
        self.panel1 = tk.PanedWindow(self.root, orient=tk.VERTICAL, showhandle=True)
        self.panel1.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        ### 集計結果
        self.frame2 = tk.Frame(self.root)
        self.frame2.pack(fill=tk.X)

        tk.Label(self.frame2, text="集計結果:", anchor=tkinter.W).pack(anchor=tk.W)

        self.task_vbar = tk.Scrollbar(self.frame2, orient=tk.VERTICAL)
        self.task_vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_textbox = tk.Text(self.frame2, height=20, yscrollcommand=self.task_vbar.set)
        self.task_textbox.pack(fill=tk.X, expand=True)

        self.task_vbar.config(command=self.task_textbox.yview)

        self.panel1.add(self.frame2)
        ### 問題
        self.frame3 = tk.Frame(self.root)
        self.frame3.pack(fill=tk.X)

        tk.Label(self.frame3, text="問題:", anchor=tkinter.W).pack(anchor=tk.W)

        self.problem_vbar = tk.Scrollbar(self.frame3, orient=tk.VERTICAL)
        self.problem_vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.problem_textbox = tk.Text(self.frame3, yscrollcommand=self.problem_vbar.set)
        self.problem_textbox.pack(fill=tk.BOTH, expand=True)

        self.problem_vbar.config(command=self.problem_textbox.yview)

        self.panel1.add(self.frame3)

    # ==================#
    # GUIイベント(menu) #
    # ==================#
    def on_menu_debug_paste_json_click(self) -> None:
        json_list = [asdict(x, dict_factory=mhtask_dict_factory) for x in self.mht_list]
        s = json.dumps(json_list, indent=2, ensure_ascii=False)
        # クリップボードに貼り付け
        self.root.clipboard_clear()
        self.root.clipboard_append(s)

    def on_menu_debug_paste_mht_list_click(self) -> None:
        s = format_mht_list(self.mht_list, output_task_time=True)
        # クリップボードに貼り付け
        self.root.clipboard_clear()
        self.root.clipboard_append(s)

    def on_menu_file_exit_click(self) -> None:
        self.root.destroy()

    def on_menu_file_open_click(self) -> None:
        file_path_s = filedialog.askopenfilename(
            title="タイトル",
            filetypes=[
                ("テキスト・Markdown", ".txt .md"),
                ("テキスト", ".txt"),
                ("Markdown", ".md"),
                ("全て", "*"),
            ],  # ファイルフィルタ
        )
        if file_path_s == "" or file_path_s == ():
            return
        file_path = Path(file_path_s)
        # 読み込み
        with open(file_path_s, mode="r", encoding="utf-8") as f:
            text = f.read()
        #
        self.update_task_textbox(text, file_name=file_path_s)
        self.set_title(file_name=file_path_s)

    def on_menu_file_reload_click(self) -> None:
        if self.file_path_s is None:
            return
        # 読み込み
        with open(self.file_path_s, mode="r", encoding="utf-8") as f:
            text = f.read()
        #
        self.update_task_textbox(text, file_name=self.file_path_s)

    def on_menu_file_notepad_open_click(self) -> None:
        if self.file_path_s is None:
            return
        #
        subprocess.Popen(["notepad", self.file_path_s])

    def on_menu_help_about_click(self) -> None:
        messagebox.showinfo("バージョン情報", f"mh_summary {__VERSION__}")

    def on_menu_tool_open_config_click(self) -> None:
        subprocess.Popen(["notepad", self.config_path_s])

    def on_menu_tool_reorder_pivot_click(self) -> None:
        DialogReorderPivotTable.show_dialog(self.root)

    def on_menu_tool_sort_began_time_paste_click(self) -> None:
        if self.mht_list is None:
            return
        ts = MhTaskSort()
        sort_mht_list = ts.sort_began_time(self.mht_list)
        s = ts.format_began_time(sort_mht_list)
        # クリップボードに出力
        self.root.clipboard_clear()
        self.root.clipboard_append(s)

    def on_menu_tool_tag_config_verify_click(self) -> None:
        DialogTagConfigVerify.show_dialog(self.root)

    # ====================#
    # GUIイベント(button) #
    # ====================#
    def on_button_copy(self) -> None:
        s = self.task_textbox.get("1.0", tk.END)
        # クリップボードに出力
        self.root.clipboard_clear()
        self.root.clipboard_append(s)

    def on_button_exec(self) -> None:
        # クリップボードから取得
        text = self.root.clipboard_get()
        #
        self.update_task_textbox(text)
        self.set_title()


@click.command(help="工数集計ツール")
@click.version_option(version=__VERSION__)
@click.option("--config", type=click.Path(), help="設定ファイル")
def main_cli(config: Optional[str]) -> None:
    # ウィンドの表示
    win = MainWindow(config_path=config)
    win.root.mainloop()


if __name__ == "__main__":
    main_cli()
