"""
aplicar os filtros PIL.image
"""

import logging

logger = logging.getLogger()


class ColorFilters:
    filters = {"sepia": "Sepia", "negativo": "Negativo", "brancopetro": "Preto & Branco"}
    SEPIA, NEGATIVE, BLACK_WHITE = filters.keys()


def sepia(img):
    pix = img.load()
    for i in range(img.width):
        for j in range(img.height):
            s = sum(pix[i, j]) // 3
            k = 30
            pix[i, j] = (s+k*2, s+k, s)


def pretoBranco(img):
    pix = img.load()
    for i in range(img.width):
        for j in range(img.height):
            s = sum(pix[i, j]) // 3
            pix[i, j] = (s, s, s)


def negativo(img):
    pix = img.load()
    for i in range(img.width):
        for j in range(img.height):
            pix[i, j] = (255 - pix[i, j][0], 255 - pix[i, j][1], 255 - pix[i, j][2])


def cor_filto(img, filter_name):
    img_copy = img.copy()
    if filter_name == ColorFilters.SEPIA:
        sepia(img_copy)
    elif filter_name == ColorFilters.NEGATIVE:
        negativo(img_copy)
    elif filter_name == ColorFilters.BLACK_WHITE:
        pretoBranco(img_copy)
    else:
        logger.error( {filter_name})
        raise ValueError( {filter_name})

    return img_copy
