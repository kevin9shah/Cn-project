from flask import Blueprint, jsonify, request, render_template, abort
from . import db, scheduler
from .models import Device, Ping
from .monitor import run_ping
import os
from datetime import datetime, timedelta
import logging

bp = Blueprint('routes', __name__)

# HTML Routes
@bp.route('/')
def index():
    return render_template('index.html')

# API Routes
@bp.route('/api/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([device.to_dict() for device in devices])

@bp.route('/api/devices', methods=['POST'])
def add_device():
    data = request.get_json()
    if not data or not 'name' in data or not 'ip_address' in data:
        abort(400)
    
    existing_device = Device.query.filter_by(ip_address=data['ip_address']).first()
    if existing_device:
        return jsonify({'error': 'Device with this IP address already exists'}), 409
    
    new_device = Device(name=data['name'], ip_address=data['ip_address'], priority=data.get('priority', 'low'))
    db.session.add(new_device)
    db.session.commit()

    # Add job to scheduler
    scheduler.add_job(
        id=f"ping_{new_device.id}",
        func=run_ping,
        args=[new_device.id],
        trigger="interval",
        seconds=10,
        replace_existing=True,
    )

    return jsonify(new_device.to_dict()), 201

@bp.route('/api/devices/<int:id>', methods=['PUT'])
def update_device(id):
    device = Device.query.get_or_404(id)
    data = request.get_json()
    device.name = data.get('name', device.name)
    device.ip_address = data.get('ip_address', device.ip_address)
    device.priority = data.get('priority', device.priority)
    db.session.commit()
    return jsonify(device.to_dict())

@bp.route('/api/devices/<int:id>', methods=['DELETE'])
def delete_device(id):
    device = Device.query.get_or_404(id)
    # Remove job from scheduler
    try:
        scheduler.remove_job(f"ping_{device.id}")
    except Exception:
        pass
    db.session.delete(device)
    db.session.commit()
    return '', 204

@bp.route('/api/devices/<int:id>/history', methods=['GET'])
def get_device_history(id):
    device = Device.query.get_or_404(id)
    pings = Ping.query.filter_by(device_id=id).order_by(Ping.timestamp.desc()).limit(100).all()
    return jsonify([ping.to_dict() for ping in pings])

@bp.route('/api/status', methods=['GET'])
def get_status():
    devices = Device.query.all()
    status_summary = []
    for device in devices:
        last_ping = Ping.query.filter_by(device_id=device.id).order_by(Ping.timestamp.desc()).first()
        status_summary.append({
            'id': device.id,
            'name': device.name,
            'ip_address': device.ip_address,
            'status': last_ping.status if last_ping else 'UNKNOWN',
            'last_checked': last_ping.timestamp.isoformat() if last_ping else None
        })
    return jsonify(status_summary)
