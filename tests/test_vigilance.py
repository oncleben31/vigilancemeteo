# coding: utf-8
# pylint: disable= unused-argument, redefined-outer-name
"""tests for vigilance module"""
import datetime
import sys
import pytest

from vigilancemeteo import ZoneAlerte

# Manage differences beetween python 2.7 and 3.6
if sys.version_info < (3, 0):
    from urllib2 import urlopen #pylint: disable=import-error
else:
    from urllib.request import urlopen


@pytest.yield_fixture()
def fix_donnees_locales():
    """Fixture to replace webiste answer by a local one."""
    # Using local answer instead of MeteoFrance website
    valeur_initiale = ZoneAlerte.URL_VIGILANCE_METEO
    ZoneAlerte.URL_VIGILANCE_METEO = "./tests/NXFR33_LFPW_.xml"
    # pylint: disable=fixme
    # TODO: Check if we need to set the local file path in a better way.
    yield None

    # Set back the initial value(using website instead of local answer)
    ZoneAlerte.URL_VIGILANCE_METEO = valeur_initiale

@pytest.yield_fixture()
def fix_donnees_innaccessibles():
    """Fixture to replace webiste answer by an inaxessible one."""
    # Using local answer instead of MeteoFrance website
    valeur_initiale = ZoneAlerte.URL_VIGILANCE_METEO
    ZoneAlerte.URL_VIGILANCE_METEO = "http://vigilance.meteofrance.com"\
                          "/data/fake_test.xml"
    yield None

    # Set back the initial value(using website instead of local answer)
    ZoneAlerte.URL_VIGILANCE_METEO = valeur_initiale

def test_fonctionnel():
    """Fonctional test"""
    zone = ZoneAlerte('32')

    # Test the forecast update date and time. It should be near today.
    test_date = (datetime.datetime.now()
                 - zone.date_mise_a_jour) < datetime.timedelta(days=1)

    # Test if the URL url_pour_en_savoir_plus is available
    test_url = urlopen(zone.url_pour_en_savoir_plus).getcode() == 200

    # Test to check if there is a overall criticity color for the department
    test_couleur = zone.synthese_couleur in ZoneAlerte.LISTE_COULEUR_ALERTE

    # Test the synthesis message
    test_synthese = zone.message_de_synthese is not None

    assert (test_date, test_url, test_couleur,
            test_synthese) == (True, True, True, True)

def test_url_innaccessible(fix_donnees_innaccessibles):
    """URL unavailable test"""
    zone = ZoneAlerte('32')

    # Test the forecast update date and time. It should be near today.
    test_date = zone.date_mise_a_jour is None

    # Test to check if there is a overall criticity color for the department
    test_couleur = zone.synthese_couleur == 'Inconnue'

    # Test the synthesis message
    test_synthese_text = zone.message_de_synthese('text')\
                         == "Impossible de récupérer l'information"
    test_synthese_html = zone.message_de_synthese('html')\
                         == "<p>Impossible de récupérer l'infmation</p>"

    assert (test_date, test_couleur,
            test_synthese_text, test_synthese_html) == (True, True, True, True)

@pytest.mark.parametrize('dep', ['92', '93', '94'])
def test_petite_couronne(fix_donnees_locales, dep):
    """Test 'Petite Couronne' specificity.

    Check code when we use a department in the Paris 'Petit Couronne' which are
    not in the vigilance.meteofrance.fr XML file. In this case we use the
    departement 75.
    """

    zone = ZoneAlerte(dep)
    assert zone.departement == '75'


@pytest.mark.parametrize('dep', [75, '2', 'bonjour', 1.5, '98', True, None])
def test_departement_non_valide(fix_donnees_locales, dep):
    """Test when creating Class instace with with wrong parameters."""
    with pytest.raises(ValueError, match=r'Departement .*'):
        ZoneAlerte(dep)


@pytest.mark.parametrize("dep, coul",
                         [('2A', 'Jaune'), ('07', 'Vert'),
                          ('95', 'Orange'), ('32', 'Rouge')])
def test_couleur_synthese(fix_donnees_locales, dep, coul):
    """Test synthesis property."""
    zone = ZoneAlerte(dep)
    assert zone.synthese_couleur == coul


def test_risque_cotier(fix_donnees_locales):
    """Test specific risks for coastal departments."""
    zone = ZoneAlerte('2A')
    resultat_attendu = "ZoneAlerte: \n - departement: '2A'"\
                      "\n - date_mise_a_jour: '2018-03-18 16:00:00'"\
                      "\n - liste_alertes: "\
                      "{'Avalanches': 'Jaune', 'Orages': 'Jaune', "\
                      "'Pluie-innodation': 'Jaune', 'Vagues-submersion': "\
                      "'Jaune'}"
    assert zone.__repr__() == resultat_attendu


@pytest.mark.parametrize('msg_format', ['text', 'html'])
def test_message_de_synthese_vert(fix_donnees_locales, msg_format):
    """Test syntesis message when no active alert."""
    zone = ZoneAlerte('34')
    if msg_format == 'text':
        resultat_attendu = "Aucune alerte météo en cours."
    elif msg_format == 'html':
        resultat_attendu = "<p>Aucune alerte météo en cours.</p>"
    assert zone.message_de_synthese(msg_format) == resultat_attendu


@pytest.mark.parametrize('msg_format', ['text', 'html'])
def test_message_de_synthese_alerte(fix_donnees_locales, msg_format):
    """Test synthesis message when at least one active alert"""
    zone = ZoneAlerte('2A')
    if msg_format == 'text':
        resultat_attendu = "Alerte météo Jaune en cours :"\
                          "\n - Avalanches: Jaune"\
                          "\n - Orages: Jaune"\
                          "\n - Pluie-innodation: Jaune"\
                          "\n - Vagues-submersion: Jaune"
    elif msg_format == 'html':
        resultat_attendu = "<p>Alerte météo Jaune en cours :</p><ul>"\
                          "<li>Avalanches: Jaune</li>"\
                          "<li>Orages: Jaune</li>"\
                          "<li>Pluie-innodation: Jaune</li>"\
                          "<li>Vagues-submersion: Jaune</li></ul>"
    assert zone.message_de_synthese(msg_format) == resultat_attendu
