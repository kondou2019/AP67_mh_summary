from typing import Optional

from src.data_model import (
    MhTask,
    MhTaskType,
)


def mh_task_print5(
    mht_list: list[MhTask],
    o_stream,
    *,
    header: bool = True,
    task_date: Optional[str] = None,
) -> None:
    """集計5 チケット外の作業を"チケット;担当"で出力"""
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
        elif "集計" in mht.tag_dict:
            o_stream.write(
                f"{task_date_column}{mht.tag_dict["task_type"]}\t{mht.tag_dict["ticket_id"]}\t{mht.task_time}\n"
            )
        else:
            o_stream.write(f"{task_date_column}{'チケット外'}\t{mht.line_text}\t{mht.task_time}\n")
    o_stream.write("\t====チケット作業====\n")
    # 集計項目の出力。チケット番号順に出力
    for k in sorted(ticket_dict.keys()):
        v = ticket_dict[k]
        o_stream.write(f"{task_date_column}{'チケット;担当'}\t{k}\t{v}\n")
    for k in sorted(ticket_review_dict.keys()):
        v = ticket_review_dict[k]
        o_stream.write(f"{task_date_column}{'チケット;レビュー'}\t{k}\t{v}\n")
