import os
from app import create_app, db, scheduler
from app.models import Device

app = create_app()

@app.cli.command("init-db")
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    print("Initialized the database.")

def run_scheduler():
    """Starts the scheduler."""
    from app.monitor import run_ping
    with app.app_context():
        devices = Device.query.all()
        for device in devices:
            scheduler.add_job(
                id=f"ping_{device.id}",
                func=run_ping,
                args=[device.id],
                trigger="interval",
                seconds=10,
                replace_existing=True,
            )
    if not scheduler.running:
        scheduler.start()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    run_scheduler()
    app.run(host="0.0.0.0", port=5001, debug=True)
