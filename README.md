
# Vigilance Météo

[![Build Status](https://travis-ci.com/oncleben31/vigilancemeteo.svg?branch=master)](https://travis-ci.com/oncleben31/vigilancemeteo)
[![codecov](https://codecov.io/gh/oncleben31/vigilancemeteo/branch/master/graph/badge.svg)](https://codecov.io/gh/oncleben31/vigilancemeteo)
[![PyPI version](https://badge.fury.io/py/vigilancemeteo.svg)](https://badge.fury.io/py/vigilancemeteo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Vigilance Météo provides a python API to fetch weather alerts in France or Andorre from Météo France ([http://vigilance.meteofrance.com](http://vigilance.meteofrance.com)) website.

## Classes descritpion

`VigilanceMeteoFranceProxy` class manages the communication with the source website. The
algorithm request a cheksum tiny file to download and update the XML source only when
needed.

`DepartmentWeatherAlert` class allows to fetch all weather alerts for a french department or Andorre. Each `DepartmenWeatherAlert` instance can have its own proxy, but you should use
only one proxy for all `DepartmenWeatherAlert` instances in your program to avoid too much HTTP request on source website.

### Public attributes from `DepartmentWeatherAlert` class

- `department_color`: return the overall criticity color for the department
- `additional_info_URL`: return the URL to access more information about
department weather alerts from the MétéoFrance website
- `bulletin_date`: return the latest bulletin update date & time with timezone
- `department`: get or set the department number corresponding to the area
watched
- `alerts_list`: return the list of all alert types
- `proxy`: return the client (a `VigilanceMeteoFranceProxy` instance) used by the
    object

### Public methods from `DepartmentWeatherAlert` class

- `update_department_status()`: update alerts list by feching latest info from
MétéoFrance forcast.
- `summary_message(format)`: return a string with textual synthesis of the
active alerts in department. According to value of 'format' parameter,
the string return change: 'text' (default) or 'html'

### Public attributes from `VigilanceMeteoFranceProxy` class

- `xml_tree` = XML representation of the weather alert bulletin
- `bulletin_date` = Date of the bulletin (with timezone)
- `checksum` = Checksum of the weather alert bulletin
- `status` = current status of the proxy (possible value in `constant.py`)

### Public Methods from `VigilanceMeteoFranceProxy`class

- `update_date()`: Check if new information are available and download them if any.
- `get_alert_list(department)`: of a given department return the list of the alerts.

## Examples

    >>>import vigilancemeteo

    >>>zone = vigilancemeteo.DepartmentWeatherAlert('92')

    >>>zone.department_color
    'Jaune'

    >>>zone.additional_info_URL
    'http://vigilance.meteofrance.com/Bulletin_sans.html?a=dept75&b=1&c='

    >>>zone.summary_message('text')
    'Alerte météo Jaune en cours :\n - Vent violent: Jaune'

## Installation

You can use the official release using the [pyPi package](https://pypi.org/project/vigilancemeteo/). Install it with the command:
`pip install vigilancemeteo`

## Contribute

If you want to contribute to the development:

- Start by cloning this repository.
- Setup a virtual environment
- Install the python package in edition mode: `pip install -e .`
- Create a branch for your feature
- Test your change using `tox`
- Send a PR when ready.

## References

Thank you to Lunarok to show an implementation example [in PHP for Jeedom](https://github.com/lunarok/jeedom_vigilancemeteo). Lot of inspiration for the first python implementation.

Since release 3.0.0, the python implementation use the the [recommendation made by Météo
France on www.data.gouv.fr](https://www.data.gouv.fr/fr/datasets/diffusion-temps-reel-de-la-vigilance-meteorologique-en-metropole/).

## License

This software is under the MIT License.
