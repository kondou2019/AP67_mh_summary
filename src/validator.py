from logging import ERROR
from typing import Optional

from src.data_model import (
    MhTask,
    MhTaskListIterable,
    MhTaskType,
    ValidationError,
    ValidationError2,
    ValidationErrorBase,
    check_validation_error,
)
from src.task_utl import calc_minute_of_day, check_began_ended_leaf


class Validator:
    def __init__(self, *, mht_list: list[MhTask]):
        self.mht_list = mht_list
        #
        self.validation_error: list[ValidationErrorBase] = []
        self.mht_parent_dict: dict[int, Optional[MhTask]] = self._build_mht_parent_dict()  # 親のMhTaskの辞書
        pass

    def _build_mht_parent_dict(self) -> dict[int, Optional[MhTask]]:
        """!
        @brief 親MhTaskを取得
        @return dict[id(MhTask), 親のMhTask]
        """

        def _build_mht_parent_dict_local(parent_mht: MhTask) -> None:
            for mht in parent_mht.child_task:
                result[id(mht)] = parent_mht
                _build_mht_parent_dict_local(mht)

        #
        result: dict[MhTask, Optional[MhTask]] = {}
        for mht in self.mht_list:
            result[id(mht)] = None  # ルートの親はなし
            _build_mht_parent_dict_local(mht)
        return result

    def _get_mht_parent(self, mht: MhTask) -> Optional[MhTask]:
        """!
        @brief 親MhTaskを取得
        @param[in] path DBのファイル名
        @retval 親MhTask
        @retval None 親なし
        """
        return self.mht_parent_dict[id(mht)]

    def _validation_began_ended_1(self) -> None:
        """バリデーション。開始時刻,終了時刻(1行内)"""
        for mht in MhTaskListIterable(self.mht_list):
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

    def _validation_began_time_in_order_for_layer(self) -> None:
        """バリデーション。タスクの順番が不正"""

        def _validation_began_time_in_order_for_layer_local(mht_list: list[MhTask]) -> None:
            # 順番を確認
            mht1: Optional[MhTask] = None
            for mht in mht_list:
                if mht.began_time is None:
                    continue
                if mht1 is None:
                    mht1 = mht
                    continue
                if mht.began_time < mht1.began_time:
                    self.validation_error.append(
                        ValidationError2(
                            level=ERROR,
                            message=f'タスクの順番が不正です。reasen="開始時刻が逆転"',
                            mht1=mht1,
                            mht2=mht,
                        )
                    )
                mht1 = mht
            # 下位レイヤを確認
            for mht in mht_list:
                _validation_began_time_in_order_for_layer_local(mht.child_task)

        #
        _validation_began_time_in_order_for_layer_local(self.mht_list)

    def _validation_task_same_began_time(self) -> None:
        """バリデーション。開始時刻,終了時刻が同じ"""
        for mht1 in MhTaskListIterable(self.mht_list):
            if mht1.began_time is None or mht1.ended_time is None:
                continue
            if check_began_ended_leaf(mht1) == False:
                continue
            for mht2 in MhTaskListIterable(self.mht_list):
                if mht1 is mht2:  # 検査対象
                    continue
                if mht2.began_time is None or mht2.ended_time is None:
                    continue
                if check_began_ended_leaf(mht2) == False:
                    continue
                # 検査
                if mht1.began_time == mht2.began_time:
                    self.validation_error.append(
                        ValidationError2(
                            level=ERROR,
                            message=f'開始時刻が同じです。line_no={str(mht2.location.line_no) if mht2.location is not None else "-"}',
                            mht1=mht1,
                            mht2=mht2,
                        )
                    )
                if mht1.ended_time == mht2.ended_time:
                    self.validation_error.append(
                        ValidationError2(
                            level=ERROR,
                            message=f'終了時刻が同じです。line_no={str(mht2.location.line_no) if mht2.location is not None else "-"}',
                            mht1=mht1,
                            mht2=mht2,
                        )
                    )
                pass
            pass

    def _validation_overlap(self) -> None:
        """バリデーション。作業時間の重複。リーフのみ対象。ブランチは重複する。"""
        for mht1 in MhTaskListIterable(self.mht_list):
            if mht1.began_time is None or mht1.ended_time is None:
                continue
            if check_began_ended_leaf(mht1) == False:
                continue
            for mht2 in MhTaskListIterable(self.mht_list):
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
                            ValidationError2(
                                level=ERROR,
                                message=f"時間が重複しています。",
                                mht1=mht1,
                                mht2=mht2,
                            )
                        )
                pass
            pass

    def _validation_work_time_in_the_text(self) -> None:
        """バリデーション。テキストに、作業時間がある"""
        for mht in MhTaskListIterable(self.mht_list):
            if len(mht.child_task) != 0:
                continue
            if mht.record_type != MhTaskType.BEGAN_ENDED:
                continue
            # 最上位まで、BEGAN_ENDEDか確認
            mht_parent = self._get_mht_parent(mht)
            while mht_parent is not None:
                if mht_parent.record_type != MhTaskType.BEGAN_ENDED:
                    self.validation_error.append(
                        ValidationError2(
                            level=ERROR,
                            message=f"テキストに、作業時間を記録しています。",
                            mht1=mht_parent,
                            mht2=mht,
                        )
                    )
                mht = mht_parent
                mht_parent = self._get_mht_parent(mht)
        pass

    def _validation_within_of_parent_time_range(self) -> None:
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
                            ValidationError2(
                                level=ERROR,
                                message='親タスクの範囲外。reason="開始時刻"',
                                mht1=mht0,
                                mht2=mht,
                            )
                        )
                # 終了時刻をチェック
                if mht0.ended_time is not None:
                    ended0_m = calc_minute_of_day(mht0.ended_time)
                    if began_m <= ended0_m <= ended_m:
                        pass
                    else:
                        self.validation_error.append(
                            ValidationError2(
                                level=ERROR,
                                message='親タスクの範囲外。reason="終了時刻"',
                                mht1=mht0,
                                mht2=mht,
                            )
                        )
                #
                if mht0.began_time is not None and mht0.ended_time is not None:
                    began0_m = calc_minute_of_day(mht0.began_time)
                    ended0_m = calc_minute_of_day(mht0.ended_time)
                    _validation_within_of_parent_time_range_local(mht0, began0_m, ended0_m)

        #
        for mht in self.mht_list:
            if mht.began_time is not None and mht.ended_time is not None:
                began_m = calc_minute_of_day(mht.began_time)
                ended_m = calc_minute_of_day(mht.ended_time)
                _validation_within_of_parent_time_range_local(mht, began_m, ended_m)
        return

    def validation(self) -> list[ValidationErrorBase]:
        """バリデーション"""
        # 1行単位
        ## バリデーション。開始時刻,終了時刻が同じ
        self._validation_task_same_began_time()
        ## バリデーション。開始時刻,終了時刻(1行内)
        self._validation_began_ended_1()
        ## 中断
        if check_validation_error(self.validation_error):
            return self.validation_error

        # レイヤ単位
        ## バリデーション。タスクの順番が不正
        self._validation_began_time_in_order_for_layer()
        # 親子
        ## バリデーション。テキストに、作業時間がある
        self._validation_work_time_in_the_text()
        ## バリデーション。親タスクの時刻範囲に範囲に入っているか?
        self._validation_within_of_parent_time_range()
        ## バリデーション。作業時間の重複。リーフのみ対象。ブランチは重複する
        self._validation_overlap()

        return self.validation_error
