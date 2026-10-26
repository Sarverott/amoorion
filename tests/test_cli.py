import amoorion


def test_version_matches_project():
    assert amoorion.__version__ == "0.1.0"


def test_main_prints_version(capsys):
    amoorion.main()
    assert amoorion.__version__ in capsys.readouterr().out
