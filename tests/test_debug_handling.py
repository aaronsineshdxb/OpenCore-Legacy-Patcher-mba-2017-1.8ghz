import unittest

from types import SimpleNamespace

from opencore_legacy_patcher.efi_builder.build import remove_redundant_bless_overrides
from opencore_legacy_patcher.efi_builder.misc import BuildMiscellaneous, sanitize_boot_args


class TestDebugHandling(unittest.TestCase):
    def test_release_build_removes_base_debug_arguments(self) -> None:
        boot_args = "keepsyms=1 debug=0x100 -lilubetaall"

        sanitized = sanitize_boot_args(boot_args, debug_enabled=False)

        self.assertEqual(sanitized, "-lilubetaall")

    def test_debug_build_preserves_base_debug_arguments(self) -> None:
        boot_args = "keepsyms=1 debug=0x100 -lilubetaall"

        sanitized = sanitize_boot_args(boot_args, debug_enabled=True)

        self.assertEqual(sanitized, boot_args)

    def test_redundant_bless_overrides_are_removed(self) -> None:
        entries = [
            "\\EFI\\Microsoft\\Boot\\bootmgfw.efi",
            "\\System\\Library\\CoreServices\\boot.efi",
            "\\EFI\\BOOT\\BOOTx64.efi",
        ]

        cleaned = remove_redundant_bless_overrides(entries)

        self.assertEqual(cleaned, ["\\EFI\\BOOT\\BOOTx64.efi"])

    def test_sanitizer_matches_complete_boot_arguments_only(self) -> None:
        boot_args = "debug=0x1000 keepsyms=10 -lilubetaall"

        sanitized = sanitize_boot_args(boot_args, debug_enabled=False)

        self.assertEqual(sanitized, boot_args)

    def test_release_debug_handler_clears_persistent_debug_settings(self) -> None:
        builder = BuildMiscellaneous.__new__(BuildMiscellaneous)
        builder.constants = SimpleNamespace(
            verbose_debug=False,
            kext_debug=False,
            opencore_debug=False,
        )
        builder.config = {
            "NVRAM": {
                "Add": {
                    "7C436110-AB2A-4BBB-A880-FE41995C9F82": {
                        "boot-args": "keepsyms=1 debug=0x100 -lilubetaall",
                    }
                }
            },
            "Misc": {
                "Debug": {
                    "ApplePanic": True,
                    "Target": 3,
                    "DisplayLevel": 2147483650,
                    "AppleDebug": True,
                }
            },
        }

        builder._debug_handling()

        self.assertEqual(
            builder.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"],
            "-lilubetaall",
        )
        self.assertEqual(
            builder.config["Misc"]["Debug"],
            {
                "ApplePanic": False,
                "Target": 0,
                "DisplayLevel": 0,
                "AppleDebug": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
