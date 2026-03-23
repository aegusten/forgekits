"""ForgeKits — output validator.

Runs sanity checks on generated files before declaring success.
Not a full linter — just catches the worst mistakes.
"""

from __future__ import annotations

import py_compile
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from forgekits.models import GeneratedFile


@dataclass
class ValidationResult:
    """Result of validating generated output."""

    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Patterns that should never appear in generated code
SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r'(?:password|secret|api_key|token)\s*=\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
    re.compile(r'(?:sk-|pk_live_|AKIA[0-9A-Z]{16})'),
    re.compile(r'postgresql://\w+:\w+@', re.IGNORECASE),
]


class OutputValidator:
    """Validates generated files for common problems."""

    def validate(self, files: list[GeneratedFile]) -> ValidationResult:
        """Run all validation checks."""
        errors: list[str] = []
        warnings: list[str] = []

        for gf in files:
            # Syntax check Python files
            if gf.path.endswith(".py"):
                syntax_err = self._check_syntax(gf)
                if syntax_err:
                    errors.append(f"{gf.path}: {syntax_err}")

            # Secret detection on all files
            secrets = self._check_secrets(gf)
            for s in secrets:
                errors.append(f"{gf.path}: Possible hardcoded secret — {s}")

            # Empty file check
            if not gf.content.strip():
                warnings.append(f"{gf.path}: File is empty")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _check_syntax(self, gf: GeneratedFile) -> str | None:
        """Check if a Python file has valid syntax."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(gf.content)
                f.flush()
                py_compile.compile(f.name, doraise=True)
            return None
        except py_compile.PyCompileError as e:
            return f"Syntax error: {e}"
        except Exception as e:
            return f"Validation error: {e}"

    def _check_secrets(self, gf: GeneratedFile) -> list[str]:
        """Scan for hardcoded secrets."""
        found: list[str] = []
        for pattern in SECRET_PATTERNS:
            matches = pattern.findall(gf.content)
            if matches:
                # Don't include the actual secret in the error
                found.append(f"Pattern match: {pattern.pattern[:40]}...")
        return found
