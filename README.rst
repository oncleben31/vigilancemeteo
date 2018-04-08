===============
Vigilance Météo
===============

Vigilance Météo fourni une API python pour récupérer les alertes météo du site http://vigilance.meteofrance.com

**Note for English-speakers**: as the source provide information for France, I assume users are French-speakers. So documentation, code and comments are in French.

Description de la classe
========================

La classe ZoneAlerte permet de récupérer les alertes en cours dans un
département en particulier.

La classe ZoneAlerte est définit par les attributs:

* _departement : le département surveillé
* _dateMiseAJour : la date et l'heure de mise à jour de la prévision par MétéoFrance
* _listeAlertes : le dictionnaire comportant les alertes. L'indice du dictionnaire correspond au type de l'alerte et la valeur associée à la gravité de l'alerte eeprésenté par une couleur.

La méthode suivante est disponibles:

- miseAJourEtat() : pour mettre à jour la liste des alertes en prenant la dernière prévision de MétéoFrance

Les propriétés suivantes sont disponibles:

- syntheseCouleur : retourne la couleur correspondant à la criticité maximum du département
- urlPourEnSavoirPlus : retourne l'URL correspondant à la page web              détaillant les alertes en cours dans le département
- messageDeSynthese : retourne une chaine de caractère faisant la synthèse des alertes en cours dans le département.

Exemple
========

Exemple de cas d'usage::

    >>>import vigilancemeteo

    >>>zone = vigilancemeteo.ZoneAlerte('92')

    >>>zone.syntheseCouleur
    'Vert'

    >>>zone.urlPourEnSavoirPlus
    'http://vigilance.meteofrance.com/Bulletin_sans.html?a=dept75&b=1&c='

    >>>zone.messageDeSynthese
    'Aucune alerte en cours.'
