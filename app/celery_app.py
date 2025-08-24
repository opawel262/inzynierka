from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "app", broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

# Split GPW_TICKERS into 3 parts
gpw_tickers = settings.GPW_TICKERS
split_size = (len(gpw_tickers) + 2) // 3

gpw_tickers_part1 = gpw_tickers[:split_size]
gpw_tickers_part2 = gpw_tickers[split_size : 2 * split_size]
gpw_tickers_part3 = gpw_tickers[2 * split_size :]

celery_app.conf.beat_schedule = {
    "fetch-gpw-part1-every-15-minutes": {
        "task": "app.tasks.fetch_gpw_data_by_tickers",
        "schedule": 900.0,
        "args": [gpw_tickers_part1],
    },
    "fetch-gpw-part2-every-15-minutes": {
        "task": "app.tasks.fetch_gpw_data_by_tickers",
        "schedule": 900.0,
        "args": [gpw_tickers_part2],
    },
    "fetch-gpw-part3-every-15-minutes": {
        "task": "app.tasks.fetch_gpw_data_by_tickers",
        "schedule": 900.0,
        "args": [gpw_tickers_part3],
    },
    "fetch-coingecko-data-every-10-minutes": {
        "task": "app.tasks.fetch_coingecko_data",
        "schedule": 600.0,
    },
    "fetch-binance-data-every-10-minutes": {
        "task": "app.tasks.fetch_binanace_data",
        "schedule": 600.0,
    },
    "fetch-currency-exchange-rates-every-5-minutes": {
        "task": "app.tasks.fetch_currency_exchange_rates",
        "schedule": 300.0,
    },
}
celery_app.conf.timezone = "UTC"
