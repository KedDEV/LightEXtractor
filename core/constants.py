from colorama import Fore, init
import os

PROCESSES = 6 # Recomendo deixar o número de núcleos do seu processador (cuidado com a memória ram/disco)
SUB_THREADS = 30

CACHE_PATH = 'cache'
EXTRACTED_PATH = 'extracted'
LOGS_FOLDER = f'{CACHE_PATH}/logs'
PASSWORDS_PATH = f'{CACHE_PATH}/passwords.txt'
BLACKLIST_PATH = f'{CACHE_PATH}/blacklist.txt'
TARGETS_PATH = f'{CACHE_PATH}/targets.txt'

os.makedirs(CACHE_PATH, exist_ok=True)
os.makedirs(EXTRACTED_PATH, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)
COLORS = {'RED':Fore.LIGHTRED_EX, 'BLUE':Fore.LIGHTBLUE_EX, 'GREEN':Fore.LIGHTGREEN_EX, 'MAGENTA':Fore.LIGHTMAGENTA_EX, 'YELLOW':Fore.LIGHTYELLOW_EX, 'WHITE':Fore.LIGHTWHITE_EX}