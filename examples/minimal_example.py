import random
from typing import Any

from versioned_lru_cache import versioned_lru_cache_with_ttl

g: dict = {}  # Fake global context for testing


def test_gen_version(*args: Any, **kwargs: Any) -> str:
    return str(random.randint(0, 1000000000000))


@versioned_lru_cache_with_ttl(
    proxy_to_session_context_object=g,
    generate_version_func=test_gen_version,
    module_name="test_module_name",
)
def test_function_we_want_to_cache(test: Any = None) -> str:
    # Some very heavy computation or database query here
    print("Doing heavy work! aka. test function body is executing.")
    return 'This is the result of the "heavy" work.'


def main() -> int:
    print(
        "Call one no params",
        test_function_we_want_to_cache(),
        test_function_we_want_to_cache.__name__,
    )
    print(
        "Call two no params",
        test_function_we_want_to_cache(),
        test_function_we_want_to_cache.__name__,
    )
    print(
        "Call three test=1 as params",
        test_function_we_want_to_cache(test=1),
        test_function_we_want_to_cache.__name__,
    )

    return 0


if __name__ == "__main__":
    SystemExit(main())
