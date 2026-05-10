from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QLabel, QFrame, QMessageBox,
)
from PySide6.QtCore import Qt

from logic import FormValidator, SlugGenerator


class DialogPost(QDialog):
    def __init__(self, parent=None, post: dict = None):
        super().__init__(parent)
        self._post = post  
        self._build_ui()
        if post:
            self._fill(post)
            
    def _build_ui(self):
        mode = "Edit Post" if self._post else "Tambah Post Baru"
        self.setWindowTitle(mode)
        self.setMinimumWidth(500)
        self.setObjectName("dialogPost")

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        header = QFrame()
        header.setObjectName("dialogHeader")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(24, 18, 24, 14)
        h_lay.setSpacing(3)

        lbl_title = QLabel(mode)
        lbl_title.setObjectName("dialogTitle")

        sub_text = "Ubah data post yang dipilih" if self._post else "Isi semua field untuk membuat post baru"
        lbl_sub = QLabel(sub_text)
        lbl_sub.setObjectName("dialogSubtitle")

        h_lay.addWidget(lbl_title)
        h_lay.addWidget(lbl_sub)
        root.addWidget(header)

        body = QFrame()
        body.setObjectName("dialogBody")
        form = QFormLayout(body)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.inp_title = QLineEdit()
        self.inp_title.setPlaceholderText("Judul post...")
        self.inp_title.setObjectName("inputField")
        self.inp_title.textChanged.connect(self._on_title_changed)
        form.addRow("Title *", self.inp_title)

        self.inp_body = QTextEdit()
        self.inp_body.setPlaceholderText("Isi konten post...")
        self.inp_body.setFixedHeight(100)
        self.inp_body.setObjectName("inputTextEdit")
        form.addRow("Body *", self.inp_body)

        self.inp_author = QLineEdit()
        self.inp_author.setPlaceholderText("Nama penulis...")
        self.inp_author.setObjectName("inputField")
        form.addRow("Author *", self.inp_author)

        slug_row = QHBoxLayout()
        self.inp_slug = QLineEdit()
        self.inp_slug.setPlaceholderText("url-friendly-slug (otomatis dari title)")
        self.inp_slug.setObjectName("inputField")
        self.lbl_slug_hint = QLabel("Unik")
        self.lbl_slug_hint.setObjectName("slugHint")
        slug_row.addWidget(self.inp_slug)
        slug_row.addWidget(self.lbl_slug_hint)
        form.addRow("Slug *", slug_row)

        self.inp_status = QComboBox()
        self.inp_status.addItems(["published", "draft"])
        self.inp_status.setObjectName("inputField")
        form.addRow("Status", self.inp_status)

        root.addWidget(body)

        footer = QFrame()
        footer.setObjectName("dialogFooter")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(24, 12, 24, 12)
        f_lay.addStretch()

        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.setObjectName("btnSecondary")
        self.btn_cancel.clicked.connect(self.reject)

        label_ok = "Simpan Perubahan" if self._post else "Tambah Post"
        self.btn_ok = QPushButton(label_ok)
        self.btn_ok.setObjectName("btnPrimary")
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self._on_submit)

        f_lay.addWidget(self.btn_cancel)
        f_lay.addWidget(self.btn_ok)
        root.addWidget(footer)

    def _on_title_changed(self, text: str):
        if self._post:
            return 
        self.inp_slug.setText(SlugGenerator.from_title(text))

    def _fill(self, post: dict):
        self.inp_title.setText(post.get("title", ""))
        self.inp_body.setPlainText(post.get("body", ""))
        self.inp_author.setText(post.get("author", ""))
        self.inp_slug.setText(post.get("slug", ""))
        idx = self.inp_status.findText(post.get("status", "draft"))
        if idx >= 0:
            self.inp_status.setCurrentIndex(idx)

    def _on_submit(self):
        raw = self.get_data()

        errors = FormValidator.validate(raw)
        if errors:
            QMessageBox.warning(self, "Validasi Form", "\n".join(errors))
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "title":  self.inp_title.text().strip(),
            "body":   self.inp_body.toPlainText().strip(),
            "author": self.inp_author.text().strip(),
            "slug":   self.inp_slug.text().strip(),
            "status": self.inp_status.currentText(),
        }

    def show_slug_error(self, msg: str):
        self.inp_slug.setStyleSheet(
            "border: 2px solid #ef4444; background-color: #fff1f2;"
        )
        self.lbl_slug_hint.setText(f"⚠ {msg}")
        self.lbl_slug_hint.setStyleSheet("color: #dc2626; font-weight: 600;")
