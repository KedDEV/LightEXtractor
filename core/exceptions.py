import logging

class FileManagerError(Exception):
    def __init__(self, status, logger_name=False):
        super().__init__(status)
        self.status = status
        
        if not logger_name:
            logger_name = 'DEFAULT'

        output = f'FileManagerError | {status}'
        logger = logging.getLogger(logger_name)
        logger.critical(output)