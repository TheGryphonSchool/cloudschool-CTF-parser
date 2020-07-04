import pytest # pylint: disable=import-error
import xml.etree.ElementTree as ET

from dicttoxml import dicttoxml # pylint: disable=import-error

import parse_CTFs as parser # pylint: disable=import-error

CORRECT_NUMBER = '07835979025'

@pytest.fixture
def phone_test_nodes() -> ET.Element:
    return ET.fromstring(dicttoxml({
        'no-spaces': { 'PhoneNo': CORRECT_NUMBER },
        'one-space': { 'PhoneNo': '07835 979025' },
        'leading-space': { 'PhoneNo': ' 07835979025' },
        'trailing-space': { 'PhoneNo': '07835979025 ' },
        'many-spaces': { 'PhoneNo': ' 0783 5979 025 '},
        'Innocuously': 'nAmEd',
        'Child': 'NODES',
        'Should': { 'be': 'ignored' }
        }))

def test_fixes_phone_number_nodes(phone_test_nodes):
    assert 4 == parser.remove_spaces_from_phone_numbers(phone_test_nodes)
    for node in phone_test_nodes.findall('.//PhoneNo'):
        assert node.text == CORRECT_NUMBER