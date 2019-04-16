# coding: utf-8
"""Implement a class to communicate with Météofrance weather alerts website."""
import re
import sys
from datetime import datetime

from lxml import etree
from pytz import timezone

from vigilancemeteo.constants import (
    ALERT_COLOR_LIST,
    ALERT_TYPE_LIST,
    COASTAL_DEPARTMENT_LIST,
    UPDATE_STATUS_CHECKSUM_CACHED_60S,
    UPDATE_STATUS_CHECKSUM_UPDATED,
    UPDATE_STATUS_ERROR_AND_BULLETIN_EXPIRED,
    UPDATE_STATUS_ERROR_BUT_PREVIOUS_BULLETIN_VALID,
    UPDATE_STATUS_SAME_CHECKSUM,
    UPDATE_STATUS_XML_UPDATED,
    VALID_DEPARTMENT_LIST,
)

# Manage differences beetween python 2.7 and 3.6
if sys.version_info < (3, 0):
    from urllib2 import urlopen, URLError  # pylint: disable=import-error
else:
    from urllib.request import urlopen, URLError


class VigilanceMeteoError(Exception):
    """Error class, used when fetching or parsing vigilance.meteofrance.com website."""


class VigilanceMeteoFranceProxy(object):
    """Class to manage the download of the data sources from MeteoFrance website.
    
    Data are fetch on vigilance.meteofrance.com website.
    
    Public attributes:
    - xml_tree = XML representation of the weather alert bulletin
    - bulletin_date = Date of the bulletin (with timezone)
    - checksum = Checksum of the weather alert bulletin
    - status = current status of the proxy (possible value in constant.py)

    Public Methods:
    - update_date(): Check if new information are available and download them if any.
    - get_alert_list(department): of a given department return the list of the alerts.
 
    Private attributes:
    - _xml_tree = XML representation of the weather alert bulletin
    - _bulletin_date = Date of the bulletin (with timezone)
    - _latest_check_date = Date of the latest check if new bulletin is available
    - _latest_checksum_value = Checksum of the weather alert bulletin
    """

    # URL used to fetch data on Météo France website.
    URL_VIGILANCE_METEO_XML = (
        "http://vigilance.meteofrance.com" "/data/NXFR33_LFPW_.xml"
    )
    # URL_VIGILANCE_METEO_XML = "./tests/NXFR33_LFPW_.xml" #for local tests.

    # URL used to check if there were any updates since last check
    URL_VIGILANCE_METEO_CHECKSUM = (
        "http://vigilance.meteofrance.com" "/data/vigilance_controle.txt"
    )
    # URL_VIGILANCE_METEO_CHECKSUM = "./tests/vigilance_controle.txt" #for local tests

    def __init__(self):
        """Class instance constructor."""
        self._xml_tree = None
        self._latest_check_date = None
        self._latest_checksum_value = None
        self._bulletin_date = None
        self._proxy_status = None

    def _get_new_checksum(self):
        """Return the checksum of the data source on MétéoFrance website.
        
        The checksum allows high frequency requests and downloads data only if 
        new information are published.
        If the data source is unvailabe, return the previous checksum if bulletin
        validity date is still not reached. If the bulletin has expired, raise
        an VigilanceMeteoError error."""
        # download checksum if not yet done or done since 60 secondes
        if (self._latest_check_date is None) or (
            datetime.now() - self._latest_check_date
        ).total_seconds() > 60:

            # get checksum in vigilance_controle.txt
            try:
                text = urlopen(self.URL_VIGILANCE_METEO_CHECKSUM).read().decode("utf-8")
            except URLError:
                # Didn't succeed to download the cheksum file
                if (
                    self.bulletin_date is not None
                    and (
                        timezone("UTC").localize(datetime.utcnow()) - self.bulletin_date
                    ).days
                    < 1
                ):
                    # If the bulletin is old of less than 24 hours. It's OK to keep it.
                    self._proxy_status = UPDATE_STATUS_ERROR_BUT_PREVIOUS_BULLETIN_VALID
                    return self._latest_checksum_value
                else:
                    self._proxy_status = UPDATE_STATUS_ERROR_AND_BULLETIN_EXPIRED
                    raise VigilanceMeteoError(
                        "Error: 'vigilance_controle.txt' unreachable and weather alert bulletin has expired"
                    )
            else:
                # Update latest check date.
                self._latest_check_date = datetime.now()

                # Return checksum
                checksum = re.search(r"\n(.+?)\s", text)
                self._proxy_status = UPDATE_STATUS_CHECKSUM_UPDATED
                return checksum.group(1)

        else:
            # No need to check so return previous value
            self._proxy_status = UPDATE_STATUS_CHECKSUM_CACHED_60S
            return self._latest_checksum_value

    def update_data(self):
        """Downloads an updates of the XML data source only if needed.
        
        The methods checks before if the checksum has changed on the website. If
        yes, XML data source is updated.
        """
        # Download only if the checksum have change since latest update.
        current_checksum = self._get_new_checksum()
        if current_checksum != self._latest_checksum_value:
            # Save the new checksum
            # TODO: how to secure concurrent update request between checksum updated and XML downloaded
            # Perhaps with a status to say data is ready.
            self._latest_checksum_value = current_checksum

            # Save the new xml source
            try:
                self._xml_tree = etree.parse(
                    self.URL_VIGILANCE_METEO_XML
                )  # pylint disable=c-extension-no-member
            except (OSError, IOError):
                # Didn't succeed to download the xml file
                if (
                    self.bulletin_date is not None
                    and (
                        timezone("UTC").localize(datetime.utcnow()) - self.bulletin_date
                    ).days
                    < 1
                ):
                    # If the bulletin is old of less than 24 hours, it's OK to keep it.
                    self._proxy_status = UPDATE_STATUS_ERROR_BUT_PREVIOUS_BULLETIN_VALID
                else:
                    # If the bulletin is older than 24 hours, it raises an Error
                    self._proxy_status = UPDATE_STATUS_ERROR_AND_BULLETIN_EXPIRED
                    # Delete lasest check date to be sure every other future call
                    # won't use the cached data
                    self._latest_check_date = None
                    raise VigilanceMeteoError(
                        "Error: 'NXFR33_LFPX_.xml' unreachable and weather alert bulletin has expired"
                    )
            else:
                # Get the weather bulletin date & time
                string_date = self._xml_tree.xpath("/CV/EV")[0].get("dateinsert")

                # Convert the string in date and time with Europe/Paris timezone
                annee = int(string_date[0:4])
                mois = int(string_date[4:6])
                jour = int(string_date[6:8])
                heure = int(string_date[8:10])
                minute = int(string_date[10:12])
                seconde = int(string_date[12:14])
                paris_timezone = timezone("Europe/Paris")
                self._bulletin_date = paris_timezone.localize(
                    datetime(annee, mois, jour, heure, minute, seconde)
                )
                self._proxy_status = UPDATE_STATUS_XML_UPDATED
        elif self._proxy_status == UPDATE_STATUS_CHECKSUM_UPDATED:
            self._proxy_status = UPDATE_STATUS_SAME_CHECKSUM

    def get_alert_list(self, department):
        """Return the list and status of the alerts for a given department.
        
        For all alert types, a status (Vert, Jaune, Orange, Rouge) is returned.
        """

        # update data
        self.update_data()

        # Set initial value for each alert type in the list
        alerts_list = {}
        for alert_type in ALERT_TYPE_LIST:
            alerts_list[alert_type] = "Vert"

        # Get the active alerts for the specific department
        department_alerts = self.xml_tree.xpath(
            "/CV/DV[attribute::dep='" + department + "']"
        )

        # Get the additional active alerts if it is a coastal department
        if department in COASTAL_DEPARTMENT_LIST:
            department_alerts.extend(
                self.xml_tree.xpath("/CV/DV[attribute::dep='" + department + "10']")
            )

        # Identify each active alert and the color associated (criticity).
        # They are grouped by color
        for alerts_group in department_alerts:
            # Get the color of the alert group
            color = int(alerts_group.get("coul"))

            # Get all the active alerts in the group
            for active_alert in list(alerts_group):
                alert_type = int(active_alert.get("val"))
                # Update the instance variable with the alert list
                alerts_list[ALERT_TYPE_LIST[alert_type - 1]] = ALERT_COLOR_LIST[
                    color - 1
                ]

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

    @property
    def status(self):
        """ Getter for _proxy_status"""
        return self._proxy_status
