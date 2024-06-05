from enum import Enum

class PlanStatus(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    FINISHED = 'FINISHED'
    CANCELLED = 'CANCELLED'
