from . import create_app, db, socketio
from .models import Device, Ping
from ping3 import ping
from datetime import datetime
import statistics
import socket
from urllib.parse import urlparse

def run_ping(device_id):
    app = create_app()
    with app.app_context():
        device = Device.query.get(device_id)
        if not device:
            return

        # Parse the address to extract the hostname
        address = device.ip_address
        if "://" in address:
            hostname = urlparse(address).hostname
        else:
            hostname = address

        if not hostname:
            print(f"Error: Could not extract hostname from {address}")
            return

        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            print(f"Error: Could not resolve hostname {hostname}")
            return

        rtts = []
        for _ in range(5):
            try:
                rtt = ping(ip_address, timeout=2)
                if rtt is not None:
                    rtts.append(rtt * 1000)
            except Exception as e:
                print(f"Error pinging {ip_address}: {e}")

        if rtts:
            status = "UP"
            rtt_avg = statistics.mean(rtts)
            packet_loss = (5 - len(rtts)) / 5 * 100
            jitter = statistics.stdev(rtts) if len(rtts) > 1 else 0
        else:
            status = "DOWN"
            rtt_avg = None
            packet_loss = 100
            jitter = None

        new_ping = Ping(
            device_id=device.id,
            status=status,
            rtt_ms=rtt_avg,
            jitter=jitter,
            packet_loss=packet_loss,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_ping)
        db.session.commit()

        socketio.emit('new_data', {
            'device_id': device.id,
            'status': status,
            'rtt_ms': rtt_avg,
            'jitter': jitter,
            'packet_loss': packet_loss,
            'timestamp': new_ping.timestamp.isoformat()
        })
