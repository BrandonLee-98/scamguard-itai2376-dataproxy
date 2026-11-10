from pydantic import BaseModel, Field
from typing import List, Dict

class UserSessionState(BaseModel):
    user_id: str = Field(default="senior_learner_01")
    current_difficulty: str = Field(default="beginner")
    scenarios_completed: int = Field(default=0)
    successful_identifications: int = Field(default=0)
    failed_identifications: int = Field(default=0)
    total_hints_used: int = Field(default=0)
    scenario_history: List[Dict[str, str]] = Field(default_factory=list)

    def update_performance(self, passed: bool, hints_used: int):
        self.scenarios_completed += 1
        self.total_hints_used += hints_used
        if passed:
            self.successful_identifications += 1
        else:
            self.failed_identifications += 1
            
        # Adaptive difficulty scaling logic
        success_rate = self.successful_identifications / max(1, self.scenarios_completed)
        if success_rate > 0.8 and self.scenarios_completed >= 3:
            self.current_difficulty = "intermediate"
        if success_rate > 0.9 and self.scenarios_completed >= 6:
            self.current_difficulty = "advanced"

    def get_summary(self) -> dict:
        return {
            "difficulty": self.current_difficulty,
            "completed": self.scenarios_completed,
            "success_rate": f"{(self.successful_identifications / max(1, self.scenarios_completed)) * 100:.1f}%",
            "hints_used": self.total_hints_used
        }
