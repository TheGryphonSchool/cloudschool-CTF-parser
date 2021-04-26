import re
import os
import json
import traceback

from tkinter import Tk, filedialog
import xml.etree.ElementTree as ET
from datetime import date


def process_ctf(ctf_path: str) -> bool:
    """Parse the XML tree, call patching methods and write repaired CTF

    Tries to open CTF file presumend to be at passed path. Checks whether CTF
    is complete and asks the user whether they want to abort if not.
    Finds the appropriate location and writes a new, fixed CTF there. The
    original is unchanged, but renamed
    Delegates:
    Removing any optional nodes that are empty
    Making proper names proper case

    Args:
        ctf_path: The full path of the CTF file to be processed

    Returns:
        A Boolean indicating whether the process was successful (Explicit
        abortion by the user is still considered unsuccessful).
    """

    print('Parsing', ctf_path.rsplit('/', 1)[-1], '...')

    try:
        # Prepare XML tree
        tree = ET.parse(ctf_path)
        root_node = tree.getroot()
        source_name = source_school(root_node)

        if is_data_missing(root_node) and yes_no_q("Do you want to abort?"):
            return False

        fixed_cases = repair_case_where_appropriate(root_node)

        fixed_empties = trim_empty_nodes(root_node, source_name)

        fixed_phone_numbers = remove_spaces_from_phone_numbers(root_node)

        fixed_surnames = ensure_surnames_are_legal(root_node)
    except Exception as _e:
        traceback.print_exc()

    # Write the new file, rename the original and tell the user what's happened
    try:
        escpd_src_name = escape_source_school(source_name)
        output_path = determine_output_path(ctf_path, escpd_src_name, root_node)
        tree.write(output_path, encoding='UTF-8', xml_declaration=True)
        if fixed_cases > 0:
            print(f"Case fixed for {fixed_cases} name{plural(fixed_cases)}")
        if fixed_empties > 0:
            print(f"Trimmed {fixed_empties} empty field{plural(fixed_empties)}")
        if fixed_phone_numbers > 0:
            print(f"Removed whitespace from {fixed_phone_numbers}" +
                  f" phone number{plural(fixed_phone_numbers)}")
        if fixed_surnames > 0:
            s = plural(fixed_surnames)
            print(f"Replaced {fixed_surnames} surname{s} with legal surname{s}")
        print('Output to:', output_path, '\n')
        os.rename(ctf_path,
                  ctf_path.replace('.', f'_{escpd_src_name}_original.'))
        return True
    except ValueError as err:
        print('CTF parsing error:', err, '\n')
        return False


def is_data_missing(root_node: ET.Element) -> bool:
    """Checks whether a XML tree claims to be a `full` CTF file

    Args:
        root_node: XML Element, expected to be the root of a CTF file

    Returns:
        False if a DocumentQualifier node is found with value `full`, else True
    """

    doc_qual = root_node.findtext('.//DocumentQualifier')
    if doc_qual is None:
        print("File is missing its DocumentQualifier tag; import will"
              " likely fail.")
        return True

    if doc_qual == 'full':
        return False

    if doc_qual == 'partial':
        print("File's DocumentQualifier tag is 'partial'. This means it is "
              "probably missing contact data.")
        return True

    print("File's DocumentQualifier tag is non-standard; import will likely "
          "fail.")
    return True


def yes_no_q(question: str) -> bool:
    """Asks user a yes/no question 3 times, assumes no on 3rd failure

    Args:
        question: A yes/no question to put to the user. Do not include options;
            '(y/n)' will be appended to the question automatically
    Returns:
        Boolean representing the user's choice, or False if they fail 3 times
        to answer with a 'y' or 'no'.
    """

    yes_regex = re.compile('[yY]')
    no_regex = re.compile('[nN]')
    attempts = 0
    while True:
        user_choice = input(f'{question} (y/n)\n')
        if yes_regex.search(user_choice) or attempts > 3:
            return True

        if no_regex.search(user_choice):
            return False


def repair_case_where_appropriate(parent_node: ET.Element) -> int:
    """Title case any upper-case names under the passed node

    Args:
        parent_node: An XML node that may contain child-nodes containing
            proper names
    Returns:
        Integer count of the number of nodes whose case has been fixed
    """

    fixed_cnt = 0
    for name_node in list_suspectly_cased_nodes(parent_node):
        name = name_node.text
        if name is not None and re.match(r'[A-Z\.\'\-\s]+$', name):
            name_node.text = name.title()
            fixed_cnt += 1
    return fixed_cnt


def list_suspectly_cased_nodes(parent_node: ET.Element) -> list:
    """Returns list of child nodes containing proper names

    Args:
        parent_node: An XML node that may contain child-nodes containing
            proper names
    Returns:
        List of all nodes containing proper names
    """

    name_nodes = []
    for tag in ['Surname', 'Forename', 'PreferredSurname', 'PreferredForename',
                'MiddleNames', 'FormerSurname', 'SchoolName']:
        name_nodes += parent_node.findall('.//' + tag)
    return name_nodes


def remove_spaces_from_phone_numbers(xml_tree: ET.Element) -> int:
    """Removes all padding and internal spaces from nodes named 'PhoneNo'

    Args:
        xml_tree: An XML node that may have children with 'PhoneNo' tags
    Returns:
        count of the phone numbers with spaces in that have been removed
    """
    fix_count = 0
    for phone_node in xml_tree.findall('.//PhoneNo'):
        if phone_node.text.find(' ') >= 0:
            fix_count += 1
            phone_node.text = phone_node.text.replace(' ', '')
    return fix_count


def ensure_surnames_are_legal(tree: ET.Element) -> int:
    """Overwrites PreferredSurname nodes with Surnames if they differ

    During import, progresso maps Surname nodes to the Legal Surname field,
    and PreferredSurname nodes to the Surname field. Some schools may not like
    this behaviour and prefer to use the Surname node value for everything.
    If a Pupil record is missing the Surname or PreferredSurname node, this
    function creates it by copying the value from the present node.
    Args:
        tree: An XML node whose descendents may include Surname and/or
            PreferredSurname nodes
    Returns:
        Integer count of the number of nodes updated or created
    Raises:
        ValueError if any students don't have surnames. The MIS will not accept
            the CTF if this is the case.
    """

    fix_count = 0
    nameless_UPNs = []
    all_pupils = tree.findall('.//Pupil')
    fix_count = len(all_pupils)
    if not fix_count:
        return 0
    for pupil_node in all_pupils:
        surname_node = pupil_node.find('Surname')
        pref_surname_node = pupil_node.find('./BasicDetails/PreferredSurname')
        if surname_node is not None and pref_surname_node is not None:
            if surname_node.text != pref_surname_node.text:
                pref_surname_node.text = surname_node.text
            else:
                fix_count -= 1
        elif surname_node is not None:
            pref_surname_node = ET.SubElement(pupil_node.find('BasicDetails'),
                                              'PreferredSurname')
            pref_surname_node.text = surname_node.text
        elif pref_surname_node is not None:
            surname_node = ET.SubElement(pupil_node, 'Surname')
            surname_node.text = pref_surname_node.text
        else:
            # Neither Surname nor Preferred Surname found -> error
            upn_node = pupil_node.find('.//UPN')
            upn = 'UPN-missing' if upn_node is None else upn_node.text
            nameless_UPNs.append(upn)
    if len(nameless_UPNs) > 0:
        raise ValueError('Students with these UPNs have no surnames: ' +
                         f"{', '.join(nameless_UPNs)}. This CTF is invalid.")
    return fix_count


def trim_empty_nodes(parent_node: ET.Element, source_name: str) -> int:
    """Remove any empty LeavingDate and RemovalGrounds nodes

    Each learner MAY have the source school as a School node under their
    SchoolHistory node. And these nodes MAY have LeavingDate and RemovalGrounds
    child nodes, but if they're blank Progresso gets upset. So we look for
    blanks and delete them.
    Args:
        parent_node: An XML node that may contain child-nodes containing
            people's names
        source_name: String representing the name (not path) of the XML file
    Returns:
        Integer count of the number of nodes trimmed
    """

    fixed_cnt = 0
    for source_in_hist in source_school_appearances_in_history(parent_node,
                                                               source_name):
        for tag in ['LeavingDate', 'RemovalGrounds']:
            bad_node = source_in_hist.find(tag)
            if bad_node and bad_node.text is None:
                source_in_hist.remove(bad_node)
                fixed_cnt += 1
    return fixed_cnt


def determine_output_path(input_path: str,
                          source_name: str,
                          root_node: ET.Element) -> str:
    """Returns string of the relative path of the output file"""
    output_name = (input_path.rsplit('/', 1)[-1]
                   .replace('.', f'_{source_name}.'))
    output_dir = os.path.join((config_parent_dir() or 'T:/CMIS/CTF Files/'),
                              get_output_dir(root_node))
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, output_name)


def config_parent_dir() -> str:
    try:
        full_path = os.path.join(os.path.dirname(__file__),
                                 'CTF_parser_config.json')
        with open(full_path) as config_file:
            config = json.load(config_file)
            return config['destinationParentDir']
    except (FileNotFoundError, KeyError):
        return ''


def get_output_dir(root: ET.Element, default_dir: str = 'CTF_In') -> str:
    """Finds the name of the appropriate folder to store the outputted CTF in

    If the first student with a specified year is in year 6, returns the
    new-cohort folder for this year, otherwise returns in-year folder: 'CTF_In'
    Falls back on calculating a student's year if all year tags are missing.
    """

    year_group = root.find('.//NCyearActual')
    year_group = ac_year(root) if year_group is None else int(year_group.text)
    if year_group == 6:
        return cohort_folder(7)
    if year_group == 11 and not are_joining_mid_year(root):
        return cohort_folder(12)
    return default_dir


def ac_year(root_node: ET.Element) -> int:
    """Returns the academic year of the first student under the passed node

    Raises:
        ValueError if any students don't have DOBs. The MIS will not accept the
            CTF if this is the case.
    """

    dob_node = root_node.find('.//Pupil/DOB')
    if dob_node is None:
        # returning 0 will mean the CTF is placed in the default output dir
        return 0
    dob = date.fromisoformat(dob_node.text)
    year_started_school = dob.year + (4 if dob.month < 9 else 5)
    ctf_date = ctf_creation_date(root_node)
    ac_start_year = ctf_date.year - (1 if ctf_date.month < 9 else 0)
    return ac_start_year - year_started_school


def are_joining_mid_year(root: ET.Element) -> bool:
    """Return True if students are joining this academic year (not next year)

    This need only be called for year 11s - the only ambiguous case.
    """

    # List the nodes where the source school appears in a pupil's school history
    source_in_hists = source_school_appearances_in_history(root,
                                                           source_school(root))
    if len(source_in_hists) > 0:
        leaving_date_node = source_in_hists[0].find('.//LeavingDate')
        if leaving_date_node is not None:
            leaving_date = leaving_date_node.text
            # Assume next cohort if LeavingDates are after May & before Sep
            if date.fromisoformat(leaving_date).month % 9 > 5:
                return False
            if len(source_in_hists) > 1:
                # Assume mid-year if any students' LeavingDates differ
                for source_in_hist in source_in_hists:
                    this_l_d = source_in_hist.find('LeavingDate')
                    if this_l_d is not None and this_l_d.text != leaving_date:
                        return True
    # Otherwise, ask
    return yes_no_q("Are these students joining MID-YEAR?")


def source_school_appearances_in_history(root_node: ET.Element,
                                         source_name: str) -> list:
    """List source school appearances in students' school histories"""
    return root_node.findall(
        # use " over ' in Xpath predicate because some school names include '
        f".//SchoolHistory/School/[SchoolName=\"{source_name}\"]")


def cohort_folder(year_group: int) -> str:
    """The path of the dir containing the CTFs for the next yr 7 or 12 cohort

    Args:
        year_group: Expected to be 7 or 12
    Returns:
        Fullpath (as String) of the directory conventionally containing CTFs for
        the incoming cohort of year 7s or 12s."""

    return f'CTF_Year{year_group:02}_{escpd_next_ac_year()}'


def escpd_next_ac_year() -> str:
    """eg Aug '19 and Sep '19 give 2019_2020, but Oct '19 gives 2020_2021

    Desirable because occasionally we get CTFs in September for members of new
    cohort who already started that month.
    """

    d = date.today()
    year = d.year
    return f'{year}_{year + 1}' if d.month < 10 else f'{year + 1}_{year + 2}'


def source_school(root_node: ET.Element) -> str:
    node = root_node.find(".//SourceSchool//SchoolName")
    return '' if node is None else node.text


def escape_source_school(source_school: str) -> str:
    return source_school.casefold().replace(' ', '_').replace('.', '')


def plural(count: int) -> str:
    return 's' if count > 1 else ''


def ctf_creation_date(root_node: ET.Element) -> date:
    datetime = root_node.find('.//DateTime').text
    return date.fromisoformat(datetime[0:datetime.find('T')])


if __name__ == '__main__':
    root = Tk()
    root.withdraw()
    ctf_s = filedialog.askopenfilenames(initialdir="..",
                                        title="Select CTFs",
                                        filetypes=(("xml files", "*.xml"),))
    if len(ctf_s) == 0:
        print("CTF parsing aborted")
    else:
        # Process each CTF, collecting a record of successes and failures
        outcomes = list(map(process_ctf, ctf_s))
        good_count = outcomes.count(True)
        out_count = len(outcomes)
        bad_count = out_count - good_count
        if good_count == out_count:
            print(f"All ({out_count}) files processed successfully")
        else:
            if good_count > 0:
                print(
                    f'{good_count} file{plural(good_count)} processed successfully.')
                all = ''
            else:
                all = 'all ' if out_count > 1 else 'the '
            print(
                f'Parsing FAILED for {all}{bad_count} file{plural(bad_count)}.')
    input('Press Enter to Exit... ')
