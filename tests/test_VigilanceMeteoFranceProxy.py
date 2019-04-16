# coding: utf-8
"""tests for vigilance module - VigilanceMeteoFranceProxy Class"""
import datetime
import sys

import pytest

from vigilancemeteo import VigilanceMeteoError, VigilanceMeteoFranceProxy
from vigilancemeteo.constants import (UPDATE_STATUS_CHECKSUM_CACHED_60S,
                                      UPDATE_STATUS_CHECKSUM_UPDATED,
                                      UPDATE_STATUS_ERROR_AND_BULLETIN_EXPIRED,
                                      UPDATE_STATUS_ERROR_BUT_PREVIOUS_BULLETIN_VALID,
                                      UPDATE_STATUS_SAME_CHECKSUM,
                                      UPDATE_STATUS_XML_UPDATED)


@pytest.yield_fixture()
def fix_local_data():
    """Fixture to replace webiste answer by a local one."""
    # Using local answer instead of MeteoFrance website
    xml_init_value = VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML
    checksum_init_value = VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_CHECKSUM

    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML = "./tests/NXFR33_LFPW_.xml"
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_CHECKSUM = (
        "file:./tests/vigilance_controle.txt"
    )
    yield None

    # Set back the initial value(using website instead of local answer)
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML = xml_init_value
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_CHECKSUM = checksum_init_value


def test_basic():
    """Basic test."""
    client = VigilanceMeteoFranceProxy()

    # first update
    client.update_data()
    test_status_1 = client.status == UPDATE_STATUS_XML_UPDATED

    # second update should do nothing as less than 60 secondes after first update
    client.update_data()
    test_status_2 = client.status == UPDATE_STATUS_CHECKSUM_CACHED_60S

    # simulation 2 minutes wait
    client._latest_check_date = client._latest_check_date - datetime.timedelta(
        seconds=120
    )
    client.update_data()
    test_status_3 = client.status == UPDATE_STATUS_SAME_CHECKSUM
    test_xml_tree = client.xml_tree is not None

    assert (test_status_1, test_status_2, test_status_3, test_xml_tree) == (
        True,
        True,
        True,
        True,
    )


def test_bulletin_date(fix_local_data):
    """Test bulletin date property."""
    client = VigilanceMeteoFranceProxy()
    client.update_data()

    assert client.bulletin_date.isoformat() == "2018-03-18T16:00:00+01:00"


def test_checksum(fix_local_data):
    """Test checksum property."""
    client = VigilanceMeteoFranceProxy()
    client.update_data()

    assert client.checksum == "1751354976"


def test_checksum_unreachable_and_bulletin_valid():
    """Test behaviour when checksum URL unreachable"""
    # First update OK
    client = VigilanceMeteoFranceProxy()
    client.update_data()
    first_checksum = client.checksum

    # fake the cheksum file to simulate unreachable file
    client.URL_VIGILANCE_METEO_CHECKSUM = "file:./tests/fake_file.txt"

    # simulate 2 minutes wait
    client._latest_check_date = client._latest_check_date - datetime.timedelta(
        seconds=120
    )
    client.update_data()

    # Should be no error and the value of the first update checksum
    assert (client.checksum, client.status) == (
        first_checksum,
        UPDATE_STATUS_ERROR_BUT_PREVIOUS_BULLETIN_VALID,
    )


def test_xml_unreachable_and_bulletin_valid():
    """Test behaviour when checksum URL unreachable"""
    # First update OK
    client = VigilanceMeteoFranceProxy()
    client.update_data()
    first_xml_tree = client.xml_tree

    # fake the cheksum file to simulate new checksum file
    client.URL_VIGILANCE_METEO_CHECKSUM = "file:./tests/vigilance_controle_2.txt"

    # fake the xml file to simulate unreachable xml file
    client.URL_VIGILANCE_METEO_XML = "./tests/fake_xml.xml"

    # simulate 2 minutes wait
    client._latest_check_date = client._latest_check_date - datetime.timedelta(
        seconds=120
    )
    client.update_data()

    # Should be no error and the value of the first update checksum
    assert (client.xml_tree, client.status) == (
        first_xml_tree,
        UPDATE_STATUS_ERROR_BUT_PREVIOUS_BULLETIN_VALID,
    )


def test_checksum_unreachable_and_bulletin_expired(fix_local_data):
    """Test checksum behaviour in case of error."""
    # First update is OK
    client = VigilanceMeteoFranceProxy()
    client.update_data()

    # fake the cheksum file to simulate unreachable file
    client.URL_VIGILANCE_METEO_CHECKSUM = "file:./tests/fake_file.txt"

    # fake the date of bulletin. Make it exipred
    client._bulletin_date = client._bulletin_date - datetime.timedelta(days=2)

    # simulate 2 minutes wait
    client._latest_check_date = client._latest_check_date - datetime.timedelta(
        seconds=120
    )

    # should raise an error
    with pytest.raises(VigilanceMeteoError):
        client.update_data()


def test_xml_unreachable_and_bulletin_expired(fix_local_data):
    """Test checksum behaviour in case of error."""
    # First update is OK
    client = VigilanceMeteoFranceProxy()
    client.update_data()

    # fake the cheksum file to simulate new checksum file
    client.URL_VIGILANCE_METEO_CHECKSUM = "file:./tests/vigilance_controle_2.txt"

    # fake the xml file to simulate unreachable xml file
    client.URL_VIGILANCE_METEO_XML = "./tests/fake_xml.xml"

    # fake the date of bulletin. Make it exipred
    client._bulletin_date = client._bulletin_date - datetime.timedelta(days=2)

    # simulate 2 minutes wait
    client._latest_check_date = client._latest_check_date - datetime.timedelta(
        seconds=120
    )

    # should raise an error
    with pytest.raises(VigilanceMeteoError):
        client.update_data()


def test_first_try_checksum_unreachable(fix_local_data):
    """Test behaviour when first checksum is unvailable."""
    client = VigilanceMeteoFranceProxy()

    # fake the cheksum file to simulate unreachable file
    client.URL_VIGILANCE_METEO_CHECKSUM = "file:./tests/fake_file.txt"

    # should raise an error
    with pytest.raises(VigilanceMeteoError):
        client.update_data()


def test_first_try_xml_unreachable(fix_local_data):
    """Test behaviour when first checksum is unvailable."""
    client = VigilanceMeteoFranceProxy()

    # fake the cheksum file to simulate unreachable file
    client.URL_VIGILANCE_METEO_XML = "./tests/fake_xml.xml"

    # should raise an error
    with pytest.raises(VigilanceMeteoError):
        client.update_data()
