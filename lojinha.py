import datetime
import csv
import os
from collections import Counter

CATALOGO = {
    "1": {"nome": "ECOBAG", "dinheiro": 30.00, "cartao": 35.00},
    "2": {"nome": "PRESILHAS", "dinheiro": 15.00, "cartao": 20.00},
    "3": {"nome": "BLUSAS: SEND ME E I BELONG JESUS", "dinheiro": 65.00, "cartao": 70.00},
    "4": {"nome": "STICKERS (1 unidade)", "dinheiro": 2.00, "cartao": 2.00},
    "5": {"nome": "STICKERS (3 unidades)", "dinheiro": 5.00, "cartao": 5.00},
    "6": {"nome": "BLUSAS: EXIT E AD1", "dinheiro": 45.00, "cartao": 50.00},
    "7": {"nome": "LAÇOS", "dinheiro": 15.00, "cartao": 20.00},
    "8": {"nome": "COMBO: 3 CAMISAS", "dinheiro": 185.00, "cartao": 185.00},
    "9": {"nome": "COMBO: ECOBAG, PRESILHA E 1 CAMISA", "dinheiro": 100.00, "cartao": 100.00},
}

ARQUIVO_VENDAS = "vendas.csv"

def inicializar_arquivo():
    if not os.path.exists(ARQUIVO_VENDAS):
        with open(ARQUIVO_VENDAS, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Data/Hora", "Itens", "Forma de Pagamento", "Valor Total (R$)"])

def mostrar_menu(carrinho):
    print("\n" + "="*30)
    print("--- CATÁLOGO AD1 ---")
    for key, item in CATALOGO.items():
        print(f"[{key}] {item['nome']}")
    print("-" * 30)
    print("[f] FECHAR COMPRA")
    print("[0] Cancelar / Sair")
    
    if carrinho:
        print("\n🛒 CARRINHO ATUAL:")
        contagem = Counter(carrinho)
        for item_key, qtd in contagem.items():
            print(f"- {qtd}x {CATALOGO[item_key]['nome']}")
    print("="*30)
    
def registrar_venda():
    while True:
        carrinho = []
        
        while True:
            mostrar_menu(carrinho)
            opcao = input("\nDigite o número do item (ou 'f' para fechar): ").strip().lower()
            
            if opcao == "0":
                if carrinho:
                    print("Compra cancelada.")
                print("Voltando ao início...")
                carrinho = []
                # Pergunta se quer sair apenas se o carrinho já estava vazio antes de apertar 0
                break 
                
            if opcao == "f":
                if not carrinho:
                    print("O carrinho está vazio!")
                    continue
                break
                
            if opcao not in CATALOGO:
                print("Opção inválida! Tente novamente.")
                continue
                
            carrinho.append(opcao)
            print(f"✅ {CATALOGO[opcao]['nome']} adicionado!")

        # Se carrinho estiver vazio após o loop interno, significa que usuário digitou 0
        if not carrinho:
            sair = input("Deseja realmente sair do programa? (s/n): ").lower()
            if sair == 's':
                print("Encerrando o programa...")
                return
            else:
                continue

        # Fechar a compra
        print("\n" + "="*30)
        print("💳 FINALIZAR COMPRA")
        print("[1] Dinheiro / PIX")
        print("[2] Cartão")
        print("[0] Cancelar compra")
        
        pagamento_opcao = input("Selecione a forma de pagamento: ").strip()
        
        if pagamento_opcao == "0":
            print("Compra cancelada.")
            continue
            
        forma_pagamento = ""
        chave_preco = ""
        
        if pagamento_opcao == "1":
            forma_pagamento = "Dinheiro/PIX"
            chave_preco = "dinheiro"
        elif pagamento_opcao == "2":
            forma_pagamento = "Cartão"
            chave_preco = "cartao"
        else:
            print("Forma de pagamento inválida! Compra cancelada.")
            continue
            
        # Calcular total e montar string de itens
        valor_total = 0.0
        nomes_itens = []
        contagem = Counter(carrinho)
        
        for item_key, qtd in contagem.items():
            item = CATALOGO[item_key]
            valor_total += item[chave_preco] * qtd
            nomes_itens.append(f"{qtd}x {item['nome']}")
            
        itens_str = ", ".join(nomes_itens)
        horario = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        with open(ARQUIVO_VENDAS, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([horario, itens_str, forma_pagamento, f"{valor_total:.2f}"])
            
        print(f"\n✅ VENDA REGISTRADA COM SUCESSO!")
        print(f"[{horario}]")
        print(f"Itens: {itens_str}")
        print(f"Pagamento: {forma_pagamento}")
        print(f"Total: R$ {valor_total:.2f}")
        
        input("\nPressione ENTER para nova venda...")

if __name__ == "__main__":
    inicializar_arquivo()
    registrar_venda()
