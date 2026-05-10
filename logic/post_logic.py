from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PostRow:
    id: int
    title: str
    author: str
    status: str


@dataclass
class PostDetail:
    id: int
    title: str
    body: str
    author: str
    slug: str
    status: str
    comments: list[dict]


@dataclass
class FormData:
    title: str
    body: str
    author: str
    slug: str
    status: str


@dataclass
class ParsedError:
    message: str
    is_slug_error: bool  
    is_not_found: bool    
    status_code: int

class ResponseParser:
    @staticmethod
    def unwrap(res: dict) -> dict | list:
        raw = res.get("data", {})
        if isinstance(raw, dict) and "data" in raw:
            return raw["data"]
        return raw

    @staticmethod
    def to_post_rows(res: dict) -> list[PostRow]:
        raw = ResponseParser.unwrap(res)
        posts = raw if isinstance(raw, list) else []
        return [
            PostRow(
                id=p.get("id", 0),
                title=p.get("title", ""),
                author=p.get("author", ""),
                status=p.get("status", "draft"),
            )
            for p in posts
        ]

    @staticmethod
    def to_post_detail(res: dict) -> PostDetail:
        raw = ResponseParser.unwrap(res)
        if isinstance(raw, list):
            raw = raw[0] if raw else {}
        return PostDetail(
            id=raw.get("id", 0),
            title=raw.get("title", ""),
            body=raw.get("body", ""),
            author=raw.get("author", ""),
            slug=raw.get("slug", ""),
            status=raw.get("status", "draft"),
            comments=raw.get("comments", []),
        )

    @staticmethod
    def created_id(res: dict) -> int | str:
        raw = ResponseParser.unwrap(res)
        if isinstance(raw, dict):
            return raw.get("id", "?")
        return "?"

class ErrorParser:
    _ERROR_KEYS = ("detail", "message", "error", "msg")

    @classmethod
    def parse(cls, res: dict) -> ParsedError:
        status  = res.get("status", 0)
        data    = res.get("data", {})
        message = cls._extract_message(data, status)

        return ParsedError(
            message=message,
            is_slug_error=cls._is_slug_error(status, data),
            is_not_found=status == 404,
            status_code=status,
        )

    @classmethod
    def _extract_message(cls, data: dict | str, status: int) -> str:
        if isinstance(data, dict):
            for key in cls._ERROR_KEYS:
                if key not in data:
                    continue
                val = data[key]
                # FastAPI validation errors → list of {loc, msg, type}
                if isinstance(val, list):
                    parts = []
                    for item in val:
                        parts.append(
                            item.get("msg", str(item))
                            if isinstance(item, dict) else str(item)
                        )
                    return " | ".join(parts)
                return str(val)
            
        if status == 422:
            return "Validasi gagal (422) — slug kemungkinan sudah digunakan."
        if status == 404:
            return "Post tidak ditemukan (404)."
        if status == 0:
            return str(data) if data else "Tidak dapat terhubung ke server."
        return f"Error {status}: {data}"

    @classmethod
    def _is_slug_error(cls, status: int, data: dict) -> bool:
        if status != 422:
            return False
        raw_str = str(data).lower()
        return "slug" in raw_str or status == 422  # 422 selalu dianggap slug error

class FormValidator:

    @staticmethod
    def validate(data: dict) -> list[str]:
        errors = []
        if not data.get("title", "").strip():
            errors.append("• Title wajib diisi.")
        if not data.get("body", "").strip():
            errors.append("• Body wajib diisi.")
        if not data.get("author", "").strip():
            errors.append("• Author wajib diisi.")
        slug = data.get("slug", "").strip()
        if not slug:
            errors.append("• Slug wajib diisi.")
        elif not FormValidator._valid_slug(slug):
            errors.append("• Slug hanya boleh berisi huruf kecil, angka, dan tanda hubung (-).")
        return errors

    @staticmethod
    def _valid_slug(slug: str) -> bool:
        import re
        return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug))

    @staticmethod
    def to_form_data(raw: dict) -> FormData:
        return FormData(
            title=raw.get("title", "").strip(),
            body=raw.get("body", "").strip(),
            author=raw.get("author", "").strip(),
            slug=raw.get("slug", "").strip(),
            status=raw.get("status", "draft"),
        )


class SlugGenerator:

    @staticmethod
    def from_title(title: str) -> str:
        import re
        slug = title.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug

class StatusFormatter:
    COLORS = {
        "published": {
            "fg": "#166534",
            "bg": "#dcfce7",
        },
        "draft": {
            "fg": "#854d0e",
            "bg": "#fef9c3",
        },
    }

    @classmethod
    def colors(cls, status: str) -> tuple[str, str]:
        c = cls.COLORS.get(status.lower(), {"fg": "#374151", "bg": "#f3f4f6"})
        return c["fg"], c["bg"]
