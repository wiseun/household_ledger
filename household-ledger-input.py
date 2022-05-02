#!/usr/bin/env python3

# household-ledger-input.py

import getopt
import sys
import sqlite3
import datetime
from datetime import timedelta

household_ledger_name = "2022_household_ledger"
usage_string = '''Usage: household-ledger-input.py [command] [value]

  This script is for writing household ledger
  This script add note to data base

  Options:

    -h --help : print this help
    -f --file : input file to db
    -t --text : input text to db
    -p --print : print data of db
    -w --week : print about last one week data of db
    -m --month : print about some month data of db

  Documentation:
  #TODO:

'''

class BookKeeper:
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

    def read_file(self, file_name):
        input_file = open(file_name, 'r')
        read_lines = []

        while True:
            read_line = input_file.readline()
            if not read_line: break

            read_lines.append(tuple(read_line.strip().split("|")))

        input_file.close()

        return read_lines

    def add_to_db(self, lines):
        self.cur.executemany("INSERT INTO '%s' VALUES (?, ?, ?, ?, ?)" % self.table_name, lines)
        self.db.commit()

    def input_file(self, file_name):
        read_lines = self.read_file(file_name)
        self.add_to_db(read_lines)

    def input_text(self, text):
        read_lines = []
        read_lines.append(tuple(text.strip().split("|")))
        self.add_to_db(read_lines)

    def convert_category(self, category):
        tags = ["N/A", "식비", "간식비", "고정지출", "변동지출"]

        return tags[category]

    def print_by_format(self, print_list):
        #sort for visibility
        print_list.sort()

        for item in print_list:
            print(f"{item[1]} : {item[2]}, {format(item[3], ',')}, {self.convert_category(item[4])}")

    def print_db(self):
        self.cur.execute("SELECT * FROM '%s'" % self.table_name)

        print_list = self.cur.fetchall()
        self.print_by_format(print_list)

    def print_month_db(self, month):
        self.cur.execute("SELECT * FROM '%s' WHERE id='%s'" % (self.table_name, month))

        print_list = self.cur.fetchall()
        self.print_by_format(print_list)

    def get_last_7days(self):
        date_list = []
        cnt = 0

        today = datetime.datetime.now()
        day = timedelta(days=1)

        for i in range(7):
            date_list.append(f"{str(today.year).zfill(4)}-{str(today.month).zfill(2)}-{str(today.day).zfill(2)}")
            today -= day

        return date_list

    def print_week_db(self):
        date_list = self.get_last_7days()
        print_list = []

        for date in date_list:
            self.cur.execute("SELECT * FROM '%s' WHERE date='%s'" % (self.table_name, date))
            result_list = self.cur.fetchall()

            if result_list:
                print_list += result_list

        self.print_by_format(print_list)

def print_usage_and_exit():
    print(usage_string)
    sys.exit(2)

if __name__ == "__main__":
    try:
        short_flags = 'hf:t:pm:w'
        long_flags = ['help', 'file=', 'text=', 'print', 'month=', 'week=']

        opts, args = getopt.gnu_getopt(sys.argv[1:], short_flags, long_flags)
    except getopt.GetoptError:
        print_usage_and_exit()

    with BookKeeper() as book_keeper:
        for o, a in opts:
            if o in ('-h', '--help'):
                print_usage_and_exit()
            if o in ('-f', '--file'):
                book_keeper.input_file(a)
            if o in ('-t', '--text'):
                book_keeper.input_text(a)
            if o in ('-p', '--print'):
                book_keeper.print_db()
            if o in ('-m', '--month'):
                book_keeper.print_month_db(a)
            if o in ('-w', '--week'):
                book_keeper.print_week_db()
