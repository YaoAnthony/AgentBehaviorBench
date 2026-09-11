"""ABB message/result boundary for an Agent whose native interface is its CLI.

RA.Aid drives its own ReAct loop, tool approval and project state from
`python -m ra_aid`. There is no importable graph to invoke, so the binding runs
that command — the Agent's real entry point — and returns what it prints. The
model call still leaves the container as native OpenAI traffic, so the
Interceptor captures it exactly as for an in-process Agent.
"""
import asyncio
import os
import subprocess
from collections.abc import Mapping

WORKDIR = "/tmp/ra-aid-workspace"
HOME = "/tmp/ra-aid-home"
MODEL = os.environ.get("RA_AID_MODEL", "gpt-4o-mini")


class RaAidCli:
    def invoke(self, value, config=None):
        return asyncio.run(self.ainvoke(value, config))

    async def ainvoke(self, value, config=None):
        task = _task(value)
        return await asyncio.to_thread(self._run, task)

    def _run(self, task):
        os.makedirs(WORKDIR, exist_ok=True)
        os.makedirs(HOME, exist_ok=True)
        environment = dict(os.environ, HOME=HOME)
        command = [
            "python", "-m", "ra_aid",
            "--message", task,
            "--research-only",      # one research pass; no implementation phase
            "--provider", "openai",
            "--model", MODEL,
            "--cowboy-mode",        # non-interactive: no shell approval prompts
            "--no-track-cost",
        ]
        completed = subprocess.run(command, capture_output=True, text=True,
                                   cwd=WORKDIR, env=environment, timeout=900)
        answer = (completed.stdout or "").strip()
        if completed.returncode != 0 and not answer:
            raise RuntimeError(
                f"ra_aid exited {completed.returncode}: {(completed.stderr or '')[-800:]}")
        if not answer:
            raise RuntimeError("ra_aid produced no output")
        return {"answer": answer, "returncode": completed.returncode,
                "stderr": (completed.stderr or "")[-4000:]}

    def close(self):
        pass


def _task(value):
    """Accept plain text, {"message": ...} or the native {"task": ...}."""
    if isinstance(value, str):
        value = {"message": value}
    if not isinstance(value, Mapping) or set(value) not in ({"message"}, {"task"}):
        raise ValueError("Supply either message text or a native task string")
    task = value.get("message") or value.get("task")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("The task must be a non-empty string")
    return task


def create_graph():
    return RaAidCli()
