from extensions import scheduler
from services.competition_service import update_likes, create_monthly_competition, update_competitions, close_competition
from functools import partial

def init_scheduler(app):
    try:
        # ✅ Prevent double-init (Flask debug mode reloads twice)
        if scheduler.running:
            app.logger.info("Scheduler already running, skipping init.")
            return

        jobs = [
            ("job_update_likes", partial(update_likes, app), "interval", {"hours": 24}),
            ("job_create_monthly", partial(create_monthly_competition, app), "interval", {"hours": 24}),
            ("job_update_competitions", partial(update_competitions, app), "interval", {"minutes": 5}),
            ("job_close_competition", partial(close_competition, app), "interval", {"minutes": 60}),
        ]

        for job_id, func, trigger, kwargs in jobs:
            # ✅ Remove existing job before re-adding to avoid duplicates
            existing = scheduler.get_job(job_id)
            if existing:
                scheduler.remove_job(job_id)
            scheduler.add_job(
                func=func,
                trigger=trigger,
                **kwargs,
                id=job_id,
                replace_existing=True,       # ✅ Safety net
                misfire_grace_time=300        # ✅ Allow 5 min grace before "missed" warning
            )

        scheduler.start()
        app.logger.info("Scheduler started successfully.")

    except Exception as e:
        app.logger.error(f"Scheduler job addition error: {e}")