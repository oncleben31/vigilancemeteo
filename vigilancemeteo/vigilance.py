# coding: utf-8
"""Implement a class for Météofrance weather alerts """
import datetime
from lxml import etree


class ZoneAlerte(object):
    """A Class to descripe French departments weather alerts.

    Data are fetch ont vigilance.meteofrance.com website.

    Private attributes from ZoneAlerte class:
    - _departement: The department watched
    - _date_mise_a_jour: Date and time of the weather forcast update from
      MétéoFrance
    - _liste_alertes: A dictionary with all the alerts. Keys for alert type and
      value for criticity (by color).

    Methods from ZoneAlerte class:
    - mise_a_jour_etat(): update alerts list by feching latest info from
      MétéoFrance forcast.
    - message_de_synthese(format): return a string with textual synthesis
      of the active alerts in department. According to value of 'format'
      parameter, the string return change: 'text' (default) or 'html'

    Public attributes  from ZoneAlerte class
    - synthese_couleur: return the overall criticity color for the department
    - url_pour_en_savoir_plus: return the URL to access more information about
      department weather alerts from the MétéoFrance website.
    - date_mise_a_jour: return latest bulletin update date & time
    - departement: Get or set the departement number corresponding to the area
      watched.
    - liste_alertes: return the list of active alerts

    Example:
    >>>import vigilancemeteo
    >>>zone = vigilancemeteo.ZoneAlerte('92')
    >>>zone.synthese_couleur
    'Vert'
    >>>zone.urlPourEnSavoirPlus
    'http://vigilance.meteofrance.com/Bulletin_sans.html?a=dept75&b=1&c='
    >>>zone.message_de_synthese
    'Aucune alerte en cours.'
    """
    # TODO: Check potential encodage issues. # pylint: disable=fixme
    # TODO: Opportunity to add advises and comments from the weather buletin.
    # TODO: Monitor change from one bulletin to another.
    # TODO: Add markdown format.

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

    # URL used to fetch data on Météo France website.
    URL_VIGILANCE_METEO = "http://vigilance.meteofrance.com"\
                          "/data/NXFR33_LFPW_.xml"
    # URL_VIGILANCE_METEO = "./tests/NXFR33_LFPW_.xml" #for local tests.

    def __init__(self, departement):
        """Class constructor.

        Expect to have the department number as a 2 character String. Can be
        between 01 and 95, 2A, 2B or 99 (for Andorre).
        """

        # Variables init
        self._date_mise_a_jour = None
        self._liste_alertes = {}
        self._departement = None

        # Check _departement variable using the property.
        # Warning the setter launch mise_a_jour_etat() methods.
        self.departement = departement

    def mise_a_jour_etat(self):
        """Fetch active weather alerts for the department.

        get the alert color for the 9 different types on the Météo France
        website and update the variable 'liste_alertes'.
        Get date and time of the buletin update on the Météo France website and
        update the variable '_date_mise_a_jour'.
        """

        # Empty the alerts list
        self._liste_alertes = {}

        # Fetch data on Météo France website
        try:
            tree = etree.parse(ZoneAlerte.URL_VIGILANCE_METEO) #pylint disable=c-extension-no-member
        except (OSError, IOError):
            # If error during reading the data on the website, all the
            # attribues are reset.
            self._date_mise_a_jour = None
            self._liste_alertes = {}
        else:
            # Get the active alerts for the specific department
            alertes_standards = tree.xpath("/CV/DV[attribute::dep='" +
                                           self._departement + "']")
            # Get the additional active alerts if it is a coastal department
            if self._departement in ZoneAlerte.LISTE_DEPARTEMENT_LITTORAL:
                alertes_standards.extend(tree.xpath("/CV/DV[attribute::dep='"
                                                    + self._departement +
                                                    "10']"))

            # Identify each active alert and the color associated (criticity).
            # They are grouped by color
            for alertes_du_departement in alertes_standards:
                # Get the color of the alert group
                couleur = int(alertes_du_departement.get('coul'))

                # Get all the active alerts in the group
                for risque in list(alertes_du_departement):
                    type_risque = int(risque.get('val'))
                    # Update the instance variable with the alert list
                    self._mise_a_jour_alerte(ZoneAlerte.LISTE_TYPE_ALERTE[type_risque - 1],
                                             ZoneAlerte.LISTE_COULEUR_ALERTE[couleur - 1])

            # Get the date and time of the buletin update
            string_date = tree.xpath("/CV/EV")[0].get('dateinsert')

            # Convert the string in date and time
            annee = int(string_date[0:4])
            mois = int(string_date[4:6])
            jour = int(string_date[6:8])
            heure = int(string_date[8:10])
            minute = int(string_date[10:12])
            seconde = int(string_date[12:14])
            self._date_mise_a_jour = datetime.datetime(annee, mois, jour,
                                                       heure, minute, seconde)

    def _mise_a_jour_alerte(self, type_risque, couleur):
        """Update on alert type."""
        self._liste_alertes[type_risque] = couleur

    def __repr__(self):
        """"instance representation"""
        # Order the dictionary keys ecause before python 3.6 keys are not
        # ordered
        liste_alertes_ordonnee = ""
        for key in sorted(self.liste_alertes.keys()):
            liste_alertes_ordonnee = liste_alertes_ordonnee +\
                                  "'{}': '{}', ".\
                                  format(key, self.liste_alertes[key])
        return "ZoneAlerte: \n - departement: '{}'\n - date_mise_a_jour: '{}'"\
               "\n - liste_alertes: {{{}}}".format(self._departement,
                                                   self._date_mise_a_jour,
                                                   liste_alertes_ordonnee[:-2])

    @property
    def synthese_couleur(self):
        """Get the department color.

        It's the color of the most critical alert.
        """
        if any(alerte == 'Rouge' for alerte in self.liste_alertes.values()):
            synthese = 'Rouge'
        elif any(alerte == 'Orange' for alerte in self.liste_alertes.values()):
            synthese = 'Orange'
        elif any(alerte == 'Jaune' for alerte in self.liste_alertes.values()):
            synthese = 'Jaune'
        elif self.date_mise_a_jour is None:
            # if update date is None it's mean we ahd issue getting
            # the information.
            synthese = 'Inconnue'
        else:
            synthese = 'Vert'
        return synthese

    @property
    def url_pour_en_savoir_plus(self):
        """Get the link to have additional info about alerts in department.

        Return the vigilance.meteofrance.com URL to get additinonal details
        about active alerts in the department.
        """
        return "http://vigilance.meteofrance.com/"\
               "Bulletin_sans.html?a=dept{}&b=1&c=".format(self._departement)

    def message_de_synthese(self, msg_format='text'):
        """Get synthesis text message to have the list of the active alerts."""
        if self.synthese_couleur == 'Vert':
            if msg_format == 'text':
                message = "Aucune alerte météo en cours."
            elif msg_format == 'html':
                message = "<p>Aucune alerte météo en cours.</p>"
        elif self.synthese_couleur == 'Inconnue':
            if msg_format == 'text':
                message = "Impossible de récupérer l'information"
            if msg_format == 'html':
                message = "<p>Impossible de récupérer l'infmation</p>"
        else:
            if msg_format == 'text':
                message = \
                    "Alerte météo {} en cours :".format(self.synthese_couleur)
                # Order the dictionary keys ecause before python 3.6 keys are
                # not ordered
                for type_risque in sorted(self.liste_alertes.keys()):
                    message = message + "\n - {}: {}"\
                              .format(type_risque,
                                      self.liste_alertes[type_risque])
            elif msg_format == 'html':
                message = \
                    "<p>Alerte météo {} en cours :"\
                    "</p><ul>".format(self.synthese_couleur)
                # Order the dictionary keys ecause before python 3.6 keys are
                # not ordered
                for type_risque in sorted(self.liste_alertes.keys()):
                    message = message + "<li>{}: {}</li>"\
                              .format(type_risque,
                                      self.liste_alertes[type_risque])
                message = message + '</ul>'
        return message

    @property
    def date_mise_a_jour(self):
        """Accessor and setter for Update date"""
        return self._date_mise_a_jour

    @property
    def liste_alertes(self):
        """Accessor and setter for weather alerts list"""
        return self._liste_alertes

    @property
    def departement(self):
        """Accessor for area code linked to the weather report"""
        return self._departement

    @departement.setter
    def departement(self, departement):
        """Setter with consitency check on the are code value.

        Departemnt variable should be a 2 chararcters string. In the source XML
        file, the 92, 93 and 95 departments do not exist. In this case we have
        to use the 75 department instead.
        This setter will call the mise_a_jour_etat() method systematicaly.
        """
        # Check the valide values for department
        if departement not in ZoneAlerte.LISTE_DEPARTEMENT_VALIDE:
            raise ValueError("Departement parameter have to be a 2 character"
                             "between '01' and '95' or '2A' or '2B' or '99'."
                             "Used value: {}".format(departement))

        # Equivalences list
        equivalence75 = ['92', '93', '94']
        departement_valide = departement

        # Replace, the missing department in the XLM by the equivalence.
        if departement in equivalence75:
            departement_valide = '75'

        # Set the variable
        self._departement = departement_valide

        # Call the first update
        self.mise_a_jour_etat()
