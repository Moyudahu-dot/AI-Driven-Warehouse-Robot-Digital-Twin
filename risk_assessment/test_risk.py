import copy
import unittest
from demo import example
from risk import evaluate


class RiskTests(unittest.TestCase):
    def test_head_on_between_samples(self):
        r = evaluate(example())
        self.assertEqual(r['status'], 'RISK')
        self.assertAlmostEqual(r['min_clearance_m'], -.6)
        self.assertAlmostEqual(r['first_buffer_entry_s'], .55)

    def test_clear(self):
        d = example()
        for p in d['obstacles'][0]['trajectory']: p['y'] = 3
        self.assertEqual(evaluate(d)['status'], 'CLEAR')

    def test_stationary_contact(self):
        d = example()
        for p in d['robot']['trajectory'] + d['obstacles'][0]['trajectory']:
            p['x'] = 0
        self.assertEqual(evaluate(d)['first_buffer_entry_s'], 0)

    def test_crossing(self):
        d = example()
        d['obstacles'][0]['trajectory'] = [{'t': 0, 'x': 1, 'y': -1}, {'t': 2, 'x': 1, 'y': 1}]
        self.assertAlmostEqual(evaluate(d)['min_clearance_m'], -.6)

    def test_invalid(self):
        for key, value in [('observed_at', -1), ('radius_m', -1), ('trajectory', []), ('observed_at', float('nan'))]:
            d = example()
            d['obstacles'][0][key] = value
            self.assertEqual(evaluate(d)['status'], 'UNKNOWN')

    def test_duplicate_ids(self):
        d = example()
        d['obstacles'].append(copy.deepcopy(d['obstacles'][0]))
        self.assertEqual(evaluate(d)['status'], 'UNKNOWN')

    def test_empty(self):
        d = example(); d['obstacles'] = []
        self.assertEqual(evaluate(d)['status'], 'CLEAR')

    def test_unequal_time_grid(self):
        d = example()
        d['robot']['trajectory'].insert(1, {'t': .7, 'x': .7, 'y': 0})
        self.assertAlmostEqual(evaluate(d)['first_buffer_entry_s'], .55)


if __name__ == '__main__': unittest.main()
