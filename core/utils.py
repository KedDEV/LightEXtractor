from exceptions import FileManagerError
from datetime import datetime
from constants import *
import colorlog
import logging
import random
import shutil
import gzip
import os


class UnlimitedCompressedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def doRollover(self):
        """Rotaciona os logs e compacta os antigos automaticamente"""
        if self.stream:
            self.stream.close()
            self.stream = None

        # Renomeia o log antigo
        new_log_index = 1
        while os.path.exists(f"{self.baseFilename}.{new_log_index}.gz"):
            new_log_index += 1
        
        new_log_filename = f"{self.baseFilename}.{new_log_index}"

        # Renomeia o log atual para o novo nome
        self.rotate(self.baseFilename, new_log_filename)

        # Compacta o novo log e remove o original
        with open(new_log_filename, 'rb') as f_in, gzip.open(new_log_filename + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(new_log_filename)  # Remove o log não compactado

        # Reabre um novo log vazio
        self.stream = self._open()


def get_formatted_date():
    return str(datetime.now().strftime('%d.%m.%Y %H.%M.%S'))


def load_file(file_path, shuffle=False):
    data = set()
    data_counter = 0

    try:ensure_file_exists(file_path)
    except:pass

    with open(file_path, 'r', encoding='latin1') as file:
        file_data = file.read().split("\n")
        if shuffle:
            random.shuffle(file_data)

        for line in file_data:
            if not line:
                continue

            data.add(line)
            data_counter += 1

    if not data:
        raise FileManagerError(f'Arquivo vazio - {file_path}')
    return data, data_counter


def ensure_file_exists(file_path, default_content=""):
    """Cria um arquivo caso ele não exista."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, "a") as f:
            f.write(default_content)
        output(COLORS['YELLOW'] + f"Arquivo criado: {file_path}")


def output(color='', base_message='', message=''):
    output_string = ''

    if color:
        output_string += color

    if base_message:
        output_string += str(base_message)
    
    if message:
        output_string += f" {message}"
    
    print(output_string)

 
def setup_logger(logs_folder_name=False, logs_file_path=False, logger_name=False, level=False):
    '''
    logs_folder_name -> Nome da pasta onde será salvo os logs caso não haja "logs_file_path"

    logs_file_path -> Caminho absoluto que irá sobrepor logs_folder_name

    logger_name -> Nome do logger, "DEFAULT" caso não seja especificado
    
    level -> ex: logging.INFO, logging.DEBUG, etc...
    
    '''
    
    if not logs_folder_name:
        logs_folder_name = 'default'

    if not logs_file_path:
        logs_file_path = f'{LOGS_FOLDER}/{logs_folder_name}/logs[{get_formatted_date()}]/logs.log'

    if not logger_name:
        logger_name = 'DEFAULT'

    if not level:
        level = logging.INFO
    os.makedirs(os.path.dirname(logs_file_path), exist_ok=True)  
  
    # Criando um handler para saída no console
    handler = colorlog.StreamHandler()

    # Definindo um formato colorido para os logs
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s| %(asctime)s | %(levelname)s: %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        },
        datefmt='%d/%m/%Y %H:%M:%S'
    )

    # Definindo como vai ser o OUTPUT no arquivo
    handler.setFormatter(formatter)
    file_handler = UnlimitedCompressedRotatingFileHandler(logs_file_path, 'a', encoding='utf-8', maxBytes=10*1024*1024, backupCount=0)
    file_handler.setFormatter(logging.Formatter('| %(asctime)s | %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S'))

    # Criando um logger
    logger = colorlog.getLogger(logger_name)
    logger.addHandler(handler)
    logger.addHandler(file_handler)
    logger.setLevel(level)

    return logger

