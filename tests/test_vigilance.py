# coding: utf-8
import datetime
import pytest
import sys

from vigilancemeteo import ZoneAlerte

# Manage differences beetween python 2.7 and 3.6
if sys.version_info < (3, 0):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen


@pytest.yield_fixture()
def donneesLocales():
    """Fixture to replace webiste answer by a local one."""
    # Using local answer instead of MeteoFrance website
    valeurInitiale = ZoneAlerte.URL_VIGILANCE_METEO
    ZoneAlerte.URL_VIGILANCE_METEO = "./tests/NXFR33_LFPW_.xml"
    # TODO: Check if we need to set the local file path in a better way.
    yield None

    # Set back the initial value(using website instead of local answer)
    ZoneAlerte.URL_VIGILANCE_METEO = valeurInitiale


def test_fonctionnel():
    """Fonctional test"""
    zone = ZoneAlerte('32')

    # Test the forecast update date and time. It should be near today.
    testDate = (datetime.datetime.now()
                - zone.dateMiseAJour) < datetime.timedelta(days=1)

    # Test if the URL urlPourEnSavoirPlus is available
    testUrl = urlopen(zone.urlPourEnSavoirPlus).getcode() == 200

    # Test to check if there is a overall criticity color for the department
    testCouleur = zone.syntheseCouleur in ZoneAlerte.LISTE_COULEUR_ALERTE

    # Test the synthesis message
    testSynthese = zone.messageDeSynthese is not None

    assert (testDate, testUrl, testCouleur,
            testSynthese) == (True, True, True, True)


@pytest.mark.parametrize('dep', ['92', '93', '94'])
def test_petiteCouronne(donneesLocales, dep):
    """Test 'Petite Couronne' specificity.

    Check code when we use a department in the Paris 'Petit Couronne' which are
    not in the vigilance.meteofrance.fr XML file. In this case we use the
    departement 75.
    """

    zone = ZoneAlerte(dep)
    assert zone.departement == '75'


@pytest.mark.parametrize('dep', [75, '2', 'bonjour', 1.5, '98', True, None])
def test_departementNonValide(donneesLocales, dep):
    """Test when creating Class instace with with wrong parameters."""
    with pytest.raises(ValueError, match=r'.* département .*'):
        ZoneAlerte(dep)


@pytest.mark.parametrize("dep, coul",
                         [('2A', 'Jaune'), ('07', 'Vert'),
                          ('95', 'Orange'), ('32', 'Rouge')])
def test_couleurSynthese(donneesLocales, dep, coul):
    """Test synthesis property."""
    zone = ZoneAlerte(dep)
    assert zone.syntheseCouleur == coul


def test_risqueCotier(donneesLocales):
    """Test specific risks for coastal departments."""
    zone = ZoneAlerte('2A')
    resultatAttendu = "ZoneAlerte: \n - departement: '2A'"\
                      "\n - dateMiseAJour: '2018-03-18 16:00:00'"\
                      "\n - listeAlertes: "\
                      "{'Avalanches': 'Jaune', 'Orages': 'Jaune', "\
                      "'Pluie-innodation': 'Jaune', 'Vagues-submersion': "\
                      "'Jaune'}"
    assert zone.__repr__() == resultatAttendu


@pytest.mark.parametrize('format', ['text', 'html'])
def test_messageDeSyntheseVert(donneesLocales, format):
    """Test syntesis message when no active alert."""
    zone = ZoneAlerte('34')
    if format == 'text':
        resultatAttendu = "Aucune alerte météo en cours."
    elif format == 'html':
        resultatAttendu = "<p>Aucune alerte météo en cours.</p>"
    assert zone.messageDeSynthese(format) == resultatAttendu


@pytest.mark.parametrize('format', ['text', 'html'])
def test_messageDeSyntheseAvecAlerte(donneesLocales, format):
    """Test synthesis message when at least one active alert"""
    zone = ZoneAlerte('2A')
    if format == 'text':
        resultatAttendu = "Alerte météo Jaune en cours :"\
                          "\n - Avalanches: Jaune"\
                          "\n - Orages: Jaune"\
                          "\n - Pluie-innodation: Jaune"\
                          "\n - Vagues-submersion: Jaune"
    elif format == 'html':
        resultatAttendu = "<p>Alerte météo Jaune en cours :</p><ul>"\
                          "<li>Avalanches: Jaune</li>"\
                          "<li>Orages: Jaune</li>"\
                          "<li>Pluie-innodation: Jaune</li>"\
                          "<li>Vagues-submersion: Jaune</li></ul>"
    assert zone.messageDeSynthese(format) == resultatAttendu
