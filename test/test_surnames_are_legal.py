from test_setup import pytest, ET, dicttoxml, parser

CORRECT_SURNAME = 'Rightname'

NON_ERROR_PUPILS = {
    'Constant': { 'Pupil': {
        'Surname': CORRECT_SURNAME,
        'PreferredSurname': CORRECT_SURNAME
    } },
    'Change': { 'Pupil': { 'BasicDetails': {
        'Surname': CORRECT_SURNAME,
        'PreferredSurname': 'Wrongname'
        } } },
    'SurnameMissing': { 'Pupil': { 'BasicDetails': {
        'PreferredSurname': CORRECT_SURNAME
    } } },
    'PreferredSurnameMissing': { 'Pupil': { 'BasicDetails': {
        'Surname': CORRECT_SURNAME
    } } },
    'Irrelevent': { 'Should': 'Ignore' }
}

@pytest.fixture
def surname_test_nodes() -> ET.Element:
    return ET.fromstring(dicttoxml(NON_ERROR_PUPILS))

@pytest.fixture
def pupils_with_surnames_missing() -> ET.Element:
    return ET.fromstring(dicttoxml({
        **NON_ERROR_PUPILS,
        'err1': { 'Pupil': { 'BasicDetails': { 'UPN': 'err1', 'no': 'names' }}},
        'err2': { 'Pupil': { 'BasicDetails': { 'UPN': 'err2', 'no': 'names' }}}
    }))

def test_surnames_are_legal(surname_test_nodes):
    assert 3 == parser.ensure_surnames_are_legal(surname_test_nodes)
    all_surname_nodes = (surname_test_nodes.findall('.//Surname') +
                        surname_test_nodes.findall('.//PreferredSurname'))
    assert 8 == len(all_surname_nodes)
    for node in all_surname_nodes:
        assert node.text == CORRECT_SURNAME

def test_pupils_without_surnames_error(pupils_with_surnames_missing):
    with pytest.raises(ValueError) as error:
        parser.ensure_surnames_are_legal(pupils_with_surnames_missing)
    assert 'err1' in str(error.value)
    assert 'err2' in str(error.value)