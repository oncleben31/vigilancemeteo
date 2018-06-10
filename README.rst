===============
Vigilance Météo
===============

Vigilance Météo provides a python API to fetch weather alerts in France from http://vigilance.meteofrance.com website.


Class descritpion
=================

ZoneAlerte class allows to fetch active alerts for a french department.

Variables from ZoneAlerte class:

* _departement : The department watched
* _dateMiseAJour : Date and time of the weather forcast update from MétéoFrance
* _listeAlertes : A dictionary with all the alerts. Keys for alert type and value for criticity (by color).

Methods from ZoneAlerte class:

- miseAJourEtat() : update alerts list by feching latest info from MétéoFrance forcast.

Properties from ZoneAlerte class

- syntheseCouleur : return the overall criticity color for the department
- urlPourEnSavoirPlus : return the URL to access more information about department weather alerts from the MétéoFrance website.
- messageDeSynthese : return a string with textual synthesis of the active alerts in department.

Example
========

Use case example::

    >>>import vigilancemeteo

    >>>zone = vigilancemeteo.ZoneAlerte('92')

    >>>zone.syntheseCouleur
    'Vert'

    >>>zone.urlPourEnSavoirPlus
    'http://vigilance.meteofrance.com/Bulletin_sans.html?a=dept75&b=1&c='

    >>>zone.messageDeSynthese
    'Aucune alerte en cours.'
