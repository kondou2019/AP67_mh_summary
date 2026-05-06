import pytest

from src.logseq import logseq_md_to_txt


def test_logseq_md_to_txt_n0101() -> None:
    text = """\
09:00 開始
17:30 終了
"""
    lines = text.splitlines()
    result = logseq_md_to_txt(lines)
    assert len(result) == 2


def test_logseq_md_to_txt_n0201() -> None:
    text = """\
- 08:00 開始
- 17:30 終了
"""
    lines = text.splitlines()
    result = logseq_md_to_txt(lines)
    assert len(result) == 2
    assert result[0] == "08:00 開始"
    assert result[1] == "17:30 終了"


def test_logseq_md_to_txt_n0202() -> None:  # インデント
    text = """\
- 09:00-09:10 [チケット1]開発1
	- 09:00-09:02 開発1-1
	- 09:05-09:10 開発1-2
"""
    lines = text.splitlines()
    result = logseq_md_to_txt(lines)
    assert len(result) == 3
    assert result[0] == "09:00-09:10 [チケット1]開発1"
    assert result[1] == "	09:00-09:02 開発1-1"
    assert result[2] == "	09:05-09:10 開発1-2"
