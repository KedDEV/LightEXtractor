# LightEXtractor DEMO 🚀

**Atenção:** Esta é apenas uma versão DEMO para demonstração de conceitos. O código não inclui o processamento de dados pós-extração e não receberá suporte ou atualizações.

## 📌 Visão Geral
Ferramenta de extração de arquivos compactados (.rar, .zip, .7z) com suporte para:
- Extração seletiva baseada em padrões
- Teste automático de senhas
- Blacklist de arquivos indesejados
- Extração recursiva

## ⚙️ Pré-requisitos
- Windows (com suporte experimental para outros SOs com modificações)
- [UnRAR](https://www.rarlab.com/rar/unrarw64.exe) instalado e no PATH
- [7-Zip](https://www.7-zip.org/download.html) instalado e no PATH

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