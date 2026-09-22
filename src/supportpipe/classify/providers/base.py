"""Abstract base class for ticket classification providers."""

from abc import ABC, abstractmethod

from supportpipe.schemas import ClassificationResult


class BaseClassifierProvider(ABC):
    @abstractmethod
    def classify(self, ticket_text: str, channel: str = "app") -> ClassificationResult:
        """Classify a support ticket into closed category, priority, and confidences."""
        pass
