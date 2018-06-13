# Vigilance Météo

Vigilance Météo provides a python API to fetch weather alerts in France from [http://vigilance.meteofrance.com](http://vigilance.meteofrance.com) website.


## Class descritpion

ZoneAlerte class allows to fetch active alerts for a french department.

### Public Methods from ZoneAlerte class:

-   miseAJourEtat(): update alerts list by feching latest info from MétéoFrance forcast.

### Public attributes from ZoneAlerte class

-   syntheseCouleur: return the overall criticity color for the department
-   urlPourEnSavoirPlus: return the URL to access more information about department weather alerts from the MétéoFrance website.
-   messageDeSynthese: return a string with textual synthesis of the active alerts in department.
-   dateMiseAJour: return latest bulletin update date & time
-   departement: Get or set the departement number corresponding to the area
    watched.
-   listeAlertes: return the list of active alerts

## Example


    >>>import vigilancemeteo

    >>>zone = vigilancemeteo.ZoneAlerte('92')

    >>>zone.syntheseCouleur
    'Vert'

    >>>zone.urlPourEnSavoirPlus
    'http://vigilance.meteofrance.com/Bulletin_sans.html?a=dept75&b=1&c='

    >>>zone.messageDeSynthese
    'Aucune alerte en cours.'

## Installation
You can install the python package by cloning this repository and launching the command `python setup.py install`

Alternatively, there is a [pyPi package available](https://pypi.org/project/vigilancemeteo/) to be installed using pip:
`pip install vigilancemeteo`

## References
Thank you to Lunarok to show an implementation example [in PHP for Jeedom](https://github.com/lunarok/jeedom_vigilancemeteo). Lot of inspiration for this python implementation.
