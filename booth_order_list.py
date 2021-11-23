import csv
import os
import argparse
import datetime
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', help='BOOTHから出力された宛名印刷用CSVファイルのファイル名（必須）', required=True)
    parser.add_argument(
        '-o', '--output', help='出力するCSVファイルのファイル名（必須）', required=True)
    parser.add_argument('-u', '--unshipped',
                        action='store_true', help='未発送の注文のリストを出力')
    parser.add_argument('-c', '--current-month',
                        action='store_true', help='今月の注文のリストを出力')
    parser.add_argument('-r', '--range', nargs=2,
                        help='指定した期間の注文リストを出力(YYYY-MM-DD YYYY-MM-DDで指定)')

    args = parser.parse_args()

    filename = args.file
    if not os.path.isfile(filename):
        raise FileExistsError('File is not found.')

    with open(filename, 'r', encoding='utf-8_sig') as f:
        csv_data = csv.reader(f)
        data = [e for e in csv_data]

    if not data:
        raise ValueError('CSV file is empty or not csv file.')
    elif not len(data[0]) == 15:
        raise ValueError('This csv file is not booth order file.')

    date_range = []
    if args.range:
        for date_str in args.range:
            if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date_str):
                raise ValueError('-r/--range option input is invalid.')
            else:
                date_range.append(datetime.datetime.strptime(date_str, '%Y-%m-%d'))

    if args.current_month:
        dt_now = datetime.datetime.now()
        start_date = datetime.datetime(dt_now.year, dt_now.month, 1)
        if dt_now.month == 12:
            end_date = datetime.datetime(dt_now.year+1, 1, 1)
        else:
            end_date = datetime.datetime(dt_now.year, dt_now.month+1, 1)
        date_range = [start_date, end_date]

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
        if date_range:
            if datetime.datetime.strptime(order[4], '%Y-%m-%d  %H:%M:%S') < date_range[0] or datetime.datetime.strptime(order[4], '%Y-%m-%d  %H:%M:%S') >= date_range[1]:
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
