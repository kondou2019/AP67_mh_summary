import io
import urllib
from pathlib import Path
from typing import Optional


def reorder_pivot_table(ticket_url_text: str, pivot_table_text: str) -> str:
    # ticket_url_textからチケットIDの一覧を作成
    ticket_id_list: list[str] = []
    for line in ticket_url_text.splitlines():
        parse_result = urllib.parse.urlparse(line)
        p = Path(parse_result.path)
        ticket_id_list.append(p.name)
    # pivot_table_textを分解
    lines = pivot_table_text.splitlines()
    ## "行ラベル","総計"のインデックスを求める
    label_index: Optional[int] = None
    total_index: Optional[int] = None
    for i, line in enumerate(lines):
        if label_index is None and line.startswith("行ラベル"):
            label_index = i
        elif total_index is None and line.startswith("総計"):
            total_index = i
    ## ヘッダ,ボディ,フッタを求める
    header_list: list[str] = []
    if label_index is not None:
        header_list = lines[0 : label_index + 1]
    footer_list: list[str] = []
    if total_index is not None:
        footer_list = lines[total_index:]
    body_list: list[str] = []
    if label_index is not None and total_index is not None:
        body_list = lines[label_index + 1 : total_index]
    elif label_index is None and total_index is None:
        body_list = lines
    elif label_index is not None and total_index is None:
        body_list = lines[label_index + 1 :]
    elif label_index is None and total_index is not None:
        body_list = lines[:total_index]
    ## 並べ替え出力
    ### body_listをチケットIDで辞書化
    body_dict: dict[str, str] = {}
    for line in body_list:
        columns = line.split("\t")
        ticket_id = columns[0]
        body_dict[ticket_id] = line
    ### 出力
    f = io.StringIO(newline="")
    #### ヘッダ出力
    for line in header_list:
        f.write(line)
        f.write("\n")  # 改行
    #### ボディ出力
    for ticket_id in ticket_id_list:
        if ticket_id in body_dict:
            f.write(body_dict[ticket_id])
            f.write("\n")  # 改行
        else:
            f.write(f"{ticket_id}\n")  # IDだけ出力
        pass
    #### フッタ出力
    for line in footer_list:
        f.write(line)
        f.write("\n")  # 改行
    #
    s = f.getvalue()  # 内容の取得
    f.close()
    return s
