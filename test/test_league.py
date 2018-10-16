# coding: utf-8

import os
from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, call
from dataclasses import FrozenInstanceError
from Footy.src.database.league import League, LeagueKeys, LeagueValues
from Footy.src.database.database import DatabaseKeys

class TestLeague(TestCase):
    """League object tests"""

    @classmethod
    def setUpClass(cls):
        os.system('cat ../database/create_db.sql | sqlite3 ../database/footy.test.db')
        os.system('cat ../database/*_test_data.sql | sqlite3 ../database/footy.test.db')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_keys_Immutablility(self):
        keys =LeagueKeys('league name TD')

        with self.assertRaises(FrozenInstanceError) as cm:
            keys.name = 'Something New'
            
        self.assertIn('cannot assign to field', cm.exception.args[0])

    def test_keys_adhoc(self):
        l = League.createAdhoc(DatabaseKeys('league', None))
        self.assertEqual(l.keys.table, 'league')
        self.assertTrue(l.keys.fields is None)

    def test_createSingle(self):
        obj = League.createSingle(('league name TD', 'league desc TD'))

        self.assertEqual(obj.keys.name, 'league name TD')
         
        self.assertEqual(obj.vals.desc, 'league desc TD')
         

    def test_createMulti(self):
        rows = [('league name TD', 'league desc TD'),
                ('league name TD2', 'league desc TD2')]
        objs = League.createMulti(rows)
        
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0].keys.name, 'league name TD')
        
        self.assertEqual(objs[0].vals.desc, 'league desc TD')
        
        self.assertEqual(objs[1].keys.name, 'league name TD2')
        
        self.assertEqual(objs[1].vals.desc, 'league desc TD2')
        

    def test_repr(self):
        obj = League('league name TD', 'league desc TD')
        self.assertEqual(str(obj), "league : Keys {'name': 'league name TD'} : Values {'desc': 'league desc TD'}")

if __name__ == '__main__':
    import unittest
    unittest.main()