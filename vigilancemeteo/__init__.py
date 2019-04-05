# coding: utf-8
"""Vigilancemeteo provide an API to fetch France weather alerts from Météo
France website.

ZoneAlerte class allows to fetch active weather alerts for a french department.
"""

from .vigilance_proxy import VigilanceMeteoFranceProxy, VigilanceMeteoError
from .department_weather_alert import DepartmentWeatherAlert
from .__version__ import __version__, VERSION

