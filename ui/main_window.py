from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QFrame, QMessageBox, QDialog,
    QMenuBar, QMenu, QStatusBar, QProgressBar, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, Slot, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QAction, QColor

from api.worker import (
    worker_get_all, worker_get_one,
    worker_create, worker_update, worker_delete,
)
from logic import ResponseParser, ErrorParser, StatusFormatter
from ui.dialog_post  import DialogPost
from ui.panel_detail import PanelDetail


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Post Manager — CRUD API")

        self._workers = []     
        self._selected_id = None

        self._build_menu()
        self._build_ui()
        self._build_statusbar()
        self._load_posts()
        
        self.showMaximized()

    def _build_menu(self):
        mb = self.menuBar()
        mb.setObjectName("menuBar")

        m_file = mb.addMenu("&File")
        act_refresh = QAction("Refresh", self)
        act_refresh.setShortcut("F5")
        act_refresh.triggered.connect(self._load_posts)
        m_file.addAction(act_refresh)
        m_file.addSeparator()
        act_quit = QAction("Keluar", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_post = mb.addMenu("&Post")
        act_new = QAction("Tambah Post", self)
        act_new.setShortcut("Ctrl+N")
        act_new.triggered.connect(self._tambah)
        m_post.addAction(act_new)

        act_edit = QAction("Edit Post", self)
        act_edit.setShortcut("Ctrl+E")
        act_edit.triggered.connect(self._edit)
        m_post.addAction(act_edit)

        act_del = QAction("Hapus Post", self)
        act_del.setShortcut("Delete")
        act_del.triggered.connect(self._hapus)
        m_post.addAction(act_del)

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("mainContainer")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_banner())

        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  
        self.loading_bar.setFixedHeight(3)
        self.loading_bar.setObjectName("loadingBar")
        self.loading_bar.setTextVisible(False)
        self.loading_bar.hide()
        root.addWidget(self.loading_bar)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("mainSplitter")
        splitter.setHandleWidth(1)

        left = self._make_left_panel()
        splitter.addWidget(left)

        self.panel_detail = PanelDetail()
        splitter.addWidget(self.panel_detail)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        root.addWidget(splitter, 1)

    def _make_banner(self) -> QFrame:
        banner = QFrame()
        banner.setObjectName("banner")
        lay = QHBoxLayout(banner)
        lay.setContentsMargins(20, 12, 20, 12)

        lbl_app = QLabel("Post Manager")
        lbl_app.setObjectName("bannerApp")
        lay.addWidget(lbl_app)

        lay.addStretch()

        lbl_api = QLabel("API: api.pahrul.my.id")
        lbl_api.setObjectName("bannerApi")
        lay.addWidget(lbl_api)
        return banner

    def _make_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("leftPanel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        lbl = QLabel("Daftar Posts")
        lbl.setObjectName("tabSectionTitle")
        toolbar.addWidget(lbl)
        toolbar.addStretch()

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("panelSubinfo")
        toolbar.addWidget(self.lbl_count)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setObjectName("btnRefresh")
        btn_refresh.setToolTip("Refresh daftar posts")
        btn_refresh.setFixedSize(34, 34)
        btn_refresh.clicked.connect(self._load_posts)
        toolbar.addWidget(btn_refresh)

        self.btn_add = QPushButton("Tambah Post")
        self.btn_add.setObjectName("btnPrimary")
        self.btn_add.setFixedHeight(34)
        self.btn_add.clicked.connect(self._tambah)
        toolbar.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("[ ]")
        self.btn_edit.setObjectName("btnSecondary")
        self.btn_edit.setFixedHeight(34)
        self.btn_edit.setFixedWidth(34)
        self.btn_edit.setToolTip("Edit post yang dipilih")
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self._edit)
        toolbar.addWidget(self.btn_edit)

        self.btn_del = QPushButton(" - ")
        self.btn_del.setObjectName("btnDanger")
        self.btn_del.setFixedHeight(34)
        self.btn_del.setFixedWidth(34)
        self.btn_del.setToolTip("Hapus post yang dipilih")
        self.btn_del.setEnabled(False)
        self.btn_del.clicked.connect(self._hapus)
        toolbar.addWidget(self.btn_del)

        lay.addLayout(toolbar)

        self._BTN_ADD_WIDE  = 130  
        self._BTN_ADD_SMALL = 34    
        self._BTN_ACT_WIDE  = 100  
        self._BTN_ACT_SMALL = 34  

        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Author", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 56)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 100)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._on_row_double_clicked)

        lay.addWidget(self.table)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("errorLabel")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()
        lay.addWidget(self.lbl_error)

        return panel

    def _build_statusbar(self):
        sb = self.statusBar()
        sb.setObjectName("statusBar")
        self.lbl_status = QLabel("Siap")
        sb.addWidget(self.lbl_status)

    def _set_loading(self, on: bool, msg: str = ""):
        self.loading_bar.setVisible(on)
        if on:
            self.lbl_status.setText(f"{msg}")
            self.table.setEnabled(False)
            self.btn_edit.setEnabled(False)
            self.btn_del.setEnabled(False)
        else:
            self.table.setEnabled(True)
            self._on_selection_changed()  

    def _set_error(self, msg: str):
        self.lbl_error.setText(f"{msg}")
        self.lbl_error.show()
        self.lbl_status.setText("Terjadi kesalahan.")

    def _clear_error(self):
        self.lbl_error.hide()
        self.lbl_error.setText("")

    def _keep_worker(self, w):
        self._workers.append(w)
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)

    @Slot()
    def _on_selection_changed(self):
        rows = self.table.selectedItems()
        has = bool(rows)
        self.btn_edit.setEnabled(has)
        self.btn_del.setEnabled(has)
        self._animate_buttons(has)
        if has:
            self._selected_id = int(self.table.item(self.table.currentRow(), 0).text())
            self._load_detail(self._selected_id)
        else:
            self._selected_id = None
            self.panel_detail.clear()

    def _animate_buttons(self, has_selection: bool):
        dur = 180  

        add_target = self._BTN_ADD_WIDE 
        add_label  = "Tambah Post"

        act_target  = self._BTN_ACT_WIDE  if has_selection else self._BTN_ACT_SMALL
        edit_label  = "Edit"         if has_selection else ""
        del_label   = "Hapus"           if has_selection else ""

        def _anim(btn: QPushButton, target_w: int, label: str):
            if hasattr(btn, "_current_anim"):
                btn._current_anim.stop()
            if hasattr(btn, "_current_anim2"):
                btn._current_anim2.stop()

            a = QPropertyAnimation(btn, b"minimumWidth", self)
            a.setDuration(dur)
            a.setStartValue(btn.width())
            a.setEndValue(target_w)
            a.setEasingCurve(QEasingCurve.OutCubic)
 
            a2 = QPropertyAnimation(btn, b"maximumWidth", self)
            a2.setDuration(dur)
            a2.setStartValue(btn.width())
            a2.setEndValue(target_w)
            a2.setEasingCurve(QEasingCurve.OutCubic)
   
            btn._current_anim = a
            btn._current_anim2 = a2

            if has_selection or btn == self.btn_add:
                a.finished.connect(lambda b=btn, l=label: b.setText(l))
            else:
                btn.setText(label)

            a.start()
            a2.start()

        _anim(self.btn_add,  add_target, add_label)
        _anim(self.btn_edit, act_target,  edit_label)
        _anim(self.btn_del,  act_target,  del_label)

    @Slot()
    def _on_row_double_clicked(self):
        self._edit()

    def _get_selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def _load_posts(self):
        self._clear_error()
        self._set_loading(True, "Memuat daftar posts...")
        self.panel_detail.clear()

        w = worker_get_all()
        w.result.connect(self._on_posts_loaded)
        w.error.connect(lambda e: self._on_api_error(e))
        w.finished.connect(lambda: self._set_loading(False))
        self._keep_worker(w)
        w.start()

    @Slot(dict)
    def _on_posts_loaded(self, res: dict):
        if not res["ok"]:
            self._set_error(ErrorParser.parse(res).message)
            return

        rows = ResponseParser.to_post_rows(res)

        self.table.setRowCount(0)
        for p in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)

            id_item = QTableWidgetItem(str(p.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 0, id_item)

            self.table.setItem(r, 1, QTableWidgetItem(p.title))
            self.table.setItem(r, 2, QTableWidgetItem(p.author))

            fg, bg = StatusFormatter.colors(p.status)
            st_item = QTableWidgetItem(p.status)
            st_item.setTextAlignment(Qt.AlignCenter)
            st_item.setForeground(QColor(fg))
            st_item.setBackground(QColor(bg))
            self.table.setItem(r, 3, st_item)

        count = len(rows)
        self.lbl_count.setText(f"{count} post")
        self.lbl_status.setText(f"{count} post dimuat.")

    def _load_detail(self, post_id: int):
        self.panel_detail.show_loading()

        w = worker_get_one(post_id)
        w.result.connect(self._on_detail_loaded)
        w.error.connect(lambda e: self.panel_detail.show_error(e))
        self._keep_worker(w)
        w.start()

    @Slot(dict)
    def _on_detail_loaded(self, res: dict):
        if not res["ok"]:
            self.panel_detail.show_error(ErrorParser.parse(res).message)
            return
        detail = ResponseParser.to_post_detail(res)
        self.panel_detail.show_post(detail.__dict__)

    def _tambah(self):
        dlg = DialogPost(self)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        self._set_loading(True, "Menyimpan post baru...")
        self._clear_error()

        w = worker_create(**data)
        w.result.connect(lambda res: self._on_create_done(res, dlg))
        w.error.connect(lambda e: self._on_api_error(e))
        w.finished.connect(lambda: self._set_loading(False))
        self._keep_worker(w)
        w.start()

    @Slot(dict)
    def _on_create_done(self, res: dict, dlg: DialogPost):
        if not res["ok"]:
     
            err = ErrorParser.parse(res)
            if err.is_slug_error:
                dlg.show_slug_error(err.message)
                dlg.exec()
            else:
                self._set_error(err.message)
            return

        new_id = ResponseParser.created_id(res)
        QMessageBox.information(
            self, "Post Ditambahkan",
            f"Post berhasil disimpan!\n\nID yang dikembalikan server: {new_id}"
        )
        self.lbl_status.setText(f"Post #{new_id} berhasil ditambahkan.")
        self._load_posts()

    def _edit(self):
        post_id = self._get_selected_id()
        if post_id is None:
            QMessageBox.information(self, "Info", "Pilih post yang ingin diedit.")
            return

        self._set_loading(True, "Memuat data post...")
        w = worker_get_one(post_id)
        w.result.connect(lambda res: self._open_edit_dialog(res, post_id))
        w.error.connect(lambda e: self._on_api_error(e))
        w.finished.connect(lambda: self._set_loading(False))
        self._keep_worker(w)
        w.start()

    def _open_edit_dialog(self, res: dict, post_id: int):
        if not res["ok"]:
            self._set_error(ErrorParser.parse(res).message)
            return
   
        detail = ResponseParser.to_post_detail(res)

        dlg = DialogPost(self, post=detail.__dict__)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        self._set_loading(True, "Menyimpan perubahan...")

        w = worker_update(post_id, **data)
        w.result.connect(lambda r: self._on_update_done(r, post_id, dlg))
        w.error.connect(lambda e: self._on_api_error(e))
        w.finished.connect(lambda: self._set_loading(False))
        self._keep_worker(w)
        w.start()

    def _on_update_done(self, res: dict, post_id: int, dlg: DialogPost):
        if not res["ok"]:
            err = ErrorParser.parse(res)
            if err.is_slug_error:
                dlg.show_slug_error(err.message)
                dlg.exec()
            else:
                self._set_error(err.message)
            return

        QMessageBox.information(
            self, "Post Diperbarui",
            f"Post #{post_id} berhasil diperbarui."
        )
        self.lbl_status.setText(f"Post #{post_id} berhasil diperbarui.")
        self._load_posts()

    def _hapus(self):
        post_id = self._get_selected_id()
        if post_id is None:
            QMessageBox.information(self, "Info", "Pilih post yang ingin dihapus.")
            return

        row = self.table.currentRow()
        title = self.table.item(row, 1).text() if row >= 0 else str(post_id)

        ret = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Hapus post berikut?\n\n"
            f"  ID    : {post_id}\n"
            f"  Title : {title}\n\n"
            f"  Semua komentar pada post ini juga akan ikut terhapus (cascade delete).\n"
            f"Tindakan ini tidak bisa dibatalkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return

        self._set_loading(True, "Menghapus post...")
        self._clear_error()

        w = worker_delete(post_id)
        w.result.connect(lambda res: self._on_delete_done(res, post_id))
        w.error.connect(lambda e: self._on_api_error(e))
        w.finished.connect(lambda: self._set_loading(False))
        self._keep_worker(w)
        w.start()

    def _on_delete_done(self, res: dict, post_id: int):
        if not res["ok"]:
            self._set_error(ErrorParser.parse(res).message)
            return

        self.panel_detail.clear()
        self._selected_id = None
        QMessageBox.information(
            self, "Post Dihapus",
            f"Post #{post_id} beserta seluruh komentarnya telah dihapus."
        )
        self.lbl_status.setText(f"Post #{post_id} dihapus.")
        self._load_posts()

    def _on_api_error(self, msg: str):
        self._set_loading(False)
        self._set_error(msg)
