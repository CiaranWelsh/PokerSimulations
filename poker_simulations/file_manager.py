import os, glob

class FileManager:
    WORKING_DIR = os.path.dirname(os.path.dirname(__file__))
    assert os.path.isdir(WORKING_DIR)
    DATA_DIR = os.path.join(WORKING_DIR, 'data')
    assert os.path.isdir(DATA_DIR)

    NL_DIR = os.path.join(DATA_DIR, 'nl')
    PLAYER_STATS_FILE = os.path.join(NL_DIR, 'player_stats.csv')
    assert os.path.isdir(NL_DIR)
    assert os.path.isfile(PLAYER_STATS_FILE)

    MICRO_STAKES_DIR = os.path.join(NL_DIR, '0.01-0.02')
    assert os.path.isdir(MICRO_STAKES_DIR)

    SMALL_STAKES_DIR = os.path.join(NL_DIR, '0.25-0.50')
    assert os.path.isdir(SMALL_STAKES_DIR)

