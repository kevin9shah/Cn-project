from . import create_app, db
from .models import Device, Ping
from ping3 import ping
from datetime import datetime

def run_ping(device_id):
    app = create_app()
    with app.app_context():
        device = Device.query.get(device_id)
        if not device:
            return

        try:
            rtt = ping(device.ip_address, timeout=2)
            if rtt is not None:
                status = "UP"
                rtt_ms = rtt * 1000
            else:
                status = "DOWN"
                rtt_ms = None
        except Exception as e:
            print(f"Error pinging {device.ip_address}: {e}")
            status = "DOWN"
            rtt_ms = None

        new_ping = Ping(
            device_id=device.id,
            status=status,
            rtt_ms=rtt_ms,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_ping)
        db.session.commit()
