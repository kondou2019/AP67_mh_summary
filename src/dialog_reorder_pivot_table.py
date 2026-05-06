import tkinter
import tkinter as tk

from reorder_pivot_table import reorder_pivot_table


class DialogReorderPivotTable:
    """!
    @brief ピボットテーブルの結果を並び替える
    """

    @classmethod
    def show_dialog(cls, parent):
        dlg_modal = DialogReorderPivotTable(parent=parent)
        # モーダルにする設定
        dlg_modal.root.transient(parent)  # タスクバーに表示しない
        dlg_modal.root.focus_set()  # フォーカスを新しいウィンドウをへ移す
        dlg_modal.root.grab_set()  # モーダルにする
        # ダイアログが閉じられるまで待つ
        parent.wait_window(dlg_modal.root)
        return

    def __init__(self, *, parent):
        self.root = tk.Toplevel(parent)
        self.MainWindow_load()

    # ===================#
    # GUIイベント,Window #
    # ===================#
    def MainWindow_load(self):
        self.root.title("ピボットテーブルの並び替え")
        self.root.geometry("512x512")
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

        tk.Label(self.frame2, text="チケットのURL:", anchor=tkinter.W).pack(anchor=tk.W)
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
        self.pivot_table_textbox = tk.Text(self.frame3, yscrollcommand=self.pivot_table_vbar.set)
        self.pivot_table_textbox.pack(fill=tk.BOTH, expand=True)
        self.panel1.add(self.frame3)

    # ====================#
    # GUIイベント(button) #
    # ====================#
    def on_button_clear_all(self) -> None:
        self.ticket_url_textbox.delete("1.0", tk.END)
        self.pivot_table_textbox.delete("1.0", tk.END)

    def on_button_reorder(self) -> None:
        ticket_url_text = self.ticket_url_textbox.get("1.0", tk.END)
        pivot_table_text = self.pivot_table_textbox.get("1.0", tk.END)
        # 並び替え
        s = reorder_pivot_table(ticket_url_text, pivot_table_text)
        # 結果をクリップボードにコピー
        # クリップボードに出力
        self.root.clipboard_clear()
        self.root.clipboard_append(s)
