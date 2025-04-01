from core.constants import *
from core.utils import *
from multiprocessing import Pool, Process
from tkinter import filedialog
import tkinter as tk
import subprocess
import threading
import random
import time
import sys
import os
init(autoreset=True)


# Gerado por IA
def dividir_lista(lista, partes):
    # Calcula o tamanho de cada parte
    tamanho = len(lista) // partes
    resto = len(lista) % partes
    
    # Cria as partes
    partes_divididas = []
    inicio = 0
    for i in range(partes):
        fim = inicio + tamanho + (1 if i < resto else 0)
        partes_divididas.append(lista[inicio:fim])
        inicio = fim
    
    return partes_divididas

# Retorna todos os caminhos possíveis de uma pasta para a extração com base no nome
def generate_folder_patterns(max_depth, argument):
    patterns = []

    for depth in range(1, max_depth + 1):
        pattern = '*/' * depth + f'*{argument}*/*'
        patterns.append(pattern)

        for sub_depth in range(1, depth + 1):
            sub_pattern = '*/' * (depth - sub_depth) + f'*{argument}*/*' + '/*' * (sub_depth - 1)
            patterns.append(sub_pattern)

    return patterns

# Retorna todos os caminhos possíveis de um arquivo para a extração com base no nome
def generate_file_patterns(max_depth, argument,):
    patterns = []

    for depth in range(1, max_depth + 1):
        # Para arquivos, o argumento não deve ser seguido por /*.
        pattern = '*/' * depth + f'{argument}'
        patterns.append(pattern)

        for sub_depth in range(1, depth + 1):
            sub_pattern = '*/' * (depth - sub_depth) + f'{argument}'
            patterns.append(sub_pattern)

    return patterns

# Itera sobre a lista de alvos para a extração e cria os possíveis caminhos das pastas
# que aquele arquivo pode estar no arquivo compactado
def generate_7zip_extraction_folder_patterns(filenames):
    results = []
    for filename in filenames:
        if not filename:
            continue
        results.extend(generate_folder_patterns(10, filename))
    
    return results

# Itera sobre a lista de alvos para a extração e cria os possíveis caminhos que aquele
# arquivo pode estar no arquivo compactado
def generate_7zip_extraction_file_patterns(filenames):
    results = []
    for filename in filenames:
        if not filename:
            continue
        results.extend(generate_file_patterns(10, filename))
    
    return results

# Os parâmetros iniciais não podem ser gerados pelas outras funções por conta das
# iterações, então essa função devolve os caminhos que não estão incluídos lá
def generate_first_patterns(filenames):
    results = []
    for filename in filenames:
        if '.' in filename:
            filename, extension = str(filename).split(".")

            if not filename.endswith('*'):
                filename += "*"

            if not filename.startswith('*'):
                filename = "*" + filename
            
            filename = f"{filename}.{extension}"

        else:
            if not filename.endswith('*'):
                filename += "*"

            if not filename.startswith('*'):
                filename = "*" + filename
            
        results.append(filename)

    return results


class LightEXtractorDEMO:
    def __init__(self):
        self.init_core_parameters()
        self.init_extraction_parameters()


    def init_core_parameters(self):
        self.version = "LightEXtractor.DemoVersion"
        self.logger = setup_logger(logs_folder_name=self.version, level=logging.INFO)
        self.running = True


    def init_extraction_parameters(self):
        self.logs_path = self.select_logs()
        self.zip_extraction_patterns = []
        self.zip_extraction_patterns.extend(generate_first_patterns(self.extraction_foldernames))
        self.zip_extraction_patterns.extend(generate_first_patterns(self.extraction_filenames))
        self.zip_extraction_patterns.extend(generate_7zip_extraction_folder_patterns(self.extraction_foldernames))
        self.zip_extraction_patterns.extend(generate_7zip_extraction_file_patterns(self.extraction_filenames))


    def init_config_parameters(self):
        self.passwords, self.passwords_len = load_file(PASSWORDS_PATH)
        self.blacklist, self.blacklist_len = load_file(BLACKLIST_PATH)
        self.extraction_foldernames, self.extraction_filenames = self.load_extraction_parameters()


    def load_extraction_parameters(self):
        extraction_foldernames = ['cookie', 'password', 'Cookie', 'Password']
        extraction_txtnames = ['*Cookie*.txt', '*cookie*.txt', '*Pass*.txt', '*pass*.txt']
        return extraction_foldernames, extraction_txtnames


    def select_logs(self):
        root = tk.Tk()
        root.withdraw()

        arquivos_selecionados = filedialog.askopenfilenames(
            title="Selecione arquivos",
            filetypes=(("RAR, ZIP, 7z", "*.rar;*.zip;*.7z"), ("Todos os Arquivos", "*.*"))
        )

        return iter(list(arquivos_selecionados))


    def test_rar_passwords(self, file_path, passwords_list):
        for password in passwords_list:
            command = ['unrar', 't', '-p' + password, file_path]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            password_incorrect = False

            for line_counter, raw_line in enumerate(iter(process.stdout.readline, b'')):
                try:
                    line = raw_line.decode("latin1").strip().lower()

                    if line_counter >= 20:
                        break

                    if not line:
                        continue

                    if "corrupt" in line or "incorrect password" in line:
                        password_incorrect = True
                        break
                except Exception as error:
                    self.logger.error(f"| unrar | Falha ao testar senha {password} no arquivo {file_path} | Erro: {error}")
            
            process.terminate()

            if not password_incorrect:
                return password

        return None


    def test_7zip_passwords(self, file_path, passwords_list):
        for password in passwords_list:
            command = ['7z', 't', '-y', '-p' + password, file_path]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            password_incorrect = False

            for line_counter, raw_line in enumerate(iter(process.stdout.readline, b'')):
                try:
                    line = raw_line.decode("latin1").strip().lower()

                    if line_counter >= 20:
                        break

                    if not line:
                        continue

                    if "wrong password" in line or "can't open" in line:
                        password_incorrect = True
                        break
                except Exception as error:
                    self.logger.error(f"| 7z | Falha ao testar senha {password} no arquivo {file_path} | Erro: {error}")
            
            process.terminate()

            if not password_incorrect:
                return password

        return None


    def process_rar(self, log_path, results_path, process_id):
        comando = ['unrar', 'x', '-y', "-inul", log_path]

        if not self.test_rar_passwords(log_path, ["a"]):
            password = self.test_rar_passwords(log_path, self.passwords)
    
            if password:
                self.logger.info(f"| {process_id} | {log_path} | {password} | Senha encontrada")
                comando.append(f'-p{password}')
            else:
                self.logger.critical(f"| {process_id} | {log_path} | Senha não encontrada")
                return

        comando.extend(self.extraction_filenames)
        comando.append(results_path)
        subprocess.run(comando)


    def process_7zip(self, log_path, results_path, process_id):
        comando = ['7z', 'x', '-y', '-bso0', '-bsp0', '-bse0', log_path]

        if not self.test_7zip_passwords(log_path, ["a"]):
            password = self.test_7zip_passwords(log_path, self.passwords)

            if password:
                self.logger.info(f"| {process_id} | {log_path} | {password} | Senha encontrada")
                comando.extend([f'-p{password}'])
            else:
                self.logger.critical(f"| {process_id} | {log_path} | Senha não encontrada")
                return
        
        comando.extend(self.zip_extraction_patterns)
        comando.extend(['*.rar', '*/*.rar', '*/*/*.rar', '*/*/*/*.rar', '*/*/*/*/*.rar', '*/*/*/*/*/*.rar', '*/*/*/*/*/*/*.rar', '*.zip', '*/*.zip', '*/*/*.zip', '*/*/*/*.zip', '*/*/*/*/*.zip', '*/*/*/*/*/*.zip', '*/*/*/*/*/*/*.zip', '*.7z', '*/*.7z', '*/*/*.7z', '*/*/*/*.7z', '*/*/*/*/*.7z', '*/*/*/*/*/*.7z', '*/*/*/*/*/*/*.7z', '-o' + results_path])

        subprocess.run(comando)
        return
    

    def process_log(self, log_path, results_path, process_id):
        log_comp = log_path.lower()

        for black_listed in self.name_black_list:
            if black_listed in log_comp:
                self.logger.warning(f'| {process_id} | {log_path} nome "{black_listed.upper()}" BLACKLISTED')
                return False

        if ".rar" in log_path:
            self.process_rar(log_path, results_path, process_id)
        
        elif ".zip" in log_path:
            self.process_7zip(log_path, results_path, process_id)
        
        elif ".7z" in log_path:
            self.process_7zip(log_path, results_path, process_id)
        
        else:
            self.logger.error(f"{log_path} tipo de arquivo não suportado.")
            return False
        
        return True


    def search_more_logs(self, logs_path, log_name):
        logs = []

        for root, dirs, files in os.walk(logs_path):
            for file in files:
                if ".zip" in file or ".rar" in file:
                    logs.append(f"{os.path.join(root, file)}")

        return logs


    def process_log_instance(self, log_path, process_id, recursive=False):
        try:
            start = time.perf_counter()
            log_name = os.path.splitext(os.path.basename(log_path))[0]
            
            if recursive:
                results_path = f"{os.path.dirname(log_path)}/{log_name}"
            else:
                results_path = f"{EXTRACTED_PATH}/{log_name}"

            os.makedirs(results_path, exist_ok=True)

            if not recursive:
                self.logger.info(f"| {process_id} | Começando a extrair {log_path}")

            if not self.process_log(log_path, results_path, process_id):
                return

            if not recursive:
                self.logger.info(f"| {process_id} | {log_path} | Extração finalizada {time.perf_counter()-start:.2f}sec")
            
            logs = self.search_more_logs(results_path, log_name)

            if logs:
                self.initiate_logs_instances(logs)

            if recursive:
                try:os.remove(log_path)
                except:pass
        
        except:
            pass

 
    def threaded_instance(self, logs_path):
        process_id = random.randint(0, 99)

        for log_path in logs_path:
            self.process_log_instance(log_path, process_id, recursive=True)


    def initiate_logs_instances(self, logs_path):
        threads_list = []
        logs_path = dividir_lista(logs_path, SUB_THREADS)

        for log_path in logs_path:
            if log_path:
                thread = threading.Thread(target=self.threaded_instance, args=(log_path,))
                thread.start()
        
        for thread in threads_list:
            thread.join()
        
        return


    def main(self):
        start = time.perf_counter()

        with Pool(processes=PROCESSES) as pool:
            pool.map(self.process_log_instance, self.logs_path)

            pool.close()
            pool.join()
    
        end = time.perf_counter()
        self.logger.info(f"| LightEXtractorDEMO | finalizado em {end-start:.2f}sec")
        self.running = False
        sys.exit()
    

if __name__ == "__main__":
    LightEXtractor = LightEXtractorDEMO()
    LightEXtractor.main()