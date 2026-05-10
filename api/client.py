import json
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "https://api.pahrul.my.id/api"
TIMEOUT  = 10  # detik


def _request(method: str, path: str, payload: dict = None) -> dict:
    url  = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload else None

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept",       "application/json")

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
            return {"ok": True, "status": resp.status, "data": json.loads(body) if body else {}}

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err_data = json.loads(body)
        except Exception:
            err_data = {"detail": body}
        return {"ok": False, "status": e.code, "data": err_data}

    except urllib.error.URLError as e:
        return {"ok": False, "status": 0, "data": {"detail": f"Koneksi gagal: {e.reason}"}}

    except TimeoutError:
        return {"ok": False, "status": 0, "data": {"detail": "Request timeout (>10 detik)."}}

def get_all_posts() -> dict:
    return _request("GET", "/posts")


def get_post(post_id: int) -> dict:
    return _request("GET", f"/posts/{post_id}")


def create_post(title: str, body: str, author: str, slug: str, status: str) -> dict:
    return _request("POST", "/posts", {
        "title": title, "body": body,
        "author": author, "slug": slug, "status": status,
    })


def update_post(post_id: int, title: str, body: str, author: str, slug: str, status: str) -> dict:
    return _request("PUT", f"/posts/{post_id}", {
        "title": title, "body": body,
        "author": author, "slug": slug, "status": status,
    })


def delete_post(post_id: int) -> dict:
    return _request("DELETE", f"/posts/{post_id}")
