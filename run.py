from multiprocessing import Pool, Process
from tkinter import filedialog
import tkinter as tk
import subprocess
import threading
import time
import sys
import os

from core.exceptions import *
from core.constants import *
from core.utils import *
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
            
            filename = f"| {filename}.{extension}"

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
        self.verify_files_integrity()
        self.init_config_parameters()
        self.init_extraction_parameters()


    def init_core_parameters(self):
        self.version = "LightEXtractor.DemoVersion"
        self.running = True


    def init_config_parameters(self):
        self.passwords, self.passwords_len = load_file(PASSWORDS_PATH)
        self.blacklist, self.blacklist_len = load_file(BLACKLIST_PATH)
        self.extraction_foldernames, self.extraction_filenames = self.load_extraction_parameters()


    def init_extraction_parameters(self):
        self.logs_path = self.select_logs()
        self.zip_extraction_patterns = []
        self.zip_extraction_patterns.extend(generate_first_patterns(self.extraction_foldernames))
        self.zip_extraction_patterns.extend(generate_first_patterns(self.extraction_filenames))
        self.zip_extraction_patterns.extend(generate_7zip_extraction_folder_patterns(self.extraction_foldernames))
        self.zip_extraction_patterns.extend(generate_7zip_extraction_file_patterns(self.extraction_filenames))


    def verify_files_integrity(self):
        os.makedirs(CACHE_PATH, exist_ok=True)
        os.makedirs(EXTRACTED_PATH, exist_ok=True)
        integrity = True

        if not os.path.exists(PASSWORDS_PATH):
            with open(PASSWORDS_PATH, 'w', encoding='latin1') as passwords_file:
                for senha_exemplo in range(1, 6):
                    passwords_file.write(f"| Senha exemplo {senha_exemplo}\n")
            print(COLORS['GREEN'] + f"| Arquivo {PASSWORDS_PATH} criado com sucesso")
            integrity = False
        
        if not os.path.exists(BLACKLIST_PATH):
            with open(BLACKLIST_PATH, 'w', encoding='latin1') as blacklist_file:
                for blacklist_exemplo in range(1, 6):
                    blacklist_file.write(f"| Blacklist exemplo {blacklist_exemplo}\n")
            print(COLORS['GREEN'] + f"| Arquivo {BLACKLIST_PATH} criado com sucesso")
            integrity = False

        if not os.path.exists(TARGETS_PATH):
            targets_default_content = '''extraction_foldernames="Fotos", "fotos", "Documentos", "documentos"
extraction_filenames="*.zip", "*.rar", "*.7z"

#######################################################################################################################################
# SÓ É NECESSÁRIO DEFINIR PASTAS QUANDO FOR USAR ALGUM FORMATO DIFERENTE DO .RAR, O .RAR PROCURA O ARQUIVO INDEPENDENTE DO NOME DA PASTA
# extraction_foldernames são as pastas que o LightEXtractor vai extrair junto com todo o conteúdo dentro dela, recomendo
# colocar em maiúsculo e em minúsculo porque não foi testado se existe algum problema com capitalização.
# Exemplo de extraction foldernames:
# example_extraction_foldernames="Fotos", "fotos", "Documentos", "documentos", "Downloads", "downloads"
#
# extraction_filenames são os arquivos que o LightEXtractor vai extrair, para extrair tudo, basta deixar "*.*"
# Exemplo de extraction_filenames
# example_extraction_filenames ="*2024*.txt", "*2025*.txt", "*evento*.txt", "*Evento*.txt", "*.zip", "*.rar", "*.7z", "*.pdf"| 
#
# Se precisar refazer esse arquivo, delete o mesmo e inicie o programa que ele irá criar um automaticamente.
#######################################################################################################################################
'''

            with open(TARGETS_PATH, 'w', encoding='latin1') as targets_path:
                targets_path.write(targets_default_content)
                print(COLORS['GREEN'] + f"| Arquivo {TARGETS_PATH} criado com sucesso")
                integrity = False
            
        if not integrity:
            print(COLORS['YELLOW'] + f"| Integridade: {integrity} | Arquivos de configuração faltando.")
            print(COLORS['YELLOW'] + "Fechando o programa...")
            sys.exit()
        
        else:
            print(COLORS['MAGENTA'] + f"| Integridade: {integrity} | Todos os arquivos de configuração estão presentes")
            return integrity


    def load_extraction_parameters(self):
        data, _ = load_file(TARGETS_PATH)
        extraction_foldernames = ''
        extraction_filenames = ''
        error = False

        try:
            for line in data:
                if line.startswith('extraction_foldernames='):
                    extraction_foldernames = eval(f'[{line.replace("extraction_foldernames=", "")}]')
                elif line.startswith('extraction_filenames='):
                    extraction_filenames = eval(f'[{line.replace("extraction_filenames=", "")}]')
        except Exception as load_error:
            print(COLORS['RED'] + f"| Erro ao carregar os padrões de extração, verifique se a formatação está correta | Erro: {load_error}")
            error = True

        if not extraction_filenames or not extraction_foldernames:
            print(COLORS['RED'] + f"| O arquivo de padrões está incompleto.")
            error = True
        
        if error:
            print(COLORS['YELLOW'] + "Fechando o programa...")
            sys.exit()

        return extraction_foldernames, extraction_filenames

    # Abre a tela do windows para selecionar os logs, foram testados .rar, .zip e 7z, para selecionar
    # outros formatos selecione todos os arquivos e dê load, o 7z será utilizado para a extração
    # de outros formatos que não forem .rar
    def select_logs(self):
        root = tk.Tk()
        root.withdraw()

        arquivos_selecionados = filedialog.askopenfilenames(
            title="Selecione arquivos",
            filetypes=(("RAR, ZIP, 7z", "*.rar;*.zip;*.7z"), ("Todos os Arquivos", "*.*"))
        )

        return iter(list(arquivos_selecionados))

    # Usa subprocess para monitorar o início do teste de arquivo, caso apareça o erro de senha,
    # a próxima senha é testada até achar a senha correta.
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
                    print(COLORS['RED'] + f"| | unrar | Falha ao testar senha {password} no arquivo {file_path} | Erro: {error}")
            
            process.terminate()

            if not password_incorrect:
                return password

        return None

    # Usa subprocess para monitorar o início do teste de arquivo, caso apareça o erro de senha,
    # a próxima senha é testada até achar a senha correta.
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
                    print(COLORS['RED'] + f"| | 7z | Falha ao testar senha {password} no arquivo {file_path} | Erro: {error}")
            
            process.terminate()

            if not password_incorrect:
                return password

        return None

    # Utiliza subprocess e o unrar (CLI) para extrair arquivos .rar
    def process_rar(self, log_path, results_path):
        comando = ['unrar', 'x', '-y', "-inul", log_path]

        if not self.test_rar_passwords(log_path, ["a"]):
            password = self.test_rar_passwords(log_path, self.passwords)
    
            if password:
                print(COLORS['GREEN'] + f"| {log_path} | {password} | Senha encontrada")
                comando.append(f'-p{password}')
            else:
                print(COLORS['RED'] + f"| {log_path} | Senha não encontrada")
                return

        comando.extend(self.extraction_filenames)
        comando.append(results_path)
        subprocess.run(comando)

    # Utiliza subprocess e o 7z (CLI) para extrair qualquer arquivo que não seja .rar
    def process_7zip(self, log_path, results_path): 
        comando = ['7z', 'x', '-y', '-bso0', '-bsp0', '-bse0', log_path]

        if not self.test_7zip_passwords(log_path, ["a"]):
            password = self.test_7zip_passwords(log_path, self.passwords)

            if password:
                print(COLORS['GREEN'] + f"| {log_path} | {password} | Senha encontrada")
                comando.extend([f'-p{password}'])
            else:
                print(COLORS['RED'] + f"| {log_path} | Senha não encontrada")
                return
        
        comando.extend(self.zip_extraction_patterns)
        comando.extend(['*.rar', '*/*.rar', '*/*/*.rar', '*/*/*/*.rar', '*/*/*/*/*.rar', '*/*/*/*/*/*.rar', '*/*/*/*/*/*/*.rar', '*.zip', '*/*.zip', '*/*/*.zip', '*/*/*/*.zip', '*/*/*/*/*.zip', '*/*/*/*/*/*.zip', '*/*/*/*/*/*/*.zip', '*.7z', '*/*.7z', '*/*/*.7z', '*/*/*/*.7z', '*/*/*/*/*.7z', '*/*/*/*/*/*.7z', '*/*/*/*/*/*/*.7z', '-o' + results_path])

        subprocess.run(comando)
        return
    

    def process_log(self, log_path, results_path):
        log_comp = log_path.lower()

        for black_listed in self.blacklist:
            if black_listed in log_comp:
                print(COLORS['YELLOW'] + f'{log_path} nome "{black_listed.upper()}" BLACKLISTED')
                return False

        if ".rar" in log_path:
            self.process_rar(log_path, results_path)
        
        elif ".zip" in log_path:
            self.process_7zip(log_path, results_path)
        
        elif ".7z" in log_path:
            self.process_7zip(log_path, results_path)
        
        else:
            if WARN_NOT_TESTED_FORMAT:
                print(COLORS['YELLOW'] + f"| {log_path} formato de arquivo não testado, desative essa mensagem de erro em core/constants.py")
            self.process_7zip(log_path, results_path)
            
        return True

    # Procura arquivos compactados extraídos para extração recursiva,
    # por padrão procura apenas por .rar, .zip e 7z, para adicionar
    # outros formatos para a extração recursiva, adicione em
    # core/constants.py
    def search_more_logs(self, logs_path, log_name):
        logs = []

        for root, dirs, files in os.walk(logs_path):
            for file in files:
                for nested in NESTED_COMPACTED_FILES:
                    if nested not in file:
                        continue

                    logs.append(f"| {os.path.join(root, file)}")
                        
        return logs

    # Inicia a extração dos arquivos, incluindo a extração recursiva e deleta os arquivos
    # compactados que foram extraídos pela extração recursiva
    # (os arquivos compactados originais não são deletados)
    def process_log_instance(self, log_path, recursive=False):
        try:
            start = time.perf_counter()
            log_name = os.path.splitext(os.path.basename(log_path))[0]
            
            if recursive:
                results_path = f"| {os.path.dirname(log_path)}/{log_name}"
            else:
                results_path = f"| {EXTRACTED_PATH}/{log_name}"

            os.makedirs(results_path, exist_ok=True)

            if not recursive:
                print(COLORS['GREEN'] + f"| Começando a extrair {log_path}")

            if not self.process_log(log_path, results_path):
                return

            if not recursive:
                print(COLORS['GREEN'] + f"| {log_path} | Extração finalizada {time.perf_counter()-start:.2f}sec")
            
            logs = self.search_more_logs(results_path, log_name)

            if logs:
                self.initiate_logs_instances(logs)

            if recursive:
                try:os.remove(log_path)
                except:pass
        
        except Exception as error:
            print(COLORS['RED'] + f"| Erro ao tentar extrair o arquivo {log_path} | Erro: {error}")

 
    def threaded_instance(self, logs_path):
        for log_path in logs_path:
            self.process_log_instance(log_path, recursive=True)

    # Divide os logs selecionados em batchs e envia pra suas respectivas threads
    # esse formato usando multiprocessing e multithreading juntos foi o método
    # mais ágil para a extração que eu encontrei.
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
        print(COLORS['GREEN'] + f"| LightEXtractorDEMO | finalizado em {end-start:.2f}sec")
        self.running = False
        sys.exit()
    

if __name__ == "__main__":
    LightEXtractor = LightEXtractorDEMO()
    LightEXtractor.main()