# coding: utf-8
"""Implement a class for Météofrance weather alerts """
import sys
import re
from datetime import datetime
from lxml import etree
from pytz import timezone
from vigilancemeteo.constants import ALERT_COLOR_LIST, VALID_DEPARTMENT_LIST

# Manage differences beetween python 2.7 and 3.6
if sys.version_info < (3, 0):
    from urllib2 import urlopen #pylint: disable=import-error
else:
    from urllib.request import urlopen

 # TODO: split the classes in 2 files

class VigilanceMeteoFranceProxy(object):
    """Class to manage the download of the data sources from MeteoFrance website.""" 

    # URL used to fetch data on Météo France website.
    URL_VIGILANCE_METEO_XML = "http://vigilance.meteofrance.com"\
                         "/data/NXFR33_LFPW_.xml"
    # URL_VIGILANCE_METEO_XML = "./tests/NXFR33_LFPW_.xml" #for local tests.

    # URL used to check if there were any updates since last check
    URL_VIGILANCE_METEO_CHECKSUM = "http://vigilance.meteofrance.com"\
                         "/data/vigilance_controle.txt"
    # URL_VIGILANCE_METEO_CHECKSUM = "./tests/vigilance_controle.txt" #for local tests

     # Alert type
    ALERT_TYPE_LIST = ['Vent violent', 'Pluie-innodation', 'Orages',
                         'Inondation', 'Neige-verglas', 'Canicule',
                         'Grand-froid', 'Avalanches', 'Vagues-submersion']
 
    # Area code list for Coastal Departments
    COASTAL_DEPARTMENT_LIST= [
        '06', '11', '13', '14', '17', '22', '29', '2A', '2B', '30', '33', '34',
        '35', '40', '44', '50', '56', '59', '62', '64', '66', '76', '80', '83',
        '85']

    def __init__(self):
        """Class instance constructor."""
        self._xml_tree = None
        self._latest_check_date = None
        self._latest_checksum_value = None
        self._bulletin_date = None

    def _get_new_checksum(self):
        """Return the checksum of the data source on MétéoFrance website"""
        # download checksum if not yet done or done since 60 secondes
        if (self._latest_check_date is None) or (datetime.now() - self._latest_check_date).seconds > 60:
            # Update latest check date.
            self._latest_check_date = datetime.now()

            # get checksum in vigilance_controle.txt
            # TODO: Add error management
            text = urlopen(VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_CHECKSUM).read().decode('utf-8')
            checksum = re.search(r'\n(.+?)\s', text)
            if checksum:
                 return checksum.group(1)
        else: 
            # No need to check so return previous value
            return self._latest_checksum_value
    
    def update_data(self):
        """Download an update of the XML data source only if needed"""
        # Download only if the checksum have change since latest update.
        current_checksum = self._get_new_checksum
        if current_checksum != self._latest_checksum_value:
            # TODO: catch error and define what to do if no answer
            # TODO: do we return status?
            # Save the new checksum
            self._latest_checksum_value = current_checksum
            
            # Save the new xml source
            self._xml_tree = etree.parse(VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML) #pylint disable=c-extension-no-member
    
            # Get the weather bulletin date & time
            string_date = self._xml_tree.xpath("/CV/EV")[0].get('dateinsert')

            # Convert the string in date and time with Europe/Paris timezone
            annee = int(string_date[0:4])
            mois = int(string_date[4:6])
            jour = int(string_date[6:8])
            heure = int(string_date[8:10])
            minute = int(string_date[10:12])
            seconde = int(string_date[12:14])
            paris_timezone = timezone('Europe/Paris')
            self._bulletin_date = paris_timezone.localize(datetime(annee, mois, jour,
                                                                   heure, minute, seconde))

    def get_alert_list(self, department):
        """Return the list and status of the alerts for a given department."""

        # update data
        self.update_data()
        
        # Set initial value for each alert type in the list
        alerts_list = {}
        for alert_type in VigilanceMeteoFranceProxy.ALERT_TYPE_LIST:
            alerts_list[alert_type] = 'Vert'

        # Get the active alerts for the specific department
        department_alerts = self.xml_tree.xpath("/CV/DV[attribute::dep='"
                                                + department + "']")

        # Get the additional active alerts if it is a coastal department
        if department in VigilanceMeteoFranceProxy.COASTAL_DEPARTMENT_LIST:
            department_alerts.extend(self.xml_tree.xpath("/CV/DV[attribute::dep='"
                                                         + department + "10']"))

        # Identify each active alert and the color associated (criticity).
        # They are grouped by color
        for alerts_group in department_alerts:
            # Get the color of the alert group
            color = int(alerts_group.get('coul'))

            # Get all the active alerts in the group
            for active_alert in list(alerts_group):
                alert_type = int(active_alert.get('val'))
                # Update the instance variable with the alert list
                alerts_list[VigilanceMeteoFranceProxy.ALERT_TYPE_LIST[alert_type - 1]]\
                    = ALERT_COLOR_LIST[color - 1]
                
        return alerts_list

    @property
    def xml_tree(self):
        """Getter of xml_tree attribute."""
        return self._xml_tree
    
    @property
    def checksum(self):
        """Getter for _latest_checksum_value"""
        return self._latest_checksum_value

    @property
    def bulletin_date(self):
        """Getter for _bulletin_date"""
        return self._bulletin_date

class ZoneAlerte(object):
    """A Class to descripe French departments weather alerts.

    Data are fetch ont vigilance.meteofrance.com website.

    Private attributes from ZoneAlerte class:
    - _department: The department watched
    - _alerts_list: A dictionary with all the alerts. Keys for alert type and
      value for criticity (by color).

    Methods from ZoneAlerte class:
    - mise_a_jour_etat(): update alerts list by feching latest info from
      MétéoFrance forcast.
    - message_de_synthese(format): return a string with textual synthesis
      of the active alerts in department. According to value of 'format'
      parameter, the string return change: 'text' (default) or 'html'

    Public attributes  from ZoneAlerte class
    - department_color: return the overall criticity color for the department
    - url_pour_en_savoir_plus: return the URL to access more information about
      department weather alerts from the MétéoFrance website.
    - bulletin_date: return latest bulletin update date & time with timezone
    - departement: Get or set the departement number corresponding to the area
      watched.
    - alerts_list: return the list of active alerts

    Example:
    >>>import vigilancemeteo
    >>>zone = vigilancemeteo.ZoneAlerte('92')
    >>>zone.department_color
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

    def __init__(self, department, vmf_proxy=None):
        """Class instance constructor.

        2 arguments expected:
         - The department (Required) number as a 2 character String. Can be between 01 and 95,
           2A, 2B or 99 (for Andorre).
         - a VigilanceMeteoFranceProxy object (Optional) to manage de communication with the
           Météo France online source.
        """

        # Variables init
        self._alerts_list = {}
        self._department = None
        if vmf_proxy is not None:
            self._viglance_MF_proxy = vmf_proxy
        else:
            self._viglance_MF_proxy = VigilanceMeteoFranceProxy()

        # Check _department variable using the property.
        # Warning the setter launch mise_a_jour_etat() methods.
        self.department = department

    def update_department_status(self):
        """Fetch active weather alerts for the department.

        get the alert color for the 9 different types on the Météo France
        website and update the variable 'alerts_list'.
        """
        self._alerts_list = self._viglance_MF_proxy.get_alert_list(self.department)

    def __repr__(self):
        """"instance representation"""
        # Order the dictionary keys ecause before python 3.6 keys are not
        # ordered
        alerts_list_ordonnee = ""
        for key in sorted(self.alerts_list.keys()):
            alerts_list_ordonnee = alerts_list_ordonnee +\
                                  "'{}': '{}', ".\
                                  format(key, self.alerts_list[key])
        return "ZoneAlerte: \n - departement: '{}'\n - bulletin_date: '{}'"\
               "\n - alerts_list: {{{}}}".format(self._department,
                                                   self.bulletin_date,
                                                   alerts_list_ordonnee[:-2])

    @property
    def department_color(self):
        """Get the department color.

        It's the color of the most critical alert.
        """
        if any(alert == 'Rouge' for alert in self.alerts_list.values()):
            synthesis = 'Rouge'
        elif any(alert == 'Orange' for alert in self.alerts_list.values()):
            synthesis = 'Orange'
        elif any(alert == 'Jaune' for alert in self.alerts_list.values()):
            synthesis = 'Jaune'
        elif all(alert == 'Vert' for alert in self.alerts_list.values()):
            synthesis = 'Vert'
        else:
            # return None if we had issue to get the data
            synthesis = None
        return synthesis

    @property
    def url_pour_en_savoir_plus(self):
        """Get the link to have additional info about alerts in department.

        Return the vigilance.meteofrance.com URL to get additinonal details
        about active alerts in the department.
        """
        return "http://vigilance.meteofrance.com/"\
               "Bulletin_sans.html?a=dept{}&b=1&c=".format(self._department)

    def message_de_synthese(self, msg_format='text'):
        """Get synthesis text message to have the list of the active alerts."""
        if self.department_color == 'Vert':
            if msg_format == 'text':
                message = "Aucune alerte météo en cours."
            elif msg_format == 'html':
                message = "<p>Aucune alerte météo en cours.</p>"
        elif self.department_color is None:
            if msg_format == 'text':
                message = "Impossible de récupérer l'information"
            if msg_format == 'html':
                message = "<p>Impossible de récupérer l'infmation</p>"
        else:
            if msg_format == 'text':
                message = \
                    "Alerte météo {} en cours :".format(self.department_color)
                # Order the dictionary keys ecause before python 3.6 keys are
                # not ordered
                for type_risque in sorted(self.alerts_list.keys()):
                    if self.alerts_list[type_risque] != 'Vert':
                        message = message + "\n - {}: {}"\
                            .format(type_risque, self.alerts_list[type_risque])
            elif msg_format == 'html':
                message = \
                    "<p>Alerte météo {} en cours :"\
                    "</p><ul>".format(self.department_color)
                # Order the dictionary keys ecause before python 3.6 keys are
                # not ordered
                for type_risque in sorted(self.alerts_list.keys()):
                    if self.alerts_list[type_risque] != 'Vert':
                        message = message + "<li>{}: {}</li>"\
                            .format(type_risque, self.alerts_list[type_risque])
                message = message + '</ul>'
        return message

    @property
    def bulletin_date(self):
        """Accessor and setter for Update date"""
        return self._viglance_MF_proxy.bulletin_date

    @property
    def alerts_list(self):
        """Accessor and setter for weather alerts list"""
        return self._alerts_list

    @property
    def department(self):
        """Accessor for area code linked to the weather report"""
        return self._department

    @department.setter
    def department(self, department):
        """Setter with consitency check on the are code value.

        Departemnt variable should be a 2 chararcters string. In the source XML
        file, the 92, 93 and 95 departments do not exist. In this case we have
        to use the 75 department instead.
        This setter will call the mise_a_jour_etat() method systematicaly.
        """
        # Check the valide values for department
        if department not in VALID_DEPARTMENT_LIST:
            raise ValueError("Departement parameter have to be a 2 characters string"
                             "between '01' and '95' or '2A' or '2B' or '99'."
                             "Used value: {}".format(department))

        # Equivalences list
        equivalence75 = ['92', '93', '94']
        validated_department = department

        # Replace, the missing department in the XLM by the equivalence.
        if department in equivalence75:
            validated_department = '75'

        # Set the variable
        self._department = validated_department

        # Call the first update
        self.update_department_status()
