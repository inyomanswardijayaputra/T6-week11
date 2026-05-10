from PySide6.QtCore import QThread, Signal
from api import client


class ApiWorker(QThread):

    result  = Signal(dict)  
    error   = Signal(str)   

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn     = fn
        self._args   = args
        self._kwargs = kwargs

    def run(self):
        try:
            res = self._fn(*self._args, **self._kwargs)
            self.result.emit(res)
        except Exception as e:
            self.error.emit(str(e))


def worker_get_all() -> ApiWorker:
    return ApiWorker(client.get_all_posts)

def worker_get_one(post_id: int) -> ApiWorker:
    return ApiWorker(client.get_post, post_id)

def worker_create(title, body, author, slug, status) -> ApiWorker:
    return ApiWorker(client.create_post, title, body, author, slug, status)

def worker_update(post_id, title, body, author, slug, status) -> ApiWorker:
    return ApiWorker(client.update_post, post_id, title, body, author, slug, status)

def worker_delete(post_id: int) -> ApiWorker:
    return ApiWorker(client.delete_post, post_id)
