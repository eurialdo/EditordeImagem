import sys
import ntpath

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

from functools import partial

from filtro_Imag import ajustarImag
from filtro_Imag import filtro

from PIL import ImageQt

from logging.config import fileConfig
import logging

logger = logging.getLogger()

# original img, can't be modified
_img_original = None
Vizualizar_Imag = None

# constants
THUMB_BORDER_COLOR_ACTIVE = "#3893F4"
THUMB_BORDER_COLOR = "#ccc"
BTN_MIN_WIDTH = 120
ROTATION_BTN_SIZE = (70, 30)
THUMB_SIZE = 120

SLIDER_MIN_VAL = -100
SLIDER_MAX_VAL = 100
SLIDER_DEF_VAL = 0


class Operacao:
    def __init__(self):
        self.color_filter = None

        self.flip_left = False
        self.flip_top = False
        self.rotation_angle = 0

        self.size = None

        self.brilho = 0
        self.sharpness = 0
        self.contrast = 0

    def reset(self):
        self.color_filter = None

        self.brilho = 0
        self.sharpness = 0
        self.contrast = 0

        self.size = None

        self.flip_left = False
        self.flip_top = False
        self.rotation_angle = 0

    def has_changes(self):
        return self.color_filter or self.flip_left\
                or self.flip_top or self.rotation_angle\
                or self.contrast or self.brilho\
                or self.sharpness or self.size

    def __str__(self):
        return f"size: {self.size}, filter: {self.color_filter}, " \
               f"b: {self.brilho} c: {self.contrast} s: {self.sharpness}, " \
               f"flip-left: {self.flip_left} flip-top: {self.flip_top} rotação: {self.rotation_angle}"


operacao = Operacao()


def _get_ratio_height(width, height, r_width):
    return int(r_width/width*height)


def _get_ratio_width(width, height, r_height):
    return int(r_height/height*width)


def _get_converted_point(user_p1, user_p2, p1, p2, x):



    r = (x - user_p1) / (user_p2 - user_p1)
    return p1 + r * (p2 - p1)


def _get_img_with_all_operations():
    logger.debug(operacao)

    b = operacao.brilho
    c = operacao.contrast
    s = operacao.sharpness

    img = Vizualizar_Imag
    if b != 0:
        img = ajustarImag.Brilho(img, b)

    if c != 0:
        img = ajustarImag.Contraste(img, c)

    if s != 0:
        img = ajustarImag.Nitidez(img, s)

    if operacao.rotation_angle:
        img = ajustarImag.Rotacao(img, operacao.rotation_angle)

    if operacao.flip_left:
        img = ajustarImag.VirarEsquerda(img)

    if operacao.flip_top:
        img = ajustarImag.girarCima(img)

    if operacao.size:
        img = ajustarImag.redimensionar(img, *operacao.size)

    return img


class ActionTabs(QTabWidget):


    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.filters_tab = AbaFiltros(self)
        self.adjustment_tab = AdjustingTab(self)
        self.modification_tab = AbaModifcarTam(self)
        self.rotation_tab = Rotacao(self)

        self.addTab(self.filters_tab, "Filtros")
        self.addTab(self.adjustment_tab, "Ajuste")
        self.addTab(self.rotation_tab, "Rotacionar")
        self.addTab(self.modification_tab, "Modificar Tamanho")


        self.setMaximumHeight(190)


class Rotacao(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        rotate_left_btn = QPushButton("↺ 90°")
        rotate_left_btn.setMinimumSize(*ROTATION_BTN_SIZE)
        rotate_left_btn.clicked.connect(self.girarEsquerda)

        rotate_right_btn = QPushButton("↻ 90°")
        rotate_right_btn.setMinimumSize(*ROTATION_BTN_SIZE)
        rotate_right_btn.clicked.connect(self.girarDireita)

        flip_left_btn = QPushButton("⇆")
        flip_left_btn.setMinimumSize(*ROTATION_BTN_SIZE)
        flip_left_btn.clicked.connect(self.VirarEsquerda)

        flip_top_btn = QPushButton("↑↓")
        flip_top_btn.setMinimumSize(*ROTATION_BTN_SIZE)
        flip_top_btn.clicked.connect(self.girarCima)

        rotate_lbl = QLabel("Giro 90º")
        rotate_lbl.setAlignment(Qt.AlignCenter)
        rotate_lbl.setFixedWidth(140)

        flip_lbl = QLabel("Rotação")
        flip_lbl.setAlignment(Qt.AlignCenter)
        flip_lbl.setFixedWidth(140)

        lbl_layout = QHBoxLayout()
        lbl_layout.setAlignment(Qt.AlignCenter)
        lbl_layout.addWidget(rotate_lbl)
        lbl_layout.addWidget(flip_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(rotate_left_btn)
        btn_layout.addWidget(rotate_right_btn)
        btn_layout.addWidget(QVLine())
        btn_layout.addWidget(flip_left_btn)
        btn_layout.addWidget(flip_top_btn)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(lbl_layout)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def girarEsquerda(self):
        logger.debug("rotate left")

        operacao.rotation_angle = 0 if operacao.rotation_angle == 270 else operacao.rotation_angle + 90
        self.parent.parent.pre_vizuImg()

    def girarDireita(self):
        logger.debug("rotate left")

        operacao.rotation_angle = 0 if operacao.rotation_angle == -270 else operacao.rotation_angle - 90
        self.parent.parent.pre_vizuImg()

    def VirarEsquerda(self):
        logger.debug("Girar para esquerda")

        operacao.flip_left = not operacao.flip_left
        self.parent.parent.pre_vizuImg()

    def girarCima(self):
        logger.debug("flip top-bottom")

        operacao.flip_top = not operacao.flip_top
        self.parent.parent.pre_vizuImg()


class AbaModifcarTam(QWidget):


    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.width_lbl = QLabel('Largura:', self)
        self.width_lbl.setFixedWidth(100)

        self.height_lbl = QLabel('Altura:', self)
        self.height_lbl.setFixedWidth(100)

        self.width_box = QLineEdit(self)
        self.width_box.textEdited.connect(self.mudancaLargura)
        self.width_box.setMaximumWidth(100)

        self.height_box = QLineEdit(self)
        self.height_box.textEdited.connect(self.mudancaAltura)
        self.height_box.setMaximumWidth(100)

        self.unit_lbl = QLabel("px")
        self.unit_lbl.setMaximumWidth(50)

        self.ratio_check = QCheckBox('Resolução da Tela', self)
        self.ratio_check.stateChanged.connect(self.mudancaRotacao)

        self.apply_btn = QPushButton("Aplicar")
        self.apply_btn.setFixedWidth(90)
        self.apply_btn.clicked.connect(self.AplicarMudanca)

        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width_box)
        width_layout.addWidget(self.height_box)
        width_layout.addWidget(self.unit_lbl)

        apply_layout = QHBoxLayout()
        apply_layout.addWidget(self.apply_btn)
        apply_layout.setAlignment(Qt.AlignRight)

        lbl_layout = QHBoxLayout()
        lbl_layout.setAlignment(Qt.AlignLeft)
        lbl_layout.addWidget(self.width_lbl)
        lbl_layout.addWidget(self.height_lbl)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(lbl_layout)
        main_layout.addLayout(width_layout)
        main_layout.addWidget(self.ratio_check)
        main_layout.addLayout(apply_layout)

        self.setLayout(main_layout)

    def caixaAjuste(self):
        self.width_box.setText(str(_img_original.width))
        self.height_box.setText(str(_img_original.height))

    def mudancaLargura(self, e):
        logger.debug(f"lagura {self.width_box.text()}")

        if self.ratio_check.isChecked():
            r_height = _get_ratio_height(_img_original.width, _img_original.height, int(self.width_box.text()))
            self.height_box.setText(str(r_height))

    def mudancaAltura(self, e):
        logger.debug(f"type altura {self.height_box.text()}")

        if self.ratio_check.isChecked():
            r_width = _get_ratio_width(_img_original.width, _img_original.height, int(self.height_box.text()))
            self.width_box.setText(str(r_width))

    def mudancaRotacao(self, e):
        logger.debug("ratio change")

    def AplicarMudanca(self, e):
        logger.debug("Aplicar")

        operacao.size = int(self.width_box.text()), int(self.height_box.text())

        self.parent.parent.AtualizarImg()
        self.parent.parent.pre_vizuImg()


class AdjustingTab(QWidget):


    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        contraste_lbl = QLabel("Contraste")
        contraste_lbl.setAlignment(Qt.AlignCenter)

        brilhos_lbl = QLabel("Brilho")
        brilhos_lbl.setAlignment(Qt.AlignCenter)

        nitidez_lbl = QLabel("Nitidez")
        nitidez_lbl.setAlignment(Qt.AlignCenter)

        self.contraste_deslize = QSlider(Qt.Horizontal, self)
        self.contraste_deslize.setMinimum(SLIDER_MIN_VAL)
        self.contraste_deslize.setMaximum(SLIDER_MAX_VAL)
        self.contraste_deslize.sliderReleased.connect(self.DelizeContraste)
        self.contraste_deslize.setToolTip(str(SLIDER_MAX_VAL))

        self.brilho_deslize = QSlider(Qt.Horizontal, self)
        self.brilho_deslize.setMinimum(SLIDER_MIN_VAL)
        self.brilho_deslize.setMaximum(SLIDER_MAX_VAL)
        self.brilho_deslize.sliderReleased.connect(self.DeslizeBrilho)
        self.brilho_deslize.setToolTip(str(SLIDER_MAX_VAL))

        self.nitizdez_deslize = QSlider(Qt.Horizontal, self)
        self.nitizdez_deslize.setMinimum(SLIDER_MIN_VAL)
        self.nitizdez_deslize.setMaximum(SLIDER_MAX_VAL)
        self.nitizdez_deslize.sliderReleased.connect(self.DeslizeNitidez)
        self.nitizdez_deslize.setToolTip(str(SLIDER_MAX_VAL))

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(contraste_lbl)
        main_layout.addWidget(self.contraste_deslize)

        main_layout.addWidget(brilhos_lbl)
        main_layout.addWidget(self.brilho_deslize)

        main_layout.addWidget(nitidez_lbl)
        main_layout.addWidget(self.nitizdez_deslize)

        self.resetarDeslize()
        self.setLayout(main_layout)

    def resetarDeslize(self):
        self.brilho_deslize.setValue(SLIDER_DEF_VAL)
        self.nitizdez_deslize.setValue(SLIDER_DEF_VAL)
        self.contraste_deslize.setValue(SLIDER_DEF_VAL)

    def DeslizeBrilho(self):
        logger.debug(f" {self.brilho_deslize.value()}")

        self.brilho_deslize.setToolTip(str(self.brilho_deslize.value()))

        factor = _get_converted_point(SLIDER_MIN_VAL, SLIDER_MAX_VAL, ajustarImag.BRIGHTNESS_FACTOR_MIN,
                                      ajustarImag.BRIGHTNESS_FACTOR_MAX, self.brilho_deslize.value())
        logger.debug(f"brilho: {factor}")

        operacao.brilho = factor

        self.parent.parent.pre_vizuImg()

    def DeslizeNitidez(self):
        logger.debug(self.nitizdez_deslize.value())

        self.nitizdez_deslize.setToolTip(str(self.nitizdez_deslize.value()))

        factor = _get_converted_point(SLIDER_MIN_VAL, SLIDER_MAX_VAL, ajustarImag.SHARPNESS_FACTOR_MIN,
                                      ajustarImag.SHARPNESS_FACTOR_MAX, self.nitizdez_deslize.value())
        logger.debug(f"nitidez: {factor}")

        operacao.sharpness = factor

        self.parent.parent.pre_vizuImg()

    def DelizeContraste(self):
        logger.debug(self.contraste_deslize.value())

        self.contraste_deslize.setToolTip(str(self.contraste_deslize.value()))

        factor = _get_converted_point(SLIDER_MIN_VAL, SLIDER_MAX_VAL, ajustarImag.CONTRAST_FACTOR_MIN,
                                      ajustarImag.CONTRAST_FACTOR_MAX, self.contraste_deslize.value())
        logger.debug(f"contraste: {factor}")

        operacao.contrast = factor

        self.parent.parent.pre_vizuImg()


class AbaFiltros(QWidget):


    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.add_filto_polegada("none")
        for key, val in filtro.ColorFilters.filters.items():
            self.add_filto_polegada(key, val)

        self.setLayout(self.main_layout)

    def add_filto_polegada(self, name, title=""):
        logger.debug(f"crear nome img: {name}")

        polegada_lbl = QLabel()
        polegada_lbl.name = name
        polegada_lbl.setStyleSheet("border:2px solid #ccc;")

        if name != "none":
            polegada_lbl.setToolTip(f"Apply <b>{title}</b> filter")
        else:
            polegada_lbl.setToolTip('aplicar filtro')

        polegada_lbl.setCursor(Qt.PointingHandCursor)
        polegada_lbl.setFixedSize(THUMB_SIZE, THUMB_SIZE)
        polegada_lbl.mousePressEvent = partial(self.selecionar_filtro, name)

        self.main_layout.addWidget(polegada_lbl)

    def selecionar_filtro(self, filter_name, e):
        logger.debug(f"apply color filter: {filter_name}")

        global Vizualizar_Imag
        if filter_name != "none":
            Vizualizar_Imag = ajustarImag.cor_filtro(_img_original, filter_name)
        else:
            Vizualizar_Imag = _img_original.copy()

        operacao.color_filter = filter_name
        self.mudar_tamanho()

        self.parent.parent.pre_vizuImg()

    def mudar_tamanho(self):
        for thumb in self.findChildren(QLabel):
            color = THUMB_BORDER_COLOR_ACTIVE if thumb.name == operacao.color_filter else THUMB_BORDER_COLOR
            thumb.setStyleSheet(f"border:2px solid {color};")


class MainLayout(QVBoxLayout):


    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.img_lbl = QLabel("<div style='margin: 30px 0'><img src='logo.png' /></div>"
                              )
        self.img_lbl.setAlignment(Qt.AlignCenter)

        self.file_name = None

        self.img_size_lbl = None
        self.img_size_lbl = QLabel()
        self.img_size_lbl.setAlignment(Qt.AlignCenter)

        upload_btn = QPushButton("Buscar Imagem")
        upload_btn.setMinimumWidth(BTN_MIN_WIDTH)
        upload_btn.clicked.connect(self.BuscarImg)
        upload_btn.setStyleSheet("font-weight:bold;")

        self.reset_btn = QPushButton("Resetar")
        self.reset_btn.setMinimumWidth(BTN_MIN_WIDTH)
        self.reset_btn.clicked.connect(self.resetar)
        self.reset_btn.setEnabled(False)
        self.reset_btn.setStyleSheet("font-weight:bold;")

        self.save_btn = QPushButton("Salvar")
        self.save_btn.setMinimumWidth(BTN_MIN_WIDTH)
        self.save_btn.clicked.connect(self.salvar)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("font-weight:bold;")

        self.addWidget(self.img_lbl)
        self.addWidget(self.img_size_lbl)
        self.addStretch()

        self.action_tabs = ActionTabs(self)
        self.addWidget(self.action_tabs)
        self.action_tabs.setVisible(False)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(upload_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.save_btn)

        self.addLayout(btn_layout)

    def pre_vizuImg(self):
        img = _get_img_with_all_operations()

        preview_pix = ImageQt.toqpixmap(img)
        self.img_lbl.setPixmap(preview_pix)

    def salvar(self):
        logger.debug("Abrir pasta para salvar")
        new_img_path, _ = QFileDialog.getSaveFileName(self.parent, "Erro",
                                                      f"ez_pz_{self.file_name}",
                                                      "Images (*.png *.jpg)")

        if new_img_path:
            logger.debug(f"salvar imagem em {new_img_path}")

            img = _get_img_with_all_operations()
            img.save(new_img_path)

    def BuscarImg(self):
        logger.debug("upload")
        img_path, _ = QFileDialog.getOpenFileName(self.parent, "Abrir imagem",
                                                  "/Users",
                                                  "Images (*.png *jpg)")

        if img_path:
            logger.debug(f"Abrir arquivo {img_path}")

            self.file_name = ntpath.basename(img_path)

            pix = QPixmap(img_path)
            self.img_lbl.setPixmap(pix)
            self.img_lbl.setScaledContents(True)
            self.action_tabs.setVisible(True)
            self.action_tabs.adjustment_tab.resetarDeslize()

            global _img_original
            _img_original = ImageQt.fromqpixmap(pix)

            self.AtualizarImg()

            if _img_original.width < _img_original.height:
                w = THUMB_SIZE
                h = _get_ratio_height(_img_original.width, _img_original.height, w)
            else:
                h = THUMB_SIZE
                w = _get_ratio_width(_img_original.width, _img_original.height, h)

            img_filter_thumb = ajustarImag.redimensionar(_img_original, w, h)

            global Vizualizar_Imag
            Vizualizar_Imag = _img_original.copy()

            for polegada in self.action_tabs.filters_tab.findChildren(QLabel):
                if polegada.name != "none":
                    img_filter_preview = ajustarImag.cor_filtro(img_filter_thumb, polegada.name)
                else:
                    img_filter_preview = img_filter_thumb

                preview_pix = ImageQt.toqpixmap(img_filter_preview)
                polegada.setPixmap(preview_pix)

            self.reset_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.action_tabs.modification_tab.caixaAjuste()

    def AtualizarImg(self):
        logger.debug("Atualizar Imagem")

        self.img_size_lbl.setText(f"<span style='font-size:11px'>"
                                  f"image size {operacao.size[0] if operacao.size else _img_original.width} × "
                                  f"{operacao.size[1] if operacao.size else _img_original.height}"
                                  f"</span>")

    def resetar(self):
        logger.debug("resetar tudo")

        global Vizualizar_Imag
        Vizualizar_Imag = _img_original.copy()

        operacao.reset()

        self.action_tabs.filters_tab.mudar_tamanho()
        self.pre_vizuImg()
        self.action_tabs.adjustment_tab.resetarDeslize()
        self.action_tabs.modification_tab.caixaAjuste()
        self.AtualizarImg()


class EasyPzUI(QWidget):


    def __init__(self):
        super().__init__()

        self.main_layout = MainLayout(self)
        self.setLayout(self.main_layout)

        self.setMinimumSize(900, 600)
        self.setMaximumSize(900, 900)
        self.setGeometry(600, 600, 600, 600)
        self.setWindowTitle('Editor de Imagem')
        self.center()
        self.show()

    def center(self):


        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        logger.debug("fechar")

        if operacao.has_changes():
            reply = QMessageBox.question(self, "",
                                         "Você tem mudanças feitas <br> Deseja sair?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def resizeEvent(self, e):
        pass


class QVLine(QFrame):
    """Vertical line"""

    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


if __name__ == '__main__':
    fileConfig('logging_config.ini')

    app = QApplication(sys.argv)
    win = EasyPzUI()
    sys.exit(app.exec_())

