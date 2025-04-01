from colorama import Fore, init

PROCESSES = 6 # Recomendo deixar o número de núcleos do seu processador (cuidado com a memória ram/disco)
SUB_THREADS = 30
WARN_NOT_TESTED_FORMAT = True
NESTED_COMPACTED_FILES = ['.rar', '.zip', '.7z']

CACHE_PATH = 'cache'
EXTRACTED_PATH = 'extracted'
PASSWORDS_PATH = f'{CACHE_PATH}/passwords.txt'
BLACKLIST_PATH = f'{CACHE_PATH}/blacklist.txt'
TARGETS_PATH = f'{CACHE_PATH}/targets.txt'

COLORS = {'RED':Fore.LIGHTRED_EX, 'BLUE':Fore.LIGHTBLUE_EX, 'GREEN':Fore.LIGHTGREEN_EX, 'MAGENTA':Fore.LIGHTMAGENTA_EX, 'YELLOW':Fore.LIGHTYELLOW_EX, 'WHITE':Fore.LIGHTWHITE_EX}