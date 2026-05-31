import json
from typing import Union


def json_escape_of_string(text: str) -> str:
    """!
    @brief 通常の文字列をJSONエスケープされた文字列に変換します。
    """
    # json.dumpsは文字列をダブルクォートで囲むため、
    # 前後のダブルクォートを除去して「中身だけ」を返します。
    return json.dumps(text)[1:-1]


def json_unescape_of_string(escaped_text: str) -> str:
    """!
    @brief JSONエスケープされた文字列を、元の通常の文字列に戻します。
    """
    # json.loadsに渡すためにダブルクォートで囲み、
    # 有効なJSON文字列の形式にしてからデコードします。
    return json.loads(f'"{escaped_text}"')


def remove_none_keys(d: Union[dict, list[dict]]):
    """!
    @brief 辞書からNoneの値をもつキーを取り除く
    @param[in] d 辞書または辞書のリスト
    """
    if isinstance(d, dict):
        for k, v in list(d.items()):  # 削除するのでlistに変換してからループする
            if v is None:
                del d[k]
            elif isinstance(v, dict):
                remove_none_keys(v)
            elif isinstance(v, list):
                remove_none_keys(v)
    elif isinstance(d, list):
        for item in d:
            remove_none_keys(item)
    else:
        raise TypeError("引数:d")
    return d
