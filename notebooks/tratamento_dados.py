import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Garante que a pasta data/raw e data/processed existem
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

print("Gerando arquivos CSV simulados...")

np.random.seed(42)
n_customers = 50
n_orders = 120

# Criando customers.csv
customer_ids = [f'cust_{i:03d}' for i in range(1, n_customers + 1)]
states = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA']
df_customers = pd.DataFrame({
    'customer_id': customer_ids,
    'customer_unique_id': [f'unique_{i:03d}' for i in range(1, n_customers + 1)],
    'customer_state': np.random.choice(states, n_customers)
})
df_customers.to_csv('data/raw/customers.csv', index=False, encoding='utf-8-sig')

# Criando orders.csv
order_ids = [f'ord_{i:04d}' for i in range(1, n_orders + 1)]
start_date = datetime(2023, 1, 1)
purchase_dates = [start_date + timedelta(days=int(np.random.randint(0, 300)), hours=int(np.random.randint(0, 24))) for _ in range(n_orders)]
delivery_dates = [p_date + timedelta(days=int(np.random.randint(2, 12))) for p_date in purchase_dates]

df_orders = pd.DataFrame({
    'order_id': order_ids,
    'customer_id': np.random.choice(customer_ids, n_orders),
    'order_status': 'delivered',
    'order_purchase_timestamp': purchase_dates,
    'order_delivered_customer_date': delivery_dates
})
df_orders.to_csv('data/raw/orders.csv', index=False, encoding='utf-8-sig')

# Criando order_items.csv
item_rows = []
categories = ['eletrônicos', 'cama_mesa_banho', 'esporte_lazer', 'moveis_decoracao', 'beleza_saude']
for o_id in order_ids:
    n_items = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1])
    for i in range(1, n_items + 1):
        item_rows.append({
            'order_id': o_id,
            'order_item_id': i,
            'product_id': f'prod_{np.random.randint(1, 20):03d}',
            'price': round(np.random.uniform(50.0, 400.0), 2),
            'freight_value': round(np.random.uniform(10.0, 40.0), 2),
            'product_category_name': np.random.choice(categories)
        })
df_items = pd.DataFrame(item_rows)
df_items.to_csv('data/raw/order_items.csv', index=False, encoding='utf-8-sig')

# Criando order_payments.csv
payment_rows = []
pay_types = ['credit_card', 'boleto', 'voucher', 'debit_card']
for o_id in order_ids:
    payment_rows.append({
        'order_id': o_id,
        'payment_type': np.random.choice(pay_types, p=[0.7, 0.2, 0.05, 0.05]),
        'payment_value': round(np.random.uniform(60.0, 500.0), 2)
    })
df_payments = pd.DataFrame(payment_rows)
df_payments.to_csv('data/raw/order_payments.csv', index=False, encoding='utf-8-sig')

print("Arquivos gerados com sucesso! Iniciando o tratamento...")

# 2. Lendo os arquivos da pasta correta
clientes = pd.read_csv('data/raw/customers.csv')
pedidos = pd.read_csv('data/raw/orders.csv')
itens = pd.read_csv('data/raw/order_items.csv')
pagamentos = pd.read_csv('data/raw/order_payments.csv')

# 3. Tratamento de Datas e Valores Nulos
pedidos['order_purchase_timestamp'] = pd.to_datetime(pedidos['order_purchase_timestamp'])
pedidos['order_delivered_customer_date'] = pd.to_datetime(pedidos['order_delivered_customer_date'])
pedidos = pedidos.dropna(subset=['order_delivered_customer_date'])

# 4. Cruzamento (Merge) das Tabelas
df_full = pd.merge(pedidos, itens, on='order_id', how='inner')
df_full = pd.merge(df_full, clientes, on='customer_id', how='inner')
df_full = pd.merge(df_full, pagamentos, on='order_id', how='inner')

# 5. Criando Novas Métricas
df_full['tempo_entrega_dias'] = (df_full['order_delivered_customer_date'] - df_full['order_purchase_timestamp']).dt.days
df_full['valor_total_item'] = df_full['price'] + df_full['freight_value']

# 6. Selecionando colunas úteis e salvando
colunas_uteis = [
    'order_id', 'customer_unique_id', 'order_purchase_timestamp', 
    'order_delivered_customer_date', 'tempo_entrega_dias', 
    'price', 'freight_value', 'valor_total_item', 
    'payment_type', 'customer_state', 'product_category_name'
]
df_final = df_full[colunas_uteis]
df_final.to_csv('data/processed/base_ecommerce_tratada.csv', index=False, encoding='utf-8-sig')

print("Processo concluído com sucesso! Base tratada salva em 'data/processed/base_ecommerce_tratada.csv'.")