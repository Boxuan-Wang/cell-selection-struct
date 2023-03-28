from cell import Cell
from table import Table
import unittest

test_example = [
    [{
        'id': 'cell_0_0_0',
        'value': '0_0',
        'is_header': False,
        'column_span': '1',
        'row_span': '1'
    },
    {
        'id': 'cell_0_0_1',
        'value': '0_1',
        'is_header': False,
        'column_span': '1',
        'row_span': '1'
    }],
    [{
        'id': 'cell_0_1_0',
        'value': '1_0',
        'is_header': False,
        'column_span': '2',
        'row_span': '1'
    }],
    [{
        'id': 'cell_0_2_0',
        'value': '2_0',
        'is_header': False,
        'column_span': '1',
        'row_span': '2'
    },
    {
        'id': 'cell_0_2_1',
        'value': '2_1',
        'is_header': False,
        'column_span': '1',
        'row_span': '1'
    }],
    [{
        'id': 'cell_0_3_0',
        'value': '3_0',
        'is_header': False,
        'column_span': '1',
        'row_span': '1'
    }]]
class TestWikiTable(unittest.TestCase):

    def test_cell_value(self):
        test_cell = Cell(test_example[0][0])
        self.assertEqual(test_cell.value, test_example[0][0]['value'])

    def test_cell_colour(self):
        test_cell = Cell(test_example[0][0])
        self.assertFalse(test_cell.selected())
        test_cell.set_colour('red')
        self.assertTrue(test_cell.selected())

    def test_col_row_mark(self):
        test_cell_1 = Cell(test_example[0][0])
        self.assertFalse(test_cell_1.selected())
        test_cell_1.mark_col()
        test_cell_1.mark_row()
        self.assertTrue(test_cell_1.selected())

        test_cell_2 = Cell(test_example[0][0])
        self.assertFalse(test_cell_2.selected())
        test_cell_2.mark_row()
        test_cell_2.mark_col()
        self.assertTrue(test_cell_2.selected())

    # For now, no idea how to test generate HTML

    def test_table_find_cell(self):
        test_table = Table(test_example)
        self.assertEqual(test_table.find_cell(0,0).value, test_example[0][0]['value'])
        self.assertEqual(test_table.find_cell(3,1).value, test_example[-1][0]['value'])

if __name__ == '__main__':
    unittest.main()