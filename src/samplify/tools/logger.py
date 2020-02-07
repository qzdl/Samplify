from time import time

class Logger:
    def __init__(self, verbosity, log_file):
        self.verbosity = verbosity
        self.log_file = log_file
        self.logs = []
        self._log(f'verbosity == {verbosity}')
        self._log(f'log_file == {log_file}')

    def log(self, message, oneline=True, function=None, data=None):
        m_message = f'Message: {message}'
        m_function = ''
        if function and self.verbosity > 0:
            m_function = f'\nFunction: {function}\n'

        m_data = ''
        if data and self.verbosity > 1:
            data = data if self.verbosity > 2 else str(data)[:250]
            m_data = f'\nData:\n{data}'

        if self.verbosity > 1 or oneline:
            log = f'{m_message}{m_function}{m_data}'
        else:
            log = f'[B]=============================================={m_message}{m_function}{m_data}[E]=============================================='
        self._log(log)

    def _log(self, content):
        print('verbosity ',self.verbosity)
        if self.verbosity >= 0:
            print(content)
        self.logs.append(content)
        with open(self.log_file, 'w+') as f:
            f.write(str(content))
