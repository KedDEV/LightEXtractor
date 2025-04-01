from datetime import datetime
import random
import pytz
import os

from .constants import *
from .exceptions import FileManagerError


# Retorna a data em formato brasileiro 
def get_formatted_date():
    return str(datetime.now(pytz.timezone("America/Sao_Paulo")).strftime('%d.%m.%Y %H.%M.%S'))

# Carrega um arquivo removendo duplicatas e contando quantos elementos ela possuí em uma iteração
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

# Cria um arquivo caso ele não exista
def ensure_file_exists(file_path, default_content=""):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, "a") as f:
            f.write(default_content)
        print(COLORS['YELLOW'] + f"Arquivo criado: {file_path}")
