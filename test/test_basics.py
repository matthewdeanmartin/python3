def test_run_import():
    import python3.__main__
    assert dir(python3.__main__)