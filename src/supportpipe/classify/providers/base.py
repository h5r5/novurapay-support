"""Abstract base class for ticket classification providers."""

from abc import ABC, abstractmethod
from typing import Any

from supportpipe.schemas import ClassificationResult


class BaseClassifierProvider(ABC):
    @abstractmethod
    def classify(
        self,
        ticket_text: str,
        channel: str = "app",
        **kwargs: Any,
    ) -> ClassificationResult:
        """Classify a support ticket into closed category, priority, and confidences."""
        pass
