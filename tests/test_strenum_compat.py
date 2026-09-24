import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


class TestStrEnumCompat(unittest.TestCase):
    def test_compat_strenum_behaves_like_string_enum(self) -> None:
        module_path = REPOSITORY_ROOT / "opencore_legacy_patcher" / "support" / "enum.py"
        spec = spec_from_file_location("opencore_legacy_patcher_support_enum", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)

        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        class CompatibilityEnum(module.StrEnum):
            VALUE = "example"

        self.assertIsInstance(CompatibilityEnum.VALUE.value, str)
        self.assertEqual(str(CompatibilityEnum.VALUE), CompatibilityEnum.VALUE.value)

    def test_strenum_imports_use_compat_module(self) -> None:
        expected_import = "from opencore_legacy_patcher.support.enum import StrEnum"
        files = [
            REPOSITORY_ROOT / "opencore_legacy_patcher" / "sucatalog" / "constants.py",
            REPOSITORY_ROOT / "opencore_legacy_patcher" / "sys_patch" / "patchsets" / "base.py",
            REPOSITORY_ROOT / "opencore_legacy_patcher" / "sys_patch" / "patchsets" / "detect.py",
            REPOSITORY_ROOT / "opencore_legacy_patcher" / "sys_patch" / "patchsets" / "hardware" / "base.py",
        ]

        for file in files:
            self.assertIn(expected_import, file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
