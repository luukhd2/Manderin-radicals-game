""" Load radicals to pandas DataFrame """
import pandas as pd 
import pathlib
import numpy as np


def fix_pinyin(pinyin : str):
    """ Fix pinyin to be more readable """
    pinyin = pinyin.strip()
    if pinyin.startswith('(') and pinyin.endswith(')'):
        pinyin = pinyin[1:-1]
    
    # temp fix for 'nv3' -> 'nuu3'
    if pinyin == 'nv3':
        print("Warning: 'nv3' audio not found, using 'nuu3' instead")
        return 'nuu3'

    return pinyin



def load_radicals():
    """ Load radicals to pandas DataFrame 
    
        Radical Variant                Meaning Pinyin Examples
    0  人       亻  human, person, people   ren2    今仁休位他
    1  口     NaN         mouth, opening   kou3    古可名告吃
    """
    script_dir = pathlib.Path(__file__).parent.absolute()
    radicals = pd.read_csv(script_dir / 'data/radicals.tsv', sep='\t')

    # variant can be a list
    radicals['Variant'] = radicals['Variant'].str.split(',')
    radicals['Examples'] = radicals['Examples'].str.split(',')
    radicals = radicals.rename(columns={'SC': 'Radical'})

    radicals['Pinyin'] = radicals['Pinyin'].apply(fix_pinyin)

    # add full file paths
    radicals['Audio'] = radicals['Pinyin'].apply(get_path_to_pinyin_sound)

    return radicals


def load_radicals_complete():
    script_dir = pathlib.Path(__file__).parent.absolute()
    radicals = pd.read_csv(script_dir / 'data/radicals_complete.tsv', sep='\t')
    # fill nan with ''
    radicals = radicals.fillna('')
    # variant can be a list
    radicals['Variant'] = radicals['Variant'].str.split(',')
    radicals = radicals.rename(columns={'SC': 'Radical'})
    radicals['Pinyin'] = radicals['Pinyin'].apply(fix_pinyin)
    # add full file paths
    radicals['Audio'] = radicals['Pinyin'].apply(get_path_to_pinyin_sound)

    return radicals
 


def get_path_to_pinyin_sound(sound : str):
    """ Get the path to the pinyin sound file 
    
    sound: 'ren2'
    """
    script_dir = pathlib.Path(__file__).parent.absolute()
    mp3_dir = script_dir / 'data/mp3-chinese-pinyin-sound/mp3'
    p = mp3_dir / f'{sound}.mp3'
    
    if p.exists():
        return p

    return np.nan



if __name__ == '__main__':
    print(load_radicals().head())
    print(load_radicals_complete().head())
