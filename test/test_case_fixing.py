import pytest # pylint: disable=import-error
import xml.etree.ElementTree as ET

import parse_CTFs as parser # pylint: disable=import-error

@pytest.fixture
def title_case_nodes_dict() -> dict:
    # Only 3 should be fixed: Forename, PreferredSurname, FormerSurname
    return {
        'Surname': { 'before': 'Surname', 'after': 'Surname' },
        'Forename': { 'before': "D'FORENAME", 'after': "D'Forename" },
        'PreferredSurname': { 'before': 'PREF. SURNAME',
                              'after': 'Pref. Surname' },
        'PreferredForename': { 'before': 'pRefeRred_ForEname',
                               'after': 'pRefeRred_ForEname' },
        'MiddleNames': { 'before': 'middle NAMES', 'after': 'middle NAMES' },
        'FormerSurname': { 'before': 'FORMER-SURNAME',
                           'after': 'Former-Surname' },
        'SchoolName': { 'before': 'name of school', 'after': 'name of school' }
    }

@pytest.fixture
def title_case_nodes(title_case_nodes_dict) -> dict:
    parent = ET.Element('parent')
    parser.add_xml_nodes_from_dict(parent, **before_only(title_case_nodes_dict))
    return parent

def before_only(dict: dict) -> dict:
    return {key:value['before'] for (key, value) in dict.items()}

@pytest.fixture
def ok_nodes():
    return { 'Innocuously': 'nAmEd', 'Child': 'NODES', 'Should': 'be ignored' }


class TestUtilities:
    def test_adds_nodes_from_dict(self, title_case_nodes_dict):
        title_case_nodes = before_only(title_case_nodes_dict)
        parent = ET.Element('parent')
        parser.add_xml_nodes_from_dict(parent, **title_case_nodes)
        for node_name in title_case_nodes:
            assert title_case_nodes[node_name] == parent.findtext(node_name)


class TestCaseFixing:
    def test_finds_no_title_case_nodes(self, ok_nodes):
        parent = ET.Element('parent')
        parser.add_xml_nodes_from_dict(parent, **ok_nodes)
        assert [] == parser.list_suspectly_cased_nodes(parent)

    def test_finds_title_case_nodes(self, title_case_nodes, ok_nodes):
        parser.add_xml_nodes_from_dict(title_case_nodes, **ok_nodes)
        # Add one duplicate to check duplicates are found
        parser.add_xml_nodes_from_dict(title_case_nodes, Surname='2nd_surname')
        assert 8 == len(parser.list_suspectly_cased_nodes(title_case_nodes))
    
    def test_only_fixes_allcaps_nodes(self,
                                      title_case_nodes,
                                      title_case_nodes_dict):
        assert 3 == parser.repair_case_where_appropriate(title_case_nodes)
        for (key, value) in title_case_nodes_dict.items():
            assert value['after'] == title_case_nodes.findtext(key)
