import argparse
import socket
import asyncio
import json

# tabela de roteamento
routing_table = []

async def send_updates(sckt, local_address, period):
    while True:
        for pair in routing_table:
            dest_address = pair[0]
            distances = {}
            message = {'type': 'update', 
            'source': local_address,
            'destination': dest_address,
            'distances': distances
            }
        await asyncio.sleep(period)

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
    update_task = asyncio.create_task(send_updates(sckt, args.addr, args.period))

main()