"""Sort and group timetable sessions for response payloads."""

from __future__ import annotations

from apps.personalization.utils import DAY_ORDER, build_empty_timetable, group_sessions_by_day


class TimetableSortingService:
	"""Sort sessions by day and time, then group them."""

	@staticmethod
	def sort_sessions(sessions):
		return sorted(
			sessions,
			key=lambda session: (
				DAY_ORDER.index(session.day_of_week) if session.day_of_week in DAY_ORDER else len(DAY_ORDER),
				session.time_slot.start_time,
				session.unit.code,
			),
		)

	@staticmethod
	def group_sessions(sessions):
		return group_sessions_by_day(TimetableSortingService.sort_sessions(sessions))

	@staticmethod
	def empty_grouped_timetable():
		return build_empty_timetable()
