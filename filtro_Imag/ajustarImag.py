"""
Image helper
Main module of the package
All image operations should go thorough this module
"""

from PIL import Image, ImageEnhance
import logging

import filtro_Imag.filtro as cf

logger = logging.getLogger()

# constants
CONTRAST_FACTOR_MAX = 1.5
CONTRAST_FACTOR_MIN = 0.5

SHARPNESS_FACTOR_MAX = 3
SHARPNESS_FACTOR_MIN = -1

BRIGHTNESS_FACTOR_MAX = 1.5
BRIGHTNESS_FACTOR_MIN = 0.5


def get_img(path):
    """Return PIL.Image object"""

    if path == "":
        logger.error("o caminho está vazio ou tem um formato incorreto")
        raise ValueError("o caminho está vazio ou tem um formato incorreto")

    try:
        return Image.open(path)
    except Exception:
        logger.error(f" não pode abrir o arquivo {path}")
        raise ValueError(f" não pode abrir o arquivo  {path}")


def redimensionar(img, width, height):


    return img.resize((width, height))


def Rotacao(img, angle):


    return img.rotate(angle, expand=True)


def cor_filtro(img, filter_name):


    return cf.cor_filto(img, filter_name)


def Brilho(img, factor):


    if factor > BRIGHTNESS_FACTOR_MAX or factor < BRIGHTNESS_FACTOR_MIN:
        raise ValueError("fator deve ser [0-2]")

    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)


def Contraste(img, factor):

    if factor > CONTRAST_FACTOR_MAX or factor < CONTRAST_FACTOR_MIN:
        raise ValueError("fator deve ser[0.5-1.5]")

    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)


def Nitidez(img, factor):

    if factor > SHARPNESS_FACTOR_MAX or factor < SHARPNESS_FACTOR_MIN:
        raise ValueError(" fator deve ser[0.5-1.5]")

    enhancer = ImageEnhance.Sharpness(img)
    return enhancer.enhance(factor)


def VirarEsquerda(img):


    return img.transpose(Image.FLIP_LEFT_RIGHT)


def girarCima(img):

    return img.transpose(Image.FLIP_TOP_BOTTOM)


def Salvar(img, path):

    img.save(path)


def open_img(img):
    """
    Salvar Arquivo em um local
    temporario
    """

    img.open()
