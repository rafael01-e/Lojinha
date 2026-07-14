import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import defaultdict
from lojinha import CATALOGO

# Nome do arquivo
ARQUIVO_VENDAS = 'vendas.csv'

def main():
    try:
        # Lê o CSV
        df = pd.read_csv(ARQUIVO_VENDAS)
        
        # Dicionários para contar
        contagem_itens = defaultdict(int)
        valor_arrecadado = defaultdict(float)
        valor_por_pagamento = defaultdict(float)
        
        # Verifica o nome da coluna
        coluna_item = 'Item' if 'Item' in df.columns else 'Itens'
        
        # Mapeamento do nome do catálogo para pegar os preços
        mapa_precos = {item['nome']: item for key, item in CATALOGO.items()}
        
        for index, row in df.dropna(subset=[coluna_item]).iterrows():
            linha = row[coluna_item]
            pagamento = str(row.get('Forma de Pagamento', 'Dinheiro/PIX'))
            
            chave_preco = 'cartao' if 'Cartão' in pagamento else 'dinheiro'
            
            partes = linha.split(', ')
            for parte in partes:
                match = re.match(r'(\d+)x\s+(.*)', parte)
                if match:
                    qtd = int(match.group(1))
                    nome = match.group(2)
                else:
                    qtd = 1
                    nome = parte.strip()
                    
                contagem_itens[nome] += qtd
                
                # Procura no catálogo e adiciona o valor correspondente
                if nome in mapa_precos:
                    preco = mapa_precos[nome][chave_preco]
                    valor_arrecadado[nome] += preco * qtd
                    valor_por_pagamento[pagamento] += preco * qtd
                    
        if not contagem_itens:
            print("Nenhum item vendido encontrado no registro.")
            return
            
        # Cria as séries do pandas
        serie_qtd = pd.Series(contagem_itens).sort_values(ascending=True)
        serie_valor = pd.Series(valor_arrecadado).sort_values(ascending=True)
        serie_pagamento = pd.Series(valor_por_pagamento).sort_values(ascending=True)
        
        # Configuração da figura (3 subplots lado a lado)
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 8))
        
        # Gráfico 1: Quantidade de Itens Vendidos
        serie_qtd.plot(kind='barh', ax=ax1, color='#4C72B0', edgecolor='black')
        ax1.set_title('Quantidade Vendida por Item', fontsize=14, fontweight='bold', pad=15)
        ax1.set_xlabel('Quantidade Total', fontsize=12)
        ax1.set_ylabel('')
        ax1.grid(axis='x', linestyle='--', alpha=0.7)
        for i, v in enumerate(serie_qtd):
            ax1.text(v + 0.1, i, str(v), color='black', va='center', fontweight='bold')
            
        # Gráfico 2: Valor Arrecadado
        serie_valor.plot(kind='barh', ax=ax2, color='#55A868', edgecolor='black')
        ax2.set_title('Valor Arrecadado por Item (R$)', fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel('Valor Total (R$)', fontsize=12)
        ax2.set_ylabel('')
        ax2.grid(axis='x', linestyle='--', alpha=0.7)
        for i, v in enumerate(serie_valor):
            ax2.text(v + 1.0, i, f'R$ {v:.2f}', color='black', va='center', fontweight='bold')
            
        # Gráfico 3: Arrecadação por Forma de Pagamento
        serie_pagamento.plot(kind='bar', ax=ax3, color=['#E6842A', '#8E44AD'], edgecolor='black')
        ax3.set_title('Forma de pagamento(R$)', fontsize=14, fontweight='bold', pad=15)
        ax3.set_xlabel('')
        ax3.set_ylabel('Valor Total (R$)', fontsize=12)
        ax3.grid(axis='y', linestyle='--', alpha=0.7)
        ax3.tick_params(axis='x', rotation=0)
        for i, v in enumerate(serie_pagamento):
            ax3.text(i, v + (serie_pagamento.max() * 0.02), f'R$ {v:.2f}', color='black', ha='center', fontweight='bold')
            
        plt.tight_layout()
        print("Abrindo os gráficos...")
        plt.show()

    except FileNotFoundError:
        print(f"Erro: O arquivo '{ARQUIVO_VENDAS}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao gerar os gráficos: {e}")

if __name__ == "__main__":
    main()
