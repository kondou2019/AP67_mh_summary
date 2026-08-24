import pytest

from src.data_model import Config, MhTask, TagEntry, TagGroup, TaskNameNormalize
from src.task_build import MhTaskBuild
from src.task_normalize import MhTaskNormalize


def test_task_name_normalize_n0101() -> None:
    text = """\
09:00-09:40 work1
"""
    build = MhTaskBuild()
    mht_list = build.task_read_str(text)
    mht_list = build._build_task_tree(mht_list)
    #
    config = Config()
    config.task_name_normalize = TaskNameNormalize(
        name_alias_dict={"作業1": ["work1"]},
    )

    tn = MhTaskNormalize()
    tn.task_name_normalize(mht_list, config)
    assert mht_list[0].line_text == "作業1"


def test_task_name_normalize_n0201() -> None:  # 正規表現
    text = """\
09:00-09:10 sprint planning;# 1
09:10-09:20 sprint planning;# 2
"""
    build = MhTaskBuild()
    mht_list = build.task_read_str(text)
    mht_list = build._build_task_tree(mht_list)
    #
    config = Config()
    config.task_name_normalize = TaskNameNormalize(
        name_alias_dict={"sprint planning": ["^sprint planning;*"]},
    )
    #
    tn = MhTaskNormalize()
    tn.task_name_normalize(mht_list, config)
    assert mht_list[0].line_text == "sprint planning"
    assert mht_list[1].line_text == "sprint planning"
