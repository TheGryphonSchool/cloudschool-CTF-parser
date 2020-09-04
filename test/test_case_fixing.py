from test_helper import pytest, ET, dicttoxml, parser

OTHER_DICT = {
    'Innocuously': 'nAmEd', 'Child': 'NODES', 'Should': { 'be': 'ignored' }
}

# Only 4 should be fixed:
#   Forename, PreferredSurname, FormerSurname & nested SchoolName
BEFORE = {
    'Surname': 'Surname',
    'Forename': "D'FORENAME",
    'PreferredSurname': 'PREF. SURNAME',
    'PreferredForename': 'pRefeRred_ForEname',
    'MiddleNames': 'middle NAMES',
    'FormerSurname': 'FORMER-SURNAME',
    'SchoolName': 'name of school',
    'nested': { 'SchoolName': 'NESTED SCHOOL NAME' }
}
AFTER = {
    'Surname': 'Surname',
    'Forename': "D'Forename",
    'PreferredSurname': 'Pref. Surname',
    'PreferredForename': 'pRefeRred_ForEname',
    'MiddleNames': 'middle NAMES',
    'FormerSurname': 'Former-Surname',
    'SchoolName': 'name of school',
    'nested': { 'SchoolName': 'Nested School Name' }
}

@pytest.fixture
def other_nodes() -> ET.Element:
    return ET.fromstring(dicttoxml(OTHER_DICT))

@pytest.fixture
def case_change_and_other_nodes() -> ET.Element:
    return ET.fromstring(dicttoxml({ **BEFORE, **OTHER_DICT }))

def test_finds_no_case_change_nodes(other_nodes: ET.Element):
    assert [] == parser.list_suspectly_cased_nodes(other_nodes)

def test_finds_case_change_nodes(case_change_and_other_nodes: ET.Element):
    assert 8 == len(parser.list_suspectly_cased_nodes(
        case_change_and_other_nodes
    ))

def test_only_fixes_allcaps_nodes(case_change_and_other_nodes: ET.Element):
    assert 4 == parser.repair_case_where_appropriate(
        case_change_and_other_nodes
    )
    for (key, value) in AFTER.items():
        if key == 'nested':
            (key, value) = list(value.items())[0]
            key = f"*/{key}"
        assert value == case_change_and_other_nodes.findtext(key)
