from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from fastapi import Request


async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom response for 429 Too Many Requests.
    """
    limit_info = exc.detail.split(" per ")[-1]  # Example format: "10 per 1 minute"

    # Now split it further into the time and unit
    limit_count, time_unit = limit_info.split(" ")

    # Extract reset time from the headers (usually found in the X-RateLimit-Reset header)
    print(exc.headers)

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Przekroczono limit żądan",
            "allowed_requests": int(limit_count),
            "time_window": f"per {time_unit}",
            # "retry_after": reset_in,  # Extracted from headers
        },
    )
