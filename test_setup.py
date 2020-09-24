import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pytest # pylint: disable=import-error
import xml.etree.ElementTree as ET
from dicttoxml import dicttoxml # pylint: disable=import-error
import parse_CTFs as parser # pylint: disable=import-error
from unittest import mock
from pytest_mock import mocker, MockerFixture
