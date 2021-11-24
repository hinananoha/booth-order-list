# BOOTH注文リスト作成スクリプト
このPythonスクリプトは、BOOTHの「宛名印刷用CSV」から、
- 未発送の注文
- 今月の注文
- 特定期間の注文

を抽出した上で、各注文を商品毎に一覧化したCSVとして出力するスクリプトです。

# 簡単な使い方
## ダウンロード
通常は、[Relase](https://github.com/hinananoha/booth-order-list/releases/latest)から、`booth_order_list.exe` をダウンロードして使ってください。

## 実行
ダウンロードした `booth_order_list.exe` を宛名印刷用CSVファイルと同じフォルダに置いてください。

その後、宛名印刷用CSVファイルが置いてあるフォルダを開いた状態で、空いているところをShiftキーを押しながら右クリックして、「PowerShellウィンドをここで開く(S)」をクリックします。

青い画面（Powershell）が表示されたら、目的に応じて以下のコマンドを入力して下さい。

- 未発送の注文のリストが欲しい時(booth_orders_unshipped.csv に出力されます)
  - `booth_order_list.exe -f [宛名印刷用CSVファイルのファイル名] -o booth_orders_unshipped.csv -u`
- 今月の注文のリストが欲しい時(booth_orders_current.csv に出力されます)
  - `booth_order_list.exe -f [宛名印刷用CSVファイルのファイル名] -o booth_orders_current.csv -c`
- 特定期間の注文のリストが欲しい時(booth_orders_range.csv に出力されます)
  - 例：2021年10月1日 ~ 2021年10月10日まで
  - `booth_order_list.exe -f [宛名印刷用CSVファイルのファイル名] -o booth_orders_range.csv -r 2021-10-01 2021-10-10`
  - 最後の `2021-10-01 2021-10-10` を、必要な期間に置き換えて入力してください。

何も表示されず、次の入力が出来る状態になったら出力完了です。フォルダを確認して下さい。

## 出力
出力されたCSVは、以下のような形式で表示されます。

| 注文番号 | 注文日時 | 注文の状態 | (商品名A) | (商品名B) | ...... |
| ------- | ------- | ------- | ------- | ------- | ------- |
| 0123456 | 2021-10-01 12:10:14 | 支払済み | 0 | 1 | ... |
| 0123476 | 2021-10-01 12:16:01 | 支払待ち | 1 | 2 | ... |

商品名が書かれた列に記載の数字は、その注文で注文された商品の数量です。

このCSVファイルをExcelで開くことで、大量の注文があった際の注文リスト生成や、月ごとの商品毎の注文数の集計などが可能となります。

# コマンドのオプションの説明
```
usage: booth_order_list.exe [-h] -f FILE -o OUTPUT [-u] [-c] [-r RANGE RANGE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  BOOTHから出力された宛名印刷用CSVファイルのファイル名（必須）
  -o OUTPUT, --output OUTPUT
                        出力するCSVファイルのファイル名（必須）
  -u, --unshipped       未発送の注文のリストを出力
  -c, --current-month   今月の注文のリストを出力
  -r RANGE RANGE, --range RANGE RANGE
                        指定した期間の注文リストを出力(YYYY-MM-DD YYYY-MM-DDで指定)
```
## ヘルプの表示
- `booth_order_list.exe -h`
  - 上に記述したヘルプが表示されます。

## リストの出力（標準）
- `booth_order_list.exe -f FILE -o OUTPUT`
- `booth_order_list.exe --file FILE --output OUTPUT`
  - `FILE`に指定したBOOTHの宛名印刷用CSVをこのプログラムで商品毎のリストに書き換えて`OUTPUT`に指定したファイルに出力します。
  - 上の `-h` オプションを付ける場合以外は `-f FILE -o OUTPUT`は必ず入力が必要です。

## 未発送の注文の出力
- `booth_order_list.exe -f FILE -o OUTPUT -u`
- `booth_order_list.exe --file FILE --output OUTPUT --unshipped`
  - `FILE`に指定したBOOTHの宛名印刷用CSVに書かれた注文のうち、現在の注文の状況が「支払待ち」か「支払済み」の注文（未発送の注文）だけ取り出し、商品毎のリストに書き換えて`OUTPUT`に指定したファイルに出力します。
  - 商品数の多い店舗で大量の注文が来たときに、わかりやすい注文リストが欲しい時に重宝します（作成者は当初これが欲しくて作りました）。

## 今月の注文の出力
- `booth_order_list.exe -f FILE -o OUTPUT -c`
- `booth_order_list.exe --file FILE --output OUTPUT --current-month`
  - `FILE`に指定したBOOTHの宛名印刷用CSVに書かれた注文のうち、今月の注文だけ抽出し（発送/未発送問わず）、商品毎のリストに書き換えて`OUTPUT`に指定したファイルに出力します。
  - 今月どの商品がどのくらい注文されたかリスト化したい際に重宝します。

## 特定期間の注文の出力
- `booth_order_list.exe -f FILE -o OUTPUT -r START_DATE END_DATE`
- `booth_order_list.exe --file FILE --output OUTPUT --range START_DATE END_DATE`
  - `FILE`に指定したBOOTHの宛名印刷用CSVに書かれた注文のうち、`START_DATE` から `END_DATE` の間に注文された商品のみ抽出し（発送/未発送問わず）、商品毎のリストに書き換えて`OUTPUT`に指定したファイルに出力します。
  - `START_DATE`及び`END_DATE`は、"年-月-日"の形式で書きます（例：2021-01-04）
  - 「今月の注文の出力」の発展版です。

# 注意事項
このスクリプトはPixiv/BOOTH公式及び公認のスクリプトではございません。そのため、Pixiv/BOOTH側の仕様変更により、突然利用できなくなる場合がございます。予めご了承下さい。（その際は是非Issueを立てていただけると幸いです）

このプログラムは個人が作成した物です。このプログラムをダウンロード・実行等した事によって発生する一切の事象について制作者は一切の責任を負いかねます。


# 詳しい人向けの説明
以下、このスクリプトを使って色々なことをしたい、上級者向けの説明です。

## Requirement (Tested environment)
- Python 3.7 or greater than
  - tested env
    - ubuntu 18.04 (Python 3.6.9)
    - Windows 10 x64 (Python 3.9.2)
  - cannot run python 2.x
- Library: Standard library
  - os, csv, argparse, datetime, re

## run
This script can run without build.

```
usage: booth_order_list.py [-h] -f FILE -o OUTPUT [-u] [-c] [-r RANGE RANGE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  BOOTHから出力された宛名印刷用CSVファイルのファイル名（必須）
  -o OUTPUT, --output OUTPUT
                        出力するCSVファイルのファイル名（必須）
  -u, --unshipped       未発送の注文のリストを出力
  -c, --current-month   今月の注文のリストを出力
  -r RANGE RANGE, --range RANGE RANGE
                        指定した期間の注文リストを出力(YYYY-MM-DD YYYY-MM-DDで指定)
```

## build
Build using "pyinstaller" in this repository release.

`pyinstaller booth_order_list.py --onefile`


# 作成者
* 作成者: hinananoha
* 所属： Ureshino Network Service
* 連絡先: info[@]ureshino.dev / [Twitter @hinananoha](https://twitter.com/hinananoha)

# License
The source code is licensed MIT.
