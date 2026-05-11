from django.test import TestCase
from apps.departments.models import Faculty, Department


class DepartmentModelTests(TestCase):
    def test_create_faculty_and_department(self):
        f = Faculty.objects.create(name="Test Faculty", code="TF")
        d = Department.objects.create(faculty=f, name="Test Dept", code="TD")
        self.assertEqual(str(f), "Test Faculty (TF)")
        self.assertEqual(str(d), "Test Dept (TD)")
