from __future__ import annotations
import csv
import os
import argparse
import datetime
from typing import Optional
import datetime
import calendar
import json


class Period(object):
    """
    期間を表す。
    期間の開始時間や終了時間はなくてかまわない。
    なので、「2020/10/10 まで」のようなものもあらわすこともできるし、
    「2020/10/10 以降」のようなものもあらわせる。
    また、期限なしということも表現できる。
    """

    def __init__(
        self,
        begin: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None
    ):
        """
        begin: 期限の開始時間。 None は開始日がないことを表す
        end: 期限の終了日。 None は終了日がないことを表す
        """
        if not (isinstance(begin, datetime.datetime) or begin is None):
            raise ValueError(
                f"begin type is not datetime.datetime: {type(begin).__name__}")
        if not (isinstance(end, datetime.datetime) or end is None):
            raise ValueError(
                f"end type is not datetime.datetime: {type(end).__name__}")
        if all(map(lambda i: isinstance(i, datetime.datetime), [begin, end])) and begin > end:
            raise ValueError(f"begin > end: begin = {begin}, end = {end}")

        self.__begin = begin
        self.__end = end

    @property
    def begin(self) -> Optional[datetime.datetime]:
        """
        期間の開始時間
        """
        return self.__begin

    @property
    def end(self) -> Optional[datetime.datetime]:
        """
        期間の終了時間
        """
        return self.__end

    @classmethod
    def from_str(cls, begin: Optional[str] = None, end: Optional[str] = None) -> Period:
        """
        文字列から組み立てる。それぞれの文字列は最終的に
        datetime.datetime.strptime によって "%Y-%m-%d"
        のようにパースされる

        begin: 期限の開始時間。 None は開始日がないことを表す
        end: 期限の終了日。 None は終了日がないことを表す
        """
        if not (isinstance(begin, str) or begin is None):
            raise ValueError(f"begin type is not str: {type(begin).__name__}")
        if not (isinstance(end, str) or end is None):
            raise ValueError(f"end type is not str: {type(end).__name__}")

        def to_datetime(s: Optional[str]) -> Optional[datetime.datetime]:
            return None if s is None else datetime.datetime.strptime(s, "%Y-%m-%d")

        return cls(to_datetime(begin), to_datetime(end))

    def __str__(self):
        return f"{self.begin} ~ {self.end}"

    def __contains__(self, date: datetime.datetime) -> bool:
        if not isinstance(date, datetime.datetime):
            raise ValueError(
                f"date type is not datetime.datetime: {type(date).__name__}")
        elif self.begin is None and self.end is None:
            # 開始時間も終了時間も指定されてないならどんな日程が渡されても期間内
            return True
        elif self.begin is None:
            # 開始時間が指定されてないなら終了時間だけ見ればよい
            return date <= self.end
        elif self.end is None:
            # 終了時間が指定されてないなら開始時間だけ見ればよい
            return self.begin <= date
        return self.begin <= date <= self.end


def parse_period(period: str) -> Period:
    """
    渡された文字列を period にパースする。

    渡される文字列の形式としては以下の形を仮定する。
    - { "type": "current-month" }: 今月が期間として指定された
    - { "type": "period", "begin": "%Y-%m-%d", "end": "%Y-%m-%d" }: ある一定の期間が指定された
        + begin や end といったプロパティはオプショナル
    """
    if not isinstance(period, str):
        ValueError(f"period type is not str: {type(period).__name__}")

    typ = json.loads(period)
    if "type" not in typ:
        raise KeyError("period format must be {\"type\": type, ...}")

    if typ["type"] == "current-month":
        today = datetime.datetime.today()
        _, last_day = calendar.monthrange(today.year, today.month)
        begin = datetime.datetime.combine(
            datetime.datetime(today.year, today.month, 1),
            datetime.time.min
        )
        end = datetime.datetime.combine(
            datetime.datetime(today.year, today.month, last_day),
            datetime.time.max,
        )
        return Period(begin, end)
    elif typ["type"] == "period":
        begin = typ["begin"] if "begin" in typ else None
        end = typ["end"] if "end" in typ else None
        return Period.from_str(begin, end)

    raise KeyError("unknown period type: {}".format(period))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', help='BOOTHから出力された宛名印刷用CSVファイルのファイル名（必須）', required=True)
    parser.add_argument(
        '-o', '--output', help='出力するCSVファイルのファイル名（必須）', required=True)
    parser.add_argument('-u', '--unshipped',
                        action='store_true', help='未発送の注文のリストを出力')
    parser.add_argument('-r', '--range', type=parse_period, action='store',
                        help='対象期間を指定する。ここで指定した対象期間内の注文リストが出力される')

    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8_sig') as f:
        csv_data = csv.reader(f)
        data = [e for e in csv_data]

    if not data:
        raise ValueError('CSV file is empty or not csv file.')
    elif not len(data[0]) == 15:
        raise ValueError('This csv file is not booth order file.')

    period: Optional[Period] = args.range

    order_data = data[1:]
    create_data = []
    order_books = []
    books = {}
    for order in order_data:
        if not order[0]:
            continue
        if args.unshipped:
            if not order[3] == '支払済み':
                if not order[3] == '支払待ち':
                    continue
        else:
            if order[3] == 'キャンセル':
                continue
        if period is not None:
            order_time = datetime.datetime.strptime(
                order[4], '%Y-%m-%d  %H:%M:%S')
            if order_time not in period:
                continue
        order_infos = {}
        for order_info in order[14].split('\n'):
            order_details = {}
            for order_detail in order_info.split(' / '):
                key = order_detail.split(' : ')[0]
                if len(order_detail.split(' : ')) == 1:
                    key = 'name'
                    value = order_detail.split(' : ')[0]
                else:
                    key = order_detail.split(' : ')[0]
                    value = order_detail.split(' : ')[1]
                if key == '商品ID':
                    order_details['id'] = value
                elif key == '数量':
                    order_details['times'] = value
                elif key == 'name':
                    order_details['name'] = value
            if str(order_details['id']) not in books:
                books[str(order_details['id'])] = order_details['name']
            order_infos[order_details['id']] = order_details['times']

        order_books.append({
            'id': order[0],
            'date': order[4],
            'paid': order[3],
            'order': order_infos
        })

    header = ['注文番号', '注文日時', '支払い状況']
    for book_name in books.values():
        header.append(book_name)
    create_data.append(header)

    for order_book in order_books:
        data = [order_book['id'], order_book['date'], order_book['paid']]
        for book_id, book_name in books.items():
            if book_id in order_book['order']:
                data.append(order_book['order'][book_id])
            else:
                data.append(0)
        create_data.append(data)

    with open(args.output, 'w', encoding='shift_jis', newline="") as f:
        writer = csv.writer(f)
        writer.writerows(create_data)


if __name__ == '__main__':
    main()
