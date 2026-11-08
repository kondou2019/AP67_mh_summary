from typing import Optional

from src.data_model import (
    MhTask,
    MhTaskListIterable,
    MhTaskType,
)
from src.task_utl import check_began_ended_leaf


def mh_task_print6(mht_list: list[MhTask], o_stream, *, header: bool = True, task_date: str = "") -> None:
    """集計6 工程別集計"""
    # CSVヘッダ
    if header == True:
        o_stream.write("task_date\tbegan_time\tended_time\ttask_time\tticket_id\tprocess_type\tline_text\n")
    # 集計
    ticket_id = ""
    for mht in MhTaskListIterable(mht_list):
        if mht.record_type != MhTaskType.BEGAN_ENDED:
            continue
        # チケット識別子の取得。ルートタスクの時に更新
        if mht in mht_list:  # ルートタスク?
            ticket_id = ""
            if "チケット" in mht.tag_dict:
                ticket_id = mht.tag_dict["チケット"]
            else:
                ticket_id = mht.line_text
        # リーフタスクのみ出力
        if check_began_ended_leaf(mht) == False:
            continue
        #
        assert mht.began_time is not None
        assert mht.ended_time is not None
        o_stream.write(
            f"{task_date}\t{mht.began_time.strftime("%H:%M")}\t{mht.ended_time.strftime("%H:%M")}\t{mht.task_time}\t{ticket_id}\t\t{mht.line_text}\n"
        )
