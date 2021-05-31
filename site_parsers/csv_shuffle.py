import pandas as pd


def prepare_csv(filename):
    flats_table = pd.read_csv(filename, sep=';', header=0)
    random_flats_table = flats_table.sample(frac=1, random_state=42)
    random_flats_table.to_csv('shuffled_flats_data.csv', index=False, sep=';')


if __name__ == '__main__':
    prepare_csv('cian_flats_data.csv')
