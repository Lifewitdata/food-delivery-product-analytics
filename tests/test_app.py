from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "dashboard" / "app.py")


def metric(at, label):
    return next(m.value for m in at.metric if m.label == label)


def test_app_runs_without_exceptions():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert len(at.tabs) == 4


def test_unfiltered_kpis_match_notebook():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert metric(at, "Orders") == "15,000"
    assert metric(at, "GMV (SAR)") == "5,797,901"
    assert metric(at, "AOV (SAR)") == "446.10"
    assert metric(at, "Cancellation rate") == "13.35%"
    assert metric(at, "On-time rate") == "90.51%"
    assert metric(at, "Avg delivery (min)") == "93.88"


def test_city_filter_changes_kpis():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.multiselect[0].set_value(["Riyadh"]).run()
    assert not at.exception
    assert metric(at, "Orders") == "3,723"
    assert metric(at, "Late rate (source flag)") != ""


def test_premium_and_month_filters_change_kpis():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.multiselect[1].set_value(["premium"]).run()
    premium_orders = metric(at, "Orders")
    at.sidebar.slider[0].set_value((1, 6)).run()
    assert not at.exception
    assert premium_orders != "15,000"
    assert metric(at, "Orders") != premium_orders


def test_empty_selection_shows_warning_without_exception():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception
    assert any("No orders match" in w.value for w in at.warning)
