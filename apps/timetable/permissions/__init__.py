from .permissions import (
    IsSuperAdminOrReadOnly,
    IsDepartmentAdminOrSuper,
    IsRegistrarOrSuper,
    CanManageTimetable,
    CanViewTimetable,
    CanManageRooms,
    CanManageTimeSlots,
    IsLecturerOrAdmin,
    IsStudentOrAdmin,
)

__all__ = [
    "IsSuperAdminOrReadOnly",
    "IsDepartmentAdminOrSuper",
    "IsRegistrarOrSuper",
    "CanManageTimetable",
    "CanViewTimetable",
    "CanManageRooms",
    "CanManageTimeSlots",
    "IsLecturerOrAdmin",
    "IsStudentOrAdmin",
]
