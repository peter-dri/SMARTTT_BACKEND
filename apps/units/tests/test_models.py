from django.test import TestCase
from apps.departments.models import Faculty, Department
from apps.units.models import Unit


class UnitModelTests(TestCase):
    def test_unit_creation(self):
        f = Faculty.objects.create(name="F", code="F2")
        d = Department.objects.create(faculty=f, name="D2", code="D2")
        u = Unit.objects.create(department=d, code="U1", name="Intro", credit_hours=3.0)
        self.assertEqual(str(u), "Intro (U1)")
