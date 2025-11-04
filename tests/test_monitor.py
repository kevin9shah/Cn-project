import pytest
from app import create_app, db
from app.models import Device, Ping
from app.monitor import run_ping
from unittest.mock import patch
import os

@pytest.fixture
def app():
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app

@patch('app.monitor.ping')
def test_run_ping_up(mock_ping, app):
    mock_ping.return_value = 0.05 # 50ms
    device = Device(name='Test Device', ip_address='127.0.0.1')
    db.session.add(device)
    db.session.commit()

    run_ping(app, device.id)

    ping_entry = Ping.query.first()
    assert ping_entry is not None
    assert ping_entry.status == 'UP'
    assert ping_entry.rtt_ms == 50

@patch('app.monitor.ping')
def test_run_ping_down(mock_ping, app):
    mock_ping.return_value = None
    device = Device(name='Test Device', ip_address='127.0.0.1')
    db.session.add(device)
    db.session.commit()

    run_ping(app, device.id)

    ping_entry = Ping.query.first()
    assert ping_entry is not None
    assert ping_entry.status == 'DOWN'
    assert ping_entry.rtt_ms is None
