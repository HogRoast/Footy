from sqlite3 import connect, IntegrityError
from Footy.src.database.database import DatabaseDataError, \
        DatabaseIntegrityError

class SQLite3Impl:
    '''
    SQLite3 implementation class to be used with the generic Database class
    '''
    def connect(self, dbname:str):
        self._dbname = dbname
        self._conn = connect(dbname)

    def select(self, table:str, where:dict = None):
        '''
        Select from db the row(s) matching the provided fields or all rows if
        fields are None

        :param table: the table name to select from
        :param where: a dictionary of where clauses, k=v and k1=v1...
        :returns: a list of rows from table
        :raises: None
        '''
        s = 'SELECT * FROM {} '.format(table)
        if where and len(where) > 0:
            s += 'WHERE '
            for k, v in where.items():
                if isinstance(v, str):
                    s += '{}="{}" and '.format(k, v) 
                else:
                    s += '{}={} and '.format(k, v) 
            # remove the extraneous ' and '
            s = s[:-5]
   
        return self.execute(s)

    def insert(self, table:str, inserts:dict):
        '''
        Insert the given data into the database

        :param table: the table name to insert into
        :param inserts: a dictionary of key value pairs to be inserted
        :returns: N/A
        :raises: DatabaseDataError if no inserts
        '''
        if inserts is None or len(inserts) == 0:
            raise DatabaseDataError('No values provided for INSERT')
    
        s = 'INSERT INTO {} ('.format(table)
        for k in inserts.keys():
            s += '{},'.format(k) 
        # remove the extraneous comma
        s = s[:-1]

        s += ') values ('
        for v in inserts.values():
            if isinstance(v, str):
                s += '"{}",'.format(v)
            else:
                s += '{},'.format(v)
        # remove the extraneous comma
        s = s[:-1]
        s += ')'

        self.execute(s)

    def update(self, table:str, updates:dict, where:dict = None):
        '''
        Update the fields whose row(s) are identified by the where dict

        :param table: the table name to update
        :param updates: a dictionary of key value pairs to be updated
        :param where: a dictionary of where clauses, k=v and k1=v1...
        :returns: N/A
        :raises: DatabaseDataError if no updates
        '''
        if updates is None or len(updates) == 0:
            raise DatabaseDataError('No values provided for UPDATE')
        
        s = 'UPDATE {} SET '.format(table)
        for k, v in updates.items():
            if isinstance(v, str):
                s += '{}="{}",'.format(k, v) 
            else:
                s += '{}={},'.format(k, v) 
        # remove the extraneous comma
        s = s[:-1]

        if where and len(where) > 0:
            s += ' WHERE '
            for k, v in where.items():
                if isinstance(v, str):
                    s += '{}="{}" and '.format(k, v) 
                else:
                    s += '{}={} and '.format(k, v) 
            # remove the extraneous ' and '
            s = s[:-5]

        self.execute(s)

    def delete(self, table:str, where:dict = None):
        '''
        Delete the row(s) identified by the where dict

        :param table: the table name to delete from
        :param where: a dictionary of where clauses, k=v and k1=v1...
        :returns: N/A
        :raises: None
        '''
        s = 'DELETE FROM {} '.format(table)
        if where and len(where) > 0:
            s += 'WHERE '
            for k, v in where.items():
                if isinstance(v, str):
                    s += '{}="{}" and '.format(k, v) 
                else:
                    s += '{}={} and '.format(k, v) 
            # remove the extraneous ' and '
            s = s[:-5]

        self.execute(s)

    def execute(self, s):
        '''
        Execute the provided SQL string against the underlying DB

        :param s: a SQL string
        :returns: a list of database rows affected, potentially an empty list
        :raises: DatabaseIntegrityError if table constraints are breached
        '''
        curs = self._conn.cursor()

        try:
            curs.execute(s)
        except IntegrityError as e:
            raise DatabaseIntegrityError(e.args[0])

        rows = curs.fetchall() 
        curs.close()

        return rows

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()
