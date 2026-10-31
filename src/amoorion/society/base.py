"""Society: personas react to a topic and to each other, round after round.

In the spirit of OASIS and MiroFish, on a much smaller scale: try how a post may be
received before it goes out. It only ever talks in memory: no plugin is involved, so
nothing a simulation says can reach a platform. What was said is a list of messages
(the `simulate` method keeps them in the inbox as `society:<run>`).

`think(persona, topic, feed)` says what a persona says, or None to stay silent. The
default is `scripted`, the same every time, which shows the mechanics and no more;
it is no prediction. A language model gives real reactions (`simulate --llm`), and
anything else callable can stand in, a model of your own included.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from pydantic import Field

from amoorion.core import Model
from amoorion.models import Account, Message
from amoorion.vault import Vault
from amoorion.utilities.llm import complete


class Persona(Model):
    """Somebody in a simulation: a name, who they are, and what they think of things."""

    name: str = Field(min_length=1)
    bio: str = ""
    stance: str = Field(
        "neutral",
        description="supportive, critical, neutral or silent: what `scripted` goes by",
    )


Think = Callable[[Persona, str, list[Message]], str | None]


def scripted(
    persona: Persona,
    topic: str,
    feed: list[Message],
) -> str | None:
    """No model: a line by stance, answering the last one who spoke."""

    last = next(
        (
            message
            for message in reversed(feed)
            if message.author and message.author.handle != persona.name
        ),
        None,
    )

    to = f"@{last.author.handle} " if last and last.author else ""

    return {
        "supportive": f"{to}{topic}? Yes, finally.",
        "critical": f"{to}I doubt {topic} is what is needed.",
        "neutral": f"{to}What does {topic} change, in practice?",
    }.get(persona.stance)


def by_model(
    vault: Vault,
    model: str | None = None,
) -> Think:
    """Reactions from a language model (`llm/url` in the vault)."""

    def think(
        persona: Persona,
        topic: str,
        feed: list[Message],
    ) -> str | None:

        lines = "\n".join(
            f"{message.author.handle if message.author else '?'}: {message.text}"
            for message in feed[-20:]
        )

        system = f"You are {persona.name}. {persona.bio} Your stance: {persona.stance}. Answer as a short social media post."

        prompt = f"The topic: {topic}\n\nSaid so far:\n{lines or '(nothing)'}\n\nWhat do you say?"

        return complete(prompt, vault, system=system, model=model).text or None

    return think


class Society:
    """Personas reacting to a topic and to each other, in rounds, on a shared feed.

    `think` decides what a persona says; nobody and nothing outside takes part.
    """

    def __init__(
        self,
        personas: list[Persona],
        think: Think = scripted,
        run: str = "default",
    ) -> None:
        """The people, the way they think, and the run that names this feed."""

        self.personas, self.think, self.platform = (
            personas,
            think,
            f"society:{run}",
        )

    def simulate(
        self,
        topic: str,
        rounds: int = 3,
    ) -> list[Message]:
        """Every persona in every round may add to the feed; returns the feed, oldest first."""

        feed: list[Message] = []

        start = datetime.now(UTC)

        for round_ in range(1, rounds + 1):
            for persona in self.personas:
                text = self.think(
                    persona,
                    topic,
                    feed,
                )

                if not text:
                    continue

                feed.append(
                    Message(
                        platform=self.platform,
                        text=text,
                        id=f"{start.timestamp():.0f}-{round_}-{persona.name}",
                        author=Account(
                            platform=self.platform,
                            handle=persona.name,
                            name=persona.bio or None,
                        ),
                        reply_to=feed[-1].id if feed else None,
                        created_at=start + timedelta(seconds=len(feed)),
                    )
                )

        return feed
