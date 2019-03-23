# coding: utf-8
"""tests for vigilance module - VigilanceMeteoFranceProxy Class"""
import datetime
import sys
import pytest

from vigilancemeteo import VigilanceMeteoFranceProxy

def test_basic():
    """Basic test."""
    client = VigilanceMeteoFranceProxy()

    client.update_data()

    assert(client.xml_tree is not None)
