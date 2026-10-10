import unittest
from check import demo_trace,inspect,parse_args
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
class ParseArgsTests(unittest.TestCase):
 def test_decodes_json_scalars_and_unicode(self):
  self.assertEqual(parse_args('"caf\u00e9"'), "café")
  self.assertEqual(parse_args('0'), 0)
  self.assertIs(parse_args('null'), None)
 def test_preserves_empty_and_invalid_strings(self):
  self.assertEqual(parse_args(''), '')
  self.assertEqual(parse_args('not json'), 'not json')
 def test_preserves_non_string_values_by_identity(self):
  value={"nested": []}
  self.assertIs(parse_args(value), value)

if __name__=="__main__":unittest.main()
