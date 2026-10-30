"""Integration tests: the full HTTP request -> response path."""

from tests.conftest import encode

URL = "/api/v1/images/analyze"


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_good_jpeg(client, sharp_rgb):
    r = client.post(URL, files={"file": ("living.jpg", encode(sharp_rgb), "image/jpeg")})
    assert r.status_code == 200
    body = r.json()
    assert body["metadata"]["format"] == "JPEG"
    assert body["metadata"]["width"] == 640
    assert body["blur"]["is_blurry"] is False
    assert body["exposure"]["verdict"] == "well_exposed"
    assert body["issues"] == []
    assert body["analyzer_version"]


def test_analyze_png_and_webp(client, sharp_rgb):
    for fmt, name in [("PNG", "a.png"), ("WEBP", "a.webp")]:
        r = client.post(URL, files={"file": (name, encode(sharp_rgb, fmt), "image/*")})
        assert r.status_code == 200, r.text
        assert r.json()["metadata"]["format"] == fmt


def test_blurry_dark_image_reports_issues(client, dark_rgb):
    r = client.post(URL, files={"file": ("dark.jpg", encode(dark_rgb), "image/jpeg")})
    body = r.json()
    assert body["exposure"]["verdict"] == "underexposed"
    assert body["blur"]["is_blurry"] is True  # a flat image has no edges
    assert len(body["issues"]) == 2


def test_rejects_non_image(client):
    r = client.post(URL, files={"file": ("evil.jpg", b"not really an image", "image/jpeg")})
    assert r.status_code == 422


def test_rejects_empty_file(client):
    r = client.post(URL, files={"file": ("empty.jpg", b"", "image/jpeg")})
    assert r.status_code == 422


def test_rejects_oversized_file(client, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "max_upload_mb", 0)
    r = client.post(URL, files={"file": ("x.jpg", b"x" * 10, "image/jpeg")})
    assert r.status_code == 413
