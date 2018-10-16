from dataclasses import dataclass
from itertools import chain

class DatabaseInvObjError(Exception):
    def __init__(self, msg):
        self.msg = msg

@dataclass(frozen=True)
class DatabaseKeys:
    def __init__(self, table:str, fields:dict):
        # Need to use setattr as the class is Frozen (immutable)
        object.__setattr__(self, 'table', table)
        object.__setattr__(self, 'fields', fields)

class DatabaseValues:
    def __init__(self, fields:dict):
        self.fields = fields

def isDatabaseKeys(fn):
    '''
    Decorator to ensure applicable methods are being passed a key object
    '''    
    def wrapper(*args, **kwargs):
        if isinstance(args[1], DatabaseKeys):
            return fn(*args, **kwargs)
        raise DatabaseInvObjError('Not a DB key object : ' + str(args[1]))
    return wrapper

def isDatabaseObject(fn):
    '''
    Decorator to ensure applicable methods are being passed a database object
    '''    
    def wrapper(*args, **kwargs):
        o = args[1]
        d = dir(o)
        if 'keys' in d and 'vals' in d and 'createSingle' in d \
                and 'createMulti' in d:
            if isinstance(o.keys, DatabaseKeys) and \
                    isinstance(o.vals, DatabaseValues):
                return fn(*args, **kwargs)
        raise DatabaseInvObjError('Not a valid DB object : ' + str(args[1]))
    return wrapper

class Database:
    '''
    Context manager enabled database class 
    '''
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._impl.close()
        return False

    def __init__(self, dbname, impl):
        self._dbname = dbname 
        self._impl = impl 
        self._impl.connect(self._dbname)

    @isDatabaseObject
    def select(self, obj):
        '''
        Select from db the object(s) matching the provided object's key
        '''
        rows = self._impl.select(obj.keys.table, obj.keys.fields)
        return obj.createMulti(rows)

    @isDatabaseObject
    def upsert(self, obj):
        '''
        Insert or update the object into the database
        '''
        if len(self.select(obj)) == 0:
            inserts = dict(chain(obj.keys.fields.items(), \
                    obj.vals.fields.items()))
            self._impl.insert(obj.keys.table, inserts)
        else:
            self._impl.update(obj.keys.table, obj.vals.fields, obj.keys.fields)

    @isDatabaseObject
    def delete(self, obj):
        '''
        Delete the object identified by the key from the database
        '''
        self._impl.delete(obj.keys.table, obj.keys.fields)

    def commit(self):
        self._impl.commit()

    def rollback(self):
        self._impl.rollback()

    def close(self):
        self._impl.close()