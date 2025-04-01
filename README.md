# LightEXtractor DEMO 🚀

**Atenção:** Esta é apenas uma versão DEMO para demonstração de conceitos. O código não inclui o processamento de dados pós-extração e não receberá suporte ou atualizações.

## 📌 Visão Geral
Ferramenta de extração de arquivos compactados (.rar, .zip, .7z) com suporte para:
- Extração seletiva baseada em padrões
- Teste automático de senhas
- Blacklist de arquivos indesejados
- Extração recursiva

# Como Adicionar UnRAR e 7-Zip ao PATH do Windows

Para que o LightEXtractorDEMO funcione corretamente, você precisa adicionar os executáveis do UnRAR e 7-Zip ao PATH do seu sistema. Siga estes passos:

## 📥 1. Baixe e instale os programas
- [UnRAR para Windows](https://www.rarlab.com/rar/unrarw64.exe)
- [7-Zip](https://www.7-zip.org/download.html)

## 🛠️ 2. Encontre o local de instalação
Após instalar, localize onde os programas foram instalados (normalmente):
- UnRAR: `C:\Program Files (x86)\UnRAR\` ou `C:\Program Files\UnRAR\`
- 7-Zip: `C:\Program Files\7-Zip\`

## ⚙️ 3. Adicionar ao PATH

### Método 1: Pelo Painel de Controle
1. Pressione `Windows + R`, digite `sysdm.cpl` e pressione Enter
2. Vá para a aba "Avançado" → "Variáveis de Ambiente"
3. Na seção "Variáveis do sistema", selecione "Path" → "Editar"
4. Clique em "Novo" e adicione os caminhos:
   - `C:\Program Files\7-Zip\`
   - `C:\Program Files (x86)\UnRAR\` (ou o caminho onde o UnRAR foi instalado)
5. Clique em "OK" em todas as janelas

### Método 2: Pelo PowerShell (como administrador)
```powershell
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) + 
    ";C:\Program Files\7-Zip\;C:\Program Files (x86)\UnRAR\",
    [EnvironmentVariableTarget]::Machine
)
```

## ✔️ 4. Verifique a instalação
Abra um novo terminal (CMD/PowerShell) e execute:
```cmd
unrar
7z
```
Se aparecer a ajuda dos programas, a configuração foi bem-sucedida!

💡 Dica: Pode ser necessário reiniciar o terminal ou o computador após essas alterações.

```bash
pip install -r requirements.txt
```

## 🛠️ Configuração
Na primeira execução, o programa criará os arquivos necessários:

1. **targets.txt** - Padrões de extração (pastas/arquivos desejados)
2. **passwords.txt** - Lista de senhas para teste
3. **blacklist.txt** - Arquivos/pastas a serem ignorados

## 🚀 Como Usar
1. Execute o programa
2. Selecione os arquivos compactados
3. Os arquivos serão extraídos para `extracted/NOME_DO_ARQUIVO`

> 💡 Dica: Para formatos não testados (.rar/.zip/.7z), selecione "Todos os arquivos" no explorador

## ⚠️ Disclaimer
- Este é um projeto DEMO sem suporte
- Use por sua conta e risco
- Sinta-se livre para modificar e usar como base para seus projetos

## 📝 Licença
Código aberto para uso e modificação sem restrições

---