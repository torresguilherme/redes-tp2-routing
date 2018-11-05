import argparse
import socket
import threading
import json
import time

# tabela de roteamento
routing_table = []
distances_table = []
links_table = []

def hop_message(sckt, destination, msg_json):
    next_hop = '0.0.0.0'
    for i in routing_table:
        if i[0] == destination:
            next_hop = i[1]
    if next_hop == '0.0.0.0':
        print('Nao existe rota para o destino: ', destination)
    else:
        sckt.sendto(msg_json.encode(), (next_hop, 55151))

def add(ip, weight, learning_addr):
    links_table_has_router = False
    for it in links_table:
        if it[0] == ip:
            links_table_has_router = True
    if not links_table_has_router:
        links_table.append([ip, weight])

    table_has_router = False
    for i in range(len(distances_table)):
        if distances_table[i][0] == ip:
            table_has_router = True
            if weight <= distances_table[i][1]:
                distances_table[i][1] = weight
                distances_table[i][2] = learning_addr
                distances_table[i][3] = 4
                routing_table[i][1] = ip
    if not table_has_router:
        distances_table.append([ip, weight, learning_addr, 4])
        routing_table.append([ip, ip])

def remove(ip):
    for i in range(len(links_table)):
        if links_table[i][0] == ip:
            del links_table[i]
    for i in range (len(distances_table)):
        if distances_table[i][0] == ip:
            del distances_table[i]
            del routing_table[i]

def trace(ip, sckt, local_addr):
    message = {'type': 'trace',
    'source': local_addr,
    'destination': ip,
    'hops': [local_addr]}
    msg_json = json.dumps(message)
    hop_message(sckt, ip, msg_json)

def send_updates(sckt, local_address, period):
    while True:
        for pair in links_table:
            dest_address = pair[0]
            # pega as distancias p cada roteador conhecido
            distances = {}
            for it in distances_table:
                # remocao de rotas desatualizadas
                it[3] -= 1
                if it[3] == 0:
                    remove(it[0])
                # verifica se a rota nao foi aprendida do destinatario
                if (it[0] != dest_address and it[2] != dest_address) or dest_address == local_address:
                    distances[it[0]] = it[1]
            message = {'type': 'update', 
            'source': local_address,
            'destination': dest_address,
            'distances': distances
            }
            msg_json = json.dumps(message)
            hop_message(sckt, dest_address, msg_json)
        time.sleep(period)

def recv_messages(sckt, local_addr):
    while True:
        encoded_msg, sender = sckt.recvfrom(32768)
        message = json.loads(encoded_msg.decode())
        if message['type'] == 'data':
            if message['destination'] == local_addr:
                print(message['payload'])
            else:
                hop_message(sckt, message['destination'], json.dumps(message))

        elif message['type'] == 'update':
            for key in message['distances'].keys():
                add(key, message['distances'][key], sender[0])

        elif message['type'] == 'trace':
            message['hops'].append(local_addr)
            if message['destination'] == local_addr:
                # manda msg data com as rotas no payload
                data_message = {'type': 'data',
                'source': local_addr,
                'destination': message['source'],
                'payload': message['hops']}
                hop_message(sckt, message['source'], json.dumps(data_message))
            else:
                hop_message(sckt, message['destination'], json.dumps(message))

def command_line(sckt, addr):
    while True:
        try:
            command = input(':> ')
            if command == 'quit':
                return
            else:
                words = command.split(' ')
                if words[0] == 'add':
                    add(words[1], int(words[2]), addr)
                elif words[0] == 'remove':
                    remove(words[1])
                elif words[0] == 'trace':
                    trace(words[1], sckt, addr)
                else:
                    print('Comando desconhecido.')
        except EOFError:
            print('Execucao terminada.')
            return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", help="endereco ao qual o roteador deve se associar", type=str)
    parser.add_argument("period", help="periodo entre envio de mensagens de update", type=float)
    parser.add_argument("startup", nargs="?", help="arquivo com instrucoes que serao executadas no inicio", type=str)
    args = parser.parse_args()

    # bind socket
    sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sckt.bind((args.addr, 55151))

    routing_table.append([args.addr, args.addr])
    distances_table.append([args.addr, 0, '0.0.0.0', 4])
    links_table.append([args.addr, 0])

    # faz os updates
    update_task = threading.Thread(target=send_updates, args=(sckt, args.addr, args.period), daemon=True)
    receive_task = threading.Thread(target=recv_messages, args=(sckt, args.addr), daemon=True)
    update_task.start()
    receive_task.start()
    command_line(sckt, args.addr)

if __name__ == '__main__':  
    main()