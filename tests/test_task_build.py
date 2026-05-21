import io
from datetime import time
from typing import Optional

import pytest

from src.data_model import MhTaskType, parse_time
from src.task_build import MhTaskBuild, check_began_ended_leaf


@pytest.mark.parametrize(
    "_test_id, text, expected",
    [
        (
            "n0101",
            """\
09:00-09:20 作業1
""",
            True,
        ),
        (
            "n0102",
            """\
09:00-09:20 作業1
	コメント1
""",
            True,
        ),
        (
            "n0103",
            """\
09:00-09:20 作業1
	コメント1
		コメント1-1
""",
            True,
        ),
        (
            "n0201",
            """\
09:00-09:20 作業1
	コメント1
		09:00-09:20 作業1-1
""",
            False,
        ),
    ],
)
def test_check_began_ended_leaf_n0101(_test_id: str, text: str, expected: bool) -> None:
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    # build = MhTaskBuild()
    result = check_began_ended_leaf(mht_list[0])
    assert result == expected


def test_task_division_task_n0101() -> None:
    text = """\
09:00-09:20 作業1;作業中に作業2を行った
09:05-09:15 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    build = MhTaskBuild()
    build._division_task(mht_list)
    # 検証
    ## 作業1を分割
    assert len(mht_list[0].child_task) == 2
    assert mht_list[0].child_task[0].began_time == parse_time("09:00")
    assert mht_list[0].child_task[0].ended_time == parse_time("09:05")
    assert mht_list[0].child_task[1].began_time == parse_time("09:15")
    assert mht_list[0].child_task[1].ended_time == parse_time("09:20")


def test_task_division_task_n0103() -> None:  # サブタスク
    text = """\
09:00-09:20 作業1
	09:00-09:20 作業1-1
09:05-09:25 作業2
	09:05-09:15 作業2-1
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    build = MhTaskBuild()
    build._division_task(mht_list)
    # 検証
    ## 作業1を分割
    assert len(mht_list[0].child_task[0].child_task) == 2
    assert mht_list[0].child_task[0].child_task[0].began_time == parse_time("09:00")
    assert mht_list[0].child_task[0].child_task[0].ended_time == parse_time("09:05")
    assert mht_list[0].child_task[0].child_task[1].began_time == parse_time("09:15")
    assert mht_list[0].child_task[0].child_task[1].ended_time == parse_time("09:20")


def test_task_division_task_n0104() -> None:  # 多重分割
    text = """\
09:00-09:30 作業1
	09:00-09:30 作業1-1(作業2,作業3で分割)
09:05-09:10 作業2
09:15-09:20 作業3
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # タスクの作業時間の分割
    build = MhTaskBuild()
    build._division_task(mht_list)
    # 検証
    ## 作業1を分割
    assert len(mht_list[0].child_task[0].child_task) == 3
    assert mht_list[0].child_task[0].child_task[0].began_time == parse_time("09:00")
    assert mht_list[0].child_task[0].child_task[0].ended_time == parse_time("09:05")
    assert mht_list[0].child_task[0].child_task[1].began_time == parse_time("09:10")
    assert mht_list[0].child_task[0].child_task[1].ended_time == parse_time("09:15")
    assert mht_list[0].child_task[0].child_task[2].began_time == parse_time("09:20")
    assert mht_list[0].child_task[0].child_task[2].ended_time == parse_time("09:30")


def test_task_division_task_n0105() -> None:  # 入れ子
    text = """\
09:00-14:00 作業1
10:00-13:00 作業2
11:00-12:00 作業3
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    build = MhTaskBuild()
    build._division_task(mht_list)
    assert len(mht_list) == 3
    # 検証
    ## 作業1を分割
    assert mht_list[0].child_task[0].began_time == parse_time("09:00")
    assert mht_list[0].child_task[0].ended_time == parse_time("10:00")
    assert mht_list[0].child_task[1].began_time == parse_time("13:00")
    assert mht_list[0].child_task[1].ended_time == parse_time("14:00")
    ## 作業2を分割
    assert mht_list[1].child_task[0].began_time == parse_time("10:00")
    assert mht_list[1].child_task[0].ended_time == parse_time("11:00")
    assert mht_list[1].child_task[1].began_time == parse_time("12:00")
    assert mht_list[1].child_task[1].ended_time == parse_time("13:00")
    ## 作業3を分割
    assert len(mht_list[2].child_task) == 0
    pass


def test_task_division_task_n0106() -> None:  # 作業1に作業2,3が内包。作業2,3が連続している
    text = """\
09:00-10:00 作業1,40
09:10-09:20 作業2,10
09:20-09:30 作業3,10
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # タスクの作業時間の分割
    build = MhTaskBuild()
    build._division_task(mht_list)
    # 検証
    ## 作業1を分割
    assert len(mht_list[0].child_task) == 2
    assert mht_list[0].child_task[0].began_time == parse_time("09:00")
    assert mht_list[0].child_task[0].ended_time == parse_time("09:10")
    assert mht_list[0].child_task[1].began_time == parse_time("09:30")
    assert mht_list[0].child_task[1].ended_time == parse_time("10:00")
    ## 作業2,3は分割無し
    assert len(mht_list[1].child_task) == 0
    assert len(mht_list[1].child_task) == 0


def test_task_division_task_n0201() -> None:  # 子タスクに、BEGAN_ENDEDが無い
    text = """\
09:00-09:20 作業1
09:05-09:15 作業2
	09:10 確認2-1
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    build = MhTaskBuild()
    build._division_task(mht_list)
    # 検証
    ## 作業1を分割
    assert len(mht_list[0].child_task) == 2
    assert mht_list[0].child_task[0].began_time == parse_time("09:00")
    assert mht_list[0].child_task[0].ended_time == parse_time("09:05")
    assert mht_list[0].child_task[1].began_time == parse_time("09:15")
    assert mht_list[0].child_task[1].ended_time == parse_time("09:20")


def test_task_division_task_n0202() -> None:  # 入れ子,コメント付き
    text = """\
09:00-14:00 作業1
	コメント1
10:00-13:00 作業2
	コメント2
11:00-12:00 作業3
	コメント2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    build = MhTaskBuild()
    build._division_task(mht_list)
    assert len(mht_list) == 3
    # 検証
    ## 作業1を分割
    assert mht_list[0].child_task[1].began_time == parse_time("09:00")
    assert mht_list[0].child_task[1].ended_time == parse_time("10:00")
    assert mht_list[0].child_task[2].began_time == parse_time("13:00")
    assert mht_list[0].child_task[2].ended_time == parse_time("14:00")
    ## 作業2を分割
    assert mht_list[1].child_task[1].began_time == parse_time("10:00")
    assert mht_list[1].child_task[1].ended_time == parse_time("11:00")
    assert mht_list[1].child_task[2].began_time == parse_time("12:00")
    assert mht_list[1].child_task[2].ended_time == parse_time("13:00")
    ## 作業3を分割
    assert len(mht_list[2].child_task) == 1
    pass


def test_filter_contained_intervals_n0101() -> None:
    text = """\
09:00-10:00 作業1
09:10-09:20 作業2
09:12-09:15 作業2-1
09:15-09:18 作業2-2
11:00-12:00 作業3
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    result = build._filter_contained_intervals(mht_list)
    assert len(result) == 2
    assert result[0].began_time == parse_time("09:00")
    assert result[0].ended_time == parse_time("10:00")
    assert result[1].began_time == parse_time("11:00")
    assert result[1].ended_time == parse_time("12:00")


def test_filter_task_began_ended_n0101() -> None:
    text = """\
09:00-09:10 作業1
10:00-10:10 作業2
11:00-11:10 作業3
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    # ツリー化
    mht_list = build._build_task_tree(mht_list)
    # 一覧
    ## 一つ
    result = build._filter_task_began_ended(mht_list, parse_time("09:00"), parse_time("09:10"))
    assert len(result) == 1
    assert result[0].line_text == "作業1"

    result = build._filter_task_began_ended(mht_list, parse_time("10:00"), parse_time("10:15"))
    assert len(result) == 1
    assert result[0].line_text == "作業2"

    result = build._filter_task_began_ended(mht_list, parse_time("11:00"), parse_time("11:10"))
    assert len(result) == 1
    assert result[0].line_text == "作業3"

    ## 複数
    result = build._filter_task_began_ended(mht_list, parse_time("09:00"), parse_time("10:20"))
    assert len(result) == 2


def test_filter_task_began_ended_n0102() -> None:  # 階層
    text = """\
09:00-09:10 作業1
	09:00-09:05 作業1-1
	09:05-09:10 作業1-2
10:00-10:10 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    # ツリー化
    mht_list = build._build_task_tree(mht_list)
    # 一覧
    result = build._filter_task_began_ended(mht_list, parse_time("09:00"), parse_time("09:20"))
    assert len(result) == 2
    assert result[0].line_text == "作業1-1"
    assert result[1].line_text == "作業1-2"


@pytest.mark.parametrize(
    "_test_id, val, began_expected, ended_expected,began_only_expected, remnant_expected",
    [
        ("n0101", "09:00 abc", time(9, 0), None, True, "abc"),
        ("n0103", "09:00-10:00 abc", time(9, 0), time(10, 0), False, "abc"),
        ("n0104", "10:00- abc", time(10, 0), None, False, "abc"),  # バリデーションエラーだが、この関数では正常
        ("n0105", "-10:00 abc", None, time(10, 0), False, "abc"),
        ("n0201", "", None, None, False, ""),
        ("n0202", "abc", None, None, False, "abc"),
        ("n0203", ":-:", None, None, False, ":-:"),
        ("n0204", "-", None, None, False, "-"),
        ("n0205", '"C:kondou.txt"', None, None, False, '"C:kondou.txt"'),  # 3文字目が':'
        ("n0206", "#09:00 abc", None, None, False, "#09:00 abc"),  # コメントアウト
        ("a0301", "09:00　abc", None, None, False, ""),  # 時刻の後が、全角スペース
        ("a0302", "-09:00　abc", None, None, False, ""),
        ("a0303", "09:00-09:10　abc", None, None, False, ""),
    ],
)
def test_parse_time_to_time_x9901(
    _test_id: str,
    val: str,
    began_expected: Optional[time],
    ended_expected: Optional[time],
    began_only_expected: bool,
    remnant_expected: str,
) -> None:
    build = MhTaskBuild()
    began_time, ended_time, began_only, remnant = build._parse_time_to_time(val)
    if began_expected is None:
        assert began_time is None
    else:
        assert began_time == began_expected
    if ended_expected is None:
        assert ended_time is None
    else:
        assert ended_time == ended_expected
    assert began_only == began_only_expected
    assert remnant == remnant_expected


@pytest.mark.parametrize(
    "_test_id, line, indent_expected, began_expected, ended_expected, type_expected, line_expected",
    [
        ("n0101", "09:00 作業", 0, time(9, 0), None, MhTaskType.TIMESTAMP, "作業"),
        (
            "n0103",
            "-10:00 作業",
            0,
            None,
            time(10, 0),
            MhTaskType.BEGAN_ENDED,
            "作業",
        ),
        (
            "n0104",
            "09:00-10:00 作業",
            0,
            time(9, 0),
            time(10, 0),
            MhTaskType.BEGAN_ENDED,
            "作業",
        ),
        # インデント有り
        ("n0201", "\t09:00 作業", 1, time(9, 0), None, MhTaskType.TIMESTAMP, "作業"),
        (
            "n0202",
            "\t\t09:00 作業",
            2,
            time(9, 0),
            None,
            MhTaskType.TIMESTAMP,
            "作業",
        ),
        # テキスト
        ("n0301", "作業", 0, None, None, MhTaskType.TEXT, "作業"),
    ],
)
def test_task_parse_line_n99xx(
    _test_id: str,
    line: str,
    indent_expected: int,
    began_expected: Optional[time],
    ended_expected: Optional[time],
    type_expected: MhTaskType,
    line_expected: str,
) -> None:
    build = MhTaskBuild()
    mht = build._task_parse_line(line)
    assert mht.indent == indent_expected
    if began_expected is None:
        assert mht.began_time is None
    else:
        assert mht.began_time == began_expected
    if ended_expected is None:
        assert mht.ended_time is None
    else:
        assert mht.ended_time == ended_expected
    assert mht.record_type == type_expected
    assert mht.line_text == line_expected


@pytest.mark.parametrize(
    "_test_id, line",
    [
        ("a0101", "02:00"),  # 作業なし
        ("a0102", "02:00-"),  # 作業なし
        ("a0103", "-02:00"),  # 作業なし
        ("a0103", "00:00-02:00"),  # 作業なし
        ("a0201", "aa:aa 作業"),  # 数字ではない
        ("a0301", "24:00 作業"),  # 時不正
        ("a0302", "00:60 作業"),  # 分不正
        ("a0303", "00:00:01:00 作業"),  # 範囲記号不正
        ("a0401", "02:00-01:00 作業"),  # 逆転
        ("a0402", "01:00-01:00 作業"),  # 同一
        ("a0501", "01:00- 作業"),  # 終了時刻の省略
    ],
)
def test_task_parse_line_a98xx(
    _test_id: str,
    line: str,
) -> None:  # バリデーションエラー
    build = MhTaskBuild()
    mht = build._task_parse_line(line)
    assert len(build.validation_error) != 0  # エラーの内容はチェックしない
