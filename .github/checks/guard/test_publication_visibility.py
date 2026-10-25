"""Public/private publication identity contract, without GitHub/network calls."""
from pathlib import Path
import importlib.util
import os
import unittest

ROOT = Path(__file__).resolve().parents[3]
PAGE = ROOT


class PublicationVisibilityTests(unittest.TestCase):
    def api(self):
        spec=importlib.util.spec_from_file_location('publisher_under_test',PAGE/'tools/publish_checked_skill.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertTrue(callable(getattr(module,'validate_repository',None)), 'Publisher still hardcodes PRIVATE without declared-visibility validation.')
        return module

    def test_public_repository_matches_public_declaration(self):
        self.assertFalse(self.api().validate_repository({'nameWithOwner':'CCcolab/AI4OrgChem-data-processing','visibility':'PUBLIC'},'PUBLIC'))

    def test_private_repository_matches_private_declaration(self):
        self.assertTrue(self.api().validate_repository({'nameWithOwner':'CCcolab/AI4OrgChem-data-processing','visibility':'PRIVATE'},'PRIVATE'))

    def test_visibility_mismatch_is_rejected(self):
        api=self.api()
        for actual,declared in [('PUBLIC','PRIVATE'),('PRIVATE','PUBLIC')]:
            with self.assertRaises(RuntimeError):api.validate_repository({'nameWithOwner':'CCcolab/AI4OrgChem-data-processing','visibility':actual},declared)

    def test_wrong_repository_is_rejected(self):
        with self.assertRaises(RuntimeError):self.api().validate_repository({'nameWithOwner':'other/repository','visibility':'PUBLIC'},'PUBLIC')

    def test_unknown_declared_visibility_is_rejected(self):
        with self.assertRaises(RuntimeError):self.api().validate_repository({'nameWithOwner':'CCcolab/AI4OrgChem-data-processing','visibility':'PUBLIC'},'INTERNAL')


if __name__=='__main__':unittest.main(verbosity=2)
