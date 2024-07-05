import datetime
import mercadopago
import telebot
import time
import threading
from telebot import types
from senhas import ID_DONO, LINK, TOKEN_MERCADOPAGO, TOKEN_BOT, PRECO_NORMAL, PRECO_PROMOCIONAL

sdk = mercadopago.SDK(TOKEN_MERCADOPAGO)
bot = telebot.TeleBot(TOKEN_BOT)

payment_check_interval = 60  # Intervalo de checagem de pagamento em segundos

def create_payment(value):
    try:
        expire = datetime.datetime.now() + datetime.timedelta(minutes=15)
        expire = expire.strftime("%Y-%m-%dT%H:%M:%S.000-03:00")

        payment_data = {
            "transaction_amount": int(value),
            "payment_method_id": 'pix',
            "installments": 1,
            "description": 'Descrição',
            "date_of_expiration": f"{expire}",
            "payer": {
                "email": 'email@gmail.com'
            }
        }
        result = sdk.payment().create(payment_data)
        return result
    except Exception as e:
        print(f"Erro ao criar pagamento: {e}")
        return None

def get_payment_status(payment_id):
    try:
        result = sdk.payment().get(payment_id)
        return result
    except Exception as e:
        print(f"Erro ao verificar pagamento: {e}")
        return None

def notify_owner(chat_id, user_id, first_name, value, plan):
    notification = f"""
✅ Pagamento aprovado!

🆔 Clientid: {user_id}
👤 User: @{first_name}
📝 Nome: {first_name}
💵 Valor: R${value}
📦 Tipo: assinatura
🔗 Plano: {plan}
"""
    bot.send_message(chat_id, notification)

def check_payment_status(payment_id, chat_id, message_id, original_price, user_id, first_name):
    start_time = time.time()
    while time.time() - start_time < 15 * 60:  # 15 minutos
        status = get_payment_status(payment_id)
        if status and 'response' in status and status['response']['status'] == 'approved':
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("ENTRAR NO GRUPO", url=LINK)
            markup.add(btn)
            bot.send_message(chat_id, "Pagamento aprovado! Bem-vindo ao GRUPO VIP.", reply_markup=markup)
            notify_owner(ID_DONO, user_id, first_name, original_price, "GRUPO VIP")
            return
        time.sleep(payment_check_interval)
    
    # Se o pagamento não foi aprovado em 15 minutos
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(f"GRUPO VIP - {PRECO_PROMOCIONAL}R$", callback_data=f"comprar_grupo_vip_promo:{PRECO_PROMOCIONAL}")
    markup.add(btn)
    bot.send_message(chat_id, f"O pagamento não foi realizado a tempo. Aproveite a promoção! Agora o valor é {PRECO_PROMOCIONAL}R$. Clique no botão abaixo para pagar.", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f"Olá {user_name}!")
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Acessar conteúdo", callback_data="acessar_conteudo")
    markup.add(btn)
    
    bot.send_message(message.chat.id, "Bem-vindo ao nosso bot! Aqui você encontra diversos benefícios exclusivos.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "acessar_conteudo")
def acessar_conteudo(call):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(f"GRUPO VIP - {PRECO_NORMAL}R$", callback_data="resumo_grupo_vip")
    markup.add(btn)
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Veja os planos disponíveis:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("resumo_grupo_vip"))
def resumo_grupo_vip(call):
    plan_name = "GRUPO VIP"
    plan_value = PRECO_NORMAL
    plan_duration = "Vitalício"
    
    resumo = f"Plano: {plan_name}\nValor: R${plan_value}\nDuração: {plan_duration}"
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Confirmar pagamento", callback_data=f"comprar_grupo_vip:{plan_value}")
    markup.add(btn)
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resumo, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("comprar_grupo_vip"))
def comprar_grupo_vip(call):
    def animate_dots(chat_id, message_id):
        for _ in range(3):
            for dots in range(1, 4):
                new_text = "Gerando pagamento" + '.' * dots
                try:
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text)
                    time.sleep(1)
                except telebot.apihelper.ApiTelegramException as e:
                    if e.result_json['description'] == 'Bad Request: message is not modified':
                        continue
                    else:
                        raise e

    message = bot.send_message(chat_id=call.message.chat.id, text="Gerando pagamento")
    threading.Thread(target=animate_dots, args=(call.message.chat.id, message.message_id)).start()
    time.sleep(3)

    original_price = float(call.data.split(":")[1]) if ":" in call.data else PRECO_NORMAL
    payment = create_payment(original_price)
    
    if payment is None:
        bot.send_message(call.message.chat.id, "Ocorreu um erro ao gerar o pagamento. Tente novamente mais tarde.")
        return

    if 'response' in payment and 'point_of_interaction' in payment['response']:
        pix_copia_cola = payment['response']['point_of_interaction']['transaction_data']['qr_code']
        payment_id = payment['response']['id']

        # Envia a instrução de pagamento
        instrucao = ("Para efetuar o pagamento, utilize a opção 'Pagar' -> 'PIX Copia e Cola' no aplicativo do seu banco. "
                     "(Não usar a opção chave aleatória)\n\nCopie o código abaixo:")
        bot.send_message(call.message.chat.id, instrucao)

        # Envia o código PIX
        bot.send_message(call.message.chat.id, f"<code>{pix_copia_cola}</code>", parse_mode='HTML')
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("EFETUEI O PAGAMENTO", callback_data=f"verificar_pagamento:{payment_id}")
        markup.add(btn)
        
        bot.send_message(call.message.chat.id, "Após efetuar o pagamento, clique no botão abaixo ⤵️", reply_markup=markup)
        
        threading.Thread(target=check_payment_status, args=(payment_id, call.message.chat.id, call.message.message_id, original_price, call.from_user.id, call.from_user.first_name)).start()
    else:
        error_message = payment.get('message', 'Erro desconhecido')
        bot.send_message(call.message.chat.id, f"Ocorreu um erro ao gerar o pagamento: {error_message}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("verificar_pagamento:"))
def verificar_pagamento(call):
    payment_id = call.data.split(":")[1]
    status = get_payment_status(payment_id)
    if status is None:
        bot.send_message(call.message.chat.id, "Ocorreu um erro ao verificar o pagamento. Tente novamente mais tarde.")
    elif 'response' in status and status['response']['status'] == 'approved':
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("ENTRAR NO GRUPO", url=LINK)
        markup.add(btn)
        bot.send_message(call.message.chat.id, "Pagamento aprovado! Bem-vindo ao GRUPO VIP.", reply_markup=markup)
        notify_owner(ID_DONO, call.from_user.id, call.from_user.first_name, PRECO_NORMAL, "GRUPO VIP")
    else:
        bot.send_message(call.message.chat.id, "Pagamento ainda não aprovado ou não encontrado. Tente novamente mais tarde.")

if __name__ == "__main__":
    bot.infinity_polling()
