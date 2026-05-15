from datetime import time

from django.test import SimpleTestCase

from apps.personalization.services import TimetableSortingService


class DummySlot:
	def __init__(self, day_of_week, start_time, unit_code):
		self.day_of_week = day_of_week
		self.time_slot = type("TimeSlot", (), {"start_time": start_time})()
		self.unit = type("Unit", (), {"code": unit_code})()


class TimetableSortingServiceTests(SimpleTestCase):
	def test_sort_sessions_orders_by_day_and_time(self):
		sessions = [
			DummySlot("WED", time(10, 0), "DBMS"),
			DummySlot("MON", time(14, 0), "OOP"),
			DummySlot("MON", time(8, 0), "ALG"),
		]

		ordered = TimetableSortingService.sort_sessions(sessions)

		self.assertEqual([slot.unit.code for slot in ordered], ["ALG", "OOP", "DBMS"])
