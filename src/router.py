import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", help="endereco ao qual o roteador deve se associar", type=str)
    parser.add_argument("period", help="periodo entre envio de mensagens de update", type=float)
    args = parser.parse_args()

main()