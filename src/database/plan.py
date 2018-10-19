from dataclasses import dataclass
from Footy.src.database.database import DatabaseKeys, DatabaseValues, AdhocKeys

@dataclass(frozen=True)
class PlanKeys(DatabaseKeys):
    '''
    plan database object primary key representation
    '''
    id:int
    

    def __init__(self, id:int):
        '''
        Construct the object from the provided primary key fields
        
        :param ...: typed primary key fields
        :returns: N/A
        :raises: None
        '''
        # Need to use setattr as the class is Frozen (immutable)
        object.__setattr__(self, 'id', id)
        
        super().__init__('plan', self.getFields())

    def getFields(self):
        '''
        Get all the PK fields for this object in a dictionary form
        
        :returns: a dictionary of all PlanKeys fields
        :raises: None
        '''
        fields = None if not (self.id) else {'id' : self.id}
        return fields
        
class PlanValues(DatabaseValues):
    '''
    plan database object values representation
    '''
    def __init__(self, name:str = None, desc:str = None, cost:float = None):
        '''
        Construct the object from the provided value fields
        
        :param ...: typed value fields
        :returns: N/A
        :raises: None
        '''
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'desc', desc)
        object.__setattr__(self, 'cost', cost)
        
        super().__init__(self.getFields())

    def getFields(self):
        '''
        Get all the value fields for this object in a dictionary form
        
        :returns: a dictionary of all PlanValues fields
        :raises: None
        '''
        fields = None if not (self. name and self.desc and self.cost) else {'name' : self.name, 'desc' : self.desc, 'cost' : self.cost}
        return fields
        
class Plan:
    '''
    plan database object representation
    '''
    @classmethod
    def createAdhoc(cls, keys:AdhocKeys):
        '''
        Class method to create a database object with the provided adhoc keys
        list

        :param keys: an AdhocKeys object
        :returns: a Plan object constructed via the primary key
        :raises: None
        '''
        l = Plan()
        l.keys = keys
        return l

    @classmethod
    def createSingle(cls, row:tuple):
        '''
        Class method to create a database object from the provided database row

        :param row: a list of values representing the objects key and values
        :returns: a Plan object constructed from row
        :raises: None
        '''
        id, name, desc, cost = row
        return Plan(id, name, desc, cost)

    @classmethod
    def createMulti(cls, rows:tuple):
        '''
        Class method to create database objects from the provided database rows

        :param rows: a list of lists of representing object keys and values
        :returns: a list of Plan objects constructed from rows
        :raises: None
        '''
        l = []
        for r in rows:
            l.append(cls.createSingle(r))
        return l

    def __init__(self, id:int = None, name:str = None, desc:str = None, cost:float = None):
        '''
        Construct the object from the provided key and value fields
        
        :param ...: typed key and value fields
        :returns: N/A
        :raises: None
        '''
        self.keys = PlanKeys(id)
        self.vals = PlanValues(name, desc, cost)

    def __repr__(self):
        return self.keys.table + ' : Keys ' + str(self.keys.getFields()) + \
                ' : Values ' + str(self.vals.getFields())
