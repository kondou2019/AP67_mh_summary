import pytest

from src.data_model import Config, MhTask, TagEntry, TagGroup
from src.task_build import MhTaskBuild
from src.task_sort import MhTaskSort


def test_task_add_tag_x99() -> None:
    text = """\
09:00-09:40 作業1
	09:00-09:10 作業1-1
	09:30-09:40 作業1-2
09:10-09:20 作業2
	09:10-09:20 作業2-1
09:20-09:30 作業3
"""
    build = MhTaskBuild()
    mht_list = build.task_read_str(text)
    mht_list = build._build_task_tree(mht_list)
    ts = MhTaskSort()
    result = ts.sort_began_time(mht_list)
    assert len(result) == 4
    assert result[0].line_text == "作業1-1"
    assert result[1].line_text == "作業2-1"
    assert result[2].line_text == "作業3"
    assert result[3].line_text == "作業1-2"
