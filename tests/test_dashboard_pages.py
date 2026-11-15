from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_restaurant_dashboard_is_additive_and_exportable():
    page = (ROOT / "dashboard/pages/08_Restaurant_Performance.py").read_text(encoding="utf-8")
    for token in ["restaurant_id", "cancellation_rate", "download_button", "synthetic"]:
        assert token.lower() in page.lower()


def test_data_quality_dashboard_checks_core_integrity():
    page = (ROOT / "dashboard/pages/09_Data_Quality_Monitoring.py").read_text(encoding="utf-8")
    for token in ["Duplicate order_id", "Null values", "Negative paid amount", "download_button", "production"]:
        assert token.lower() in page.lower()


def test_restaurant_dashboard_renders_without_exceptions():
    page = str(ROOT / "dashboard/pages/08_Restaurant_Performance.py")
    at = AppTest.from_file(page, default_timeout=60).run()
    assert not at.exception
    assert any("Restaurant Performance" in title.value for title in at.title)


def test_data_quality_dashboard_renders_without_exceptions():
    page = str(ROOT / "dashboard/pages/09_Data_Quality_Monitoring.py")
    at = AppTest.from_file(page, default_timeout=60).run()
    assert not at.exception
    assert any("Data Quality Monitoring" in title.value for title in at.title)
