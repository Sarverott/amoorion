"""Skill: amoorion's agent skill, what an agent reads to learn to use it."""

from pathlib import Path
from typing import ClassVar

from amoorion.core import Model
from amoorion.methods.base import METHODS, Method

SKILL = Path(__file__).parents[1] / "SKILL.md"


class SkillText(Model):
    """The skill's file: `path` to copy it into an agent's skills, `text` to read it."""

    path: str
    text: str


@METHODS.register
class Skill(Method):
    """Hands out the SKILL.md installed with the package, so its version always fits."""

    name: ClassVar[str] = "skill"
    description: ClassVar[str] = (
        "The agent skill of amoorion: how an AI agent should use it"
    )
    read_only: ClassVar[bool] = True

    def run(
        self,
        params: Model,
    ) -> SkillText:
        """Read the file; nothing else is touched, so it needs no vault."""

        return SkillText(
            path=str(SKILL),
            text=SKILL.read_text(),
        )
