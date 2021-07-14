from functools import wraps

def test_generator(test_obj, test_function):
    def test(self):
        try:
            getattr(test_obj, test_function)()
        except AssertionError:
            self.assertTrue(False)
    return test

class Mark:
    '''Ignore pytest.mark decorators for IronPython testing'''

    def skipif(self, cond, reason=None):
        def inner_function(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not cond:
                    func(*args, **kwargs)
            return wrapper
        return inner_function

    def skip(self, reason=None):
        def inner_function(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                pass
            return wrapper
        return inner_function

mark = Mark()

def fixture(scope='session', autouse=True):
    def inner_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pass
        return wrapper
    return inner_function
