import re
from logging import ERROR, WARNING
from typing import Optional

from src.data_model import (
    Config,
    MhTask,
    MhTaskType,
    TagEntry,
    ValidationError,
    ValidationErrorBase,
)


class MhTaskCategorize:

    def __init__(self, *, config: Config = Config()):
        self.config = config
        self.validation_error: list[ValidationErrorBase] = []
        # デバッグ用
        self.debug_identifier_dict: dict[str, str] = {}
        pass

    def _tag_add_local(
        self,
        mht: MhTask,
        te: TagEntry,
    ) -> bool:
        """!
        @brief タグの付与
        """
        line = mht.line_text
        match = re.search(te.match_re, line)
        if match is None:
            return False
        #
        task_type = te.task_type
        # 識別子
        identifier_dict: dict[str, str] = {}
        self.debug_identifier_dict = {}
        if te.identifier_dict is not None:
            for k, v in te.identifier_dict.items():
                match = re.search(v, line)
                if match:
                    if len(match.group()) == 1:
                        v_id = match.group()
                    else:
                        v_id = match.group(1)
                    identifier_dict[k] = v_id
                else:
                    if k == "ticket_id":
                        self.validation_error.append(
                            ValidationError(
                                level=WARNING,
                                message="チケット番号が省略されています。記入漏れを確認してください。",
                                mht=mht,
                            )
                        )
                    return False
            self.debug_identifier_dict = identifier_dict
        #
        tag_dict: dict[str, str] = {}
        for k, v in te.tag_entry_dict.items():
            if v.startswith("$"):
                id_key = v[1:]
                if id_key not in identifier_dict:
                    self.validation_error.append(
                        ValidationError(
                            level=ERROR,
                            message=f'タグの追加に失敗しました。reason="{id_key}が見つかりません"',
                            mht=mht,
                        )
                    )
                    return False
                v = identifier_dict[id_key]
            tag_dict[k] = v
        # mht セット
        mht.task_type = task_type
        mht.tag_dict = tag_dict
        return True

    def _tag_add(
        self,
        mht: MhTask,
    ) -> None:
        """!
        @brief タグの付与
        """
        if self.config.tag_config is None:
            return
        for tg in self.config.tag_config:
            for te in tg.tag_entry_list:
                result = self._tag_add_local(mht, te)
                if result == True:
                    return

    def mh_task_print4(
        self,
        mht_list: list[MhTask],
        o_stream,
        *,
        header: bool = True,
        task_date: Optional[str] = None,
    ) -> None:
        task_date_column = ""
        if task_date is not None:
            task_date_column = f"{task_date}\t"
        # CSVヘッダ
        if header == True:
            if task_date is None:
                o_stream.write("task_type\tticket_id\ttask_time\n")
            else:
                o_stream.write("task_date\ttask_type\tticket_id\ttask_time\n")
        # 集計;チケット
        ticket_dict: dict[str, int] = {}
        ticket_review_dict: dict[str, int] = {}
        for mht in mht_list:
            if mht.record_type != MhTaskType.BEGAN_ENDED:
                continue
            if "チケット" in mht.tag_dict:
                ticket_id = mht.tag_dict["チケット"]
                if "レビュー" in mht.tag_dict:
                    if ticket_id in ticket_review_dict:
                        ticket_review_dict[ticket_id] += mht.task_time
                    else:
                        ticket_review_dict[ticket_id] = mht.task_time
                else:
                    if ticket_id in ticket_dict:
                        ticket_dict[ticket_id] += mht.task_time
                    else:
                        ticket_dict[ticket_id] = mht.task_time
            else:
                o_stream.write(f"{task_date_column}{mht.line_text}\t\t{mht.task_time}\n")
        o_stream.write("====チケット作業====\n")
        # 集計項目の出力
        for k, v in ticket_dict.items():
            o_stream.write(f"{task_date_column}{'チケット;担当'}\t{k}\t{v}\n")
        for k, v in ticket_review_dict.items():
            o_stream.write(f"{task_date_column}{'チケット;レビュー'}\t{k}\t{v}\n")

    def task_add_tag(
        self,
        mht_list: list[MhTask],
    ) -> None:
        # タグを付与
        for mht in mht_list:
            self._tag_add(mht)
