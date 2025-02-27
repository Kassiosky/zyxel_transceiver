# Telnet Transceiver Data Collector

## 📌 Descrição
Este projeto permite a coleta de dados de transceptores dos switches Zygxel via **Telnet**, autenticando-se e executando comandos para obter informações sobre status e medições.

## 🚀 Funcionalidades
- ✅ Conexão automática via **Telnet**
- 🔐 Autenticação com credenciais armazenadas em variáveis de ambiente
- ⚡ Execução de comandos remotos e captura de saída
- 📊 Extração e formatação de dados de transceptores
- 📝 Registro de logs e armazenamento de dados **JSON**

## 📋 Requisitos
- 🐍 **Python 3.8+**
- 📦 Bibliotecas:
  - `asyncio`
  - `telnetlib3`
  - `dotenv`
  - `hashlib`
  - `re`
  - `json`
  - `datetime`

## ⚙️ Configuração
1. Clone este repositório:
   ```sh
   git clone https://github.com/seu-usuario/seu-repositorio.git
   ```
2. Instale as dependências necessárias:
   ```sh
   pip install -r requirements.txt
   ```
3. Crie um arquivo **`.env`** dentro da pasta `includes/` com as credenciais:
   ```env
   switch_list=IP_DO_SWITCH
   default_switch_user=SEU_USUARIO
   default_switch_password=SUA_SENHA
   switch_command=COMANDO_A_EXECUTAR
   ```

## ▶️ Uso
Execute o script principal:
```sh
python main.py
```

Ou execute diretamente o método assíncrono:
```sh
python -m asyncio run main()
```

Os resultados serão armazenados no arquivo **`logs/log_transceiver_data.json`**.

## 📂 Estrutura do JSON de Saída
```json
{
    "device_name": "Switch01",
    "date": "2025-02-27 12:00:00",
    "transceiver_data": {
        "TX Power(dBm)": {
            "Current": "-2.1",
            "High Alarm": "2.0",
            "High Warn": "1.5",
            "Low Warn": "-3.0",
            "Low Alarm": "-5.0"
        }
    },
    "status_code": 200
}
```

## 📝 Logs
Os logs são armazenados na pasta **`logs/`**, com detalhes das conexões e erros.

## 🤝 Contribuição
Contribuições são bem-vindas! Para isso:
1. Faça um **fork** do repositório
2. Crie uma branch (`git checkout -b minha-feature`)
3. Faça commit das alterações (`git commit -am 'Adiciona nova feature'`)
4. Envie um push (`git push origin minha-feature`)
5. Abra um **Pull Request**

## 📜 Licença
Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
