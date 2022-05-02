#!/usr/bin/env python3

# household-ledger-calculate.py

import getopt
import sys
import sqlite3
import datetime
from datetime import timedelta

household_ledger_name = "2022_household_ledger"
usage_string = '''Usage: household-ledger-calculate.py [command] [value]

  This script is for writing household ledger

  Options:

    -h --help : print this help
    -w --week : get result ot last week
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
        food_fee_list = []
        # 간식비
        snack_fee_list = []
        # 고정지출
        fix_cost_list = []
        # 변동지출
        change_cost_list = []

        for item in account_list:
            if item[4] == 1:
                food_fee_list.append(item[3])
            elif item[4] == 2:
                snack_fee_list.append(item[3])
            elif item[4] == 3:
                fix_cost_list.append(item[3])
            elif item[4] == 4:
                change_cost_list.append(item[3])

        food_fee = sum(food_fee_list)
        snack_fee = sum(snack_fee_list)
        fix_cost = sum(fix_cost_list)
        change_cost = sum(change_cost_list)
        total_fee = food_fee + snack_fee + fix_cost + change_cost

        print(f"식비 : {format(food_fee, ',')}")
        print(f"간식비 : {format(snack_fee, ',')}")
        print(f"고정지출 : {format(fix_cost, ',')}")
        print(f"변동지출 : {format(change_cost, ',')}")
        print(f"총합 : {format(total_fee, ',')}")

    def get_last_7days(self):
        date_list = []
        cnt = 0

        today = datetime.datetime.now()
        day = timedelta(days=1)

        for i in range(7):
            date_list.append(f"{str(today.year).zfill(4)}-{str(today.month).zfill(2)}-{str(today.day).zfill(2)}")
            today -= day

        return date_list

    def get_week_result(self):
        date_list = self.get_last_7days()
        account_list = []

        for date in date_list:
            self.cur.execute("SELECT * FROM '%s' WHERE date='%s'" % (self.table_name, date))
            result_list = self.cur.fetchall()

            if result_list:
                account_list += result_list
        self.caculate(account_list)

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
        short_flags = 'hwm:y'
        long_flags = ['help', 'week', 'month=', 'year']

        opts, args = getopt.gnu_getopt(sys.argv[1:], short_flags, long_flags)
    except getopt.GetoptError:
        print_usage_and_exit()

    with Accountant() as accountant:
        for o, a in opts:
            if o in ('-h', '--help'):
                print_usage_and_exit()
            if o in ('-w', '--week'):
                accountant.get_week_result()
            if o in ('-m', '--month'):
                accountant.get_month_result(a)
            if o in ('-y', '--year'):
                accountant.get_year_result()
