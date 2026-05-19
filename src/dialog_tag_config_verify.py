import io
import tkinter
import tkinter as tk

from src.common import json_escape_of_string, json_unescape_of_string
from src.data_model import (
    MhTask,
    TagEntry,
)
from src.task_categorize import MhTaskCategorize


class DialogTagConfigVerify:

    @classmethod
    def show_dialog(cls, parent):
        dlg_modal = DialogTagConfigVerify(parent=parent)
        # モーダルにする設定
        dlg_modal.root.transient(parent)  # タスクバーに表示しない
        dlg_modal.root.focus_set()  # フォーカスを新しいウィンドウをへ移す
        dlg_modal.root.grab_set()  # モーダルにする
        # ダイアログが閉じられるまで待つ
        parent.wait_window(dlg_modal.root)
        return

    """!
    @brief tag_configの検証
    """

    def __init__(self, *, parent):
        self.root = tk.Toplevel(parent)
        self.MainWindow_load()

    # ===================#
    # GUIイベント,Window #
    # ===================#
    def MainWindow_load(self):
        self.root.title("tag_configの検証")
        self.root.geometry("576x512")
        # メインフレーム
        # main_frm = ttk.Frame(self)
        # コントロール
        ##
        self.frame1 = tk.Frame(self.root)
        tk.Button(self.frame1, text="実行", command=self.on_button_execute).pack(side=tk.LEFT)
        tk.Button(self.frame1, text="全クリア", command=self.on_button_clear_all).pack(side=tk.LEFT)
        ## サンプル
        self.frame2 = tk.Frame(self.root)
        tk.Label(self.frame2, text="サンプル:").pack(anchor=tkinter.W)
        self.sample_textbox = tk.Entry(self.frame2, width=30)
        self.sample_textbox.pack(anchor=tkinter.W, fill=tk.X, expand=True)
        ## match_re
        self.frame3 = tk.Frame(self.root)
        tk.Label(self.frame3, text="match_re:", anchor=tkinter.W).pack(anchor=tkinter.W)
        self.match_re_textbox = tk.Entry(self.frame3, width=40)
        self.match_re_textbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(self.frame3, text="esc", command=self.on_button_match_re_escape).pack(side=tk.LEFT)
        tk.Button(self.frame3, text="une", command=self.on_button_match_re_unescape).pack(side=tk.LEFT)
        ## 識別子;identifier_require_dict
        self.frame4 = tk.Frame(self.root)
        ###
        self.frame41 = tk.Frame(self.frame4)
        self.frame41.pack(fill=tk.X)
        tk.Label(self.frame41, text="identifier_require_dict:").pack(side=tk.LEFT)
        ###
        self.frame42 = tk.Frame(self.frame4)
        self.frame42.pack(fill=tk.X)

        tk.Label(self.frame42, text="k:").grid(column=0, row=0)
        self.identifier_require_dict_k1_textbox = tk.Entry(self.frame42)
        self.identifier_require_dict_k1_textbox.grid(column=1, row=0)
        tk.Label(self.frame42, text="v_re:").grid(column=2, row=0)
        self.identifier_require_dict_v1_textbox = tk.Entry(self.frame42)
        self.identifier_require_dict_v1_textbox.grid(column=3, row=0)
        tk.Button(self.frame42, text="esc", command=self.on_button_identifier_require_dict_v1_escape).grid(column=4, row=0)
        tk.Button(self.frame42, text="une", command=self.on_button_identifier_require_dict_v1_unescape).grid(column=5, row=0)

        tk.Label(self.frame42, text="k:").grid(column=0, row=1)
        self.identifier_require_dict_k2_textbox = tk.Entry(self.frame42)
        self.identifier_require_dict_k2_textbox.grid(column=1, row=1, sticky=tk.NSEW)
        tk.Label(self.frame42, text="v_re:").grid(column=2, row=1)
        self.identifier_require_dict_v2_textbox = tk.Entry(self.frame42)
        self.identifier_require_dict_v2_textbox.grid(column=3, row=1)
        tk.Button(self.frame42, text="esc", command=self.on_button_identifier_require_dict_v2_escape).grid(column=4, row=1)
        tk.Button(self.frame42, text="une", command=self.on_button_identifier_require_dict_v2_unescape).grid(column=5, row=1)
        ## 識別子;identifier_dict
        self.frame5 = tk.Frame(self.root)
        ###
        self.frame51 = tk.Frame(self.frame5)
        self.frame51.pack(fill=tk.X)
        tk.Label(self.frame51, text="identifier_dict:").pack(side=tk.LEFT)
        ###
        self.frame52 = tk.Frame(self.frame5)
        self.frame52.pack(fill=tk.X)

        tk.Label(self.frame52, text="k:").grid(column=0, row=0)
        self.identifier_dict_k1_textbox = tk.Entry(self.frame52)
        self.identifier_dict_k1_textbox.grid(column=1, row=0)
        tk.Label(self.frame52, text="v_re:").grid(column=2, row=0)
        self.identifier_dict_v1_textbox = tk.Entry(self.frame52)
        self.identifier_dict_v1_textbox.grid(column=3, row=0)
        tk.Button(self.frame52, text="esc", command=self.on_button_identifier_dict_v1_escape).grid(column=4, row=0)
        tk.Button(self.frame52, text="une", command=self.on_button_identifier_dict_v1_unescape).grid(column=5, row=0)

        tk.Label(self.frame52, text="k:").grid(column=0, row=1)
        self.identifier_dict_k2_textbox = tk.Entry(self.frame52)
        self.identifier_dict_k2_textbox.grid(column=1, row=1, sticky=tk.NSEW)
        tk.Label(self.frame52, text="v_re:").grid(column=2, row=1)
        self.identifier_dict_v2_textbox = tk.Entry(self.frame52)
        self.identifier_dict_v2_textbox.grid(column=3, row=1)
        tk.Button(self.frame52, text="esc", command=self.on_button_identifier_dict_v2_escape).grid(column=4, row=1)
        tk.Button(self.frame52, text="une", command=self.on_button_identifier_dict_v2_unescape).grid(column=5, row=1)
        ## 実行結果
        self.frame6 = tk.Frame(self.root)
        tk.Label(self.frame6, text="実行結果:").pack(anchor=tk.W)
        ###
        self.result_vbar = tk.Scrollbar(self.frame6, orient=tk.VERTICAL)
        self.result_vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_textbox = tk.Text(self.frame6, yscrollcommand=self.result_vbar.set)
        self.result_textbox.pack(fill=tk.BOTH, expand=True)
        #
        self.frame1.pack(side=tk.TOP, fill=tk.X)
        self.frame2.pack(fill=tk.X)
        self.frame3.pack(fill=tk.X)
        self.frame4.pack(fill=tk.X)
        self.frame5.pack(fill=tk.X)
        self.frame6.pack(fill=tk.X)

    # ====================#
    # GUIイベント(button) #
    # ====================#
    def on_button_clear_all(self) -> None:
        self.sample_textbox.delete(0, tkinter.END)
        self.match_re_textbox.delete(0, tkinter.END)
        self.identifier_require_dict_k1_textbox.delete(0, tkinter.END)
        self.identifier_require_dict_v1_textbox.delete(0, tkinter.END)
        self.identifier_require_dict_k2_textbox.delete(0, tkinter.END)
        self.identifier_require_dict_v2_textbox.delete(0, tkinter.END)
        self.identifier_dict_k1_textbox.delete(0, tkinter.END)
        self.identifier_dict_v1_textbox.delete(0, tkinter.END)
        self.identifier_dict_k2_textbox.delete(0, tkinter.END)
        self.identifier_dict_v2_textbox.delete(0, tkinter.END)

        self.result_textbox.delete("1.0", tk.END)

    def on_button_execute(self) -> None:
        sample_text = self.sample_textbox.get()
        match_re_text = self.match_re_textbox.get()
        identifier_require_dict_k1_text = self.identifier_require_dict_k1_textbox.get()
        identifier_require_dict_v1_text = self.identifier_require_dict_v1_textbox.get()
        identifier_require_dict_k2_text = self.identifier_require_dict_k2_textbox.get()
        identifier_require_dict_v2_text = self.identifier_require_dict_v2_textbox.get()
        identifier_dict_k1_text = self.identifier_dict_k1_textbox.get()
        identifier_dict_v1_text = self.identifier_dict_v1_textbox.get()
        identifier_dict_k2_text = self.identifier_dict_k2_textbox.get()
        identifier_dict_v2_text = self.identifier_dict_v2_textbox.get()

        self.result_textbox.delete("1.0", tk.END)
        # 実行
        ## MhTask作成
        mht = MhTask()
        mht.line_text = sample_text

        ## TagEntry作成
        te = TagEntry()
        te.task_type = "sample"
        te.match_re = match_re_text
        te.identifier_dict = {}
        if identifier_require_dict_k1_text != "" and identifier_require_dict_v1_text != "":
            te.identifier_dict[identifier_require_dict_k1_text] = identifier_require_dict_v1_text
        if identifier_require_dict_k2_text != "" and identifier_require_dict_v2_text != "":
            te.identifier_dict[identifier_require_dict_k2_text] = identifier_require_dict_v2_text
        if identifier_dict_k1_text != "" and identifier_dict_v1_text != "":
            te.identifier_dict[identifier_dict_k1_text] = identifier_dict_v1_text
        if identifier_dict_k2_text != "" and identifier_dict_v2_text != "":
            te.identifier_dict[identifier_dict_k2_text] = identifier_dict_v2_text

        ## 実行
        categorize = MhTaskCategorize()
        result = categorize._tag_add_local(mht, te)

        # 結果出力
        with io.StringIO(newline="") as f:
            f.write(f"_tag_add_local():result={result}\n")
            f.write("==identifier_dict==\n")
            # 識別子辞書の解析結果
            for k, v in categorize.debug_identifier_dict.items():
                f.write(f"{k}={v}\n")
            # validationエラー
            f.write("==validation error==\n")
            if len(categorize.validation_error) > 0:
                msg_list: list[str] = []
                for err in categorize.validation_error:
                    msg_list.append(str(err))
                s = "\n".join(msg_list)
                f.write(s)
            # 内容の取得
            s = f.getvalue()

        self.result_textbox.insert("1.0", s)
        # 結果をクリップボードにコピー
        # クリップボードに出力
        # self.root.clipboard_clear()
        # self.root.clipboard_append(s)
        pass

    def on_button_identifier_require_dict_v1_escape(self) -> None:
        # 変換
        s = self.identifier_require_dict_v1_textbox.get()
        s = json_escape_of_string(s)
        # 更新
        self.identifier_require_dict_v1_textbox.delete(0, tkinter.END)
        self.identifier_require_dict_v1_textbox.insert(tkinter.END, s)

    def on_button_identifier_require_dict_v1_unescape(self) -> None:
        # 変換
        s = self.identifier_require_dict_v1_textbox.get()
        s = json_unescape_of_string(s)
        # 更新
        self.identifier_require_dict_v1_textbox.delete(0, tkinter.END)
        self.identifier_require_dict_v1_textbox.insert(tkinter.END, s)

    def on_button_identifier_require_dict_v2_escape(self) -> None:
        # 変換
        s = self.identifier_require_dict_v2_textbox.get()
        s = json_escape_of_string(s)
        # 更新
        self.identifier_require_dict_v2_textbox.delete(0, tkinter.END)
        self.identifier_require_dict_v2_textbox.insert(tkinter.END, s)

    def on_button_identifier_require_dict_v2_unescape(self) -> None:
        # 変換
        s = self.identifier_require_dict_v2_textbox.get()
        s = json_unescape_of_string(s)
        # 更新
        self.identifier_require_dict_v2_textbox.delete(0, tkinter.END)
        self.identifier_require_dict_v2_textbox.insert(tkinter.END, s)

    def on_button_identifier_dict_v1_escape(self) -> None:
        # 変換
        s = self.identifier_dict_v1_textbox.get()
        s = json_escape_of_string(s)
        # 更新
        self.identifier_dict_v1_textbox.delete(0, tkinter.END)
        self.identifier_dict_v1_textbox.insert(tkinter.END, s)

    def on_button_identifier_dict_v1_unescape(self) -> None:
        # 変換
        s = self.identifier_dict_v1_textbox.get()
        s = json_unescape_of_string(s)
        # 更新
        self.identifier_dict_v1_textbox.delete(0, tkinter.END)
        self.identifier_dict_v1_textbox.insert(tkinter.END, s)

    def on_button_identifier_dict_v2_escape(self) -> None:
        # 変換
        s = self.identifier_dict_v2_textbox.get()
        s = json_escape_of_string(s)
        # 更新
        self.identifier_dict_v2_textbox.delete(0, tkinter.END)
        self.identifier_dict_v2_textbox.insert(tkinter.END, s)

    def on_button_identifier_dict_v2_unescape(self) -> None:
        # 変換
        s = self.identifier_dict_v2_textbox.get()
        s = json_unescape_of_string(s)
        # 更新
        self.identifier_dict_v2_textbox.delete(0, tkinter.END)
        self.identifier_dict_v2_textbox.insert(tkinter.END, s)

    def on_button_match_re_escape(self) -> None:
        # 変換
        match_re_text = self.match_re_textbox.get()
        s = json_escape_of_string(match_re_text)
        # 更新
        self.match_re_textbox.delete(0, tkinter.END)
        self.match_re_textbox.insert(tkinter.END, s)

    def on_button_match_re_unescape(self) -> None:
        # 変換
        match_re_text = self.match_re_textbox.get()
        s = json_unescape_of_string(match_re_text)
        # 更新
        self.match_re_textbox.delete(0, tkinter.END)
        self.match_re_textbox.insert(tkinter.END, s)
