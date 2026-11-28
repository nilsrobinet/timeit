"""
Abstract storage interface. to be implemented by storage classes.
The implementing class shall provide methods for saving and loading data as well as managing and accessing it.
"""

import abc
from src.data_model import Day


class Storage(abc.ABC):
    """Abstract storage. Defines interface.
    The methods of the implementation shall not fail. In case of missing data, they should handle it gracefully and return None or similar.
    """

    @abc.abstractmethod
    def save(self):
        """Save data."""

    @abc.abstractmethod
    def load(self):
        """Load data."""

    @abc.abstractmethod
    def get(self, date) -> Day | None:
        """Get Day for date."""

    @abc.abstractmethod
    def get_or_create(self, date) -> Day:
        """Get Day for date."""

    @abc.abstractmethod
    def add(self, day: Day) -> None:
        """Add a day."""

    def update(self, day: Day) -> None:
        """Update a day. This shall work regardless of existence. In case it doesn't exist, add it."""

    @abc.abstractmethod
    def remove(self, date) -> None:
        """Remove a day."""

    @abc.abstractmethod
    def has(self, date) -> bool:
        """Check if a day exists."""

    @abc.abstractmethod
    def get_next_id(self) -> int:
        """Get next entry id."""

    @abc.abstractmethod
    def get_dates(self) -> list[str]:
        """Get all dates."""

    @abc.abstractmethod
    def update_storage(self) -> None:
        """Update the underlying storage."""
