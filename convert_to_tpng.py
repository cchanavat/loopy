from PIL import Image
import numpy as np
import tqdm


def convert_to_png(folder_name, N, id_=0):
    PATH = "data/raw/"
    PATH_SAVE = PATH + folder_name + "_png/"
    for n in tqdm.tqdm(range(N)):
        arr = np.loadtxt("data/raw/{0}/{2}/{1}.loop".format(folder_name, n, id_)).astype("int")
        arr = 255 * arr / np.max(arr)
        arr = np.round(arr).astype("uint8")

        im = Image.fromarray(arr)
        im.save(PATH_SAVE + "{}.png".format(n))


convert_to_png("raw_8", 10000)