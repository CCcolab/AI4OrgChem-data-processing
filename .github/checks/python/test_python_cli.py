"""Offline CLI integration, output identity and tamper rejection."""

from pathlib import Path
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[3]
IDS = ["organic-smiles-rdkit", "table-fitting-residuals"]


class PythonCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / ".guard-test-tmp"
        base.mkdir(exist_ok=True)
        cls.tmp = tempfile.TemporaryDirectory(dir=base)
        cls.base = Path(cls.tmp.name)
        cls.results = {}
        # A sitecustomize tripwire forbids provider calls in every CLI subprocess.
        site = cls.base / "offline"
        site.mkdir()
        (site / "sitecustomize.py").write_text(
            "import socket,urllib.request\n"
            "def denied(*args, **kwargs): raise AssertionError('NETWORK_FORBIDDEN')\n"
            "urllib.request.urlopen=denied\nsocket.socket.connect=denied\nsocket.getaddrinfo=denied\n",
            encoding="utf-8",
        )
        cls.env = dict(
            os.environ, PYTHONPATH=str(site), PYTHONUTF8="1", MPLBACKEND="Agg"
        )
        cls.env.pop("DEEPSEEK_API_KEY", None)
        for id_ in IDS:
            page = ROOT / "skills" / id_
            for mode in ["default", "modified"]:
                params = json.loads((page / ("runtime/examples/03-similarity/parameters.json" if id_ == IDS[0] else "runtime/parameters.json")).read_bytes())
                if mode == "modified":
                    if id_ == IDS[0]:
                        params["radius"] = 3
                    else:
                        params["include_highest_standard"] = False
                parameter_file = cls.base / f"{id_}-{mode}.json"
                parameter_file.write_text(json.dumps(params), encoding="utf-8")
                output = cls.base / f"{id_}-{mode}"
                process = cls.cli(
                    id_, *(["--case", "similarity"] if id_ == IDS[0] else []), "--params", str(parameter_file), "--output", str(output)
                )
                if process.returncode:
                    raise AssertionError(process.stdout + process.stderr)
                cls.results[id_, mode] = output

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def cli(cls, id_, *args, page=None):
        page = page or ROOT / "skills" / id_
        return subprocess.run(
            [sys.executable, "-B", str(page / (("runtime/" if id_ == IDS[0] else "") + id_ + ".py")), *args],
            cwd=cls.base,
            env=cls.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=90,
        )

    def test_four_real_numerical_runs_without_provider(self):
        for (id_, mode), output in self.results.items():
            receipt = json.loads((output / "run-receipt.json").read_bytes())
            self.assertEqual(receipt["status"], "PASS_LOCAL_TOOLS" if id_ == IDS[0] else "PASS_LOCAL_NUMERICAL")
            self.assertEqual(receipt["model_calls"], 0)
            self.assertFalse(receipt["agent_called"])
            skill = ROOT / "skills" / id_ / "SKILL.md"
            self.assertEqual(
                receipt["skill_sha256"], hashlib.sha256(skill.read_bytes()).hexdigest()
            )
            self.assertEqual(self.cli(id_, "--verify", str(output)).returncode, 0)

    def test_rdkit_identity_and_radius_comparison(self):
        def rows(mode, name):
            with (self.results[IDS[0], mode] / name).open(
                encoding="utf-8-sig", newline=""
            ) as stream:
                return list(csv.DictReader(stream))

        a, b = rows("default", "analysis.csv"), rows("modified", "analysis.csv")
        self.assertEqual(len(a), 5)
        self.assertEqual(len(rows("default", "errors.csv")), 0)
        for x, y in zip(a, b):
            for key in ["id", "canonical_isomeric_smiles", "formula", "mol_wt_g_mol"]:
                if key in x:
                    self.assertEqual(x[key], y[key])
        self.assertNotEqual(
            rows("default", "similarity.csv"), rows("modified", "similarity.csv")
        )

    def test_table_independent_oracle_both_ranges(self):
        for mode, n in [("default", 4), ("modified", 3)]:
            result = json.loads(
                (self.results[IDS[1], mode] / "numerical-result.json").read_bytes()
            )
            self.assertEqual(result["n"], n)
            self.assertEqual(result["numerical_checks"], "PASS")
            exact = float(result["independent_decimal_oracle"]["concentration_mg_L"])
            self.assertAlmostEqual(exact, result["sample_concentration_mg_L"], places=8)
        result = json.loads(
            (self.results[IDS[1], "default"] / "numerical-result.json").read_bytes()
        )
        self.assertAlmostEqual(
            result["sample_concentration_mg_L"], 94.37792857876974, places=8
        )

    def test_reports_are_self_contained_and_link_actual_zip(self):
        for output in self.results.values():
            text = (output / "report.html").read_text("utf-8")
            self.assertTrue("PASS_LOCAL_NUMERICAL" in text or "PASS_LOCAL_TOOLS" in text)
            self.assertIn("data:image/png;base64,", text)
            self.assertTrue("href='results.zip'" in text or 'href="results.zip"' in text)
            self.assertNotIn("<script", text.lower())
            self.assertNotIn("<iframe", text.lower())
            self.assertNotIn("https://", text)
            with zipfile.ZipFile(output / "results.zip") as archive:
                self.assertIn("report.html", archive.namelist())
                self.assertIn("SKILL.md", archive.namelist())

    def test_existing_directory_is_never_overwritten(self):
        output = self.base / "existing"
        output.mkdir()
        (output / "sentinel").write_bytes(b"preserve")
        for id_ in IDS:
            self.assertNotEqual(self.cli(id_, "--output", str(output)).returncode, 0)
        self.assertEqual(list(output.iterdir()), [output / "sentinel"])
        self.assertEqual((output / "sentinel").read_bytes(), b"preserve")

    def test_invalid_json_and_parameters_rejected_before_output(self):
        for id_ in IDS:
            valid = json.loads(
                (ROOT / "skills" / id_ / ("runtime/examples/03-similarity/parameters.json" if id_ == IDS[0] else "runtime/parameters.json")).read_bytes()
            )
            bad = dict(valid)
            bad["radius" if id_ == IDS[0] else "unknown_peak_area"] = True
            for index, raw in enumerate(
                ['{"x":1,"x":2}', '{"x":NaN}', "[]", json.dumps(bad)]
            ):
                params = self.base / "bad.json"
                params.write_text(raw)
                out = self.base / f"rejected-{id_}-{index}"
                result = self.cli(id_, "--params", str(params), "--output", str(out))
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(out.exists())
                self.assertNotIn("Traceback", result.stderr)

    def test_tampered_resource_rejected_before_import(self):
        page = self.base / "tampered"
        shutil.copytree(
            ROOT / "skills" / IDS[0],
            page,
            ignore=shutil.ignore_patterns("downloads", "__pycache__"),
        )
        (page / "runtime/molecule_tool.py").write_text(
            "raise AssertionError('IMPORTED_TAMPER')"
        )
        result = self.cli(
            IDS[0], "--output", str(self.base / "must-not-exist"), page=page
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("IMPORTED_TAMPER", result.stderr)
        self.assertFalse((self.base / "must-not-exist").exists())

    def test_tampered_result_and_zip_rejected(self):
        for index, name in enumerate(["parameters.json", "results.zip"]):
            output = self.base / f"tampered-output-{index}"
            shutil.copytree(self.results[IDS[0], "default"], output)
            with (output / name).open("ab") as stream:
                stream.write(b"broken")
            self.assertNotEqual(self.cli(IDS[0], "--verify", str(output)).returncode, 0)

    def test_agent_requires_explicit_config_without_exposing_value(self):
        for id_ in IDS:
            self.assertNotEqual(self.cli(id_, "--agent").returncode, 0)
            self.assertNotEqual(self.cli(id_, "--env-file", "absent.env").returncode, 0)
            output = self.base / ("missing-key-" + id_)
            result = self.cli(
                id_,
                "--agent",
                "--env-file",
                str(self.base / "absent.env"),
                "--output",
                str(output),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
