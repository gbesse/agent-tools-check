import unittest
from check import demo_trace,inspect
class CheckTests(unittest.TestCase):
 def test_good_trace(self): self.assertEqual(inspect(demo_trace(False)),[])
 def test_broken_trace_reports_all_missing_parts(self):
  codes={x for x,_ in inspect(demo_trace(True))}
  self.assertEqual(codes,{"tool","call","message"})
 def test_plaintext_encryption_marker_required(self):
  trace=demo_trace(False);trace["client_response"]["output"][0].pop("encrypted_function_args")
  self.assertIn("encryption",[x for x,_ in inspect(trace)])
 def test_arguments_must_survive(self):
  trace=demo_trace(False);trace["client_response"]["output"][0]["arguments"]='{"message":"WRONG"}'
  self.assertIn("args",[x for x,_ in inspect(trace)])
if __name__=="__main__":unittest.main()
