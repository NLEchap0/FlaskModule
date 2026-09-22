# eventi in tempo reale: una coda di messaggi per ogni browser collegato
import json
import queue

subscribers = []


def subscribe():
    q = queue.Queue()
    subscribers.append(q)
    return q


def unsubscribe(q):
    if q in subscribers:
        subscribers.remove(q)


def broadcast(event_type, data):
    message = json.dumps({'type': event_type, 'data': data})
    for q in subscribers:
        q.put(message)


def format_sse(message):
    return 'data: ' + message + '\n\n'
