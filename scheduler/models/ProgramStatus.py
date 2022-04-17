from enum import Enum

class ProgramStatus(Enum):
    UNINITIALIZED = 'UNINITIALIZED'
    BUILDING = 'BUILDING'
    UNFEASIBLE = 'UNFEASIBLE'
    WAITING_APPROVAL = 'WAITING_APPROVAL'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    SELECTED = 'SELECTED'
