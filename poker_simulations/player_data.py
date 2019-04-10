import os, glob
import pandas, numpy
from file_manager import FileManager
import matplotlib.pyplot as plt
import seaborn

FILE_MANAGER = FileManager()

def x(f):
    df = pandas.read_csv(f, encoding='ISO-8859-1')
    df.set_index('Player Name', inplace=True)
    print(df.columns)
    # plt.figure()
    # seaborn.barplot(df['Net Won']/df['Hands'])
    # print(df)
    # plt.show()
    desc = df.describe()
    print(desc['Net Won'])









if __name__ == '__main__':
    x(FILE_MANAGER.PLAYER_STATS_FILE)
