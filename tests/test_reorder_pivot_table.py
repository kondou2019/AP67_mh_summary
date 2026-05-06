from typing import IO, Optional

import pytest

from src.reorder_pivot_table import reorder_pivot_table


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

    result = reorder_pivot_table(ticket_url_text, pivot_table_text)
    # assert len(result) == 2


def test_reorder_pivot_table_n0102() -> None:  # ヘッダ・フッタなし
    ticket_url_text = """\
https://jira.abc.com/browse/TICKET-0002
https://jira.abc.com/browse/TICKET-0001
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
    result = reorder_pivot_table(ticket_url_text, pivot_table_text)
    assert result == expeced_text


@pytest.mark.parametrize(
    "_test_id, ticket_url_text, pivot_table_text, expeced_text",
    [
        (
            "n0101",
            """\
https://jira.abc.com/browse/TICKET-0002
https://jira.abc.com/browse/TICKET-0001
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
        (  # 作業したチケットが多い;TICKET-0003	3
            "n0201",
            """\
https://jira.abc.com/browse/TICKET-0002
https://jira.abc.com/browse/TICKET-0001
""",
            """\
TICKET-0001	1
TICKET-0002	2
TICKET-0003	3
""",
            """\
TICKET-0002	2
TICKET-0001	1
""",
        ),
        (  # ticket_urlが多い;TICKET-0003
            "n0202",
            """\
https://jira.abc.com/browse/TICKET-0002
https://jira.abc.com/browse/TICKET-0003
https://jira.abc.com/browse/TICKET-0001
""",
            """\
TICKET-0001	1
TICKET-0002	2
""",
            """\
TICKET-0002	2
TICKET-0003
TICKET-0001	1
""",
        ),
    ],
)
def test_reorder_pivot_table_x9001(
    _test_id: str, ticket_url_text: str, pivot_table_text: str, expeced_text: str
) -> None:  # ヘッダ・フッタなし
    #
    result = reorder_pivot_table(ticket_url_text, pivot_table_text)
    assert result == expeced_text
    pass
