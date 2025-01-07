# JustCats

JustCats est un bot Discord qui vous permet d'obtenir des images de chats à la demande en utilisant l'API CATAAS.

## Prérequis

- Python 3.11
- Un token Discord pour votre bot
- Les dépendances listées dans `requirements.txt`

> Pour créer un bot Discord et obtenir le token, suivez [ce guide](https://discord.com/developers/docs/quick-start/getting-started#step-1-creating-an-app)

## Installation

1. Clonez ce dépôt :

   ```sh
   git clone https://github.com/Plexi09/JustInCats.git
   cd JustInCat
   ```

2. Créez un environnement virtuel et activez-le :

   ```sh
   python3.11 -m venv venv
   source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
   ```

3. Installez les dépendances :

   ```sh
   pip install -r requirements.txt
   ```

4. Créez un fichier [.env](http://_vscodecontentref_/1) en vous basant sur le fichier [.env.example](http://_vscodecontentref_/2) et ajoutez votre token Discord et votre ID:

   ```env
   DISCORD_TOKEN=your_token_here
   OWNER_ID=your_id_here
   ```

## Utilisation

1. Démarrez le bot :

   ```sh
   python bot.py
   ```

2. Invitez le bot sur votre serveur Discord en utilisant le lien d'invitation généré par le portail des développeurs Discord.

## Commandes

- `/ping` : Vérifiez la latence du bot.
- `/info` : Obtenez des informations sur le bot.
- `/howmanycats` : Affiche le nombre d'images de chats disponibles.
- `/randomcat` : Obtenez une image de chat aléatoire.
- `/customcat` : Obtenez une image de chat avec des options avancées (type, largeur, hauteur, filtre, flou, luminosité, saturation, etc.).

## Arrêter le bot

Pour arrêter le bot, envoyez la commande `!shutdown` en tant que propriétaire du bot.

## Utilisation avec Docker

1. Construisez l'image Docker :

   ```sh
   docker build -t justincats-bot .
   ```

2. Démarez le conteneur Docker :

   ```sh
   docker run --env-file .env justincats-bot
   ```

## Contribution

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements que vous souhaitez apporter.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.
