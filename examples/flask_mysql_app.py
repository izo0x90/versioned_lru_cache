from __future__ import annotations
from flask import Flask, g, request
import functools
from enum import Enum
import time
from typing import Any, Callable

from versioned_lru_cache import versioned_lru_cache_with_ttl


# Mock DB
class DbCols(Enum):
    EXPENSIVE_DATA = "expensive_data"
    UPDATED_AT = "updated_at"
    # Only used to keep and display call stats
    FUNC_CALLS = "function_calls"


class DataBase(dict):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.access_count: dict[str, int] = {}
        super().__init__(*args, **kwargs)
        print("DB initialized ...")

    def get(self, key: str) -> int:  # type: ignore[override]
        counter_name = key + "_accessed"
        self.access_count[counter_name] = (
            self.access_count.setdefault(counter_name, 0) + 1
        )
        print("Getting item ...")

        if key == DbCols.EXPENSIVE_DATA.value:
            print("Some expensive_ish query running ...")

        return super().get(key)  # type: ignore[return-value]


# Setup "Database" and Flask app
db = DataBase({DbCols.EXPENSIVE_DATA.value: 10000, DbCols.UPDATED_AT.value: time.time})
app = Flask(__name__)


def inexpensive_cache_versioning(*args: Any, **kwargs: Any) -> str:
    """
    Some cheap function to invalidate cached data when changed, this can hash/ calc.
    'versions' of our data in a cheap way so that we know when the cached data has
    gone stale.

    The versioned_lru_cache_with_ttl logic will also going to
    cache(loll)/ store the cache version on the flask request object 'g',
    this way if we have to access our cached data multiple times within the same
    request we do not pay the cost of the invalidation function either.

    This should be sensible as we probably would want the dataset to stay consistent
    within request boundaries.
    """
    # In this case we are ignoring the arg and/ or kwargs passed in but in real life
    # we would use those to know what data to calculate a version for/ invalidate
    args
    kwargs
    return str(db.get(DbCols.UPDATED_AT.value))


def call_and_track(d: dict[str, int]) -> Callable:
    """We will use this to count every time we call our func. within request"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            d["func_calls"] += 1
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Setup cached version of our expensive function
@call_and_track(db.access_count)
@versioned_lru_cache_with_ttl(
    proxy_to_session_context_object=g,
    generate_version_func=inexpensive_cache_versioning,
    module_name="big_calc_route",
)
def some_expensive_operation(dataset_id: str) -> int:
    """
    This is our expensive-ish function, lets imagine it has to perform a large DB query
    and do some expensive-ish computation with this data.

    Not something that would be expensive enough to warrant kicking of an async task
    for, but expensive enough where we would like to not pay the cost on subsequent
    requests if no change has taken place.
    """
    our_data = db.get(dataset_id)  # Maybe this is expensive-ish
    processed_data = expensive_ish_processing(our_data)  # Maybe this is expensive-ish
    return processed_data


def expensive_ish_processing(data: int) -> int:
    print("Some expensive-ish processing ...")
    return data


@app.route("/")
def hello_world() -> str:
    # Reset the function call counter so that we keep track within request
    db.access_count["func_calls"] = 0
    if new_time_stamp := request.args.get("update_data"):
        db[DbCols.UPDATED_AT.value] = float(new_time_stamp)

    result = some_expensive_operation(dataset_id=DbCols.EXPENSIVE_DATA.value)
    # Let us imagine these calls are spread across the code base and call stack
    result = some_expensive_operation(dataset_id=DbCols.EXPENSIVE_DATA.value)
    result = some_expensive_operation(dataset_id=DbCols.EXPENSIVE_DATA.value)
    return f'<body style="background-color: #303030; color: #BBB">\
             <div>Request loads and we get the result of our function...</div>\
             <div>The result of work functions is: {result}...</div>\
             <div>✨ Notice that we have called the function a number of times\
             within the request however the work in the function was performed once...\
             </div>\
             <div style="color: violet; margin-bottom: 1em">\
             Access/ run counters: {db.access_count}\
             </div>\
             <a href="/?update_data={time.time()}"\
             style="color: plum;">\
             🔗 Click this to simulate data update...\
             </a>\
             <div style="margin-top: 1em">\
             Once you have clicked the link that simulates an underlying data update\
             the cache is invalidated and the 🐌 work inside the function has executed\
             again and this new value is now cached...\
             </div>\
             <div>\
             If you refresh 🔃 the page you will see that the access couter for the\
             updated_at value ticks up meaning that we had to rerun the function that\
             generates the cache versions/ invalidated but not the "heavy" work func.\
             </div>\
             </body>'
