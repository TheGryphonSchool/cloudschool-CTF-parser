from test_helper import ET, dicttoxml, parser

def test_full_file():
    assert False == parser.is_data_missing(
        ET.fromstring(dicttoxml({ 'DocumentQualifier': 'full' } ))
    )

def test_nested_full_file():
    assert False == parser.is_data_missing(
        ET.fromstring(dicttoxml(
            { 'nested': { 'other': 'stuff', 'DocumentQualifier': 'full' } }
        ))
    )

def test_partial_file(capsys):
    assert True == parser.is_data_missing(
        ET.fromstring(dicttoxml({ 'DocumentQualifier': 'partial' }))
    )
    assert 'partial' in capsys.readouterr().out

def test_unqualified_file(capsys):
    assert True == parser.is_data_missing(
        ET.fromstring(dicttoxml({ 'Look': { 'ma': 'no qualifier' } }))
    )
    assert 'missing' in capsys.readouterr().out

def test_irregularly_qualified_file(capsys):
    assert True == parser.is_data_missing(
        ET.fromstring(dicttoxml({ 'DocumentQualifier': 'irregular' }))
    )
    assert 'standard' in capsys.readouterr().out