import tkinter
import tkinter as tk

from reorder_pivot_table import ReorderPivotTable
from src.data_model import (
    Config,
    ValidationError,
    ValidationErrorBase,
    check_validation_error,
)


class DialogReorderPivotTable:
    """!
    @brief ピボットテーブルの結果を並び替える
    """

    @classmethod
    def show_dialog(cls, parent, *, config: Config = None):
        dlg_modal = DialogReorderPivotTable(parent=parent, config=config)
        # モーダルにする設定
        dlg_modal.root.transient(parent)  # タスクバーに表示しない
        dlg_modal.root.focus_set()  # フォーカスを新しいウィンドウをへ移す
        dlg_modal.root.grab_set()  # モーダルにする
        # ダイアログが閉じられるまで待つ
        parent.wait_window(dlg_modal.root)
        return

    def __init__(self, *, parent, config: Config = None):
        self.root = tk.Toplevel(parent)
        self.config = config
        self.MainWindow_load()

    def update_result_textbox(self, validation_error: list[ValidationErrorBase]) -> None:
        """!
        @brief 更新;結果出力
        """
        if len(validation_error) == 0:
            return
        #
        msg_list: list[str] = []
        for err in validation_error:
            if isinstance(err, ValidationError):
                msg_list.append(str(err))
            else:
                msg_list.append(str(err))
        s = "\n".join(msg_list)
        # エラー更新
        self.result_textbox.delete("1.0", tk.END)
        self.result_textbox.insert(tk.END, s)
        self.result_textbox.insert(tk.END, "\n")

    # ===================#
    # GUIイベント,Window #
    # ===================#
    def MainWindow_load(self):
        self.root.title("ピボットテーブルの並び替え")
        self.root.geometry("512x576")
        # メインフレーム
        # main_frm = ttk.Frame(self)
        # コントロール
        ##
        self.frame1 = tk.Frame(self.root)
        self.frame1.pack(fill=tk.X)

        tk.Button(self.frame1, text="並び替え", command=self.on_button_reorder).pack(side=tk.LEFT)
        tk.Button(self.frame1, text="全クリア", command=self.on_button_clear_all).pack(side=tk.LEFT)
        ##
        self.panel1 = tk.PanedWindow(self.root, orient=tk.VERTICAL, showhandle=True, sashwidth=8)
        self.panel1.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        ### チケットのURL
        self.frame2 = tk.Frame(self.root)
        self.frame2.pack(fill=tk.X)

        self.frame21 = tk.Frame(self.frame2)
        self.frame21.pack(fill=tk.X)

        tk.Label(self.frame21, text="チケットのURL:").pack(side=tk.LEFT)
        tk.Button(self.frame21, text="クリア", command=self.on_button_ticket_url_clear).pack(side=tk.LEFT)

        self.ticket_url_vbar = tk.Scrollbar(self.frame2, orient=tk.VERTICAL)
        self.ticket_url_vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ticket_url_textbox = tk.Text(self.frame2, height=10, yscrollcommand=self.ticket_url_vbar.set)
        self.ticket_url_textbox.pack(fill=tk.BOTH, expand=True)
        self.panel1.add(self.frame2)
        ### ピボットテーブル
        self.frame3 = tk.Frame(self.root)
        self.frame3.pack(fill=tk.X)

        tk.Label(self.frame3, text="ピボットテーブル:").pack(anchor=tk.W)
        self.pivot_table_vbar = tk.Scrollbar(self.frame3, orient=tk.VERTICAL)
        self.pivot_table_vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pivot_table_textbox = tk.Text(self.frame3, height=10, yscrollcommand=self.pivot_table_vbar.set)
        self.pivot_table_textbox.pack(fill=tk.BOTH, expand=True)
        self.panel1.add(self.frame3)
        ### 問題
        self.frame4 = tk.Frame(self.root)
        self.frame4.pack(fill=tk.X)

        tk.Label(self.frame4, text="実行結果:", anchor=tkinter.W).pack(anchor=tk.W)

        self.result_vbar = tk.Scrollbar(self.frame4, orient=tk.VERTICAL)
        self.result_vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_textbox = tk.Text(self.frame4, yscrollcommand=self.result_vbar.set)
        self.result_textbox.pack(fill=tk.BOTH, expand=True)

        self.result_vbar.config(command=self.result_textbox.yview)

        self.panel1.add(self.frame4)

    # ====================#
    # GUIイベント(button) #
    # ====================#
    def on_button_clear_all(self) -> None:
        self.ticket_url_textbox.delete("1.0", tk.END)
        self.pivot_table_textbox.delete("1.0", tk.END)
        self.result_textbox.delete("1.0", tk.END)

    def on_button_reorder(self) -> None:
        # 実行結果をクリア
        self.result_textbox.delete("1.0", tk.END)
        # uiが取得
        ticket_url_text = self.ticket_url_textbox.get("1.0", tk.END)
        pivot_table_text = self.pivot_table_textbox.get("1.0", tk.END)
        # 並び替え
        pivot_table = ReorderPivotTable(config=self.config)
        s = pivot_table.reorder_pivot_table(ticket_url_text, pivot_table_text)
        if check_validation_error(pivot_table.validation_error):
            self.update_result_textbox(pivot_table.validation_error)
            return
        ## バリデーションエラー(I,W)出力
        self.update_result_textbox(pivot_table.validation_error)
        # 結果をクリップボードにコピー
        # クリップボードに出力
        self.root.clipboard_clear()
        self.root.clipboard_append(s)
        #
        self.result_textbox.insert(tk.END, "結果をクリップボードにコピーしました。\n")

    def on_button_ticket_url_clear(self) -> None:
        self.ticket_url_textbox.delete("1.0", tk.END)
