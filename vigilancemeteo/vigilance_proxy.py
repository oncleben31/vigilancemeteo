# coding: utf-8
"""class to communicate Météofrance weather alerts website"""
import sys
import re
from datetime import datetime
from lxml import etree
from pytz import timezone
from vigilancemeteo.constants import ALERT_COLOR_LIST, VALID_DEPARTMENT_LIST, ALERT_TYPE_LIST, COASTAL_DEPARTMENT_LIST

# Manage differences beetween python 2.7 and 3.6
if sys.version_info < (3, 0):
    from urllib2 import urlopen #pylint: disable=import-error
else:
    from urllib.request import urlopen

# TODO: review all docstring

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
        current_checksum = self._get_new_checksum()
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
        for alert_type in ALERT_TYPE_LIST:
            alerts_list[alert_type] = 'Vert'

        # Get the active alerts for the specific department
        department_alerts = self.xml_tree.xpath("/CV/DV[attribute::dep='"
                                                + department + "']")

        # Get the additional active alerts if it is a coastal department
        if department in COASTAL_DEPARTMENT_LIST:
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
                alerts_list[ALERT_TYPE_LIST[alert_type - 1]]\
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
