# NetCat Python Tool

Ce script implémente un outil NetCat en Python qui peut être utilisé pour écouter des connexions entrantes sur un serveur, envoyer et recevoir des données, exécuter des commandes à distance, ou téléverser des fichiers.

## Fonctionnalités

- **Écoute d'une connexion distante (mode serveur)**
- **Shell interactif**
- **Exécution de commandes à distance**
- **Téléversement de fichiers**
- **Envoi de données vers un serveur distant (mode client)**

## Installation

-Aucune installation spécifique n'est nécessaire. Vous devez simplement avoir Python installé sur votre machine. 

-git clone https://github/unezeable/netcat
-cd netcat

## Utilisation

### Mode serveur (écoute)

Écoutez sur un port spécifié et gérez les connexions entrantes.

```bash
python netcat.py -t 192.168.1.108 -p 5555 -l -c
```

### Exécuter une commande à distance

Exécutez une commande spécifique et retournez sa sortie à l'hôte distant.

```bash
python netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd"
```

### Téléverser un fichier

Téléversez un fichier depuis un client vers le serveur.

```bash
python netcat.py -t 192.168.1.108 -p 5555 -l -u="test.txt"
```

### Connexion vers un serveur (mode client)

Envoyer des données à un serveur distant.

```bash
echo 'ABC' | python netcat.py -t 192.168.1.108 -p 5555
```

## Arguments

- `-t` ou `--target`: Spécifie l'adresse IP cible.
- `-p` ou `--port`: Spécifie le port à utiliser (par défaut 5555).
- `-l` ou `--listen`: Active le mode écoute sur le serveur.
- `-c` ou `--command`: Lance un shell interactif (serveur).
- `-e` ou `--execute`: Exécute une commande spécifiée à distance.
- `-u` ou `--upload`: Téléverse un fichier sur le serveur.

## Remarques

- Ce script nécessite des privilèges administratifs pour fonctionner correctement dans certains cas (par exemple, pour ouvrir des sockets bruts ou certains ports).
- L'outil peut être utilisé pour des tests de pénétration, alors veillez à ne l'utiliser que sur des réseaux où vous avez l'autorisation de le faire.
- **Inspiration** : Ce script est inspiré du livre *Black Hat Python* de Justin Seitz, qui explique comment utiliser Python pour réaliser des attaques de sécurité, manipuler des protocoles réseau et automatiser des tâches de pénétration.
