import io
import re
from datetime import datetime, time
from logging import ERROR, WARNING
from typing import IO, Optional

from src.data_model import (
    Location,
    MhTask,
    MhTaskType,
    ValidationError,
    ValidationErrorBase,
    check_validation_error,
)
from src.logseq import logseq_md_to_txt
from src.task_utl import calc_minute_of_day, check_began_ended_leaf
from src.validator import Validator


class MhTaskBuild:

    def __init__(self):
        self.validation_error: list[ValidationErrorBase] = []
        pass

    def _build_task_tree(self, tasks: list[MhTask]) -> list[MhTask]:
        """!
        @brief indentによるツリー構造への変更
        """
        if not tasks:
            return []

        roots = []
        # 直近の各インデントレベルにおける親候補を保持するスタック
        stack: list[MhTask] = []

        for task in tasks:
            # 現在のタスクのインデントより深い（または同じ）タスクをスタックから除去
            # これにより、stack[-1] が常に現在のタスクの親になる
            while stack and stack[-1].indent >= task.indent:
                stack.pop()

            if not stack:
                # 親がいない場合はルート要素
                roots.append(task)
            else:
                # スタックの最後にある要素の child_task に追加
                stack[-1].child_task.append(task)

            # 自身を次のタスクの親候補としてスタックに追加
            stack.append(task)
        return roots

    def _calc_task_time(self, mht_list: list[MhTask]) -> None:
        def _calc_task_time_local(mht: MhTask) -> None:
            if not any(x.record_type == MhTaskType.BEGAN_ENDED for x in mht.child_task):
                if mht.record_type == MhTaskType.BEGAN_ENDED:
                    if mht.began_time is not None and mht.ended_time is not None:
                        min1 = calc_minute_of_day(mht.began_time)
                        min2 = calc_minute_of_day(mht.ended_time)
                    mht.task_time = min2 - min1
                return
            # サブタスクの作業時間を集計
            for mht0 in mht.child_task:
                _calc_task_time_local(mht0)
                mht.task_time += mht0.task_time
            return

        for mht in mht_list:
            _calc_task_time_local(mht)

    def _division_task(self, mht_list: list[MhTask]) -> None:
        """タスクの分割"""

        def _division_task_local(mht: MhTask) -> None:
            if mht.record_type != MhTaskType.BEGAN_ENDED:
                return
            if check_began_ended_leaf(mht) == True:
                include_list = self._filter_task_began_ended(mht_list, mht.began_time, mht.ended_time)
                include_list.remove(mht)  # 自分自身が含まれているので削除
                # 分割タスクの一覧の作成。包含されているタスクを除外
                division_task_list = self._filter_contained_intervals(include_list)
                if len(division_task_list) > 0:
                    mht0 = division_task_list[0]  # 先頭だけ分割する
                    # サブタスクに分割
                    mht_new = MhTask()
                    mht_new.task_interrupt = True
                    mht_new.record_type = MhTaskType.BEGAN_ENDED
                    mht_new.began_time = mht.began_time
                    mht_new.ended_time = mht0.began_time
                    if mht_new.began_time != mht_new.ended_time:  # 一致していたら追加しない
                        mht.child_task.append(mht_new)  # 前半を追加
                    #
                    mht_new = MhTask()
                    mht_new.task_interrupt = True
                    mht_new.record_type = MhTaskType.BEGAN_ENDED
                    mht_new.began_time = mht0.ended_time
                    mht_new.ended_time = mht.ended_time
                    if mht_new.began_time != mht_new.ended_time:  # 一致していたら追加しない
                        mht.child_task.append(mht_new)  # 後半を追加
            # 子タスク
            for mht0 in mht.child_task:
                _division_task_local(mht0)
            return

        def _division_task_flat_local(mht: MhTask) -> None:
            if len(mht.child_task) == 0:
                return
            # 子タスク
            i = 0
            while i < len(mht.child_task):
                mht0 = mht.child_task[i]
                if mht0.task_interrupt != True:  # 分割タスク以外?
                    _division_task_flat_local(mht0)
                    i += 1
                    continue
                # 子タスクの子タスクをchildに追加する
                if len(mht0.child_task) == 0:
                    i += 1
                    continue
                ## 自分の次に追加して、自分を削除する
                mht.child_task[i + 1 : i + 1] = mht0.child_task
                del mht.child_task[i]

        # 分割
        for mht in mht_list:
            _division_task_local(mht)
        # 最適化。サブタスクの分割が多重になっているところをフラットにする
        for mht in mht_list:
            _division_task_flat_local(mht)
        pass

    def _filter_contained_intervals(self, intervals):
        if not intervals:
            return []

        # 1. 開始時間(began_time)で昇順にソート
        #    同じ開始時間の場合は、終了時間(ended_time)で降順にソート（長い方を優先）
        sorted_intervals = sorted(
            intervals,
            # key=lambda x: (x.began_time, -x.ended_time.timestamp())
            key=lambda x: (x.began_time, -(calc_minute_of_day(x.ended_time))),
        )

        result = []
        if sorted_intervals:
            # 暫定的に最初の要素を「現在もっとも長い範囲」として保持
            current_max_end = sorted_intervals[0].ended_time
            result.append(sorted_intervals[0])

            for i in range(1, len(sorted_intervals)):
                # 次の要素の終了時間が、これまでの最大終了時間より後ろであれば、
                # それは「包含されていない」新しい範囲（または一部重複）とみなす
                if sorted_intervals[i].ended_time > current_max_end:
                    result.append(sorted_intervals[i])
                    current_max_end = sorted_intervals[i].ended_time
                # 逆に ended_time が current_max_end 以下なら、
                # その要素は完全に包含されているので無視（削除）する

        return result

    def _filter_task_began_ended(
        self, mht_list: list[MhTask], began_time: time, ended_time: time, *, exclude_task: Optional[MhTask] = None
    ) -> list[MhTask]:
        """時間範囲を含むタスクを列挙する"""

        def _filter_task_began_ended_local(
            mht: MhTask, began_m: int, ended_m: int, *, exclude_task: Optional[MhTask] = None
        ) -> None:
            if mht.record_type != MhTaskType.BEGAN_ENDED:
                return
            if check_began_ended_leaf(mht) == True:
                mht_began_m = calc_minute_of_day(mht.began_time)
                mht_ended_m = calc_minute_of_day(mht.ended_time)
                if began_m <= mht_began_m and ended_m >= mht_ended_m:  # 含まれている?
                    result.append(mht)
                return
            for mht0 in mht.child_task:
                _filter_task_began_ended_local(mht0, began_m, ended_m, exclude_task=exclude_task)

        began_m = calc_minute_of_day(began_time)
        ended_m = calc_minute_of_day(ended_time)
        result: list[MhTask] = []
        for mht in mht_list:
            _filter_task_began_ended_local(mht, began_m, ended_m, exclude_task=exclude_task)

        return result

    def _parse_time_to_time(
        self, line: str, *, mht: Optional[MhTask] = None
    ) -> tuple[Optional[time], Optional[time], bool, str]:
        if mht is None:
            mht = MhTask()
        #
        began_only = False
        began_time: Optional[time] = None
        ended_time: Optional[time] = None
        remnant = line
        # TEXT判定
        if len(line) > 1 and line[0] in ['"', "'", "#"]:
            return (began_time, ended_time, began_only, remnant)
        # 時刻判定
        ## 4文字目が':'のときは、時刻ありとする。
        if line.startswith("-"):  # "-00:00"
            if len(line) <= 4 or line[3] != ":":
                return (began_time, ended_time, began_only, remnant)
        else:
            ## 3文字目が':'のときは、時刻ありとする。
            if len(line) <= 3 or line[2] != ":":  # "00:00"
                return (began_time, ended_time, began_only, remnant)
        # 開始時刻を省略
        if line.startswith("-"):  # "-00:00"
            line0 = line[1:]
            # 終了時刻
            result = re.match(r"^([01][0-9]|2[0-3]):[0-5][0-9]", line0)
            if result:
                s = line0[0:5]
                ended_time = datetime.strptime(s, "%H:%M").time()
                line = line0[5:]
            else:
                self.validation_error.append(
                    ValidationError(
                        level=ERROR,
                        message='時刻が不正です。reasen="書式不正"',
                        mht=mht,
                    )
                )
                return (None, None, False, "")
        else:
            # 開始時刻
            result = re.match(r"^([01][0-9]|2[0-3]):[0-5][0-9]", line)
            if result:
                s = line[0:5]
                began_time = datetime.strptime(s, "%H:%M").time()
                line = line[5:]
            else:
                self.validation_error.append(
                    ValidationError(
                        level=ERROR,
                        message='時刻が不正です。reasen="書式不正"',
                        mht=mht,
                    )
                )
                return (None, None, False, "")
            # '-'の判定
            if line.startswith("-"):
                line0 = line[1:]
                # 終了時刻
                if line0.startswith(" "):  # 終了時刻を省略。"00:00-"
                    line = line0  # '-'を削除
                else:
                    result = re.match(r"^([01][0-9]|2[0-3]):[0-5][0-9]", line0)
                    if result:
                        s = line0[0:5]
                        ended_time = datetime.strptime(s, "%H:%M").time()
                        line = line0[5:]
                    else:
                        self.validation_error.append(
                            ValidationError(
                                level=ERROR,
                                message='時刻が不正です。reasen="書式不正"',
                                mht=mht,
                            )
                        )
                        return (None, None, False, "")
            elif line.startswith(" "):  # "00:00"。開始時刻のみ
                began_only = True
        # 時刻とタイトルの区切り文字(スペース)のチェック
        if len(line) >= 1 and line[0] != " ":  # 時刻との隙間
            self.validation_error.append(
                ValidationError(
                    level=ERROR,
                    message='時刻タスクの書き方が不正です。reasen="時刻と作業タイトルの間にスペースが無い"',
                    mht=mht,
                )
            )
            return (None, None, False, "")
        # 作業タイトル
        line = line.strip()
        if len(line) == 0:
            self.validation_error.append(
                ValidationError(
                    level=ERROR,
                    message='作業タイトルがありません。reasen="時刻のみ"',
                    mht=mht,
                )
            )
            return (None, None, False, "")
        remnant = line
        return (began_time, ended_time, began_only, remnant)

    def _set_began_ended_default(self, mht_list: list[MhTask]) -> None:
        """開始・終了時刻の省略値を設定"""

        def _set_began_ended_default_local(mht_list: list[MhTask]) -> None:
            # 開始時刻または、終了時刻が無い場合
            before_mht: Optional[MhTask] = None  # 直前のMhTask
            for mht in mht_list:
                if mht.began_time is None and mht.ended_time is not None:  # "-00:00"
                    # 直前のタスクの終了時刻を設定する
                    if before_mht is None:
                        self.validation_error.append(
                            ValidationError(
                                level=ERROR,
                                message='開始時刻が省略されています。reasen="直前のタスクが有りません"',
                                mht=mht,
                            )
                        )
                        continue
                    if before_mht.indent == mht.indent:
                        # 同一レベル
                        if before_mht.record_type == MhTaskType.TIMESTAMP:
                            mht.began_time = before_mht.began_time
                        elif before_mht.record_type == MhTaskType.BEGAN_ENDED:
                            assert before_mht.ended_time is not None
                            mht.began_time = before_mht.ended_time
                        elif before_mht.record_type == MhTaskType.TEXT:
                            self.validation_error.append(
                                ValidationError(
                                    level=ERROR,
                                    message='開始時刻が省略されています。reasen="直前のタスクが、TEXT形式です",suggestion="直前のタスクを削除するか、インデントを追加してください"',
                                    mht=mht,
                                )
                            )
                            continue
                    else:  # 異なるインデント
                        self.validation_error.append(
                            ValidationError(
                                level=ERROR,
                                message='開始時刻が省略されています。reasen="直前のタスクとインデントが異なります"',
                                mht=mht,
                            )
                        )
                        continue
                before_mht = mht
            # 子タスク
            for mht in mht_list:
                # if len(mht.child_task):
                if check_began_ended_leaf(mht):
                    _set_began_ended_default_local(mht.child_task)
            pass

        #
        _set_began_ended_default_local(mht_list)

    def _task_parse_line(
        self,
        line: str,
        *,
        mht: Optional[MhTask] = None,
        logseq: bool = False,
    ) -> MhTask:
        if mht is None:
            mht = MhTask()
        # インデント
        tab_count = 0
        for c in line:
            if c == "\t":
                tab_count += 1
            else:
                break
        if tab_count != 0:
            mht.indent = tab_count
            line = line[tab_count:]
        # logset
        if logseq == True:
            if line.startswith("- "):
                line = line[2:]
        # 開始時刻-終了時刻
        mht.began_time, mht.ended_time, began_only, line = self._parse_time_to_time(line, mht=mht)
        # テキスト
        line = line.strip(" ")  # スペースのみ削除
        mht.line_text = line
        # 種別
        if mht.began_time is not None and mht.ended_time is not None:
            # "00:00-00:00"
            mht.record_type = MhTaskType.BEGAN_ENDED
            # バリデーション
            if mht.began_time == mht.ended_time:
                self.validation_error.append(
                    ValidationError(
                        level=ERROR,
                        message='開始時刻と終了時刻が間違っています。reasen="開始時刻と終了時刻が同じです"',
                        mht=mht,
                    )
                )
            if mht.began_time > mht.ended_time:
                self.validation_error.append(
                    ValidationError(
                        level=ERROR,
                        message='開始時刻と終了時刻が間違っています。reasen="開始時刻と終了時刻が逆転してます"',
                        mht=mht,
                    )
                )
        elif mht.began_time is None and mht.ended_time is None:
            # "作業"
            mht.record_type = MhTaskType.TEXT
        elif began_only == True:
            # "00:00"
            mht.record_type = MhTaskType.TIMESTAMP
        elif mht.began_time is not None and mht.ended_time is None:
            # "00:00-"
            self.validation_error.append(
                ValidationError(
                    level=ERROR,
                    message='終了時刻が省略されています。"',
                    mht=mht,
                )
            )
        else:
            # "-00:00"
            mht.record_type = MhTaskType.BEGAN_ENDED
        return mht

    def _task_parse(
        self,
        lines: list[str],
        *,
        file_name: str = "",
    ) -> list[MhTask]:
        result: list[MhTask] = []
        for index, line in enumerate(lines):
            mht = MhTask()
            mht.location = Location(file_name=file_name, line_no=index + 1)
            mht = self._task_parse_line(line, mht=mht)
            result.append(mht)
        return result

    def task_read(
        self,
        i_stream: IO[str],
        *,
        file_name: str = "",
        logseq: bool = False,
    ) -> list[MhTask]:
        lines = i_stream.read().splitlines()
        if logseq == True:
            lines = logseq_md_to_txt(lines)
        mht_list = self._task_parse(lines, file_name=file_name)
        return mht_list

    def task_read_str(
        self,
        text: str,
        *,
        file_name: str = "",
        logseq: bool = False,
    ) -> list[MhTask]:
        f = io.StringIO(text)
        return self.task_read(f, file_name=file_name, logseq=logseq)

    def task_summary(self, mht_list: list[MhTask]) -> list[MhTask]:
        # ツリー化
        mht_list = self._build_task_tree(mht_list)
        # 開始・終了時刻の省略値を設定
        self._set_began_ended_default(
            mht_list,
        )
        if check_validation_error(self.validation_error):
            return mht_list
        # バリデーション
        self.validation_error.extend(Validator(mht_list=mht_list).validation())
        if check_validation_error(self.validation_error):
            return mht_list
        # タスクの作業時間の分割
        self._division_task(mht_list)
        # 作業時間を求める
        self._calc_task_time(mht_list)
        return mht_list
