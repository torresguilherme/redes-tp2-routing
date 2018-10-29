import argparse
import socket
from multiprocessing import Process
import json
import time

# tabela de roteamento
routing_table = []
distances_table = []
links_table = []

def add(ip, weight):
    links_table_has_router = False
    for it in links_table:
        if it[0] == ip:
            links_table_has_router = True
    if not links_table_has_router:
        links_table.append([ip, weight])

    if not links_table_has_router:
        table_has_router = False
        for i in range (len(distances_table)):
            if distances_table[i][0] == ip:
                table_has_router = True
                if weight < distances_table[i][1]:
                    distances_table[i][1] = weight
                    routing_table[i][1] = ip
        if not table_has_router:
            distances_table.append([ip, weight])
            routing_table.append([ip, ip])
    print(routing_table)
    print(distances_table)
    print(links_table)

def remove(ip):
    for i in range(len(links_table)):
        if links_table[i][0] == ip:
            del links_table[i]
    for i in range (len(distances_table)):
        if distances_table[i][0] == ip:
            del distances_table[i]
            del routing_table[i]
    print(routing_table)
    print(distances_table)
    print(links_table)

def trace(ip):
    pass

def send_updates(sckt, local_address, period):
    while True:
        for pair in distances_table:
            dest_address = pair[0]
            # pega as distancias p cada roteador conhecido
            distances = {}
            message = {'type': 'update', 
            'source': local_address,
            'destination': dest_address,
            'distances': distances
            }
        time.sleep(period)

def command_line():
    while True:
        try:
            command = input(':> ')
            if command == '':
                return
            else:
                words = command.split(' ')
                if words[0] == 'add':
                    add(words[1], int(words[2]))
                elif words[0] == 'remove':
                    remove(words[1])
                elif words[0] == 'trace':
                    trace(words[1])
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

    # faz os updates
    update_task = Process(target=send_updates, args=(sckt, args.addr, args.period))
    update_task.start()
    command_line()
    update_task.terminate()

if __name__ == '__main__':  
    main()