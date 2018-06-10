# coding: utf-8
from lxml import etree
import datetime


class ZoneAlerte(object):
    """A Class to descripe French departments weather alerts.

    Data are fetch ont vigilance.meteofrance.com website.

    Variables from ZoneAlerte class:
    - _departement : The department watched
    - _dateMiseAJour : Date and time of the weather forcast update from
      MétéoFrance
    - _listeAlertes : A dictionary with all the alerts. Keys for alert type and
      value for criticity (by color).

    Methods from ZoneAlerte class:
    - miseAJourEtat() : update alerts list by feching latest info from
      MétéoFrance forcast.

    Properties from ZoneAlerte class
    - syntheseCouleur : return the overall criticity color for the department
    - urlPourEnSavoirPlus : return the URL to access more information about
      department weather alerts from the MétéoFrance website.
    - messageDeSynthese : return a string with textual synthesis of the active
      alerts in department.

    Example:
    >>>import vigilancemeteo
    >>>zone = vigilancemeteo.ZoneAlerte('92')
    >>>zone.syntheseCouleur
    'Vert'
    >>>zone.urlPourEnSavoirPlus
    'http://vigilance.meteofrance.com/Bulletin_sans.html?a=dept75&b=1&c='
    >>>zone.messageDeSynthese
    'Aucune alerte en cours.'
    """
    # TODO: Define behaviour if no network available
    # TODO: Check potential encodage issues.
    # TODO: Opportunity to add advises and comments from the weather buletin

    # enums used in this class. Warning first indice is 0
    # Alert criticity
    LISTE_COULEUR_ALERTE = ['Vert', 'Jaune', 'Orange', 'Rouge']
    # Alert type
    LISTE_TYPE_ALERTE = ['Vent violent', 'Pluie-innodation', 'Orages',
                         'Inondation', 'Neige-verglas', 'Canicule',
                         'Grand-froid', 'Avalanches', 'Vagues-submersion']
    # Coastal Departments list
    LISTE_DEPARTEMENT_LITTORAL = [
        '06', '11', '13', '14', '17', '22', '29', '2A', '2B', '30', '33', '34',
        '35', '40', '44', '50', '56', '59', '62', '64', '66', '76', '80', '83',
        '85']
    # Valide departments list
    LISTE_DEPARTEMENT_VALIDE = [
        '01', '02', '03', '04', '05', '06', '07', '08', '09',
        '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
        '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2A', '2B',
        '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
        '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
        '50', '51', '52', '53', '54', '55', '56', '57', '58', '59',
        '60', '61', '62', '63', '64', '65', '66', '67', '68', '69',
        '70', '71', '72', '73', '74', '75', '76', '77', '78', '79',
        '80', '81', '82', '83', '84', '85', '86', '87', '88', '89',
        '90', '91', '92', '93', '94', '95', '99']

    # URL used to fetch data on Météo France website
    URL_VIGILANCE_METEO = "http://vigilance.meteofrance.com"\
                          "/data/NXFR33_LFPW_.xml"
    # URL_VIGILANCE_METEO = "./tests/NXFR33_LFPW_.xml" #for local tests

    def __init__(self, departement):
        """Class constructor.

        Expect to have the department number as a 2 character String. Can be
        between 01 and 95, 2A, 2B or 99 (for Andorre).
        """

        # Variables init
        self._dateMiseAJour = None
        self._listeAlertes = {}

        # Check _departement variable by the property.
        # Warning the setter launch miseAJourEtat() methods
        self.departement = departement

    def miseAJourEtat(self):
        """Fetch active weather alerts for the department.

        get the alert color for the 9 different types on the Météo France
        website and update the variable 'listeAlertes'.
        Get date and time of the buletin update on the Météo France website and
        update the variable '_dateMiseAJour'.
        """

        # Empty the alerts list
        self._listeAlertes = {}

        # Fetch data on Mété France website
        tree = etree.parse(ZoneAlerte.URL_VIGILANCE_METEO)

        # Get the acitve alerts for the specific department
        alertesStandards = tree.xpath("/CV/DV[attribute::dep='" +
                                      self._departement + "']")
        # Get the additional active alerts if it is a coastal department
        if self._departement in ZoneAlerte.LISTE_DEPARTEMENT_LITTORAL:
            alertesStandards.extend(tree.xpath("/CV/DV[attribute::dep='" +
                                    self._departement + "10']"))

        # Identify each active alert and the color associated (criticity).
        # They are grouped by color
        for alertesDuDepartement in alertesStandards:
            # Get the color of the alert group
            couleur = int(alertesDuDepartement.get('coul'))

            # Get all the active alerts in the group
            for risque in list(alertesDuDepartement):
                type = int(risque.get('val'))
                # Update the instance variable with the alert list
                self._miseAJourAlerte(ZoneAlerte.LISTE_TYPE_ALERTE[type - 1],
                                      ZoneAlerte.LISTE_COULEUR_ALERTE[couleur
                                                                      - 1])

        # Get the date and time of the buletin update
        elementDate = tree.xpath("/CV/EV")
        stringDate = elementDate[0].get('dateinsert')

        # Convert the string in date and time
        annee = int(stringDate[0:4])
        mois = int(stringDate[4:6])
        jour = int(stringDate[6:8])
        heure = int(stringDate[8:10])
        minute = int(stringDate[10:12])
        seconde = int(stringDate[12:14])
        self._dateMiseAJour = datetime.datetime(annee, mois, jour, heure,
                                                minute, seconde)

    def _miseAJourAlerte(self, type, couleur):
        """Update on alert type."""
        self._listeAlertes[type] = couleur

    def __repr__(self):
        """"instance representation"""
        # Order the dictionary keys ecause before python 3.6 keys are not
        # ordered
        listeAlertesOrdonnee = ""
        for key in sorted(self.listeAlertes.keys()):
            listeAlertesOrdonnee = listeAlertesOrdonnee +\
                                  "'{}': '{}', ".\
                                  format(key, self.listeAlertes[key])
        return "ZoneAlerte: \n - departement: '{}'\n - dateMiseAJour: '{}'"\
               "\n - listeAlertes: {{{}}}".format(self._departement,
                                                  self._dateMiseAJour,
                                                  listeAlertesOrdonnee[:-2])

    @property
    def syntheseCouleur(self):
        """Get the department color.

        It's the color of the most critical alert.
        """
        if any(alerte == 'Rouge' for alerte in self.listeAlertes.values()):
            synthese = 'Rouge'
        elif any(alerte == 'Orange' for alerte in self.listeAlertes.values()):
            synthese = 'Orange'
        elif any(alerte == 'Jaune' for alerte in self.listeAlertes.values()):
            synthese = 'Jaune'
        else:
            synthese = 'Vert'
        return synthese

    @property
    def urlPourEnSavoirPlus(self):
        """Get the link to have additional info about alerts in department.

        Return the vigilance.meteofrance.com URL to get additinonal details
        about active alerts in the department.
        """
        return "http://vigilance.meteofrance.com/"\
               "Bulletin_sans.html?a=dept{}&b=1&c=".format(self._departement)

    @property
    def messageDeSynthese(self):
        """Get synthesis text message to have the list of the active alerts."""
        if self.syntheseCouleur == 'Vert':
            message = "Aucune alerte en cours."
        else:
            message = "Alerte {} en cours :".format(self.syntheseCouleur)
            # Order the dictionary keys ecause before python 3.6 keys are not
            # ordered
            for type in sorted(self.listeAlertes.keys()):
                message = message + "\n - {}: {}"\
                          .format(type, self.listeAlertes[type])

        return message

    @property
    def dateMiseAJour(self):
        return self._dateMiseAJour

    @property
    def listeAlertes(self):
        return self._listeAlertes

    @property
    def departement(self):
        return self._departement

    @departement.setter
    def departement(self, departement):
        """Setter with consitency check on the 'departement' value.

        Departemnt variable should be a 2 chararcters string. In the source XML
        file, the 92, 93 and 95 departments do not exist. In this case we have
        to use the 75 department instead.
        This setter will call the miseAJourEtat() method systematicaly.
        """
        # Check the valide values for department
        if departement not in ZoneAlerte.LISTE_DEPARTEMENT_VALIDE:
            raise ValueError("Le département doit être une chaine de 2 "
                             "caractères compris entre '01' et '95' ou '2A' "
                             "ou '2B' ou '99'")

        # Equivalences list
        equivalence75 = ['92', '93', '94']
        departementValide = departement

        # Replace, the missing department in the XLM by the equivalence.
        if departement in equivalence75:
            departementValide = '75'

        # Set the variable
        self._departement = departementValide

        # Call the first update
        self.miseAJourEtat()
