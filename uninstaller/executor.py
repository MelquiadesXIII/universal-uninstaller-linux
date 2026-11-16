"""Controlled execution of plan steps."""

from __future__ import annotations

from pathlib import Path

from . import runner, trash
from .models import Plan, Result, Risk, Step
from .safety import validate_path


def execute(
    plan: Plan,
    *,
    dry_run: bool = False,
    home: Path | None = None,
    user_roots: tuple[Path, ...] = (),
    root_roots: tuple[Path, ...] = (),
) -> Result:
    """Execute steps, revalidating paths immediately before deletion."""

    if plan.blocked_reason:
        return Result("blocked", notes=[plan.blocked_reason])
    done: list[Step] = []
    failed: list[Step] = []
    notes: list[str] = []
    if not dry_run and any(step.needs_root for step in plan.steps):
        if runner.validate_sudo() != 0:
            return Result("failed", notes=["Privileged credentials could not be validated."])
    for step in plan.steps:
        if dry_run:
            notes.append(step.description)
            continue
        if step.kind in {"trash", "root_rm"}:
            roots = root_roots if step.kind == "root_rm" else user_roots
            if step.path is None:
                failed.append(step)
                notes.append(f"Ruta ausente: {step.description}")
                continue
            valid, reason = validate_path(step.path, home=home, roots=roots)
            if not valid:
                failed.append(step)
                notes.append(f"Ruta rechazada ({reason}): {step.path}")
                continue
        success = _execute_step(step, home=home)
        (done if success else failed).append(step)
        if not success:
            notes.append(f"Failed: {step.description}")
    if failed and done:
        status = "partial"
    elif failed:
        status = "failed"
    else:
        status = "ok"
    return Result(status, done=done, failed=failed, notes=notes)


def _execute_step(step: Step, *, home: Path | None) -> bool:
    if step.kind == "info":
        return True
    if step.kind == "run":
        return step.argv is not None and runner.run_mutating(step.argv) == 0
    if step.kind == "trash":
        return step.path is not None and trash.move_to_trash(step.path, home=home)
    if step.kind == "root_rm":
        return (
            step.path is not None
            and runner.run_mutating(
                ["sudo", "rm", "-r", "--one-file-system", "--", str(step.path)]
            )
            == 0
        )
    return False
