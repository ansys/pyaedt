from functools import wraps
from unittest import TestCase


class PytestMockup(TestCase):
    def assertRaises(self, excClass, callableObj, *args, **kwargs):
        # try:
        TestCase.assertRaises(self, excClass, callableObj, *args, **kwargs)
        # except:
        #     print("\n    " + repr(sys.exc_info()[1]))

    def assertTrue(self, callableObj, *args, **kwargs):
        # try:
        TestCase.assertTrue(self, callableObj, *args, **kwargs)
        # except:
        #    print("\n    " + repr(sys.exc_info()[1]))


def test_generator(test_obj, test_function):
    def test(self):
        try:
            return getattr(test_obj, test_function)()
        except AssertionError as e:
            return self.assertTrue(False, msg=e)

    return test


class Mark:
    """Ignore pytest.mark decorators for IronPython testing"""

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

    def parametrize(self, arg1=None, arg2=None):
        def inner_function(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                print("pytest.mark.parametrize not implemented yet")
                pass
                # self.assertTrue(False, msg="pytest.mark.parametrize not implemented yet")

            return wrapper

        return inner_function


mark = Mark()


def fixture(scope="session", autouse=True):
    def inner_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pass

        return wrapper

    return inner_function
