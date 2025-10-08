"""Constraint registry."""
from scheduler.constraints.base import Constraint
from scheduler.constraints.coverage import CoverageConstraint
from scheduler.constraints.hours import DailyLimitConstraint, MaxHoursConstraint
from scheduler.constraints.rest import RestPeriodConstraint

__all__ = [
    "Constraint",
    "CoverageConstraint",
    "DailyLimitConstraint",
    "MaxHoursConstraint",
    "RestPeriodConstraint",
]
