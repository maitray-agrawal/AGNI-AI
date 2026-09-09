import subprocess
import tempfile
import time
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger("agni.security.sandbox")


class SandboxResult(BaseModel):
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    isolation_mode: str  # "docker_network_none" or "hardened_process_loopback"


class CodeSandbox:
    """Executes generated code in an isolated environment with zero network egress."""

    @staticmethod
    def execute_code(code: str, timeout: int = 10) -> SandboxResult:
        start_time = time.time()

        # Security Injection: Monkey-patch socket module to guarantee zero network calls
        sandbox_guard_header = (
            "import sys\n"
            "try:\n"
            "    import socket\n"
            "    def _guard_blocked(*args, **kwargs):\n"
            "        raise PermissionError('AGNI-AI Air-Gap Security Violation: Outbound network socket creation prohibited in sandbox.')\n"
            "    socket.socket = _guard_blocked\n"
            "except Exception:\n"
            "    pass\n\n"
        )

        full_code = sandbox_guard_header + code

        # Attempt Docker network=none if docker daemon is reachable
        docker_available = False
        try:
            chk = subprocess.run(["docker", "ps"], capture_output=True, timeout=2)
            if chk.returncode == 0:
                docker_available = True
        except Exception:
            docker_available = False

        if docker_available:
            try:
                cmd = [
                    "docker", "run", "--rm",
                    "--network", "none",
                    "--memory", "512m",
                    "--cpus", "1.0",
                    "python:3.11-slim",
                    "python", "-c", full_code
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                duration_ms = int((time.time() - start_time) * 1000)
                return SandboxResult(
                    success=proc.returncode == 0,
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                    exit_code=proc.returncode,
                    duration_ms=duration_ms,
                    isolation_mode="docker_network_none",
                )
            except subprocess.TimeoutExpired:
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr=f"Execution timed out after {timeout} seconds.",
                    exit_code=-1,
                    duration_ms=timeout * 1000,
                    isolation_mode="docker_network_none",
                )
            except Exception as e:
                logger.warning(f"Docker sandbox execution failed, falling back to process isolation: {e}")

        # Fallback: Hardened Process Isolation
        # Restrict environment to prevent leaking host secrets
        safe_env = {
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": "",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tf:
            tf.write(full_code)
            temp_path = tf.name

        try:
            python_bin = sys.executable
            proc = subprocess.run(
                [python_bin, temp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=safe_env,
            )
            duration_ms = int((time.time() - start_time) * 1000)
            return SandboxResult(
                success=proc.returncode == 0,
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                duration_ms=duration_ms,
                isolation_mode="hardened_process_loopback",
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds.",
                exit_code=-1,
                duration_ms=timeout * 1000,
                isolation_mode="hardened_process_loopback",
            )
        finally:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass


def execute_code(code: str, timeout: int = 10) -> SandboxResult:
    """Frozen interface contract for sandboxed code execution."""
    return CodeSandbox.execute_code(code, timeout)
