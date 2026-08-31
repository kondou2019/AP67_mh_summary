import io
import tkinter
import tkinter as tk
from typing import Self


class DialogOpenFileRange:

    @classmethod
    def create(cls, parent) -> Self:
        dlg_modal = DialogOpenFileRange(parent=parent)
        # モーダルにする設定
        dlg_modal.root.transient(parent)  # タスクバーに表示しない
        dlg_modal.root.focus_set()  # フォーカスを新しいウィンドウをへ移す
        dlg_modal.root.grab_set()  # モーダルにする
        return dlg_modal

    """!
    @brief tag_configの検証
    """

    def __init__(self, *, parent):
        self.result = False
        self.m_directory: str = ""
        self.m_start_filename: str = ""
        self.m_ended_filename: str = ""
        #
        self.root = tk.Toplevel(parent)
        self.MainWindow_load()

    def show_dialog(self, parent) -> bool:
        # コントロールの初期化
        self.directory_textbox.delete(0, tkinter.END)
        self.directory_textbox.insert(tkinter.END, self.m_directory)  # 末尾に追加
        self.start_filename_textbox.delete(0, tkinter.END)
        self.start_filename_textbox.insert(tkinter.END, self.m_start_filename)  # 末尾に追加
        self.ended_filename_textbox.delete(0, tkinter.END)
        self.ended_filename_textbox.insert(tkinter.END, self.m_ended_filename)  # 末尾に追加
        # ダイアログが閉じられるまで待つ
        parent.wait_window(self.root)
        return self.result

    # ===================#
    # GUIイベント,Window #
    # ===================#
    def MainWindow_load(self):
        self.root.title("ファイル範囲選択")
        self.root.geometry("576x128")
        # メインフレーム
        # main_frm = ttk.Frame(self)
        # コントロール
        ##
        self.frame1 = tk.Frame(self.root)
        tk.Button(self.frame1, text="OK", command=self.on_button_ok).pack(side=tk.LEFT)
        tk.Button(self.frame1, text="キャンセル", command=self.on_button_cancel).pack(side=tk.LEFT)
        ##
        self.frame2 = tk.Frame(self.root)
        tk.Label(self.frame2, text="ディレクトリ:").pack(anchor=tkinter.W)
        self.directory_textbox = tk.Entry(self.frame2, width=30)
        self.directory_textbox.pack(anchor=tkinter.W, fill=tk.X, expand=True)
        ##
        self.frame3 = tk.Frame(self.root)
        tk.Label(self.frame3, text="開始ファイル:").grid(column=0, row=0)
        self.start_filename_textbox = tk.Entry(self.frame3)
        self.start_filename_textbox.grid(column=1, row=0)
        tk.Label(self.frame3, text="終了ファイル:").grid(column=2, row=0)
        self.ended_filename_textbox = tk.Entry(self.frame3)
        self.ended_filename_textbox.grid(column=3, row=0)
        #
        self.frame1.pack(side=tk.TOP, fill=tk.X)
        self.frame2.pack(fill=tk.X)
        self.frame3.pack(fill=tk.X)

    # ====================#
    # GUIイベント(button) #
    # ====================#
    def on_button_cancel(self) -> None:
        self.root.destroy()

    def on_button_ok(self) -> None:
        self.m_directory = self.directory_textbox.get()
        self.m_start_filename = self.start_filename_textbox.get()
        self.m_ended_filename = self.ended_filename_textbox.get()
        # 実行
        self.result = True
        self.root.destroy()
