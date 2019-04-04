# coding: utf-8
# pylint: disable= unused-argument, redefined-outer-name
"""tests for vigilance module - DepartmentWeatherAlert"""
import datetime
import sys

import pytest
from pytz import timezone

from vigilancemeteo import DepartmentWeatherAlert, VigilanceMeteoFranceProxy
from vigilancemeteo.constants import ALERT_COLOR_LIST

# Manage differences beetween python 2.7 and 3.6
if sys.version_info < (3, 0):
    from urllib2 import urlopen  # pylint: disable=import-error
else:
    from urllib.request import urlopen

# TODO: add pylint and doc check in tox ?


@pytest.yield_fixture()
def fix_local_data():
    """Fixture to replace webiste answer by a local one."""
    # Using local answer instead of MeteoFrance website
    valeur_initiale = VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML = "./tests/NXFR33_LFPW_.xml"
    yield None

    # Set back the initial value(using website instead of local answer)
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML = valeur_initiale


@pytest.yield_fixture()
def fix_data_unavailable():
    """Fixture to replace webiste answer by an inaxessible one."""
    # Using local answer instead of MeteoFrance website
    valeur_initiale = VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML = (
        "http://vigilance.meteofrance.com" "/data/fake_test.xml"
    )
    yield None

    # Set back the initial value(using website instead of local answer)
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML = valeur_initiale


def test_functional():
    """Functional test"""
    client = VigilanceMeteoFranceProxy()
    zone = DepartmentWeatherAlert("32", client)

    # Test the forecast update date and time. It should be near today.
    test_date = (
        timezone("UTC").localize(datetime.datetime.utcnow()) - zone.bulletin_date
    ) < datetime.timedelta(days=1)

    # Test if the URL url_pour_en_savoir_plus is available
    test_url = urlopen(zone.additional_info_URL).getcode() == 200

    # Test to check if there is a overall criticity color for the department
    test_color = zone.department_color in ALERT_COLOR_LIST

    # Test the synthesis message
    test_summary = zone.summary_message is not None

    assert (test_date, test_url, test_color, test_summary) == (True, True, True, True)


# def test_url_innaccessible(fix_data_unavailable):
#     """URL unavailable test"""
#     zone = DepartmentWeatherAlert('32')

#     # Test to check if there is a overall criticity color for the department
#     test_couleur = zone.synthese_couleur is None

#     # Test the synthesis message
#     test_synthese_text = zone.summary_message('text')\
#                          == "Impossible de récupérer l'information"
#     test_synthese_html = zone.summary_message('html')\
#                          == "<p>Impossible de récupérer l'infmation</p>"

#     assert (test_couleur,
#             test_synthese_text, test_synthese_html) == (True, True, True)


@pytest.mark.parametrize("dep", ["92", "93", "94"])
def test_petite_couronne(fix_local_data, dep):
    """Test 'Petite Couronne' specificity.

    Check code when we use a department in the Paris 'Petit Couronne' which are
    not in the vigilance.meteofrance.fr XML file. In this case we use the
    departement 75.
    """

    zone = DepartmentWeatherAlert(dep)
    assert zone.department == "75"


@pytest.mark.parametrize("dep", [75, "2", "bonjour", 1.5, "98", True, None])
def test_department_parameter_not_valid(fix_local_data, dep):
    """Test when creating Class instace with with wrong parameters."""
    with pytest.raises(ValueError, match=r"Department .*"):
        DepartmentWeatherAlert(dep)


@pytest.mark.parametrize(
    "department, color",
    [("2A", "Jaune"), ("07", "Vert"), ("95", "Orange"), ("32", "Rouge")],
)
def test_department_color(fix_local_data, department, color):
    """Test synthesis property."""
    zone = DepartmentWeatherAlert(department)
    assert zone.department_color == color


def test_coastal_risks(fix_local_data):
    """Test specific risks for coastal departments."""
    zone = DepartmentWeatherAlert("2A")
    excpected_result = (
        "DepartmentWeatherAlert: \n - department: '2A'"
        "\n - bulletin_date: '2018-03-18 16:00:00+01:00'"
        "\n - alerts_list: "
        "{'Avalanches': 'Jaune', 'Canicule': 'Vert', 'Grand-froid': 'Vert'"
        ", 'Inondation': 'Vert', 'Neige-verglas': 'Vert', 'Orages': 'Jaune'"
        ", 'Pluie-innodation': 'Jaune', 'Vagues-submersion': 'Jaune'"
        ", 'Vent violent': 'Vert'}"
    )
    assert zone.__repr__() == excpected_result


@pytest.mark.parametrize("msg_format", ["text", "html"])
def test_summary_message_vert(fix_local_data, msg_format):
    """Test syntesis message when no active alert."""
    zone = DepartmentWeatherAlert("34")
    if msg_format == "text":
        excpected_result = "Aucune alerte météo en cours."
    elif msg_format == "html":
        excpected_result = "<p>Aucune alerte météo en cours.</p>"
    assert zone.summary_message(msg_format) == excpected_result


@pytest.mark.parametrize("msg_format", ["text", "html"])
def test_summary_message_alerte(fix_local_data, msg_format):
    """Test synthesis message when at least one active alert"""
    zone = DepartmentWeatherAlert("2A")
    if msg_format == "text":
        excpected_result = (
            "Alerte météo Jaune en cours :"
            "\n - Avalanches: Jaune"
            "\n - Orages: Jaune"
            "\n - Pluie-innodation: Jaune"
            "\n - Vagues-submersion: Jaune"
        )
    elif msg_format == "html":
        excpected_result = (
            "<p>Alerte météo Jaune en cours :</p><ul>"
            "<li>Avalanches: Jaune</li>"
            "<li>Orages: Jaune</li>"
            "<li>Pluie-innodation: Jaune</li>"
            "<li>Vagues-submersion: Jaune</li></ul>"
        )
    assert zone.summary_message(msg_format) == excpected_result
