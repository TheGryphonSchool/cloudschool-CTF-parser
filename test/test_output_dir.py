from test_helper import parser, ET, dicttoxml, pytest, mocker, MockerFixture
from datetime import date

@pytest.fixture
def ctf_data() -> dict:
    return { 'Header': {
        'SourceSchool': { 'School Name': 'School', 'URN': 1234 }
        },
        'CTFpupilData': { 'Pupil': { 'SchoolHistory': { 'School': {
                'School Name': 'School',
                'URN': 1234
        } } } }
    }

@pytest.mark.parametrize(
    "correct_dir, year_group, leaving_date, user_asked", [
    ('year 7 folder', 6, '', False),#Y6 -> Y7 folder
    ('CTF_In', 12, '', False),#Other year -> default folder
    ('year 12 folder', 11, '', True),#Y11 with no leaving date -> ask user
    ('year 12 folder', 11, '2020-05-31', True),#Y11 left Sep-May -> ask user
    ('year 12 folder', 11, '2020-09-01', True),#Y11 left Sep-May -> ask user
    ('year 12 folder', 11, '2020-06-01', False),#Y11 left Jun-Aug -> Y12 folder
    ('year 12 folder', 11, '2020-08-31', False),#Y11 left Jun-Aug -> Y12 folder
    ('CTF_In', 0, '2020-05-31', False)#no DOB & no NCyearActual -> default folder
    ]
)
def test_output_dir_correct(mocker: MockerFixture,
                            ctf_data: dict,
                            correct_dir: str,
                            year_group: int,
                            leaving_date: str,
                            user_asked: bool):
    if year_group:
        ctf_data['CTFpupilData']['Pupil']['BasicDetails'] = {
            'NCyearActual': year_group
        }
    if leaving_date:
        ctf_data['CTFpupilData']['Pupil']['LeavingDate'] = leaving_date
    mocker.patch('parse_CTFs.cohort_folder',
                 return_value=f'year {year_group + 1} folder')
    mocked_UI = mocker.patch('parse_CTFs.yes_no_q', return_value=False)
    ctf = ET.fromstring(dicttoxml(ctf_data))
    assert correct_dir == parser.get_output_dir(ctf, 'CTF_In')
    if user_asked:
        mocked_UI.assert_called_once()

@pytest.mark.parametrize(
    "year_group, creation_datetime, dob", [
    (6, '2020-08-31T12:00:00', '2008-09-01'),#Oldest Y6; last day of ac-year
    (7, '2020-08-31T12:00:00', '2008-08-31'),#Youngest Y7; last day of ac-year
    (11, '2020-09-01T12:00:00', '2004-09-01'),#Oldest Y11; 1st day of ac-year
    (12, '2020-09-01T12:00:00', '2004-08-31'),#Youngest Y12; 1st day of ac-year
])
def test_gets_academic_year_from_DOB(ctf_data: dict,
                                     year_group: int,
                                     creation_datetime: str,
                                     dob: str):
    ctf_data['Header']['DateTime'] = creation_datetime
    ctf_data['CTFpupilData']['Pupil']['DOB'] = dob
    ctf = ET.fromstring(dicttoxml(ctf_data))
    assert year_group == parser.ac_year(ctf)

# todo: Year 11s with different leaving dates go to mid-year folder
