import pytest
from backend.app.security.sandbox import execute_code


def test_sandbox_calculation_execution():
    """Validates code sandbox computes deterministic calculation."""
    code = (
        "t_initial = 8.2\n"
        "t_final = 7.4\n"
        "reduction = ((t_initial - t_final) / t_initial) * 100\n"
        "print(f'PERCENTAGE_REDUCTION={reduction:.2f}%')\n"
    )
    result = execute_code(code, timeout=5)
    assert result.success is True
    assert result.exit_code == 0
    assert "PERCENTAGE_REDUCTION=9.76%" in result.stdout
    print(f"\n[Sandbox Execution Output]: {result.stdout.strip()}")
    print(f"[Isolation Mode]: {result.isolation_mode}, Duration: {result.duration_ms}ms")


def test_sandbox_network_blocking():
    """Security test: Validates that sandbox strictly prevents network socket creation."""
    malicious_code = (
        "import socket\n"
        "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "s.connect(('1.1.1.1', 80))\n"
    )
    result = execute_code(malicious_code, timeout=5)
    # The execution must fail with PermissionError
    assert result.success is False
    assert result.exit_code != 0
    assert "prohibited in sandbox" in result.stderr or "PermissionError" in result.stderr
    print(f"\n[Air-Gap Security Defense Verified]: Outbound socket attempt successfully intercepted.")
    print(f"[Sandbox Error Message]: {result.stderr.strip()}")
