# Bot de Pagamento e Envio para Telegram

Bot de Telegram que facilita pagamentos via Mercado Pago e envia produtos digitais após confirmação. Gerencia produtos, notifica pagamentos e controla acesso a grupos VIP. Ideal para automação de vendas de conteúdo premium.

## Funcionalidades

- **Integração com Mercado Pago**
- **Envio Automático de Produtos**
- **Gerenciamento de Produtos**
- **Notificações de Pagamento**
- **Controle de Acesso a Grupos VIP**

## Requisitos

- **Python 3.8+**
- Bibliotecas: `datetime`, `mercadopago`, `telebot`, `time`, `threading`
- Conta no Telegram para gerenciar o bot

## Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/lipehsz05/bot-pagamentos-telegram.git
    ```
2. Navegue até o diretório do projeto:
    ```bash
    cd nome-do-repositorio
    ```
3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4. Configure as variáveis de ambiente com as credenciais do bot e informações do Mercado Pago.

## Uso

1. Inicie o bot:
    ```bash
    python main.py
    ```
2. Siga as instruções para cadastrar produtos e configurar opções de pagamento.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.

---

<style>
    h1 {
        color: #2e86c1;
        font-size: 2.5em;
        border-bottom: 2px solid #2e86c1;
        padding-bottom: 0.3em;
    }
    h2 {
        color: #2874a6;
        font-size: 2em;
        border-bottom: 1px solid #2874a6;
        padding-bottom: 0.2em;
    }
    h3 {
        color: #21618c;
        font-size: 1.5em;
    }
    p, li {
        font-size: 1.2em;
        line-height: 1.6;
    }
    code {
        background-color: #f7f9f9;
        padding: 0.2em 0.4em;
        border-radius: 4px;
    }
</style>
