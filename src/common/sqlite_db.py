# =========================================================================== #
# File    : sqlite_db.py                                                      #
# Author  : Pfesesani V. van Zyl                                              #
# =========================================================================== #

# Standard library imports
# --------------------------------------------------------------------------- #
import os
import sys
import sqlite3
import numpy as np
import time
import subprocess

from dataclasses import dataclass
# from .
try:
    from .msgConfiguration import msg_wrapper
except:
    from msgConfiguration import msg_wrapper

try:
    from .miscellaneousFunctions import set_table_name
except:
    from common.miscellaneousFunctions import set_table_name
# Local imports
# --------------------------------------------------------------------------- #
@dataclass
class SQLiteDB:
    dbPath: str # name of database
    log: object # logger
    # __dict__: dict

    def create_db(self):
        """ Create a new database. """

        msg_wrapper('debug',self.log.debug,'Opened new Database')
        self.conn = sqlite3.connect(self.dbPath)
        self.c = self.conn.cursor()

    def close_db(self):
        """ Close the database connection."""
        
        msg_wrapper('debug',self.log.debug,'Closed new Database')
        if self.c:
            self.conn.close()
    
    def commit_changes(self):
        """ Commit/save changes you have implemented to the database. """
        self.conn.commit()
        print('>>>> Commited changes')

    def create_table_stmt(self, data, tableName):
        """ Create table from dictionary. """

        sqlStmt = ""
       
        for key, value in data.items():
            # print(key,value, type(value).__name__)
            if type(value).__name__ == 'list':
                # pass
                data[key]=';'.join(value)
                # print(type(value))

            # Make the filename a foreign key
            if key == "FILENAME":
                sqlStmt +=f'CREATE TABLE IF NOT EXISTS {tableName} ('
                idKey = sqlStmt + "id INTEGER PRIMARY KEY AUTOINCREMENT" + ", "
                sqlStmt = idKey + key + " " + "TEXT" + " UNIQUE , "
            elif isinstance(value, float):
                sqlStmt = sqlStmt + key + " " + "REAL" + " , "
            elif type(value).__name__ == "float64":
                sqlStmt = sqlStmt + key + " " + "REAL" + " , "
            elif isinstance(value, int):
                sqlStmt = sqlStmt + key + " " + "INTEGER" + " , "
            elif isinstance(value, str):
                sqlStmt = sqlStmt + key + " " + "TEXT" + " , "
            elif isinstance(value, list):
                sqlStmt = sqlStmt + key + " " + "TEXT" + " , "
        return sqlStmt[:-2] + ")"
    
    def create_table(self, data, tableName):
        """ Create an sql statement to create a table."""

        tableName=set_table_name(tableName,self.log).upper()

        sqlStmt = self.create_table_stmt(data, tableName)
        # print(sqlStmt)
        # sys.exit()
        # self.c.execute(sqlStmt)
        try:
            # sqlStmt = self.create_table_stmt(data, tableName)
            self.c.execute(sqlStmt)
            # print('added')
        except:
            # tableName=f'_{tableName}'
            # sqlStmt = self.create_table_stmt(data, tableName)
            
            # self.c.execute(sqlStmt)
            # print(data)
            print('Already exists')
            # print('added')

        return tableName
    
    def insert_into_table_stmt_with_pk(self, data, tableName):
        """ Insert values into table and create a primary key."""

        sqlStmt = ""

        dataListKey = list(data.keys())
        dataListKeyString = ""
        dataListValues = list(data.values())
        dataListValueString = ""

        # print(dataListKey)
        for i in range(len(data)):
            if i == 0:
                dataListKeyString = dataListKeyString + dataListKey[i]
            else:
                dataListKeyString = dataListKeyString + ", " + dataListKey[i]


        placeHolders = "?,"*len(data)

        sqlStmt = "INSERT INTO " + tableName + \
            " (" + dataListKeyString + ") VALUES (" + placeHolders[:-1] + ")"

        return sqlStmt, dataListValues
    
    def populate_table(self, data, tableName, key=""):
        """ populate a database table with values. """

        try:
            self.create_db()
        except Exception as e:
            # print(e)
            pass

        #print('data: ',data)

        sqlStmt, values = self.insert_into_table_stmt_with_pk(data, tableName)
        # for i in range(len(values)):
        # self.c.execute(sqlStmt, values)
        # sys.exit()

        # print(data)
        # print('\n')
        # print('*'*50)
        fp=data['FILEPATH']
        cf=int(data['CENTFREQ'])
        sp=fp.split('/')
        # print(f'FILEPATH: {fp}')
        # print(sp[-2])
        # print(f'CENTFREQ: {cf}')
        # print(str(cf) in fp)
        x=fp.replace(str(sp[-2]),str(cf))
        # print(x)
        # print('*'*50)
        # print('\n')

        # sys.exit()
        # print(sqlStmt)
        # print(values)
        # self.c.execute(sqlStmt, values)
        # print('here')
        # sys.exit()
        try:
            self.c.close()
            self.create_db()
            self.c.execute(sqlStmt, values)
            self.commit_changes()
            self.c.close()
        except sqlite3.IntegrityError as e:
            print('Already in file')
            sys.exit()
        except sqlite3.OperationalError as e:
            print('SQLite operational error, skipping until I find a solution on how to handle this error')
            # time.sleep(10)
            # cmd=['fuser', 'HART26DATA.db']
            # print(f'fuser HART26DATA.db')
            # output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
            # output=subprocess.run("fuser HART26DATA.db", capture_output=True).stdout
            # print('out: ',output)
            # s=os.system(f'fuser HART26DATA.db')
            pass
        except Exception as e:
            # TODO: fix this exception
            print(e)

            time.sleep(10)
            self.c.close()
            self.create_db()
            self.c.execute(sqlStmt, values)
            self.commit_changes()
            self.c.close()

            msg_wrapper('debug',self.log.debug,f"issue: {e}")

            if 'UNIQUE constraint failed:' in str(e):
                print('--',str(e))
                if (str(cf) in fp)==False:
                    print('hello')
                    # try:
                    #     os.system(f'mv {fp} {x}')
                    #     print(f'moved {v1} to {newpath}')
                    #     print('Moving on\n')
                    # except:
                    #     print(f'Can not move {v1} to {newpath}')
                    #     print('Closing program')
                    #     sys.exit()
            elif 'unable to open database file' in str(e):

                assert os.path.exists(self.dbPath), "The file doesn't exist"
                print('PAth: ',self.dbPath)
                self.c.close()
                self.create_db()
                self.c.execute(sqlStmt, values)
                print('catch me if you can')
                print(e)

            else:
                print(e, 'out')
            sys.exit()
            s=sqlStmt.split(' ')
            v1=values[1]
            v=values[1].upper()
            s=(s[2]).replace('_','/')
            # v=v[]
            # print(s,v)
            # print(s in v)
            # print('/'.join((v1.split('/'))[:-3])+'/'+s)
            newpath='/'.join((v1.split('/'))[:-3])+'/'+s

            if s not in v:
                try:
                    os.makedirs(newpath)
                    print('Crated new directory: ',newpath)
                except:
                    print(f"Cant create {newpath}, already exists")

                try:
                    os.system(f'mv {v1} {newpath}')
                    print(f'moved {v1} to {newpath}')
                    print('Moving on\n')
                except:
                    print(f'Can not move {v1} to {newpath}')
                    print('Closing program')
                    sys.exit()
            # # if s in v:
            # # print('\n',s, v,'\n')
              
            else:
                print(f'File {s} already exists in the database')
                # sys.exit()

            sys.exit()
        

    def set_database_name(self, databaseName):
        """ Set the name of the database. """

        msg_wrapper("debug", self.log.debug, "Setup database name")
       
        if ".db" in databaseName:
            self.databaseName = databaseName
        else:
            self.databaseName = databaseName+".db"

    def get_table_names(self,db):
        """Get table names from the database.

        Args:
            db (str): The name of the database

        Returns:
            table_names (list): List of table names
        """

        msg_wrapper('debug',self.log.debug,f"Getting tables from: {db}")
        self.set_database_name(db)
        
        table_names = []
        sql_stmt = "SELECT name FROM sqlite_master WHERE type = 'table';"
        # print(sql_stmt)
        # tables = self.c.execute(sql_stmt).fetchall()
        try:
            tables = self.c.execute(sql_stmt).fetchall()
        except sqlite3.OperationalError:
            print("Failed to fetch data from the server")
            sys.exit()

        # print('Tables: ',tables)
        for i in range(len(tables)):
            if tables[i][0].startswith("data"):
                table_names.append(tables[i][0])
        for i in range(len(tables)):
            if tables[i][0].startswith("sqlite_sequence"):
                pass
            else:
                table_names.append(tables[i][0])
        return table_names
    
    def get_rows(self, tbname):
        """ Get the rows in the database table.

            Parameters
            ----------
                tbname : str
                    table name

            Returns
            -------
                rows: str
                    table row list
        """

        # print(tbname)
        # open the database
        # self.create_db()

        # read from selected table
        stmt = f"SELECT * FROM '{tbname}' ORDER BY FILENAME ASC;"
        # print(stmt)
        self.c.execute(stmt)
        data = self.c.fetchall()

        # get filenames and return them
        rows = []
        for row in data:
            rows.append(row)

        return rows
    
    def get_all_table_coloumns(self, table_name):
        """
            Get coloumns of table
            return index, coloumn name and coloumn type
        """

        col_ind = []
        col_name = []
        col_type = []

        res = self.c.execute("PRAGMA table_info('%s') " %
                             table_name).fetchall()

        # print(res)
        # sys.exit()
        for i in range(len(res)):
            col_ind.append(res[i][0])
            col_name.append(res[i][1])
            col_type.append(res[i][2])

        return col_ind, col_name, col_type
    
    def get_rows_of_cols(self, tbname,cols):
        """ Get the rows in the database table.

            Parameters
            ----------
                tbname : str
                    table name

            Returns
            -------
                rows: str
                    table row list
        """

        print('Getting rows of cols for table '+tbname)
        colNames=""
        for i in range(len(cols)):
                if i == len(cols)-1:
                    colNames = colNames + cols[i]+" "
                else:
                    colNames = colNames + cols[i]+", "
     
        # read from selected table
        stmt = "SELECT "+colNames[:-1]+"  FROM '"+tbname+"' ORDER BY FILENAME ASC;"

        # print(stmt)
        # print('\nExecuting: ',stmt,'\n')
        self.c.execute(stmt)
        data = self.c.fetchall()

        # get filenames and return them
        rows = []
        for row in data:
            rows.append(row)

        return rows
    
