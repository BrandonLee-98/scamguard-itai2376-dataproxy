from typing import Any, Dict, List
from pydantic import BaseModel, Field


class UserSessionState(BaseModel):
    """
    Pydantic-backed session tracker monitoring senior learner progress,
    score, hint usage, and adaptive difficulty scaling.
    """
    current_difficulty: str = "Beginner"
    score: int = 0
    total_attempts: int = 0
    hints_used: int = 0
    history: List[Dict[str, Any]] = Field(default_factory=list)

    def update_performance(self, passed: bool, hints_used: int = 0) -> None:
        """Updates session metrics, logs history, and scales difficulty."""
        self.total_attempts += 1
        self.hints_used += hints_used

        if passed:
            self.score += 1

        self.history.append({
            "attempt": self.total_attempts,
            "passed": passed,
            "hints_used": hints_used,
            "difficulty": self.current_difficulty
        })

        # Adaptive difficulty scaling
        if self.score >= 3 and self.current_difficulty == "Beginner":
            self.current_difficulty = "Intermediate"
        elif self.score >= 6 and self.current_difficulty == "Intermediate":
            self.current_difficulty = "Advanced"

    def get_summary(self) -> Dict[str, Any]:
        """Returns standardized session metrics for the simulation runner."""
        return {
            "difficulty": self.current_difficulty,
            "score": self.score,
            "attempts": self.total_attempts,
            "hints_used": self.hints_used
        }
