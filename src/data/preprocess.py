import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import utils.split as splt
import librosa



if __name__ == "__main__":

    import multiprocessing
    multiprocessing.freeze_support()

    print(splt.split_audio('data/raw/busoni_sonata/Busoni_sonata_no2_op_8-BV_61_Scherzo.mp3'))