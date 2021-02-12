from .base import BaseModel


class TeamTask(BaseModel):
    team_id: int
    task_id: int
    status: int
    stolen: int
    lost: int
    score: float
    checks: int
    check_passed: int
    public_message: str
    private_message: str
    command: str
