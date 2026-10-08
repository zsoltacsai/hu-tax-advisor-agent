import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class FixtureDeterminismTests(unittest.TestCase):
    def test_generator_is_byte_stable(self):
        command=[sys.executable,str(ROOT/"scripts/generate_synthetic_fixtures.py")]
        subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
        paths=sorted((ROOT/"fixtures/scenarios").glob("*.json"))
        first={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
        second={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        self.assertEqual(first,second)
        self.assertEqual(len(paths),17)

if __name__=="__main__": unittest.main()
