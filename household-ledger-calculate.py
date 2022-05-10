#!/usr/bin/env python3

# household-ledger-calculate.py

import os
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

class Accountant:
    def __init__(self):
        self.table_name = household_ledger_name

    def __enter__(self):
        db_directory = "./db"

        try:
            if not os.path.exists(db_directory):
                os.makedirs(db_directory)
        except OSError:
            print (f"Error: Creating directory. {db_directory}")
            sys.exit(2)

        self.db = sqlite3.connect("./db/account_book.db")
        self.cur = self.db.cursor()

        self.cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='%s'" % self.table_name)

        if self.cur.fetchone()[0] != 1:
            print("Table does not exist. So we make new one.")
            self.cur.execute("CREATE TABLE '%s'(id INTEGER, date TEXT, name TEXT, cost INTEGER, category INTEGER)" % self.table_name)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

    def caculate_total(self, account_list):
        # 식비
        food_fee = sum([item[3] for item in account_list if item[4] == 1])
        # 간식비
        snack_fee = sum([item[3] for item in account_list if item[4] == 2])
        # 고정지출
        fix_cost = sum([item[3] for item in account_list if item[4] == 3])
        # 변동지출
        change_cost = sum([item[3] for item in account_list if item[4] == 4])

        total_fee = food_fee + snack_fee + fix_cost + change_cost

        print(f"식비 : {format(food_fee, ',')}")
        print(f"간식비 : {format(snack_fee, ',')}")
        print(f"고정지출 : {format(fix_cost, ',')}")
        print(f"변동지출 : {format(change_cost, ',')}")
        print(f"총합 : {format(total_fee, ',')}")

        return total_fee

    def caculate_per_day(self, account_list):
        # Deduplication using set
        days_list = list(set([item[1] for item in account_list]))
        days_list.sort()

        total_fee = 0

        for day in days_list:
            day_cost = sum(int(item[3]) for item in account_list if day == item[1])
            total_fee += day_cost

            print(f"{day} : {format(day_cost, ',')}")
        print(f"총합 : {format(total_fee, ',')}")

        return total_fee

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

        print("[일일 결산]---------------------------")
        result_by_day = self.caculate_per_day(account_list)
        print("[주간 결산]---------------------------")
        result_by_week = self.caculate_total(account_list)
        print("--------------------------------------")

        if result_by_day == result_by_week:
            print("일일 총합과 주간 총합이 일치 합니다.")
        else:
            print("일일 총합과 주간 총합이 일치 하지 않습니다. 문제가 있습니다.")

    def get_month_result(self, month):
        self.cur.execute("SELECT * FROM '%s' WHERE id='%s'" % (self.table_name, month))
        account_list = self.cur.fetchall()
        self.caculate_total(account_list)

    def get_year_result(self):
        self.cur.execute("SELECT * FROM '%s'" % self.table_name)
        account_list = self.cur.fetchall()
        self.caculate_total(account_list)

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
