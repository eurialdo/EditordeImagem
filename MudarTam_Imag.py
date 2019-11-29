
import getopt
import sys
import logging

from filtro_Imag import ajustarImag

logger = logging.getLogger()


def init():


    args = sys.argv[1:]

    if len(args) == 0:
        logger.error("-p não pode estar vazio")
        raise ValueError("-p não pode estar vazio")

    logger.debug(f"run with params: {args}")

    # transform arguments from console
    opts, rem = getopt.getopt(args, "p:", ["rotacao=", "redimencionar=", "cor_filtro=", "girar_cima", "girar_esquerda"])
    rotate_angle = resize = color_filter = flip_top = flip_left = None

    path = None
    for opt, arg in opts:
        if opt == "-p":
            path = arg
        elif opt == "--rotacao":
            rotate_angle = int(arg)
        elif opt == "--redimencionar":
            resize = arg
        elif opt == "--cor_filtro":
            color_filter = arg
        elif opt == "--giro_cima":
            flip_top = True
        elif opt == "--giro_esquerda":
            flip_left = arg

    if not path:
        raise ValueError("sem caminho")

    img = ajustarImag.get_img(path)
    if rotate_angle:
        img = ajustarImag.Rotacao(img, rotate_angle)

    if resize:
        w, h = map(int, resize.split(','))
        img = ajustarImag.redimensionar(img, w, h)

    if color_filter:
        img = ajustarImag.cor_filtro(img, color_filter)

    if flip_left:
        img = ajustarImag.VirarEsquerda(img)

    if flip_top:
        img = ajustarImag.girarCima(img)

    if __debug__:
        img.show()


if __name__ == "__main__":
    init()
