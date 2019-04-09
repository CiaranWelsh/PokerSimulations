import os, glob

class FileManager:
    WORKING_DIR = os.path.dirname(os.path.dirname(__file__))
    assert os.path.isdir(WORKING_DIR)
    DATA_DIR = os.path.join(WORKING_DIR, 'data')
    assert os.path.isdir(DATA_DIR)

    NL_DIR = os.path.join(DATA_DIR, 'nl')
    assert os.path.isdir(NL_DIR)

    MICRO_STAKES_DIR = os.path.join(NL_DIR, '0.01-0.02')
    assert os.path.isdir(MICRO_STAKES_DIR)

