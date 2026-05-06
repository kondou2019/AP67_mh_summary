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
        tk.Button(self.frame1, text="実行", command=self.on_button_execute).grid(column=0, row=0)
        tk.Button(self.frame1, text="全クリア", command=self.on_button_clear_all).grid(column=1, row=0)
        ##
        self.frame2 = tk.Frame(self.root)
        tk.Label(self.frame2, text="サンプル:", anchor=tkinter.W).grid(column=0, row=0, sticky=tk.EW)
        self.sample_textbox = tk.Entry(self.frame2, width=30)
        self.sample_textbox.grid(column=0, row=1, sticky=tk.NSEW)
        ##
        self.frame3 = tk.Frame(self.root)
        tk.Label(self.frame3, text="match_re:", anchor=tkinter.W).grid(column=0, row=0, sticky=tk.EW)
        self.match_re_textbox = tk.Entry(self.frame3, width=40)
        self.match_re_textbox.grid(column=0, row=1, sticky=tk.NSEW)
        tk.Button(self.frame3, text="esc", command=self.on_button_match_re_escape).grid(column=1, row=1)
        tk.Button(self.frame3, text="une", command=self.on_button_match_re_unescape).grid(column=2, row=1)
        ## 識別子
        self.frame4 = tk.Frame(self.root)
        tk.Label(self.frame4, text="identifier_dict:", anchor=tkinter.W).grid(column=0, row=0, sticky=tk.EW)

        tk.Label(self.frame4, text="k:", anchor=tkinter.W).grid(column=0, row=1, sticky=tk.EW)
        self.identifier_dict_k1_textbox = tk.Entry(self.frame4)
        self.identifier_dict_k1_textbox.grid(column=1, row=1, sticky=tk.NSEW)
        tk.Label(self.frame4, text="v_re:", anchor=tkinter.W).grid(column=2, row=1, sticky=tk.EW)
        self.identifier_dict_v1_textbox = tk.Entry(self.frame4)
        self.identifier_dict_v1_textbox.grid(column=3, row=1, sticky=tk.NSEW)
        tk.Button(self.frame4, text="esc", command=self.on_button_identifier_dict_v1_escape).grid(column=4, row=1)
        tk.Button(self.frame4, text="une", command=self.on_button_identifier_dict_v1_unescape).grid(column=5, row=1)

        tk.Label(self.frame4, text="k:", anchor=tkinter.W).grid(column=0, row=2, sticky=tk.EW)
        self.identifier_dict_k2_textbox = tk.Entry(self.frame4)
        self.identifier_dict_k2_textbox.grid(column=1, row=2, sticky=tk.NSEW)
        tk.Label(self.frame4, text="v_re:", anchor=tkinter.W).grid(column=2, row=2, sticky=tk.EW)
        self.identifier_dict_v2_textbox = tk.Entry(self.frame4)
        self.identifier_dict_v2_textbox.grid(column=3, row=2, sticky=tk.NSEW)
        tk.Button(self.frame4, text="esc", command=self.on_button_identifier_dict_v2_escape).grid(column=4, row=2)
        tk.Button(self.frame4, text="une", command=self.on_button_identifier_dict_v2_unescape).grid(column=5, row=2)
        ##
        self.frame5 = tk.Frame(self.root)
        tk.Label(self.frame5, text="実行結果:", anchor=tkinter.W).grid(column=0, row=0, sticky=tk.EW)
        self.result_textbox = tk.Text(self.frame5)
        self.result_textbox.grid(column=0, row=1, sticky=tk.NSEW)
        #
        self.frame1.pack(side=tk.TOP)
        self.frame2.pack(expand=True, fill=tk.X)
        self.frame3.pack(expand=True, fill=tk.X)
        self.frame4.pack(expand=True, fill=tk.X)
        self.frame5.pack(expand=True, fill=tk.X)

    # ====================#
    # GUIイベント(button) #
    # ====================#
    def on_button_clear_all(self) -> None:
        self.sample_textbox.delete(0, tkinter.END)
        self.match_re_textbox.delete(0, tkinter.END)
        self.identifier_dict_k1_textbox.delete(0, tkinter.END)
        self.identifier_dict_v1_textbox.delete(0, tkinter.END)
        self.identifier_dict_k2_textbox.delete(0, tkinter.END)
        self.identifier_dict_v2_textbox.delete(0, tkinter.END)

        self.result_textbox.delete("1.0", tk.END)

    def on_button_execute(self) -> None:
        sample_text = self.sample_textbox.get()
        match_re_text = self.match_re_textbox.get()
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
