import telebot
import csv
import datetime
import os
from collections import Counter
from lojinha import CATALOGO, ARQUIVO_VENDAS

# Token fornecido pelo usuário
TOKEN = '8962776872:AAG6SkwPzD_ItRBsWqfLoAB9qxKaoH0uGzo'
bot = telebot.TeleBot(TOKEN)

# Armazena o carrinho temporário de cada usuário: {chat_id: ['1', '2', '1']}
carrinhos = {}

def get_menu_text():
    texto = "🛍 *CATÁLOGO AD1*\n\n"
    for key, item in CATALOGO.items():
        texto += f"/{key} - {item['nome']} (Dinheiro: R${item['dinheiro']:.2f} | Cartão: R${item['cartao']:.2f})\n"
    texto += "\n*Comandos:*\n"
    texto += "/carrinho - Ver itens atuais\n"
    texto += "/finalizar 1 - Pagar c/ Dinheiro/PIX\n"
    texto += "/finalizar 2 - Pagar c/ Cartão\n"
    texto += "/cancelar - Esvaziar carrinho\n"
    texto += "/estornar - Apagar a última venda salva\n"
    return texto

@bot.message_handler(commands=['start', 'menu', 'ajuda'])
def send_welcome(message):
    bot.reply_to(message, get_menu_text(), parse_mode='Markdown')

# Permite adicionar um item apenas clicando no comando numérico, ex: /1
@bot.message_handler(func=lambda message: message.text and message.text.startswith('/') and message.text[1:] in CATALOGO)
def add_item_by_number(message):
    chat_id = message.chat.id
    item_id = message.text[1:]
    
    if chat_id not in carrinhos:
        carrinhos[chat_id] = []
        
    carrinhos[chat_id].append(item_id)
    nome = CATALOGO[item_id]['nome']
    
    bot.reply_to(message, f"✅ *{nome}* adicionado ao carrinho!\n\nUse /carrinho para ver ou /finalizar para fechar a compra.", parse_mode='Markdown')

@bot.message_handler(commands=['add'])
def add_item_by_command(message):
    chat_id = message.chat.id
    partes = message.text.split()
    if len(partes) < 2:
        bot.reply_to(message, "Uso incorreto. Exemplo: /add 1")
        return
        
    item_id = partes[1]
    if item_id not in CATALOGO:
        bot.reply_to(message, "Item inválido! Digite /menu para ver os itens.")
        return
        
    if chat_id not in carrinhos:
        carrinhos[chat_id] = []
        
    carrinhos[chat_id].append(item_id)
    nome = CATALOGO[item_id]['nome']
    bot.reply_to(message, f"✅ *{nome}* adicionado ao carrinho!\n\nUse /carrinho para ver ou /finalizar para fechar a compra.", parse_mode='Markdown')

@bot.message_handler(commands=['carrinho'])
def ver_carrinho(message):
    chat_id = message.chat.id
    carrinho = carrinhos.get(chat_id, [])
    
    if not carrinho:
        bot.reply_to(message, "Seu carrinho está vazio. Digite /menu para ver os itens.")
        return
        
    contagem = Counter(carrinho)
    texto = "🛒 *SEU CARRINHO:*\n\n"
    
    total_dinheiro = 0
    total_cartao = 0
    
    for item_key, qtd in contagem.items():
        item = CATALOGO[item_key]
        texto += f"- {qtd}x {item['nome']}\n"
        total_dinheiro += item['dinheiro'] * qtd
        total_cartao += item['cartao'] * qtd
        
    texto += f"\n💰 *Total (Dinheiro/PIX):* R$ {total_dinheiro:.2f}"
    texto += f"\n💳 *Total (Cartão):* R$ {total_cartao:.2f}\n"
    texto += "\nPara finalizar: /finalizar 1 (Dinheiro) ou /finalizar 2 (Cartão)\nPara cancelar: /cancelar"
    
    bot.reply_to(message, texto, parse_mode='Markdown')

@bot.message_handler(commands=['cancelar'])
def cancelar_compra(message):
    chat_id = message.chat.id
    if chat_id in carrinhos:
        carrinhos[chat_id] = []
        bot.reply_to(message, "🛑 Carrinho esvaziado!")
    else:
        bot.reply_to(message, "Seu carrinho já estava vazio.")

@bot.message_handler(commands=['finalizar'])
def finalizar_compra(message):
    chat_id = message.chat.id
    carrinho = carrinhos.get(chat_id, [])
    
    if not carrinho:
        bot.reply_to(message, "Seu carrinho está vazio! Adicione itens primeiro.")
        return
        
    partes = message.text.split()
    if len(partes) < 2 or partes[1] not in ["1", "2"]:
        bot.reply_to(message, "❌ *Forma de pagamento não informada ou inválida!*\nUse:\n/finalizar 1 (para Dinheiro/PIX)\n/finalizar 2 (para Cartão)", parse_mode='Markdown')
        return
        
    opcao_pagamento = partes[1]
    forma_pagamento = "Dinheiro/PIX" if opcao_pagamento == "1" else "Cartão"
    chave_preco = "dinheiro" if opcao_pagamento == "1" else "cartao"
    
    valor_total = 0.0
    nomes_itens = []
    contagem = Counter(carrinho)
    
    for item_key, qtd in contagem.items():
        item = CATALOGO[item_key]
        valor_total += item[chave_preco] * qtd
        nomes_itens.append(f"{qtd}x {item['nome']}")
        
    itens_str = ", ".join(nomes_itens)
    horario = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Criar arquivo se não existir
    if not os.path.exists(ARQUIVO_VENDAS):
        with open(ARQUIVO_VENDAS, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Data/Hora", "Itens", "Forma de Pagamento", "Valor Total (R$)"])
            
    with open(ARQUIVO_VENDAS, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([horario, itens_str, forma_pagamento, f"{valor_total:.2f}"])
        
    # Limpa o carrinho
    carrinhos[chat_id] = []
    
    recibo = "✅ *VENDA REGISTRADA COM SUCESSO!*\n\n"
    recibo += f"🕒 *Data:* {horario}\n"
    recibo += f"🛍 *Itens:* {itens_str}\n"
    recibo += f"💳 *Pagamento:* {forma_pagamento}\n"
    recibo += f"💰 *Total:* R$ {valor_total:.2f}\n"
    
    bot.reply_to(message, recibo, parse_mode='Markdown')

@bot.message_handler(commands=['estornar'])
def estornar_ultima_venda(message):
    if not os.path.exists(ARQUIVO_VENDAS):
        bot.reply_to(message, "Ainda não há vendas registradas.")
        return
        
    try:
        with open(ARQUIVO_VENDAS, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            linhas = list(reader)
            
        if len(linhas) <= 1:
            bot.reply_to(message, "Ainda não há vendas registradas (apenas cabeçalho).")
            return
            
        ultima_venda = linhas[-1]
        
        # Reescreve o arquivo sem a última linha
        with open(ARQUIVO_VENDAS, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(linhas[:-1])
            
        recibo_cancelamento = "🔄 *ÚLTIMA VENDA CANCELADA (ESTORNO)*\n\n"
        recibo_cancelamento += f"🕒 *Data:* {ultima_venda[0]}\n"
        recibo_cancelamento += f"🛍 *Itens:* {ultima_venda[1]}\n"
        recibo_cancelamento += f"💳 *Pagamento:* {ultima_venda[2]}\n"
        recibo_cancelamento += f"💰 *Total:* R$ {ultima_venda[3]}\n"
        
        bot.reply_to(message, recibo_cancelamento, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro ao tentar estornar: {e}")

if __name__ == "__main__":
    print("Iniciando o bot... (Aperte Ctrl+C para sair)")
    bot.infinity_polling()
