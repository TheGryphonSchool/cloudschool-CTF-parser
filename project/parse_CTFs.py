def process_ctf(ctf_path):
    """Parse the XML tree, call patching methods and write repaired CTF"""
    import traceback

    print('Parsing', ctf_path.rsplit('/', 1)[-1], '...')
    
    try:
        # Prepare XML tree
        tree = ET.parse(ctf_path)
        root_node = tree.getroot()
        source_name = source_school(root_node)
        
        if is_data_missing(root_node) and yes_no_q("Do you want to abort?"):
            return False

        fixed_case_cnt = repair_case_where_appropriate(root_node)

        fixed_empty_cnt = trim_empty_nodes(root_node, source_name)
    except Exception as _e:
        traceback.print_exc()
        

    # Write the new file, rename the original and tell the user what's happened
    try:
        escpd_src_name = escape_source_school(source_name)
        output_path = determine_output_path(ctf_path, escpd_src_name, root_node)
        tree.write(output_path)
        if fixed_case_cnt > 0:
            print(f"Case fixed for {fixed_case_cnt} name{plural(fixed_case_cnt)}")
        if fixed_empty_cnt > 0:
            print(f"Trimmed {fixed_empty_cnt} empty field{plural(fixed_empty_cnt)}")
        print('Output to:', output_path, '\n')
        os.rename(ctf_path,
                  ctf_path.replace('.', f'_{escpd_src_name}_original.'))
        return True
    except NameError as err:
        print('CTF parsing error:', err, '\n')
        return False

def is_data_missing(root_node):
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

def yes_no_q(question):
    yes_regex = re.compile('[yY]')
    no_regex = re.compile('[nN]')
    attempts = 0
    while True:
        user_choice = input(f'{question} (y/n)\n')
        if yes_regex.search(user_choice) or attempts > 3:
            return True

        if no_regex.search(user_choice):
            return False

def repair_case_where_appropriate(parent_node):
    """Title case any upper-case names under the passed node

    Return count of fixes.
    """
    fixed_cnt = 0
    for name_node in list_suspectly_cased_nodes(parent_node):
        name = name_node.text
        if name is not None and re.match(r'[A-Z\.\'\-\s]+$', name):
            name_node.text = name.title()
            fixed_cnt += 1
    return fixed_cnt

def list_suspectly_cased_nodes(parent_node):
    """Returns a list of all nodes that are sometimes incorrectly upper-cased"""
    name_nodes = []
    for tag in ['Surname', 'Forename', 'PreferredSurname', 'PreferredForename',
                'MiddleNames', 'FormerSurname', 'SchoolName']:
        name_nodes += parent_node.findall('.//' + tag)
    return name_nodes

def trim_empty_nodes(parent_node, source_name):
    """Remove any empty LeavingDate and RemovalGrounds nodes

    Each learner MAY have the source school as a School node under SchoolHistory.
    These nodes MAY have LeavingDate and RemovalGrounds child nodes, but if
    they're blank Progresso gets upset. So we look for blanks and delete them. 
    """
    fixed_cnt = 0
    for source_in_hist in source_as_previouses(parent_node, source_name):
        for tag in ['LeavingDate', 'RemovalGrounds']:
            bad_node = source_in_hist.find(tag)
            if bad_node and bad_node.text is None:
                source_in_hist.remove(bad_node)
                fixed_cnt += 1
    return fixed_cnt

def source_as_previouses(root_node, source_name):
    return  root_node.findall(
        # use " over ' in Xpath predicate because some school names include '
        f".//SchoolHistory/School/[SchoolName=\"{source_name}\"]")

def determine_output_path(input_path, source_name, root_node):
    """Returns string of the rlative path of the output file"""
    output_name = (input_path.rsplit('/', 1)[-1]
                   .replace('.', f'_{source_name}.'))
    output_dir = f'T:\CMIS\CTF Files\{get_output_dir(root_node)}'
    os.makedirs(output_dir, exist_ok=True)
    return f'{output_dir}\{output_name}'

def get_output_dir(root):
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
    return "CTF_In"

def ac_year(root_node):
    """Returns the academic year of the first student under the passed node"""
    dob_node = root_node.find('.//Pupil/DOB')
    if dob_node is None:
        raise NameError('Pupils are missing their DOBs; this CTF is invalid')
    dob = date.fromisoformat(dob_node.text)
    year_started_school = dob.year + (4 if dob.month < 9 else 5)
    today = date.today()
    ac_start_year = today.year - (1 if today.month < 9 else 0)
    return ac_start_year - year_started_school

def are_joining_mid_year(root):
    """Return True if students are joining next academic year (not this year)"""
    # List the nodes where the source school appears in a pupil's school history
    source_in_hists = source_as_previouses(root, source_school(root))
    leaving_date_node = source_in_hists[0].find('.//LeavingDate')
    if leaving_date_node is not None and len(source_in_hists) > 1:
        leaving_date_1 = leaving_date_node.text
        # Assume mid-year if any students' LeavingDate nodes have different values
        for source_in_hist in source_in_hists:
            this_l_d = source_in_hist.find('LeavingDate')
            if this_l_d is not None and this_l_d.text != leaving_date_1:
                return True
        # Assume next cohort if LeavingDates are after May and before September
        if date.fromisoformat(leaving_date_1).month % 9 > 5:
            return False
    # Otherwise, ask
    return yes_no_q("Are these students joining MID-YEAR?")

def cohort_folder(year_group):
    """Returns the (conventional) name of the folder for the next yr 7 cohort"""
    return f'CTF_Year{year_group:02}_{escpd_next_ac_year()}'

def escpd_next_ac_year():
    """eg Aug '19 and Sep '19 give 2019_2020, but Oct '19 gives 2020_2021

    Desirable because occasionally we get CTFs in September for members of new
    cohort who already started that month.
    """
    d = date.today()
    year = d.year
    return f'{year}_{year + 1}' if d.month < 10 else f'{year + 1}_{year + 2}'

def source_school(root_node):
    node = root_node.find(".//SourceSchool//SchoolName")
    return '' if node is None else node.text

def escape_source_school(source_school):
    return source_school.casefold().replace(' ', '_').replace('.', '')

def plural(count):
    return 's' if count > 1 else ''

if __name__ == '__main__':
    from tkinter import filedialog
    from tkinter import *
    import re
    import xml.etree.ElementTree as ET
    import os
    from datetime import date

    root = Tk()
    root.withdraw()
    ctf_s = filedialog.askopenfilenames(initialdir = "..",
                                        title = "Select CTFs",
                                        filetypes = (("xml files", "*.xml"),))
    if len(ctf_s) == 0:
        print("CTF parsing aborted")
    else:
        outcomes = list(map(process_ctf, ctf_s))
        good_count = outcomes.count(True)
        out_count = len(outcomes)
        bad_count = out_count - good_count
        if good_count == out_count:
            print(f"All ({out_count}) files processed successfully")
        else:
            if good_count > 0:
                print(f'{good_count} file{plural(good_count)} processed successfully.')
                all = ''
            else:
                all = 'all ' if out_count > 1 else 'the '
            print(f'Parsing FAILED for {all}{bad_count} file{plural(bad_count)}.')
    input('Press Enter to Exit... ')
