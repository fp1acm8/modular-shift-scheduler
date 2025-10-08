"""Objective term registry."""
from scheduler.objective.base import ObjectiveTerm
from scheduler.objective.preferences import OvertimePenalty, PreferenceSatisfaction, WeekendDistribution

__all__ = [
    "ObjectiveTerm",
    "OvertimePenalty",
    "PreferenceSatisfaction",
    "WeekendDistribution",
]
