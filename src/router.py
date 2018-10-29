import argparse
import socket
from multiprocessing import Process
import json
import time

# tabela de roteamento
routing_table = []
distances_table = []

def add(ip, weight):
    pass

def remove(ip):
    pass

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
            command = input(':>')
            if command == '':
                return
            else:
                words = command.split(' ')
                if words[0] == 'add':
                    add(words[1], words[2])
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