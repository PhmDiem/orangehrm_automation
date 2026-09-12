from datetime import datetime

import pytest

from utils.test_data import TestData


pytestmark = pytest.mark.regression


def test_future_leave_dates_are_future_and_have_expected_duration():
    from_date, to_date = TestData.generate_future_leave_dates(
        min_days=5,
        max_days=5,
        duration_days=2,
    )

    start = datetime.strptime(from_date, "%Y-%m-%d")
    end = datetime.strptime(to_date, "%Y-%m-%d")
    assert (start - datetime.now()).days >= 4
    assert (end - start).days == 2


def test_past_leave_dates_create_reverse_range():
    from_date, to_date = TestData.generate_past_leave_dates(
        days_ago=30,
        duration_days=2,
    )

    assert to_date < from_date
    assert TestData.calculate_days_needed(from_date, to_date) == -1


def test_to_ui_date_format_converts_iso_date():
    assert TestData.to_ui_date_format("2026-09-12") == "2026-12-09"


def test_unique_marker_contains_requested_prefix():
    assert TestData.generate_unique_marker("UNIT") .startswith("UNIT_")
