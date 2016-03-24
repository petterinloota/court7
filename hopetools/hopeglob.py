import sys

class Global(object):

    test = False

    def __init__(self, **kwargs):
        set(**kwargs)

    def set(self, **kwargs):
        if 'test' in kwargs:
            Global.test = kwargs['test']

    @staticmethod
    def testing(value=None):

        if (value != None):
            Global.test = value

        if Global.test:
            return True
        return False

    @staticmethod
    def debugOut(text, **kwargs):
        sys.stderr.write(text)
        sys.stderr.write("\n")