"""Turn and scorecard state for a complete Hoopreel game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .models import Lock, PlayerTeamSeason
from .roulette import RouletteEngine
from .scoring import Category, category_score, score_preview, upper_bonus


MAX_SPINS_PER_TURN = 3


@dataclass(slots=True)
class TurnState:
    current: PlayerTeamSeason
    spins_used: int = 1
    last_locks: frozenset[Lock] = field(default_factory=frozenset)


class GameState:
    def __init__(self, roulette: RouletteEngine, goat_pools: dict[str, tuple[PlayerTeamSeason, ...]] | None = None) -> None:
        self.roulette = roulette
        self.goat_pools = goat_pools or {}
        if self.goat_pools and (set(self.goat_pools) != {"award", "prehistoric"} or not all(self.goat_pools.values())):
            raise ValueError("Both GOAT pools must be nonempty")
        self.scorecard: dict[Category, int] = {}
        self.turn: TurnState | None = None
        self.scored_records: dict[Category, PlayerTeamSeason] = {}

    @property
    def turns_completed(self) -> int:
        return len(self.scorecard)

    @property
    def is_complete(self) -> bool:
        return self.turns_completed == len(Category)

    @property
    def bonus(self) -> int:
        return upper_bonus(self.scorecard)

    @property
    def total_score(self) -> int:
        return sum(self.scorecard.values()) + self.bonus

    @property
    def open_categories(self) -> tuple[Category, ...]:
        return tuple(category for category in Category if category not in self.scorecard)

    def start_turn(self, force_pool: str | None = None) -> PlayerTeamSeason:
        if self.is_complete:
            raise RuntimeError("The game is complete")
        if self.turn is not None:
            raise RuntimeError("A turn is already active")
        current = self._draw(force_pool=force_pool)
        self.turn = TurnState(current=current)
        return current

    def reroll(self, locks: Iterable[Lock] = (), force_pool: str | None = None) -> PlayerTeamSeason:
        if self.turn is None:
            raise RuntimeError("Start a turn before rerolling")
        if self.turn.spins_used >= MAX_SPINS_PER_TURN:
            raise RuntimeError("No rerolls remain this turn")
        lock_set = frozenset(locks)
        if not lock_set.issubset(frozenset(Lock)):
            raise ValueError("Unknown roulette lock")
        if lock_set == frozenset(Lock):
            raise ValueError("Cannot reroll while all three slots are locked")
        if self.turn.current.pool != "normal" and lock_set:
            raise ValueError("GOAT results cannot be kept. Score this result or spin again.")
        current = self._draw(self.turn.current, lock_set, force_pool)
        self.turn.current = current
        self.turn.spins_used += 1
        self.turn.last_locks = lock_set
        return current

    def _draw(self, current=None, locks=frozenset(), force_pool=None):
        if force_pool is not None and (not isinstance(force_pool, str) or locks or force_pool not in self.goat_pools):
            raise ValueError("A GOAT preview requires open reels and a valid pool")
        if not locks and self.goat_pools:
            if force_pool is not None or self.roulette.rng.randrange(1296) == 0:
                name = force_pool or self.roulette.rng.choice(("award", "prehistoric"))
                return self.roulette.rng.choice(self.goat_pools[name])
        # A GOAT reroll returns to the normal pool without keeping GOAT identities.
        return self.roulette.spin(current if current and current.pool == "normal" else None, locks)

    def preview(self) -> dict[Category, int]:
        if self.turn is None:
            raise RuntimeError("No active turn")
        return {category: score for category, score in score_preview(self.turn.current).items()
                if category in self.open_categories}

    def score(self, category: Category) -> int:
        if self.turn is None:
            raise RuntimeError("No active turn")
        if category in self.scorecard:
            raise ValueError(f"Category already used: {category.value}")
        value = category_score(self.turn.current, category)
        self.scorecard[category] = value
        self.scored_records[category] = self.turn.current
        self.turn = None
        return value
