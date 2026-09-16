import json
import queue
import threading

_lock = threading.Lock()
_subscribers = []  # lista di Queue, una per ogni client connesso


def subscribe():
    q = queue.Queue(maxsize=100)
    with _lock:
        _subscribers.append(q)
    return q


def unsubscribe(q):
    with _lock:
        if q in _subscribers:
            _subscribers.remove(q)


def broadcast(event_type, data):
    message = json.dumps({'type': event_type, 'data': data})
    with _lock:
        subs = list(_subscribers)
    for q in subs:
        try:
            q.put_nowait(message)
        except queue.Full:
            pass


def format_sse(message):
    return f"data: {message}\n\n"
