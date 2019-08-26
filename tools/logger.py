from time import time

class Logger:
    def __init__(self, verbosity):
        self.verbosity = verbosity
        print(f'verbosity == {verbosity}')
        self.logs = []

    def log(self, message, oneline=True, function=None, data=None):
        m_message = f'\nMessage: {message}\n'
        m_function = ''
        if function and self.verbosity > 0:
            m_function = f'\nFunction: {function}\n'

        m_data = ''
        if data and self.verbosity > 1:
            data = data if self.verbosity > 2 else str(data)[:250]
            m_data = f'\nData:\n{data}\n'

        if self.verbosity > 1 or oneline:
            log = f'{m_message}{m_function}{m_data}'
        else:
            log = f'[B]=============================================={m_message}{m_function}{m_data}[E]=============================================='
        self.logs.append(log)
        print(log)

    def write_log(self, name):
        name = name.replace(' ','-').replace(':','_')
        with open(f'./logs/{name}.debug_{time()}.log', 'w+') as f:
            f.write(str(self.logs))
