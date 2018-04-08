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
    """Fixture pour utiliser une réponse locale."""
    # Utilisation d'une réponse local à la place du site de Météo France
    valeurInitiale = ZoneAlerte.URL_VIGILANCE_METEO
    ZoneAlerte.URL_VIGILANCE_METEO = "./tests/NXFR33_LFPW_.xml"
    # TODO: Voir si il faut pas coder le chemin autrement
    yield None

    # On rétabli la valeur initiale
    ZoneAlerte.URL_VIGILANCE_METEO = valeurInitiale


def test_fonctionnel():
    """Test fonctionel global."""
    zone = ZoneAlerte('32')

    # Test sur la date de prevision. Elle doit être proche d'ajourd'hui
    # à 1 jour près.
    testDate = (datetime.datetime.now()
                - zone.dateMiseAJour) < datetime.timedelta(days=1)

    # Test si urlPourEnSavoirPlus est bien accessible
    testUrl = urlopen(zone.urlPourEnSavoirPlus).getcode() == 200

    # Test pour savoir si le département à bien une couleur
    testCouleur = zone.syntheseCouleur in ZoneAlerte.LISTE_COULEUR_ALERTE

    # Test le message de synthese
    testSynthese = zone.messageDeSynthese is not None

    assert (testDate, testUrl, testCouleur,
            testSynthese) == (True, True, True, True)


@pytest.mark.parametrize('dep', ['92', '93', '94'])
def test_petiteCouronne(donneesLocales, dep):
    """Test la petite Couronne.

    Test le fonctionnement quand on utiliser un département de la petite
    couronne de Paris qui ne sont pas dans le fichier XML du site
    vigilance.meteofrance.fr. Dans ce cas on utilise le département 75.
    """

    zone = ZoneAlerte(dep)
    assert zone.departement == '75'


@pytest.mark.parametrize('dep', [75, '2', 'bonjour', 1.5, '98', True, None])
def test_departementNonValide(donneesLocales, dep):
    """Test la creation d'une instance en utilisant des valeurs invalides."""
    with pytest.raises(ValueError, match=r'.* département .*'):
        ZoneAlerte(dep)


@pytest.mark.parametrize("dep, coul",
                         [('2A', 'Jaune'), ('07', 'Vert'),
                          ('95', 'Orange'), ('32', 'Rouge')])
def test_couleurSynthese(donneesLocales, dep, coul):
    """Test les propriétés de synthèse."""
    zone = ZoneAlerte(dep)
    assert zone.syntheseCouleur == coul


def test_risqueCotier(donneesLocales):
    """Test les risques exclusifs aux départements du littoral."""
    zone = ZoneAlerte('2A')
    resultatAttendu = "ZoneAlerte: \n - departement: '2A'"\
                      "\n - dateMiseAJour: '2018-03-18 16:00:00'"\
                      "\n - listeAlertes: "\
                      "{'Avalanches': 'Jaune', 'Orages': 'Jaune', "\
                      "'Pluie-innodation': 'Jaune', 'Vagues-submersion': "\
                      "'Jaune'}"
    assert zone.__repr__() == resultatAttendu


def test_messageDeSyntheseVert(donneesLocales):
    """Test du message de synthèse quand il n'y a pas d'alerte en cours"""
    zone = ZoneAlerte('34')
    assert zone.messageDeSynthese == "Aucune alerte en cours."


def test_messageDeSyntheseAvecAlerte(donneesLocales):
    """Test du message de synthèse quand il y a au moins une alerte"""
    zone = ZoneAlerte('2A')
    resultatAttendu = "Alerte Jaune en cours :"\
                      "\n - Avalanches: Jaune"\
                      "\n - Orages: Jaune"\
                      "\n - Pluie-innodation: Jaune"\
                      "\n - Vagues-submersion: Jaune"
    assert zone.messageDeSynthese == resultatAttendu
