#!/usr/bin/env python3

# household-ledger-calculate.py

import getopt
import sys
import sqlite3

household_ledger_name = "2022_household_ledger"
usage_string = '''Usage: household-ledger-calculate.py [command] [value]

  This script is for writing household ledger

  Options:

    -h --help : print this help
    -m --month : get result of month
    -y --year : get result ot year

  Documentation:
  #TODO:

'''

def cal_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t

    avg = sum_num / len(num)
    return avg

class Accountant:
    def __init__(self):
        self.table_name = household_ledger_name

    def __enter__(self):
        self.db = sqlite3.connect("./db/account_book.db")
        self.cur = self.db.cursor()

        self.cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='%s'" % self.table_name)

        if self.cur.fetchone()[0] != 1:
            print("Table does not exist. So we make new one.")
            self.cur.execute("CREATE TABLE '%s'(id INTEGER, date TEXT, name TEXT, cost INTEGER, category INTEGER)" % self.table_name)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

    def caculate(self, account_list):
        # 식비
        food_fee = []
        # 간식비
        snack_fee = []
        # 고정지출
        fix_cost = []
        # 변동지출
        change_cost = []

        for item in account_list:
            if item[4] == 1:
                food_fee.append(item[3])
            elif item[4] == 2:
                snack_fee.append(item[3])
            elif item[4] == 3:
                fix_cost.append(item[3])
            elif item[4] == 4:
                change_cost.append(item[3])

        print(f"식비 : {format(sum(food_fee), ',')}")
        print(f"간식비 : {format(sum(snack_fee), ',')}")
        print(f"고정지출 : {format(sum(fix_cost), ',')}")
        print(f"변동지출 : {format(sum(change_cost), ',')}")

    def get_month_result(self, month):
        self.cur.execute("SELECT * FROM '%s' WHERE id='%s'" % (self.table_name, month))
        account_list = self.cur.fetchall()
        self.caculate(account_list)

    def get_year_result(self):
        self.cur.execute("SELECT * FROM '%s'" % self.table_name)
        account_list = self.cur.fetchall()
        self.caculate(account_list)

def print_usage_and_exit():
    print(usage_string)
    sys.exit(2)

if __name__ == "__main__":
    try:
        short_flags = 'hm:y'
        long_flags = ['help', 'month=', 'year']

        opts, args = getopt.gnu_getopt(sys.argv[1:], short_flags, long_flags)
    except getopt.GetoptError:
        print_usage_and_exit()

    with Accountant() as accountant:
        for o, a in opts:
            if o in ('-h', '--help'):
                print_usage_and_exit()
            if o in ('-m', '--month'):
                accountant.get_month_result(a)
            if o in ('-y', '--year'):
                accountant.get_year_result()