import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute_command(cmd):
    """Exécute une commande sur le système et retourne la sortie."""
    cmd = cmd.strip()
    if not cmd:
        return
    # Exécution de la commande
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


class NetCat:
    """Classe qui implémente les fonctionnalités de NetCat: écoute ou connexion vers un hôte distant."""
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # Création d'un socket TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        """Exécute l'action de NetCat (écouter ou se connecter)."""
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        """Envoie des données à l'hôte spécifié et écoute la réponse."""
        # Connexion au serveur spécifié par l'IP et le port
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)  # Affiche la réponse du serveur
                    buffer = input('> ')  # Invite pour l'utilisateur
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('Terminé par l\'utilisateur.')
            self.socket.close()
            sys.exit()

    def listen(self):
        """Écoute les connexions entrantes sur l'adresse IP et le port spécifiés."""
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)  # Attends jusqu'à 5 connexions en attente
        print(f"Écoute sur {self.args.target}:{self.args.port}...")
        while True:
            # Accepte une connexion entrante
            client_socket, _ = self.socket.accept()
            # Lance un thread pour gérer la connexion client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        """Gère une connexion client (exécution de commandes, téléversement de fichiers, etc.)."""
        if self.args.execute:
            # Si une commande est spécifiée, l'exécute et envoie la sortie au client
            output = execute_command(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            # Si un fichier est spécifié pour le téléversement, le reçoit et l'enregistre
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Fichier {self.args.upload} enregistré.'
            client_socket.send(message.encode())
        elif self.args.command:
            # Si une commande shell est demandée, fournit un shell interactif
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'NetCat: #> ')  # Invite pour la commande
                    while b'\n' not in cmd_buffer:
                        cmd_buffer += client_socket.recv(64)
                    response = execute_command(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''  # Réinitialisation du tampon de commande
                except Exception as e:
                    print(f'Server killé: {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    # Configuration de l'analyseur d'arguments pour une utilisation en ligne de commande
    parser = argparse.ArgumentParser(
        description="Outil NetCat pour écouter ou se connecter à un serveur distant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Exemple d\'utilisation:
            netcat.py -t 192.168.1.108 -p 5555 -l -c  # Shell de commande
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mystest.txt  # Téléverser un fichier
            netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd"  # Exécuter une commande
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135  # Écrire un texte sur le serveur
            netcat.py -t 192.168.1.108 -p 5555  # Connexion vers un serveur
        '''))
    
    parser.add_argument('-c', '--command', action='store_true', help='Shell de commande')
    parser.add_argument('-e', '--execute', help='Exécuter la commande spécifiée')
    parser.add_argument('-l', '--listen', action='store_true', help='Mettre le programme en mode écoute')
    parser.add_argument('-p', '--port', type=int, default=5555, help='Port à utiliser')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='IP cible')
    parser.add_argument('-u', '--upload', help='Spécifie le fichier à téléverser')
    args = parser.parse_args()

    # Si le mode écoute n'est pas activé, on lit l'entrée de l'utilisateur
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    # Initialisation de l'objet NetCat et exécution
    netcat = NetCat(args, buffer.encode())
    netcat.run()
