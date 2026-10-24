"""Real RDKit boundary tests and explicitly offline provider failure simulations.

Run with Python 3.12/3.13 and the runtime requirements installed.
Network calls are replaced in every agent test; these are not live-provider acceptance.
"""

from pathlib import Path
from contextlib import redirect_stdout
import copy
import csv
import hashlib
import importlib.util
import io
import json
import sys
import subprocess
import tempfile
import types
import unittest
from unittest.mock import Mock, patch
import zipfile

ROOT = Path(__file__).resolve().parents[3]
RT = ROOT / "skills/organic-smiles-rdkit/runtime"
sys.path.insert(0, str(RT))
import molecule_tool as tool
import agent
import execution
import credential_config as credentials

PAGE = RT.parent
DEFAULT = json.loads((RT / "examples/02-smarts/parameters.json").read_bytes())


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        base = ROOT / ".guard-test-tmp"
        base.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def input_root(self, rows, raw=None):
        root = self.base / "input"
        root.mkdir()
        for name in ["SKILL.md", "sources.json"]:
            (root / name).write_bytes(((PAGE if name == "SKILL.md" else RT) / name).read_bytes())
        if raw is None:
            with (root / "molecules.csv").open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=tool.INPUT_FIELDS)
                writer.writeheader()
                writer.writerows(rows)
        else:
            (root / "molecules.csv").write_bytes(raw)
        tool.dump(
            root / "data-provenance.json", {"sha256": tool.sha(root / "molecules.csv")}
        )
        return root

    def row(self, smiles="CCO", id_="x"):
        return dict(id=id_, label="test", smiles=smiles, source_id="test", role="test")

    def boundary_root(self):
        with (RT / 'examples/chemistry-boundaries.csv').open(encoding='utf-8', newline='') as f:
            return self.input_root([self.row(row['smiles'], row['id']) for row in csv.DictReader(f)])


class ParameterAndInputTests(WorkspaceTest):
    def test_strict_parameter_types_and_ranges(self):
        for key, values in {
            "radius": [True, False, 0, 5, 2.0, "2", None],
            "fp_size": [True, 0, 2048.0, 512, "2048"],
            "include_chirality": [0, 1, "True", None],
            "reference_id": ["", "x" * 65, "../x", None],
            "query_smarts": ["", "C ignored_name", "C |$name$|", "C" * 121, "[", None],
        }.items():
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    tool.validate(dict(DEFAULT, **{key: value}))
        for params in [[], {}, dict(DEFAULT, extra=1)]:
            with self.subTest(params=params), self.assertRaises(ValueError):
                tool.validate(params)

    def test_malformed_csv_rows_rejected_before_output(self):
        for raw in [
            b"id,label,smiles,source_id,role\nx,truncated\n",
            b"id,label,smiles,source_id,role\nx,test,CCO,test,test,extra\n",
            b'id,label,smiles,source_id,role\nx,"unterminated,CCO,test,test\n',
            b"id,label,smiles,source_id,role\nx,\xff,CCO,test,test\n",
        ]:
            with self.subTest(raw=raw):
                root = self.input_root([], raw)
                with self.assertRaises(ValueError):
                    tool.analyze(
                        root, dict(DEFAULT, reference_id="x"), self.base / "out"
                    )
                self.assertFalse((self.base / "out").exists())
                for path in root.iterdir():
                    path.unlink()
                root.rmdir()

    def test_oversized_input_rejected(self):
        root = self.input_root([], b"x" * (tool.MAX_INPUT_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "128000"):
            tool.analyze(root, DEFAULT, self.base / "out")

    def test_record_count_and_id_bounds(self):
        cases = [
            [],
            [self.row(id_=str(i)) for i in range(51)],
            [self.row(), self.row()],
            [self.row(id_="")],
            [self.row(id_="../outside")],
            [self.row(id_="=SUM(A1)")],
            [self.row("C" * 513)],
            [dict(self.row(), label="=1+1")],
        ]
        for rows in cases:
            with self.subTest(rows=len(rows)):
                root = self.input_root(rows)
                with self.assertRaises(ValueError):
                    tool.analyze(
                        root, dict(DEFAULT, reference_id="x"), self.base / "out"
                    )
                self.assertFalse((self.base / "out").exists())
                for path in root.iterdir():
                    path.unlink()
                root.rmdir()

    def test_hash_mismatch_and_missing_reference(self):
        root = self.input_root([self.row()])
        with self.assertRaisesRegex(ValueError, "reference_id"):
            tool.analyze(root, DEFAULT, self.base / "out")
        with (root / "molecules.csv").open("ab") as f:
            f.write(b"\n")
        with self.assertRaisesRegex(ValueError, "哈希"):
            tool.analyze(root, DEFAULT, self.base / "out")

    def test_annotations_dummy_atoms_and_oversized_graphs_are_rejected(self):
        rows = [
            self.row("CCO", "ref"),
            self.row("CCO hidden_name", "name"),
            self.row("CCO |$C2;C1;O$|", "cx"),
            self.row("*", "dummy"),
            self.row("C" * 129, "large"),
            self.row("C1CC", "invalid"),
            self.row("", "empty"),
        ]
        root = self.input_root(rows)
        result = tool.analyze(
            root, dict(DEFAULT, reference_id="ref"), self.base / "out"
        )
        self.assertEqual((result["valid"], result["rejected"]), (1, 6))
        with (self.base / "out/analysis.csv").open(encoding="utf-8") as f:
            output = list(csv.DictReader(f))
        self.assertEqual([r["id"] for r in output], [r["id"] for r in rows])

    def test_match_saturation_is_not_reported_as_an_exact_count(self):
        root = self.input_root([self.row("C" * 80)])
        with self.assertRaisesRegex(ValueError, "截断"):
            tool.analyze(
                root,
                dict(DEFAULT, reference_id="x", query_smarts="C.C.C"),
                self.base / "out",
            )
        self.assertFalse((self.base / "out").exists())

    def test_fixture_ids_do_not_trigger_unrelated_chemical_expectations(self):
        root = self.input_root([self.row("C", f"{i:03}") for i in range(1, 15)])
        result = tool.analyze(
            root, dict(DEFAULT, reference_id="001"), self.base / "out"
        )
        self.assertEqual(result["valid"], 14)
        self.assertNotIn("benzene_formula", result["checks"])

    def test_upper_record_and_atom_bounds_complete(self):
        root = self.input_root([self.row("C" * 128, str(i)) for i in range(50)])
        result = tool.analyze(root, dict(DEFAULT, reference_id="0"), self.base / "out")
        self.assertEqual((result["records"], result["valid"]), (50, 50))


class ChemistryRegressionTests(WorkspaceTest):
    def test_parameter_matrix_retains_chemical_identity(self):
        root = self.boundary_root()
        for radius in [1, 2, 3, 4]:
            for bits in [1024, 2048, 4096]:
                for chirality in [False, True]:
                    with self.subTest(radius=radius, bits=bits, chirality=chirality):
                        params = dict(
                            DEFAULT,
                            radius=radius,
                            fp_size=bits,
                            include_chirality=chirality,
                            reference_id="E01",
                        )
                        output = self.base / f"out-{radius}-{bits}-{chirality}"
                        result = tool.analyze(root, params, output)
                        self.assertEqual(
                            (result["records"], result["valid"], result["rejected"]),
                            (33, 28, 5),
                        )
                        self.assertTrue(all(result["checks"].values()))
                        self.assertEqual(len(result["checks"]), 6)
                        self.assertEqual(
                            (output / "molecules.csv").read_bytes(),
                            (root / "molecules.csv").read_bytes(),
                        )

    def test_chirality_parameter_changes_fingerprint_not_structure(self):
        scores = {}
        canonical = {}
        root = self.boundary_root()
        for flag in [False, True]:
            output = self.base / str(flag)
            tool.analyze(
                root, dict(DEFAULT, reference_id="EPOS", include_chirality=flag), output
            )
            with (output / "similarity.csv").open(encoding="utf-8") as f:
                scores[flag] = {
                    r["id"]: float(r["tanimoto"]) for r in csv.DictReader(f)
                }
            with (output / "analysis.csv").open(encoding="utf-8") as f:
                canonical[flag] = {
                    r["id"]: r.get("canonical_isomeric_smiles")
                    for r in csv.DictReader(f)
                }
        self.assertEqual(scores[False]["ENEG"], 1.0)
        self.assertLess(scores[True]["ENEG"], 1.0)
        self.assertEqual(canonical[False], canonical[True])

    def test_existing_output_never_overwritten(self):
        output = self.base / "existing"
        output.mkdir()
        (output / "keep.txt").write_text("original")
        with self.assertRaises(FileExistsError):
            tool.analyze(RT, DEFAULT, output)
        self.assertEqual((output / "keep.txt").read_text(), "original")




class CredentialTests(WorkspaceTest):
    def test_local_secret_errors_do_not_echo_values(self):
        invalid = ["", "abc def", "abc\x00def", "秘密", "x" * 1025]
        for value in invalid:
            with self.subTest(length=len(value)):
                with self.assertRaises(credentials.CredentialConfigError) as caught:
                    credentials.validate_value(value, "test")
                if value:
                    self.assertNotIn(value, str(caught.exception))

    def test_env_bom_quotes_comments_duplicates_and_bad_encoding(self):
        path = self.base / "test-config"
        path.write_text(
            '\ufeffexport DEEPSEEK_API_KEY="TEST_ONLY_CREDENTIAL" # comment\n',
            encoding="utf-8",
        )
        self.assertEqual(credentials.read_local_key(path), "TEST_ONLY_CREDENTIAL")
        for raw in [
            b"DEEPSEEK_API_KEY=x\nDEEPSEEK_API_KEY=y\n",
            b'DEEPSEEK_API_KEY="unterminated',
            b"\xff",
        ]:
            path.write_bytes(raw)
            with self.assertRaises(credentials.CredentialConfigError):
                credentials.read_local_key(path)



class OfflineAgentTests(WorkspaceTest):
    KEY = "NOT_A_REAL_CREDENTIAL"

    def reply(self, *, calls=None, content=None, reason="stop"):
        return {
            "model": "OFFLINE_TEST_DOUBLE",
            "choices": [
                {
                    "finish_reason": reason,
                    "message": {"content": content, "tool_calls": calls or []},
                }
            ],
        }

    def call(self, params=None, name="analyze_organic_molecules"):
        return {
            "id": "offline-call",
            "type": "function",
            "function": {"name": name, "arguments": json.dumps(params or DEFAULT)},
        }

    def execute(self, responses):
        opener = Mock()

        def opened(*args, **kwargs):
            value = responses.pop(0)
            if isinstance(value, Exception):
                raise value
            raw = value if isinstance(value, bytes) else json.dumps(value).encode()
            response = Mock()
            response.__enter__ = Mock(return_value=response)
            response.__exit__ = Mock(return_value=False)
            response.read = Mock(side_effect=lambda size: raw[:size])
            return response

        opener.open.side_effect = opened
        output = self.base / "agent-output"
        with patch.object(agent.urllib.request, "build_opener", return_value=opener):
            spec = importlib.util.spec_from_file_location('tested_skill', RT / 'organic-smiles-rdkit.py')
            api = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(api)
            with patch.object(credentials, 'read_local_key', return_value=self.KEY):
                result = api.run_skill(skill_file=PAGE / 'SKILL.md',
                                       input_csv=RT / 'examples/02-smarts/molecules.csv',
                                       parameters=DEFAULT, task='Offline CI protocol test',
                                       output_dir=output, mode='agent', env_file=self.base / 'unused.env')
        return result, opener

    def test_two_round_offline_agent_calls_real_bounded_tool_and_verifies_zip(self):
        final = (
            json.dumps(self.reply(content="解释 " + self.KEY))
            .replace("NOT_A", "\\u004eOT_A")
            .encode()
        )
        receipt, opener = self.execute(
            [self.reply(calls=[self.call()], reason="tool_calls"), final]
        )
        self.assertEqual((receipt["tool_calls"], opener.open.call_count), (1, 2))
        for path in (self.base / "agent-output").iterdir():
            if path.suffix != ".zip":
                self.assertNotIn(self.KEY.encode(), path.read_bytes())
        self.assertEqual(receipt["status"], "PASS_MODEL_AND_TOOL_CALL")
        execution.verify_results(self.base / "agent-output")

    def test_no_tool_call_cannot_pass(self):
        with self.assertRaises(RuntimeError):
            self.execute([self.reply(content="I completed it")])

    def test_invalid_reference_fails_before_any_provider_request(self):
        spec = importlib.util.spec_from_file_location('tested_skill', RT / 'organic-smiles-rdkit.py')
        api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api)
        for reference in ['absent', '011', '012']:
            with self.subTest(reference=reference), patch.object(agent, 'request') as request:
                with self.assertRaisesRegex(ValueError, 'reference_id'):
                    api.run_skill(skill_file=PAGE / 'SKILL.md',
                                  input_csv=RT / 'examples/02-smarts/molecules.csv',
                                  parameters=dict(DEFAULT, reference_id=reference), task='Offline invalid input',
                                  output_dir=self.base / reference, mode='agent', env_file=self.base / 'unused.env')
                request.assert_not_called()
                self.assertFalse((self.base / reference).exists())

    def test_wrong_tool_and_changed_parameters_cannot_run(self):
        for call in [
            self.call(name="arbitrary_code"),
            self.call(dict(DEFAULT, radius=3)),
            self.call(dict(DEFAULT, radius=True)),
        ]:
            with self.subTest(call=call), self.assertRaises((ValueError, RuntimeError)):
                self.execute([self.reply(calls=[call], reason="tool_calls")])
            self.assertFalse((self.base / "agent-output/analysis.csv").exists())
            for path in (self.base / "agent-output").iterdir():
                path.unlink()
            (self.base / "agent-output").rmdir()

    def test_duplicate_tool_calls_are_blocked(self):
        with self.assertRaisesRegex(RuntimeError, "一次工具"):
            self.execute(
                [self.reply(calls=[self.call(), self.call()], reason="tool_calls")]
            )
        self.assertFalse((self.base / "agent-output/run-receipt.json").exists())

    def test_broken_oversized_json_and_timeout_fail_closed(self):
        for response in [
            b"{broken",
            b"x" * (1_000_000 + 1),
            TimeoutError("timeout"),
        ]:
            with (
                self.subTest(type=type(response).__name__),
                self.assertRaises(Exception),
            ):
                self.execute([response])
            self.assertFalse((self.base / "agent-output/run-receipt.json").exists())
            for path in (self.base / "agent-output").iterdir():
                path.unlink()
            (self.base / "agent-output").rmdir()

    def test_redirects_and_nonfinite_or_duplicate_json_are_rejected(self):
        with self.assertRaises(RuntimeError):
            agent.NoRedirect().redirect_request(
                None, None, 302, "redirect", {}, "https://example.invalid/"
            )
        for text in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}']:
            with self.assertRaises(ValueError):
                execution.json_text(text)


    def test_interpretation_failure_preserves_completed_numerical_zip(self):
        with self.assertRaises(RuntimeError):
            self.execute([self.reply(calls=[self.call()], reason='tool_calls'), TimeoutError('offline timeout')])
        output = self.base / 'agent-output'
        receipt = json.loads((output / 'run-receipt.json').read_bytes())
        self.assertEqual(receipt['status'], 'PARTIAL_NUMERICAL_COMPLETE')
        self.assertEqual(receipt['interpretation_status'], 'FAILED')
        self.assertEqual(receipt['tool_calls'], 1)
        self.assertEqual(receipt['model_calls'], 2)
        self.assertTrue((output / 'analysis.csv').is_file())
        self.assertTrue((output / 'failure.json').is_file())
        execution.verify_results(output)


class ExplicitSemanticRegressionTests(WorkspaceTest):
    def test_shipped_semantic_regression_always_executes(self):
        output = self.base / 'chemical'
        process = subprocess.run([sys.executable, '-B', str(RT / 'chemical_regression.py'),
                                  '--output', str(output)], capture_output=True, timeout=240)
        self.assertEqual(process.returncode, 0, process.stderr.decode('utf-8', errors='replace'))
        result = json.loads((output / 'chemical-semantics-acceptance.json').read_bytes())
        self.assertEqual(result['status'], 'PASS_CHEMICAL_SEMANTICS_DEFINED_REGRESSION')
        self.assertEqual(len(result['checks']), 44)
        self.assertEqual(result['model_calls'], 0)


if __name__ == "__main__":
    unittest.main()
