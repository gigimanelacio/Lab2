import random
import datetime

sql = []
sql.append("-- Script de inserção de dados gerado automaticamente")
sql.append("-- Limpeza dos dados existentes (com CASCADE para dependências e RESTART IDENTITY para as chaves primárias)")

tabelas = [
    'validacoes', 'transacoes', 'portas', 'pontos_venda', 
    'bilhetes', 'tipos_bilhete', 'clientes', 
    'concertos', 'artistas', 'palcos', 'dias', 'eventos'
]
sql.append(f"TRUNCATE TABLE {', '.join(['public.' + t for t in tabelas])} RESTART IDENTITY CASCADE;\n")

# 1. Eventos
sql.append("INSERT INTO public.eventos (nome, descricao) VALUES ('Wireless Festival 2026', 'Maior festival de música no Reino Unido');")

# 2. Dias
dias = ['2026-07-10', '2026-07-11', '2026-07-12']
for i, d in enumerate(dias):
    sql.append(f"INSERT INTO public.dias (id_evento, data_dia) VALUES (1, '{d}');")

# 3. Palcos
palcos = [('Main Stage', 50000), ('Second Stage', 20000), ('Dance Stage', 15000)]
for p in palcos:
    sql.append(f"INSERT INTO public.palcos (nome, capacidade) VALUES ('{p[0]}', {p[1]});")

# 4. Artistas
artistas = [
    ('Drake', 'Hip Hop'), ('Kendrick Lamar', 'Hip Hop'), ('J Cole', 'Hip Hop'),
    ('Travis Scott', 'Hip Hop'), ('A$AP Rocky', 'Hip Hop'), ('Tyler The Creator', 'Hip Hop'),
    ('Nicki Minaj', 'Hip Hop / Pop'), ('Cardi B', 'Hip Hop'), ('Eminem', 'Hip Hop'),
    ('Snoop Dogg', 'Hip Hop'), ('The Weeknd', 'R&B'), ('Frank Ocean', 'R&B'),
    ('SZA', 'R&B'), ('Doja Cat', 'Pop / R&B'), ('Post Malone', 'Hip Hop / Pop'),
    ('Central Cee', 'UK Drill'), ('Dave', 'UK Rap'), ('Stormzy', 'Grime'),
    ('Skepta', 'Grime'), ('Burna Boy', 'Afrobeats')
]
for i, a in enumerate(artistas):
    sql.append(f"INSERT INTO public.artistas (nome, genero) VALUES ('{a[0]}', '{a[1]}');")

# 5. Concertos
for i in range(1, 21):
    id_dia = random.randint(1, 3)
    id_palco = random.randint(1, 3)
    hora = f"{random.randint(14, 23):02d}:00:00"
    
    # enum estado_concerto: Confirmado, A decorrer, Terminado, Cancelado (usar Confirmado ou Cancelado para ter cancelamento realista)
    estado = random.choices(['Confirmado', 'Cancelado'], weights=[90, 10])[0]
    sql.append(f"INSERT INTO public.concertos (id_dia, id_artista, id_palco, hora_inicio, estado) VALUES ({id_dia}, {i}, {id_palco}, '{hora}', '{estado}');")

# 6. Tipos Bilhete
tipos_bilhete = [('Passe Geral VIP', 250.00), ('Passe Geral', 150.00), ('Bilhete Diario', 65.00)]
for t in tipos_bilhete:
    sql.append(f"INSERT INTO public.tipos_bilhete (id_evento, nome, preco) VALUES (1, '{t[0]}', {t[1]});")

# 7. Pontos Venda
tipos_pv = ['Bar', 'Comida', 'Merchandising', 'Carregamento']
for i in range(1, 11):
    tipo = random.choice(tipos_pv)
    sql.append(f"INSERT INTO public.pontos_venda (nome, tipo) VALUES ('{tipo} {i}', '{tipo}');")

# 8. Portas
for i in range(1, 6):
    tipo_acesso = 'Geral' if i <= 4 else 'VIP'
    sql.append(f"INSERT INTO public.portas (nome_porta, tipo_acesso) VALUES ('Porta {i}', '{tipo_acesso}');")

# 9. Clientes e 10. Bilhetes
nomes = ['Joao', 'Maria', 'Pedro', 'Ana', 'Rui', 'Marta', 'Nuno', 'Sara', 'Ricardo', 'Tiago', 'Rita', 'Joana', 'Luis', 'Sofia']
apelidos = ['Silva', 'Santos', 'Ferreira', 'Pereira', 'Costa', 'Martins', 'Oliveira', 'Fernandes', 'Rodrigues', 'Gomes']

for i in range(1, 251):
    nome = f"{random.choice(nomes)} {random.choice(apelidos)}"
    email = f"cliente{i}@example.com"
    nif = f"2{random.randint(0, 99999999):08d}"
    sql.append(f"INSERT INTO public.clientes (nome, email, nif) VALUES ('{nome}', '{email}', '{nif}');")
    
    id_tipo_bilhete = random.choices([1, 2, 3], weights=[10, 40, 50])[0]
    rfid = f"RFID{i:05d}{random.randint(1000,9999)}"
    
    # enum estado_bilhete: Ativo, Cancelado, Utilizado, Reembolsado
    estado = random.choices(['Ativo', 'Cancelado', 'Utilizado', 'Reembolsado'], weights=[20, 5, 70, 5])[0]
    saldo = round(random.uniform(0.0, 150.0), 2)
    sql.append(f"INSERT INTO public.bilhetes (id_cliente, id_tipo_bilhete, rfid, estado, saldo_cashless) VALUES ({i}, {id_tipo_bilhete}, '{rfid}', '{estado}', {saldo});")

# 11. Transacoes
for i in range(1, 501):
    id_bilhete = random.randint(1, 250)
    id_ponto_venda = random.randint(1, 10)
    valor = round(random.uniform(2.5, 45.0), 2)
    dia = random.choice(dias)
    hora = f"{random.randint(14, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
    dt = f"{dia} {hora}+01"
    sql.append(f"INSERT INTO public.transacoes (id_bilhete, id_ponto_venda, valor, data_hora) VALUES ({id_bilhete}, {id_ponto_venda}, {valor}, '{dt}');")

# 12. Validacoes
for i in range(1, 501):
    id_bilhete = random.randint(1, 250)
    id_porta = random.randint(1, 5)
    
    # enum direcao_movimento: Entrada, Saída
    direcao = random.choice(['Entrada', 'Saída'])
    dia = random.choice(dias)
    hora = f"{random.randint(13, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
    dt = f"{dia} {hora}+01"
    sql.append(f"INSERT INTO public.validacoes (id_bilhete, id_porta, horario, direcao) VALUES ({id_bilhete}, {id_porta}, '{dt}', '{direcao}');")

# Gravar para o ficheiro
file_path = 'insercoes.sql'
with open(file_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql))

print(f"Script SQL gerado com sucesso: {file_path}")
