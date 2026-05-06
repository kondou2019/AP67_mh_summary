import io

from src.data_model import (
    MhTask,
    MhTaskListIterable,
)
from src.task_utl import calc_minute_of_day, check_began_ended_leaf


class MhTaskSort:

    def __init__(self):
        pass

    def sort_began_time(self, mht_list: list[MhTask]) -> list[MhTask]:
        """!
        @brief 開始時刻でソートされたリストを作成する
        @return list[MhTask] リーフタスクのリスト
        """
        # リーフタスクのリストを作成
        leaf_mht_list: list[MhTask] = []
        for mht in MhTaskListIterable(mht_list):
            if mht.began_time is None or mht.ended_time is None:
                continue
            if check_began_ended_leaf(mht) == False:
                continue
            leaf_mht_list.append(mht)
        # 開始時刻でソート
        result = sorted(leaf_mht_list, key=lambda x: x.began_time)
        return result

    def format_began_time(self, mht_list: list[MhTask]) -> str:
        """!
        @brief 開始時刻でソートされたリストをフォーマットする
        @return str
        """
        with io.StringIO(newline="") as f:
            before_mht = mht_list[0]
            assert before_mht.began_time is not None
            before_min = calc_minute_of_day(before_mht.began_time)  # 最初の表示を0にするためにbegan_timeで計算する
            for mht in mht_list:
                began_s = mht.began_time.strftime("%H:%M")
                began_e = mht.ended_time.strftime("%H:%M")
                assert before_mht.began_time is not None
                current_min = calc_minute_of_day(mht.began_time)
                diff_min = current_min - before_min
                f.write(f"{began_s}\t{began_e}\t{diff_min}\t{mht.line_text}\n")
                before_mht = mht
                assert before_mht.ended_time is not None
                before_min = calc_minute_of_day(before_mht.ended_time)
            s = f.getvalue()  # 内容の取得
        return s
