from logging import ERROR
from typing import Optional

from src.data_model import (
    MhTask,
    MhTaskListIterable,
    MhTaskType,
    ValidationError,
    ValidationErrorBase,
    check_validation_error,
)
from src.task_utl import calc_minute_of_day, check_began_ended_leaf


class Validator:
    def __init__(self):
        self.validation_error: list[ValidationErrorBase] = []
        pass

    def _validation_began_ended_1(self, task_list: list[MhTask]) -> None:
        """バリデーション。開始時刻,終了時刻(1行内)"""
        for mht in MhTaskListIterable(task_list):
            if mht.began_time is None or mht.ended_time is None:
                continue
            if mht.began_time == mht.ended_time:
                self.validation_error.append(
                    ValidationError(
                        level=ERROR,
                        message=f'時刻が不正です。reasen="開始時刻と終了時刻が同じ"',
                        mht=mht,
                    )
                )
            if mht.began_time > mht.ended_time:
                self.validation_error.append(
                    ValidationError(
                        level=ERROR,
                        message=f'時刻が不正です。reasen="開始時刻と終了時刻が逆転"',
                        mht=mht,
                    )
                )

    def _validation_task_same_began_time(self, task_list: list[MhTask]) -> None:
        """バリデーション。開始時刻,終了時刻が同じ"""
        for mht1 in MhTaskListIterable(task_list):
            if mht1.began_time is None or mht1.ended_time is None:
                continue
            if check_began_ended_leaf(mht1) == False:
                continue
            for mht2 in MhTaskListIterable(task_list):
                if mht1 is mht2:  # 検査対象
                    continue
                if mht2.began_time is None or mht2.ended_time is None:
                    continue
                if check_began_ended_leaf(mht2) == False:
                    continue
                # 検査
                if mht1.began_time == mht2.began_time:
                    self.validation_error.append(
                        ValidationError(
                            level=ERROR,
                            message=f'開始時刻が同じです。line_no={str(mht2.location.line_no) if mht2.location is not None else "-"}',
                            mht=mht1,
                        )
                    )
                if mht1.ended_time == mht2.ended_time:
                    self.validation_error.append(
                        ValidationError(
                            level=ERROR,
                            message=f'終了時刻が同じです。line_no={str(mht2.location.line_no) if mht2.location is not None else "-"}',
                            mht=mht1,
                        )
                    )
                pass
            pass

    def _validation_overlap(self, task_list: list[MhTask]) -> None:
        """バリデーション。作業時間の重複。リーフのみ対象。ブランチは重複する。"""
        for mht1 in MhTaskListIterable(task_list):
            if mht1.began_time is None or mht1.ended_time is None:
                continue
            if check_began_ended_leaf(mht1) == False:
                continue
            for mht2 in MhTaskListIterable(task_list):
                if mht1 is mht2:  # 検査対象
                    continue
                if mht2.began_time is None or mht2.ended_time is None:
                    continue
                if check_began_ended_leaf(mht2) == False:
                    continue
                # 検査
                if mht1.began_time < mht2.began_time < mht1.ended_time:
                    if mht2.ended_time > mht1.ended_time:
                        self.validation_error.append(
                            ValidationError(
                                level=ERROR,
                                message=f'時間が重複しています。line_no={str(mht2.location.line_no) if mht2.location is not None else "-"}',
                                mht=mht1,
                            )
                        )
                pass
            pass

    def _validation_within_of_parent_time_range(self, mht_list: list[MhTask]) -> None:
        """バリデーション。親タスクの時刻範囲に範囲に入っているか?"""

        def _validation_within_of_parent_time_range_local(mht: MhTask, began_m: int, ended_m: int) -> None:
            for mht0 in mht.child_task:
                # 開始時刻をチェック
                if mht0.began_time is not None:
                    began0_m = calc_minute_of_day(mht0.began_time)
                    if began_m <= began0_m <= ended_m:
                        pass
                    else:
                        self.validation_error.append(
                            ValidationError(
                                level=ERROR,
                                message=f'親タスクの範囲外。reason="開始時刻", line_no={str(mht0.location.line_no) if mht0.location is not None else "-"}',
                                mht=mht,
                            )
                        )
                # 終了時刻をチェック
                if mht0.ended_time is not None:
                    ended0_m = calc_minute_of_day(mht0.ended_time)
                    if began_m <= ended0_m <= ended_m:
                        pass
                    else:
                        self.validation_error.append(
                            ValidationError(
                                level=ERROR,
                                message=f'親タスクの範囲外。reason="終了時刻", line_no={str(mht0.location.line_no) if mht0.location is not None else "-"}',
                                mht=mht,
                            )
                        )
                #
                if mht0.began_time is not None and mht0.ended_time is not None:
                    began0_m = calc_minute_of_day(mht0.began_time)
                    ended0_m = calc_minute_of_day(mht0.ended_time)
                    _validation_within_of_parent_time_range_local(mht0, began0_m, ended0_m)

        #
        for mht in mht_list:
            if mht.began_time is not None and mht.ended_time is not None:
                began_m = calc_minute_of_day(mht.began_time)
                ended_m = calc_minute_of_day(mht.ended_time)
                _validation_within_of_parent_time_range_local(mht, began_m, ended_m)
        return

    def validation(self, mht_list: list[MhTask]) -> list[ValidationErrorBase]:
        """バリデーション"""
        # 1行単位
        ## バリデーション。開始時刻,終了時刻が同じ
        self._validation_task_same_began_time(mht_list)
        if check_validation_error(self.validation_error):
            return self.validation_error
        ## バリデーション。開始時刻,終了時刻(1行内)
        self._validation_began_ended_1(mht_list)
        if check_validation_error(self.validation_error):
            return self.validation_error

        # 親子
        ## バリデーション。親タスクの時刻範囲に範囲に入っているか?
        self._validation_within_of_parent_time_range(mht_list)
        if check_validation_error(self.validation_error):
            return self.validation_error
        ## バリデーション。作業時間の重複。リーフのみ対象。ブランチは重複する
        self._validation_overlap(mht_list)
        if check_validation_error(self.validation_error):
            return self.validation_error

        return self.validation_error
