from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QHBoxLayout,
)
from PySide6.QtCore import Qt


class BadgeLabel(QLabel):
    STYLES = {
        "published": "background:#dcfce7;color:#166534;border:1px solid #86efac;",
        "draft":     "background:#fef9c3;color:#854d0e;border:1px solid #fde68a;",
    }

    def __init__(self, status: str, parent=None):
        super().__init__(status.upper(), parent)
        style = self.STYLES.get(status.lower(), "background:#f3f4f6;color:#374151;")
        self.setStyleSheet(
            f"font-size:11px;font-weight:700;padding:2px 10px;"
            f"border-radius:10px;{style}"
        )
        self.setFixedHeight(22)


class CommentCard(QFrame):
    def __init__(self, comment: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("commentCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)

        header = QHBoxLayout()
        lbl_name = QLabel(comment.get("name", "—"))
        lbl_name.setObjectName("commentName")
        lbl_email = QLabel(comment.get("email", ""))
        lbl_email.setObjectName("commentEmail")
        header.addWidget(lbl_name)
        header.addStretch()
        header.addWidget(lbl_email)
        lay.addLayout(header)

        lbl_body = QLabel(comment.get("body", ""))
        lbl_body.setObjectName("commentBody")
        lbl_body.setWordWrap(True)
        lay.addWidget(lbl_body)


class PanelDetail(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panelDetail")
        self.setMinimumWidth(320)
        self._build_ui()
        self.clear()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        hdr = QFrame()
        hdr.setObjectName("panelHeader")
        h_lay = QVBoxLayout(hdr)
        h_lay.setContentsMargins(16, 12, 16, 12)
        lbl_t = QLabel("Detail Post")
        lbl_t.setObjectName("panelTitle")
        self.lbl_sub = QLabel("Klik baris tabel untuk melihat detail")
        self.lbl_sub.setObjectName("panelSubinfo")
        h_lay.addWidget(lbl_t)
        h_lay.addWidget(self.lbl_sub)
        root.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("scrollDetail")

        self.content = QWidget()
        self.content.setObjectName("detailContent")
        self.lay = QVBoxLayout(self.content)
        self.lay.setContentsMargins(16, 16, 16, 16)
        self.lay.setSpacing(14)
        self.lay.addStretch()

        scroll.setWidget(self.content)
        root.addWidget(scroll)

    def clear(self):
        self._clear_layout()
        placeholder = QLabel("Pilih post dari tabel\nuntuk melihat detail lengkapnya.")
        placeholder.setObjectName("detailPlaceholder")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setWordWrap(True)
        self.lay.insertWidget(0, placeholder)
        self.lbl_sub.setText("Klik baris tabel untuk melihat detail")

    def show_loading(self):
        self._clear_layout()
        lbl = QLabel("Memuat detail post...")
        lbl.setObjectName("detailPlaceholder")
        lbl.setAlignment(Qt.AlignCenter)
        self.lay.insertWidget(0, lbl)

    def show_post(self, post: dict):
        self._clear_layout()
        idx = 0

        def insert(w):
            nonlocal idx
            self.lay.insertWidget(idx, w)
            idx += 1

        top = QHBoxLayout()
        lbl_id = QLabel(f"# {post.get('id', '')}")
        lbl_id.setObjectName("detailID")
        badge = BadgeLabel(post.get("status", "draft"))
        top.addWidget(lbl_id)
        top.addStretch()
        top.addWidget(badge)
        top_frame = QFrame()
        top_frame.setLayout(top)
        insert(top_frame)

        lbl_title = QLabel(post.get("title", "—"))
        lbl_title.setObjectName("detailTitle")
        lbl_title.setWordWrap(True)
        insert(lbl_title)

        meta = QFrame()
        meta.setObjectName("detailMeta")
        m_lay = QVBoxLayout(meta)
        m_lay.setContentsMargins(12, 8, 12, 8)
        m_lay.setSpacing(4)

        def meta_row(label: str, val: str):
            row = QHBoxLayout()
            l = QLabel(label)
            l.setObjectName("metaLabel")
            l.setFixedWidth(60)
            v = QLabel(val or "—")
            v.setObjectName("metaValue")
            v.setWordWrap(True)
            row.addWidget(l)
            row.addWidget(v, 1)
            m_lay.addLayout(row)

        meta_row("Penulis:", post.get("author", "—"))
        meta_row("Slug:", post.get("slug", "—"))
        insert(meta)

        lbl_body_hdr = QLabel("Konten")
        lbl_body_hdr.setObjectName("detailSectionHdr")
        insert(lbl_body_hdr)

        lbl_body = QLabel(post.get("body", "—"))
        lbl_body.setObjectName("detailBody")
        lbl_body.setWordWrap(True)
        insert(lbl_body)

        comments = post.get("comments", [])
        lbl_cmt_hdr = QLabel(f"Komentar ({len(comments)})")
        lbl_cmt_hdr.setObjectName("detailSectionHdr")
        insert(lbl_cmt_hdr)

        if comments:
            for c in comments:
                insert(CommentCard(c))
        else:
            lbl_no = QLabel("Belum ada komentar.")
            lbl_no.setObjectName("detailPlaceholder")
            insert(lbl_no)

        self.lbl_sub.setText(f"ID {post.get('id')} • {post.get('author', '')}")

    def show_error(self, msg: str):
        self._clear_layout()
        lbl = QLabel(f"{msg}")
        lbl.setObjectName("detailError")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        self.lay.insertWidget(0, lbl)

    def _clear_layout(self):
        while self.lay.count() > 1:
            item = self.lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            else:
                pass
