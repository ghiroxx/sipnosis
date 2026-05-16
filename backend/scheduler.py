from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def start_scheduler(hourly_tick_callback):
    scheduler.add_job(
        hourly_tick_callback,
        "interval",
        seconds=30,
        id="hourly_tick",
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()
