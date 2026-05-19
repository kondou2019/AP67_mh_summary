import pytest

from src.data_model import Config, MhTask, TagEntry, TagGroup, check_validation_error
from src.task_categorize import MhTaskCategorize


@pytest.mark.parametrize(
    "_test_id, line_text, return_bool, tag_expected",
    [
        ("n0101", "[チケット1]開発1", True, {"チケット": "チケット1"}),
    ],
)
def test_tag_add_local_x99(
    _test_id: str, line_text: str, return_bool: bool, tag_expected: dict[str, str]
) -> None:  # チケット作業
    mht = MhTask()
    mht.line_text = line_text
    #
    te = TagEntry(
        task_type="チケット",
        match_re="^\\[.*\\]",
        identifier_dict={"ticket_id": "^\\[(チケット.*?)\\]"},
        tag_entry_dict={"チケット": "$ticket_id"},
    )
    categorize = MhTaskCategorize()
    result = categorize._tag_add_local(mht, te)
    assert return_bool == result
    for k in tag_expected.keys():  # tag_expectedの分だけチェックする。多い分は気にしない。
        assert mht.tag_dict[k] == tag_expected[k]


@pytest.mark.parametrize(
    "_test_id, line_text, tag_expected",
    [
        ("n0101", "相談;[チケット1]開発1", {"チケット": "チケット1", "レビュー": ""}),
        ("n0102", "チケット作成;[チケット1]開発2", {"チケット": "チケット1"}),
        (
            "n0201",
            "PRレビュー;PR# 3;[チケット1]チケットタイトル",
            {"チケット": "チケット1", "レビュー": ""},
        ),
        (
            "n0202",
            "PRレビュー;PR# 3;PRタイトル",
            {"レビュー": ""},
        ),  # チケット番号がない
        (
            "n0301",
            "ドキュメントレビュー;[チケット1]チケットタイトル",
            {"チケット": "チケット1", "レビュー": ""},
        ),
        (
            "n0302",
            "ドキュメントレビュー;ドキュメントタイトル",
            {"レビュー": ""},
        ),  # チケット番号がない
        (
            "n0401",
            "相談;[チケット1]チケットタイトル",
            {"チケット": "チケット1", "レビュー": ""},
        ),
        (
            "n0402",
            "相談;ドキュメントタイトル",
            {"レビュー": ""},
        ),  # チケット番号がない
        (
            "n0501",
            "気になる;[チケット1]チケットタイトル",
            {"チケット": "チケット1", "レビュー": ""},
        ),
        (
            "n0402",
            "気になる;ドキュメントタイトル",
            {"レビュー": ""},
        ),  # チケット番号がない
    ],
)
def test_task_add_tag_x99(_test_id: str, line_text: str, tag_expected: dict[str, str]) -> None:
    mht = MhTask()
    mht.line_text = line_text
    #
    config = Config()
    config.tag_config = [
        TagGroup(
            group_name="ticket",
            tag_entry_list=[
                TagEntry(
                    task_type="チケット",
                    match_re="^\\[.*\\]",
                    identifier_dict={"ticket_id": "^\\[(チケット.*?)\\]"},
                    tag_entry_dict={"チケット": "$ticket_id"},
                ),
                TagEntry(
                    task_type="チケット作成",
                    match_re="^チケット作成;",
                    identifier_dict={"ticket_id": "^.*;\\[(チケット.*?)\\]"},
                    tag_entry_dict={"チケット": "$ticket_id"},
                ),
                TagEntry(
                    task_type="PRレビュー",
                    match_re="^PRレビュー;",
                    identifier_dict={"ticket_id": "^.*;\\[(チケット.*?)\\]", "pr_id": ";PR#\\s*(\\d+);"},
                    tag_entry_dict={"レビュー": "", "チケット": "$ticket_id", "pull_request": "$pr_id"},
                ),
                TagEntry(
                    task_type="ドキュメントレビュー",
                    match_re="^ドキュメントレビュー;",
                    identifier_dict={"ticket_id": ";\\[(チケット.*?)\\]"},
                    tag_entry_dict={"レビュー": "", "チケット": "$ticket_id"},
                ),
                TagEntry(
                    task_type="相談",
                    match_re="^相談;",
                    identifier_dict={"ticket_id": ";\\[(チケット.*?)\\]"},
                    tag_entry_dict={"レビュー": "", "チケット": "$ticket_id"},
                ),
                TagEntry(
                    task_type="気になる",
                    match_re="^気になる;",
                    identifier_dict={"ticket_id": ";\\[(チケット.*?)\\]"},
                    tag_entry_dict={"レビュー": "", "チケット": "$ticket_id"},
                ),
            ],
        ),
        TagGroup(
            group_name="pull_request",
            tag_entry_list=[
                TagEntry(
                    task_type="PRレビュー",
                    match_re="^PRレビュー;",
                    identifier_dict={"pr_id": ";PR#\\s*(\\d+);"},
                    tag_entry_dict={"レビュー": "", "pull_request": "$pr_id"},
                ),
            ],
        ),
        TagGroup(
            group_name="general",
            tag_entry_list=[
                TagEntry(
                    task_type="ドキュメントレビュー",
                    match_re="^ドキュメントレビュー;",
                    tag_entry_dict={"レビュー": ""},
                ),
                TagEntry(
                    task_type="相談",
                    match_re="^相談;",
                    tag_entry_dict={"レビュー": ""},
                ),
                TagEntry(
                    task_type="気になる",
                    match_re="^気になる;",
                    tag_entry_dict={"レビュー": ""},
                ),
            ],
        ),
    ]
    categorize = MhTaskCategorize(config=config)
    categorize.task_add_tag([mht])
    for k in tag_expected.keys():  # tag_expectedの分だけチェックする。多い分は気にしない。
        assert mht.tag_dict[k] == tag_expected[k]

@pytest.mark.parametrize(
    "_test_id, line_text",
    [
        ("a0101", "チケット作成;識別子なし"),
        (
            "a0102",
            "PRレビュー;識別子なし",
        ),
    ],
)
def test_task_add_tag_x98(_test_id: str, line_text: str) -> None: # 必須識別子なし
    mht = MhTask()
    mht.line_text = line_text
    #
    config = Config()
    config.tag_config = [
        TagGroup(
            group_name="ticket",
            tag_entry_list=[
                TagEntry(
                    task_type="チケット作成",
                    match_re="^チケット作成;",
                    identifier_require_dict={"ticket_id": "^.*;\\[(チケット.*?)\\]"},
                    tag_entry_dict={"チケット": "$ticket_id"},
                ),
            ],
        ),
        TagGroup(
            group_name="pull_request",
            tag_entry_list=[
                TagEntry(
                    task_type="PRレビュー",
                    match_re="^PRレビュー;",
                    identifier_require_dict={"pr_id": ";PR#\\s*(\\d+);"},
                    tag_entry_dict={"レビュー": "", "pull_request": "$pr_id"},
                ),
            ],
        ),
    ]
    categorize = MhTaskCategorize(config=config)
    categorize.task_add_tag([mht])
    assert True == check_validation_error(categorize.validation_error) # ERROR バリデーション
