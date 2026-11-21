import tempfile
import unittest
from pathlib import Path
from image_update_plans.scan import analyze, parse_dockerfile, write_outputs

ROOT = Path(__file__).resolve().parents[1]

class ScanTests(unittest.TestCase):
    def test_fixture_graph(self):
        g = analyze(ROOT / 'examples/inventory.json')
        self.assertEqual([(e['from'], e['to']) for e in g['edges']], [('ubi-9', 'java-21'), ('java-21', 'tomcat-10')])
        self.assertEqual(g['rebuild_waves'], [['ubi-9'], ['java-21'], ['tomcat-10']])
        self.assertFalse(g['cycle_or_blocked_nodes'])
        self.assertFalse(g['unresolved'])

    def test_unresolved_arg(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / 'Containerfile'
            f.write_text('FROM ${UNKNOWN}\n')
            parents, unknown = parse_dockerfile(f)
            self.assertFalse(parents)
            self.assertEqual(len(unknown), 1)

    def test_multistage_not_external(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / 'Containerfile'
            f.write_text('FROM example.invalid/ubi:9 AS first\nFROM first AS final\n')
            parents, unknown = parse_dockerfile(f)
            self.assertEqual(len(parents), 1)
            self.assertFalse(unknown)

    def test_reports_written(self):
        with tempfile.TemporaryDirectory() as td:
            write_outputs(analyze(ROOT / 'examples/inventory.json'), Path(td))
            for n in ('graph.json', 'graph.mmd', 'dependencies.csv', 'report.md'):
                self.assertTrue((Path(td) / n).is_file())

if __name__ == '__main__':
    unittest.main()
