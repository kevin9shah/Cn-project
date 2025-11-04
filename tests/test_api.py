import pytest
from app import create_app, db
from app.models import Device
import os

@pytest.fixture
def client():
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['API_KEY'] = 'test-key'
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_get_devices(client):
    res = client.get('/api/devices')
    assert res.status_code == 200

def test_add_device(client):
    res = client.post('/api/devices', json={
        'name': 'Test Device',
        'ip_address': '127.0.0.1'
    }, headers={'X-API-KEY': 'test-key'})
    assert res.status_code == 201
    assert b'Test Device' in res.data

def test_add_device_unauthorized(client):
    res = client.post('/api/devices', json={
        'name': 'Test Device',
        'ip_address': '127.0.0.1'
    })
    assert res.status_code == 401

def test_delete_device(client):
    # First add a device
    client.post('/api/devices', json={
        'name': 'Test Device',
        'ip_address': '127.0.0.1'
    }, headers={'X-API-KEY': 'test-key'})
    
    res = client.delete('/api/devices/1', headers={'X-API-KEY': 'test-key'})
    assert res.status_code == 204

def test_get_status(client):
    client.post('/api/devices', json={'name': 'Test Device', 'ip_address': '127.0.0.1'}, headers={'X-API-KEY': 'test-key'})
    res = client.get('/api/status')
    assert res.status_code == 200
    assert b'Test Device' in res.data
