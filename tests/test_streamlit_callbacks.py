import ast
import unittest
from pathlib import Path

class CallbackRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (Path(__file__).resolve().parents[1] / 'app.py').read_text()
        cls.tree = ast.parse(cls.source)

    def test_three_policy_buttons_use_callbacks(self):
        buttons = ['Apply density bonus', 'Apply land contribution', 'Apply grant']
        callbacks = ['apply_density_bonus', 'apply_land_contribution', 'apply_grant']
        for label, callback in zip(buttons, callbacks):
            calls = [n for n in ast.walk(self.tree) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute) and n.func.attr == 'button'
                     and any(isinstance(a, ast.Constant) and a.value == label for a in n.args)]
            self.assertEqual(len(calls), 1, label)
            on_click = next((k.value for k in calls[0].keywords if k.arg == 'on_click'), None)
            self.assertIsInstance(on_click, ast.Name)
            self.assertEqual(on_click.id, callback)

    def test_callback_math_and_caps(self):
        # Execute only the three small callback definitions with a mocked Streamlit state.
        funcs = [n for n in self.tree.body if isinstance(n, ast.FunctionDef)
                 and n.name in {'apply_density_bonus','apply_land_contribution','apply_grant'}]
        self.assertEqual(len(funcs), 3)
        state = {'x_units': 200, 'x_land_credit_m': 5.0, 'x_grant_m': 95.0}
        mock_st = type('StreamlitMock', (), {'session_state': state})()
        env = {'st': mock_st}
        exec(compile(ast.Module(body=funcs, type_ignores=[]), '<callbacks>', 'exec'), env)
        env['apply_density_bonus']()
        self.assertEqual(state['x_units'], 250)
        env['apply_land_contribution']()
        self.assertEqual(state['x_land_credit_m'], 15.0)
        env['apply_grant']()
        self.assertEqual(state['x_grant_m'], 100.0)
        state['x_units'] = 500
        env['apply_density_bonus']()
        self.assertEqual(state['x_units'], 500)

if __name__ == '__main__':
    unittest.main()
