import io
from datetime import time
from typing import IO

from src.data_model import (
    MhTask,
    MhTaskType,
)


def calc_minute_of_day(tm: time) -> int:
    """!
    @brief Time オブジェクトから、00:00 からの経過分を計算する
    @return
    """
    return tm.hour * 60 + tm.minute


def check_began_ended_leaf(mht: MhTask) -> bool:
    """!
    @brief リーフタスクか判定
    @return True リーフ
    @return False 以外
    """

    def check_began_ended_leaf_local(mht: MhTask) -> bool:
        if mht.record_type == MhTaskType.BEGAN_ENDED and len(mht.child_task) == 0:
            return True
        for mht0 in mht.child_task:
            if mht0.record_type == MhTaskType.BEGAN_ENDED:
                return False
            b = check_began_ended_leaf_local(mht0)
            if b == False:
                return False
        return True

    #
    return check_began_ended_leaf_local(mht)


def format_mht_list(mht_list: list[MhTask], *, output_task_time: bool = False) -> str:
    def _debug_format_task_local(mht: MhTask, indent: int, i_stream: IO[str]) -> None:
        indent_s = "\t" * indent
        time_s = ""
        if mht.record_type == MhTaskType.BEGAN_ENDED:
            began_s = mht.began_time.strftime("%H:%M")
            began_e = mht.ended_time.strftime("%H:%M")
            time_s = f"{began_s}-{began_e} "
        elif mht.record_type == MhTaskType.TIMESTAMP:
            began_s = mht.began_time.strftime("%H:%M")
            time_s = f"{began_s} "
        # 出力
        if output_task_time == True:
            i_stream.write(f"{mht.task_time}\t{indent_s}{time_s}{mht.line_text}\n")
        else:
            i_stream.write(f"{indent_s}{time_s}{mht.line_text}\n")
        #
        for mht0 in mht.child_task:
            _debug_format_task_local(mht0, indent + 1, f)
        return

    #
    f = io.StringIO(newline="")
    for mht in mht_list:
        _debug_format_task_local(mht, 0, f)
    s = f.getvalue()  # 内容の取得
    f.close()
    return s
