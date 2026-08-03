from dataclasses import dataclass, field
from datetime import datetime, time
from enum import IntEnum, StrEnum, auto
from logging import ERROR, getLevelName
from typing import Any, Iterator, Optional, Self


@dataclass
class Location:
    line_no: int
    file_name: str


class MhTaskType(StrEnum):
    UNKNOWN = (auto(),)
    BEGAN_ENDED = (auto(),)  # 時刻(範囲)
    TIMESTAMP = (auto(),)  # 作業記録(開始時刻のみ)
    TEXT = (auto(),)  # 時刻なし


# class MhTaskType(IntEnum):
#    UNKNOWN = auto(),
#    BEGAN_ENDED = auto(),  # 時刻(範囲)
#    TIMESTAMP = auto(),  # 作業記録(開始時刻のみ)
#    TEXT = auto(),  # 時刻なし

# Enumにすると、update_task_textbox()でtask_summary()をすると、record_typeが変化してしまう。
# class MhTaskType:
# UNKNOWN = (auto(),)
# BEGAN_ENDED = (auto(),)  # 時刻(範囲)
# TIMESTAMP = (auto(),)  # 作業記録(開始時刻のみ)
# TEXT = (auto(),)  # 時刻なし


@dataclass
class MhTask:
    indent: int = 0
    began_time: Optional[time] = None
    ended_time: Optional[time] = None
    tag_dict: dict[str, str] = field(default_factory=dict)
    line_text_raw: str = ""  # 入力データ(加工前)
    line_text: str = ""  # 入力データ(時刻部分を削除)
    task_type: str = ""
    record_type: MhTaskType = MhTaskType.UNKNOWN
    child_task: list[Self] = field(default_factory=list)
    #
    task_time: int = 0  # 作業時間(分)
    task_interrupt: bool = False  # 作業が中断して作業時間が分割された。
    #
    location: Optional[Location] = None

    def __iter__(self) -> Iterator[Self]:
        """
        自分自身を返し、その後、子タスクを再帰的に走査するイテレータ
        """
        # まず自分自身を返す
        yield self

        # 子要素を順に走査し、それぞれの中身も yield from で展開する
        for child in self.child_task:
            yield from child


class MhTaskListIterable:
    """
    list[Task] を受け取り、全階層をループするラッパークラス
    """

    def __init__(self, tasks: list[MhTask]):
        self.tasks = tasks

    def __iter__(self) -> Iterator[MhTask]:
        for task in self.tasks:
            yield from task


def mhtask_dict_factory(items: list[tuple[str, Any]]) -> dict[str, Any]:
    """!
    @brief asdict() dict_factory関数
    """
    adict = {}
    for key, value in items:
        if isinstance(value, time):
            value = value.strftime("%H:%M")
        adict[key] = value

    return adict


@dataclass(kw_only=True)
class WindowGeometry:
    width: int = 0
    height: int = 0
    x: int = 0
    y: int = 0


@dataclass
class TagEntry:
    task_type: str = ""
    match_re: str = ""
    description: str = ""
    sample: Optional[str] = None
    identifier_require_dict: Optional[dict[str, str]] = None
    identifier_dict: Optional[dict[str, str]] = None
    tag_entry_dict: dict[str, str] = field(default_factory=dict)


@dataclass
class TagGroup:
    group_name: str = ""
    tag_entry_list: list[TagEntry] = field(default_factory=list)


@dataclass
class Config:
    version: str = ""
    main_window_geometry: WindowGeometry = field(default_factory=WindowGeometry)
    tag_config: Optional[list[TagGroup]] = None


@dataclass
class ValidationErrorBase:
    level: int  # logging
    pass


@dataclass
class ValidationError(ValidationErrorBase):
    message: str = ""
    mht: Optional[MhTask] = None

    def __str__(self):
        if self.mht is not None and self.mht.location is not None:
            return f"{self.mht.location.line_no}:{getLevelName(self.level)}:{self.message},file_name={self.mht.location.file_name}"
        else:
            return f"-:{getLevelName(self.level)}:{self.message}"


@dataclass
class ValidationError2(ValidationErrorBase):
    """2つのMhTaskでエラー"""

    mht1: MhTask
    mht2: MhTask
    message: str = ""

    def __str__(self):
        msg1 = ""
        if self.mht1.location is not None:
            msg1 = f"{self.mht1.location.line_no}:{getLevelName(self.level)}:{self.message},file_name={self.mht1.location.file_name}"
        else:
            msg1 = f"-:{getLevelName(self.level)}:{self.message}"
        msg2 = ""
        if self.mht2.location is not None:
            msg2 = f"{self.mht2.location.line_no}"
        else:
            msg2 = f"-"

        return f"{msg1},mht2={msg2}"


def check_validation_error(validation_error: list[ValidationErrorBase]) -> bool:
    return any(x.level == ERROR for x in validation_error)


def parse_time(s: str) -> time:
    return datetime.strptime(s, "%H:%M").time()
