import io
from typing import Optional

import pytest

from src.data_model import (
    MhTask,
)
from src.task_build import MhTaskBuild
from src.validator import Validator


def make_testdata(text: str) -> list[MhTask]:
    """テストデータの作成"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    return mht_list


def test__build_mht_parent_dict_n0101() -> None:
    text = """\
09:00-09:30 作業1
	09:00-09:10 作業1-1
09:10-09:40 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    result = validatior._build_mht_parent_dict()
    # 検証
    assert len(result) == 3
    assert result[id(mht_list[0])] == None
    assert result[id(mht_list[0].child_task[0])].line_text == "作業1"
    assert result[id(mht_list[1])] == None


@pytest.mark.parametrize(
    "_test_id, text",
    [
        (
            "a0101",  # 作業時間のみ
            """\
09:00-09:10 作業1
    """,
        ),
        (
            "a0102",  # タイムスタンプのみ
            """\
09:00-09:10 作業1
	09:05 確認1
	09:10 確認2
    """,
        ),
    ],
)
def test_validation_x99(
    _test_id: str,
    text: str,
) -> None:  # バリデーションエラーにならないことを確認
    mht_list = make_testdata(text)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior.validation()
    # 検証
    assert len(validatior.validation_error) == 0


def test_validation_began_ended_1_n0101() -> None:  # 正常
    text = """\
09:00-09:10 作業1
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_began_ended_1()
    # 検証
    assert len(validatior.validation_error) == 0  # 正常


@pytest.mark.parametrize(
    "_test_id, text",
    [
        (
            "n0101",
            "09:00-09:00 作業1",  # 開始時刻と終了時刻が同じ
        ),
        (
            "n0102",
            "09:10-09:00 作業1",  # 開始時刻と終了時刻が逆転
        ),
    ],
)
def test_validation_began_ended_1_x99(
    _test_id: str,
    text: str,
) -> None:  # 正常
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_began_ended_1()
    # 検証
    assert len(validatior.validation_error) != 0  # エラーの内容はチェックしない


@pytest.mark.parametrize(
    "_test_id, text",
    [
        (
            "n0101",
            """\
09:10-09:20 作業2
09:00-09:10 作業1
""",
        ),
        (
            "n0102",
            """\
09:00-09:30 作業1
	09:10-09:20 作業1-2
	09:00-09:10 作業1-1
""",
        ),
        (
            "n0103",
            """\
09:10-09:20 作業1
09:00 確認1
""",
        ),
        # 途中にタスク以外
        (
            "n0201",
            """\
09:10-09:20 作業2
テキスト1
09:00-09:10 作業1
""",
        ),
    ],
)
def test_validation_began_time_in_order_for_layer_x99(
    _test_id: str,
    text: str,
) -> None:  # 正常
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_began_time_in_order_for_layer()
    # 検証
    assert len(validatior.validation_error) != 0  # エラーの内容はチェックしない


@pytest.mark.parametrize(
    "_test_id, text",
    [
        # 開始時刻が一致しない
        (
            "n0102",
            """\
09:00-09:30 作業1
	09:10-09:30 作業1-2
""",
        ),
        # 終了時刻が一致しない
        (
            "n0102",
            """\
09:00-09:30 作業1
	09:00-09:20 作業1-2
""",
        ),
        # 開始時刻,終了時刻が一致しない
        (
            "n0102",
            """\
09:00-09:30 作業1
	09:10-09:20 作業1-2
""",
        ),
    ],
)
def test_validation_enough_child_task_x99(
    _test_id: str,
    text: str,
) -> None:  # エラー
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_enough_child_task()
    # 検証
    assert len(validatior.validation_error) != 0  # エラーの内容はチェックしない


@pytest.mark.parametrize(
    "_test_id, text",
    [
        # 子タスクなし
        (
            "n0102",
            """\
09:00-09:30 作業1
	コメント
""",
        ),
    ],
)
def test_validation_enough_child_task_x98(
    _test_id: str,
    text: str,
) -> None:  # 正常
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_enough_child_task()
    # 検証
    assert len(validatior.validation_error) == 0


def test_validation_task_same_began_time_n0101() -> None:  # 正常
    text = """\
09:00-09:10 作業1
09:10-09:15 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_task_same_began_time()
    # 検証
    assert len(validatior.validation_error) == 0  # 正常


def test_validation_task_same_began_time_n0201() -> None:  # 開始時刻が同じ
    text = """\
09:00-09:10 作業1
09:00-09:15 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_task_same_began_time()
    # 検証
    assert len(validatior.validation_error) != 0  # エラーの内容はチェックしない


def test_validation_task_same_began_time_n0202() -> None:  # 終了時刻が同じ
    text = """\
09:00-09:10 作業1
09:05-09:10 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_task_same_began_time()
    # 検証
    assert len(validatior.validation_error) != 0  # エラーの内容はチェックしない


def test_validation_overlap_n0101() -> None:  # 開始時刻が重複
    text = """\
09:00-09:10 作業1
09:05-09:15 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_overlap()
    # 検証
    assert len(validatior.validation_error) != 0  # エラーの内容はチェックしない


def test_validation_overlap_n0102() -> None:  # 終了時刻が重複
    text = """\
09:00-09:10 作業1
08:55-09:05 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_overlap()
    # 検証
    assert len(validatior.validation_error) != 0  # エラーの内容はチェックしない


def test_validation_overlap_n0201() -> None:  # エラーなし。重複なし
    text = """\
09:00-09:10 作業1
09:10-09:20 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_overlap()
    # 検証
    assert len(validatior.validation_error) == 0


def test_validation_overlap_b0202() -> None:  # エラーなし。包含
    text = """\
09:00-09:10 作業1
09:02-09:04 作業2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_overlap()
    # 検証
    assert len(validatior.validation_error) == 0


def test_validation_overlap_n0203() -> None:  # エラーなし。親タスクで重複
    text = """\
09:00-09:30 作業1
	09:00-09:10 作業1-1
	09:20-09:30 作業1-2
09:10-09:40 作業2
	09:10-09:20 作業2-1
	09:30-09:40 作業2-2
"""
    build = MhTaskBuild()
    f = io.StringIO(text)
    mht_list = build.task_read(f)
    mht_list = build._build_task_tree(mht_list)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_overlap()
    # 検証
    assert len(validatior.validation_error) == 0


@pytest.mark.parametrize(
    "_test_id, text",
    [
        (
            "n0101",
            """\
09:00-09:30 作業1
	09:10-09:20 作業1-1
    """,
        ),
        (
            "n0102",
            """\
09:00-09:30 作業1
	めも
    """,
        ),
    ],
)
def test_validation_within_of_parent_time_range_x99(
    _test_id: str,
    text: str,
) -> None:  # 正常
    mht_list = make_testdata(text)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_within_of_parent_time_range()
    # 検証
    assert len(validatior.validation_error) == 0


@pytest.mark.parametrize(
    "_test_id, text",
    [
        (
            "a0101",  # 開始時刻,終了時刻が範囲外
            """\
09:00-09:30 作業1
	10:00-10:10 作業1-1
    """,
        ),
        (
            "a0102",  # 開始時刻が範囲外
            """\
09:00-09:30 作業1
	08:00-09:10 作業1-1
    """,
        ),
        (
            "a0103",  # 終了時刻が範囲外
            """\
09:00-09:30 作業1
	09:10-10:00 作業1-1
    """,
        ),
        (
            "a0201",  # タイムスタンプで範囲外
            """\
09:00-09:30 作業1
	10:00 記録1
    """,
        ),
    ],
)
def test_validation_within_of_parent_time_range_x98(
    _test_id: str,
    text: str,
) -> None:  # エラー
    mht_list = make_testdata(text)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_within_of_parent_time_range()
    # 検証
    assert len(validatior.validation_error) != 0


@pytest.mark.parametrize(
    "_test_id, text",
    [
        (
            "a0101",  # テキストに作業時間
            """\
テキスト1
	10:00-10:10 作業1-1
    """,
        ),
        (
            "a0102",  # 途中のテキストに作業時間
            """\
10:00-10:10 作業1
    テキスト1
		10:00-10:10 作業1-1
    """,
        ),
    ],
)
def test_validation_work_time_in_the_text_x99(
    _test_id: str,
    text: str,
) -> None:  # エラー
    mht_list = make_testdata(text)
    # 実行
    validatior = Validator(mht_list=mht_list)
    validatior._validation_work_time_in_the_text()
    # 検証
    assert len(validatior.validation_error) != 0
