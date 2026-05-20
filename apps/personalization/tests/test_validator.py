from django.test import SimpleTestCase

from rest_framework.exceptions import ValidationError

from apps.personalization.validators import PersonalizationValidator


class PersonalizationValidatorTests(SimpleTestCase):
	def test_validate_semester_rejects_invalid_value(self):
		with self.assertRaises(ValidationError):
			PersonalizationValidator.validate_semester(3)
