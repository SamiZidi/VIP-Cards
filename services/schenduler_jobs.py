from extensions import scheduler
from services.competition_service import update_likes, create_monthly_competition, update_competitions, close_competition
from functools import partial
def init_scheduler(app):
    try:
        jobs = [
            ("job_update_likes", partial(update_likes, app), "interval", {"minutes": 15}),
            ("job_create_monthly", partial(create_monthly_competition, app), "interval", {"hours": 24}),
            ("job_update_competitions", partial(update_competitions, app), "interval", {"minutes": 5}),
            ("job_close_competition", partial(close_competition, app), "interval", {"minutes": 60}),
        ]

        for job_id, func, trigger, kwargs in jobs:
            if not scheduler.get_job(job_id):
                scheduler.add_job(func=func, trigger=trigger, **kwargs, id=job_id)

        if not scheduler.running:
            scheduler.start()
            
    except Exception as e:
        app.logger.error(f"Scheduler job addition error: {e}")
