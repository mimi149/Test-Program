# This class contains:
# - The common method db_CRUD for db Creating, Retrieving, Updating, and Deleting.
# - The methods for updating the test results to db.

import os
import inspect
import psycopg2
import datetime
from sys import platform

class DB_test():

    @staticmethod
    def init():
        DB_test.db_connection = "host='localhost' port='5432' dbname='mimi_vtest' user='postgres' password=''"
        DB_test.id_testrun = ''

    def get_function_ids(self, function_name):
        sqls = [{"query": "select idwhenexpectfunction from whenexpectfunctions where name = '{0}';", "args":[function_name]}]
        try:
            id_whenexpectfunction = DB_test.db_CRUD(sqls, DB_test.db_connection)[0][0]
        except:
            raise Exception('db test error: whenexpectfunction does not exists in db.')
        return id_whenexpectfunction

    @staticmethod
    def testrun_update(git, timestamp, driver):
        sqls = []
        gitbranch = git.split(':')[0]
        githash = git.split(':')[-1]
        args = [gitbranch, githash, timestamp, driver, platform]
        query = "insert into testruns (gitbranch, githash, stamp, driver, os) values ('{0}', '{1}', '{2}', '{3}', '{4}');"
        sqls.append({"query": query, "args": args})
        query = "select idtestrun from testruns where gitbranch = '{0}' and githash = '{1}' and stamp = '{2}' and driver = '{3}' and os = '{4}';"
        sqls.append({"query": query, "args": args})
        try:
            DB_test.id_testrun = DB_test.db_CRUD(sqls, DB_test.db_connection)[0][0]
        except:
            raise Exception('db test error: cannot add testrun into db.')
        return DB_test.id_testrun

    def testcase_update(self, caller, fail):
        id_whenexpectfunction = self.get_function_ids(caller)
        sqls = []
        args = [DB_test.id_testrun, id_whenexpectfunction, fail]
        query = "insert into testcases (idtestrun, idwhenexpectfunction, fail) values ({0}, {1}, {2});"
        sqls.append({"query": query, "args": args})
        query = "select idtestcase from testcases where idtestrun = {0} and idwhenexpectfunction = {1} and fail = {2};"
        sqls.append({"query": query, "args": args})
        try:
            id_testcase = DB_test.db_CRUD(sqls, DB_test.db_connection)[0][0]
        except:
            raise Exception('db test error: cannot add testcase into db.')
        return id_testcase

    def teststep_update(self, id_testcase, logs):
        sqls = []
        query = "insert into teststeps (idtestcase, logtype, logmessage) values ({0}, '{1}', '{2}');"
        for event in logs:
            # event.message = event.message.encode('ascii', 'ignore')
            event.type = event.type if event.type else ""
            event.message = event.message.replace("'", "''") if event.message else ""
            args = [id_testcase, event.type, event.message]
            sqls.append({"query": query, "args": args})
        DB_test.db_CRUD(sqls, DB_test.db_connection)

    @staticmethod
    def db_test_result_update(detail_report, caller, fail, logs=[]):
        fail = fail if fail else False
        if DB_test.id_testrun:
            id_testcase = DB_test.testcase_update(DB_test(), caller, fail)
            if id_testcase:
                if detail_report or fail:
                    DB_test.teststep_update(DB_test(), id_testcase, logs)
        else:
            raise Exception('db test error: testrun does not exists in db.')

    @staticmethod
    def db_CRUD(sqlList, db_connection):
        '''
        Do the options in db: CREATE, RETRIEVE, UPDATE, DELETE.
        Execute every sql in sqlList and return the result of the last one.
        :param:
         sqlList: a list of dictionary
         sqlList[i]["query"]: a query string
         sqlList[i]["args"]: a list of arguments
        :return: a list of tuples selected from db or None.
        '''
        conn = psycopg2.connect(db_connection)
        cur = conn.cursor()
        result = None
        try:
            for sql in sqlList:
                query = sql["query"].format(*sql["args"])
                cur.execute(query)
                conn.commit()
        except:
            raise Exception('db test update error')

        try:
            result = cur.fetchall()
        except:
            result = None

        conn.commit()
        conn.close()
        return result

    @staticmethod
    def function_and_category_update(test_to_add, categories):
        for name, function in inspect.getmembers(test_to_add, predicate=inspect.ismethod):
            if name.startswith('when_') and '_expect_' in name:
                sqls = [{"query": "INSERT INTO whenexpectfunctions (name) SELECT('{0}') WHERE NOT EXISTS (SELECT 1 FROM whenexpectfunctions WHERE name = '{0}')", "args": [name]}]
                sqls.append({"query": "SELECT idwhenexpectfunction FROM whenexpectfunctions WHERE name = '{0}';", "args": [name]})
                id_whenexpectfunction = DB_test.db_CRUD(sqls, DB_test.db_connection)[0][0]

                for cat in categories[name]:
                    sqls = [{"query": "INSERT INTO categories (name) SELECT('{0}') WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = '{0}')", "args": [cat]}]
                    sqls.append({"query": "SELECT idcategory FROM categories WHERE name = '{0}';", "args": [cat]})
                    id_category = DB_test.db_CRUD(sqls, DB_test.db_connection)[0][0]

                    sqls = [{"query": "SELECT 1 FROM function_category WHERE idcategory = {0} AND idwhenexpectfunction = {1};", "args": [id_category, id_whenexpectfunction]}]
                    if not DB_test.db_CRUD(sqls, DB_test.db_connection):
                        sqls = [{"query": "INSERT INTO function_category (idcategory, idwhenexpectfunction) VALUES({0}, {1})", "args": [id_category, id_whenexpectfunction]}]
                        DB_test.db_CRUD(sqls, DB_test.db_connection)

DB_test.init()