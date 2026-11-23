
from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services.sla_monitor import check_sla_breaches


scheduler = BackgroundScheduler()


def run_sla_monitor():
    db = SessionLocal()

    try:
        result = check_sla_breaches(db)
        print("SLA Monitor:", result)

    except Exception as error:
        db.rollback()
        print("SLA Monitor Error:", error)

    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            run_sla_monitor,
            trigger="interval",
            seconds=60,
            id="sla_monitor_job",
            replace_existing=True
        )

        scheduler.start()
        print("SLA monitoring scheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("SLA monitoring scheduler stopped.")
