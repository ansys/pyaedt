import sys

def test_generator(test_obj, test_function):
    def test(self):
        try:
            getattr(test_obj, test_function)()
        except AssertionError:
            print("AssertionError")
            print(sys.exc_info())
            self.assertTrue(False)
        except Exception as e:
            print(sys.exc_info())
            print("Other non-assert Error")
            self.assertTrue(False)
    return test
