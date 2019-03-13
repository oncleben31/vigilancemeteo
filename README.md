# Vigilance Météo
[![Build Status](https://travis-ci.com/oncleben31/vigilancemeteo.svg?branch=master)](https://travis-ci.com/oncleben31/vigilancemeteo)
[![codecov](https://codecov.io/gh/oncleben31/vigilancemeteo/branch/master/graph/badge.svg)](https://codecov.io/gh/oncleben31/vigilancemeteo)
[![PyPI version](https://badge.fury.io/py/vigilancemeteo.svg)](https://badge.fury.io/py/vigilancemeteo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Vigilance Météo provides a python API to fetch weather alerts in France or Andorre from Météo France ([http://vigilance.meteofrance.com](http://vigilance.meteofrance.com)) website.


## Class descritpion

ZoneAlerte class allows to fetch active weather alerts for a french department or Andorre.

### Public Methods from ZoneAlerte class:

-   `mise_a_jour_etat()`: update alerts list by feching latest info from MétéoFrance forcast.
-   `message_de_synthese(msg_format)`: return a string with textual synthesis
    of the active weather alerts in the department. Depending of the `msg_format` value, the string change: `'text'` (default) or `'html'`.


### Public attributes from ZoneAlerte class

-   `synthese_couleur`: return the overall criticity color for the department.
-   `url_pour_en_savoir_plus`: return the URL to access more information about department weather alerts on the MétéoFrance website.
-   `date_mise_a_jour`: return latest bulletin update date & time.
-   `departement`: get or set the department number corresponding to the area
    watched. Should be a 2 characters string.
-   `liste_alertes`: return the list of active alerts.


## Examples


    >>>import vigilancemeteo

    >>>zone = vigilancemeteo.ZoneAlerte('92')

    >>>zone.synthese_couleur
    'Jaune'

    >>>zone.url_pour_en_savoir_plus
    'http://vigilance.meteofrance.com/Bulletin_sans.html?a=dept75&b=1&c='

    >>>zone.message_de_synthese('text')
    'Alerte météo Jaune en cours :\n - Vent violent: Jaune'

## Installation

You can use official release using the [pyPi package](https://pypi.org/project/vigilancemeteo/). Install it with the command:
`pip install vigilancemeteo`

## Contribute
If you want to contribute to the development:
-   Start by cloning this repository.
-   Setup a virtual environment
-   Install the python package in edition mode: `pip install -e .`
-   Create a branch for your feature
-   Test your change using `tox`
-   Send a PR when ready.

## References
Thank you to Lunarok to show an implementation example [in PHP for Jeedom](https://github.com/lunarok/jeedom_vigilancemeteo). Lot of inspiration for this python implementation.

## License

This software is under the MIT License.
