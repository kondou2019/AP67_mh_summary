from typing import IO, Optional

import pytest

from src.reorder_pivot_table import ReorderPivotTable


def test_reorder_pivot_table_n0101() -> None:
    ticket_url_text = """\
	https://jira.abc.com/browse/TICKET-0002
	https://jira.abc.com/browse/TICKET-0001
"""

    pivot_table_text = """\
	
	
	列ラベル
	PRレビュー		チケット		チケット作成		ドキュメントレビュー		
行ラベル	合計 / task_time	合計 / 作業時間	合計 / task_time	合計 / 作業時間	合計 / task_time	合計 / 作業時間
TICKET-0001	407	6.783333	0	0	0	0
TICKET-0002	407	6.783333	0	0	0	0
総計	


"""
    pivot_table = ReorderPivotTable()
    result = pivot_table.reorder_pivot_table(ticket_url_text, pivot_table_text)
    # assert len(result) == 2


def test_reorder_pivot_table_n0102() -> None:  # ヘッダ・フッタなし
    ticket_url_text = """\
チケット2	https://jira.abc.com/browse/TICKET-0002
チケット1	https://jira.abc.com/browse/TICKET-0001
"""

    pivot_table_text = """\
TICKET-0001	1
TICKET-0002	2
"""

    expeced_text = """\
TICKET-0002	2
TICKET-0001	1
"""
    #
    pivot_table = ReorderPivotTable()
    result = pivot_table.reorder_pivot_table(ticket_url_text, pivot_table_text)
    assert result == expeced_text


def test_reorder_pivot_table_n0103() -> None:  # チケットURLにURL以外の指定
    ticket_url_text = """\
改善活動	改善活動
チケット2	https://jira.abc.com/browse/TICKET-0002
チケット1	https://jira.abc.com/browse/TICKET-0001
"""

    pivot_table_text = """\
TICKET-0001	1
TICKET-0002	2
改善活動	3
"""

    expeced_text = """\
改善活動	3
TICKET-0002	2
TICKET-0001	1
"""
    #
    pivot_table = ReorderPivotTable()
    result = pivot_table.reorder_pivot_table(ticket_url_text, pivot_table_text)
    assert result == expeced_text


def test_reorder_pivot_table_n0201() -> None:  # チケット外
    ticket_url_text = """\
改善活動	
チケット2	https://jira.abc.com/browse/TICKET-0002
チケット1	https://jira.abc.com/browse/TICKET-0001
チケット3	https://jira.abc.com/browse/TICKET-0003
"""

    pivot_table_text = """\
	
	
	列ラベル
	PRレビュー		チケット		チケット作成		ドキュメントレビュー		
行ラベル	合計 / task_time	合計 / 作業時間	合計 / task_time	合計 / 作業時間	合計 / task_time	合計 / 作業時間
改善活動	3
TICKET-0001	407	6.783333	0	0	0	0
TICKET-0002	407	6.783333	0	0	0	0
総計	


"""
    pivot_table = ReorderPivotTable()
    result = pivot_table.reorder_pivot_table(ticket_url_text, pivot_table_text)
    # assert len(result) == 2


@pytest.mark.parametrize(
    "_test_id, ticket_url_text, pivot_table_text, expeced_text",
    [
        (
            "n0101",
            """\
チケット2	https://jira.abc.com/browse/TICKET-0002
チケット1	https://jira.abc.com/browse/TICKET-0001
""",
            """\
TICKET-0001	1
TICKET-0002	2
""",
            """\
TICKET-0002	2
TICKET-0001	1
""",
        ),
    ],
)
def test_reorder_pivot_table_x9001(
    _test_id: str, ticket_url_text: str, pivot_table_text: str, expeced_text: str
) -> None:  # ヘッダ・フッタなし
    #
    pivot_table = ReorderPivotTable()
    result = pivot_table.reorder_pivot_table(ticket_url_text, pivot_table_text)
    assert result == expeced_text


def test_validation_n0101() -> None:  # エラーなし
    pivot_table = ReorderPivotTable()
    result = pivot_table.validation(["TICKET-0001", "TICKET-0002"], {"TICKET-0001": "", "TICKET-0002": ""})
    assert len(pivot_table.validation_error) == 0


def test_validation_a0201() -> None:  # ticket_id_listの重複
    pivot_table = ReorderPivotTable()
    result = pivot_table.validation(["TICKET-0001", "TICKET-0001"], {"TICKET-0001": ""})
    assert len(pivot_table.validation_error) != 0


def test_validation_a0202() -> None:  # ticket_id_listの不足
    pivot_table = ReorderPivotTable()
    result = pivot_table.validation(["TICKET-0001", "TICKET-0002"], {"TICKET-0001": "", "TICKET-0003": ""})
    assert len(pivot_table.validation_error) != 0
