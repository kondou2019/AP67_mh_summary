import io
import re
from datetime import datetime, time
from logging import ERROR, WARNING
from typing import IO, Optional

from src.data_model import (
    Config,
    Location,
    MhTask,
    MhTaskType,
    TaskNameNormalize,
    ValidationError,
    ValidationErrorBase,
    check_validation_error,
)
from src.logseq import logseq_md_to_txt
from src.task_utl import calc_minute_of_day, check_began_ended_leaf
from src.validator import Validator


class MhTaskNormalize:

    def __init__(self):
        self.validation_error: list[ValidationErrorBase] = []
        pass

    def task_name_normalize(self, mht_list: list[MhTask], config: Config):
        """!
        @brief line_text の正規化※揺らぎを統一する
        """
        if config.task_name_normalize is None:
            return
        # TaskNameNormalizeを辞書に変換
        normalize_dict: dict[str] = {}  # k:値, v:正規化したタスク名
        for k, v in config.task_name_normalize.name_alias_dict.items():
            for v0 in v:
                normalize_dict[v0] = k
        #
        for mht in mht_list:
            if mht.line_text in normalize_dict:
                mht.line_text = normalize_dict[mht.line_text]
        pass
