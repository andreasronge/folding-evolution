"""Selection: tournament selection and elitism."""

from __future__ import annotations

import random

from .individual import Individual


def tournament_select(
    population: list[Individual],
    tournament_size: int,
    rng: random.Random,
) -> Individual:
    """Select one individual via tournament selection."""
    competitors = rng.sample(population, min(tournament_size, len(population)))
    return max(competitors, key=lambda ind: ind.fitness)


def select_next_generation(
    population: list[Individual],
    elite_count: int,
    tournament_size: int,
    rng: random.Random,
) -> list[Individual]:
    """Select parents for the next generation: elitism + tournament."""
    sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=True)
    elites = sorted_pop[:elite_count]

    selected = list(elites)
    while len(selected) < len(population):
        selected.append(tournament_select(population, tournament_size, rng))

    return selected
