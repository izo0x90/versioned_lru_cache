# TODO: Add actual tests
from contextlib import contextmanager
from unittest.mock import Mock
import random

import pytest

from versioned_lru_cache import versioned_lru_cache_with_ttl


@contextmanager
def dummy_session_context():
    class global_session_context_proxy(dict):

        def new_session(self):
           self.clear() 

    try:
        yield global_session_context_proxy() 
    finally:
        pass


def gen_random_version(*args, **kwargs):
    return str(random.randint(0, 1000000000000))


def function_we_want_to_cache(test = None):
    # Some very heavy computation or database query here
    print("Doing heavy work! aka. test function body is executing.")
    return 'This is the result of the "heavy" work.'


def test_hello_world():
    print('Hello world!')
    assert True


def test_version_id_stored_on_context():
    with dummy_session_context() as g:
        random.seed(10)
        wrapped_function_we_want_to_cache = versioned_lru_cache_with_ttl(
            proxy_to_session_context_object=g,
            generate_version_func=gen_random_version,
            module_name="test_module_name",
        )(function_we_want_to_cache)

        wrapped_function_we_want_to_cache()
        
        random.seed(10)
        expected_version_id = gen_random_version()
        
        stored_version_id = g
        for _ in range(3):
            stored_version_id = next(iter(stored_version_id.values()))
        
        print(f'{g = }, {expected_version_id = }, {stored_version_id = }')
        
        assert stored_version_id == expected_version_id
    
    
def test_return_value_is_cached():
    mock_function_we_want_to_cache = Mock()
    mock_function_we_want_to_cache.__name__ = 'test_mock_function'
    with dummy_session_context() as g:
        random.seed(10)
        wrapped_function_we_want_to_cache = versioned_lru_cache_with_ttl(
            proxy_to_session_context_object=g,
            generate_version_func=gen_random_version,
            module_name="test_module_name",
        )(mock_function_we_want_to_cache)

        wrapped_function_we_want_to_cache()
        wrapped_function_we_want_to_cache()
        
        mock_function_we_want_to_cache.assert_called_once()
        

def test_return_value_is_cached_across_sessions():
    mock_function_we_want_to_cache = Mock()
    mock_function_we_want_to_cache.__name__ = 'test_mock_function'

    with dummy_session_context() as g:
        random.seed(10)
        wrapped_function_we_want_to_cache = versioned_lru_cache_with_ttl(
                proxy_to_session_context_object=g,
                generate_version_func=gen_random_version,
                module_name="test_module_name",
                )(mock_function_we_want_to_cache)

        wrapped_function_we_want_to_cache()
        
        g.new_session()
        random.seed(10) # Simulate version no changing across sessions
        wrapped_function_we_want_to_cache()
        
        mock_function_we_want_to_cache.assert_called_once()
        
        
def test_return_value_is_cached_version_changed_across_sessions():
    mock_function_we_want_to_cache = Mock()
    mock_function_we_want_to_cache.__name__ = 'test_mock_function'
    
    with dummy_session_context() as g:
        random.seed(10)
        wrapped_function_we_want_to_cache = versioned_lru_cache_with_ttl(
            proxy_to_session_context_object=g,
            generate_version_func=gen_random_version,
            module_name="test_module_name",
        )(mock_function_we_want_to_cache)

        wrapped_function_we_want_to_cache()
        
        g.new_session()
        wrapped_function_we_want_to_cache()
        
        assert len(mock_function_we_want_to_cache.call_args_list) == 2
        
