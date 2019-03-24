# coding: utf-8
"""tests for vigilance module - VigilanceMeteoFranceProxy Class"""
import datetime
import sys
import pytest

from vigilancemeteo import VigilanceMeteoFranceProxy

@pytest.yield_fixture()
def fix_local_data():
    """Fixture to replace webiste answer by a local one."""
    # Using local answer instead of MeteoFrance website
    xml_init_value = VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML
    checksum_init_value = VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_CHECKSUM

    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML = "./tests/NXFR33_LFPW_.xml"
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_CHECKSUM = "./tests/vigilance_controle.txt"
    yield None

    # Set back the initial value(using website instead of local answer)
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_XML = xml_init_value
    VigilanceMeteoFranceProxy.URL_VIGILANCE_METEO_CHECKSUM = checksum_init_value


def test_basic():
    """Basic test."""
    client = VigilanceMeteoFranceProxy()

    client.update_data()

    assert(client.xml_tree is not None)

def test_bulletin_date(fix_local_data):
    """Test bulletin date"""
    client = VigilanceMeteoFranceProxy()
    client.update_data()

    assert(client.bulletin_date.isoformat() == "2018-03-18T16:00:00+01:00")
    