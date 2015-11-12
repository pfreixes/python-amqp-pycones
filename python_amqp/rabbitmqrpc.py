# -*- coding: utf-8 -*-
"""
Rabbitmq rpc client interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Derivated and relaxed work made by M2M.

It requires the installation of the RabbitMQ Management plugin. It is
included in the standard RabbitMQ distribution, all you have to do is
enable it with the rommand ``rabbitmq-plugins enable rabbitmq_management``.
More information here: https://www.rabbitmq.com/management.html
"""
import urllib
import requests
from json import loads, dumps

# Api Endpoints
_CONNECTIONS = '/api/connections'
_CONNECTION_ITEM = _CONNECTIONS + '/%2f/{name}'
_EXCHANGES = '/api/exchanges'
_EXCHANGE_ITEM = _EXCHANGES + '/%2f/{name}'
_BINDINGS = '/api/bindings'
_BINDING_POST = _BINDINGS + '/%2f/e/{source}/{dest_type}/{dest}'
_BINDING_ITEM = _BINDING_POST + '/{routing}'
_QUEUES = '/api/queues'
_QUEUE_ITEM = _QUEUES + '/%2f/{name}'


def prepare_session(user=None, password=None):
    """ Returns a requests session with the basic auth required by the rabbitmq plugin """
    session = requests.Session()
    session.auth = (user or 'guest', password or 'guest')
    session.headers.update({'Content-Type': 'application/json'})
    return session

def delete_queue(queue_name, host='localhost', user=None, password=None):
    """ Deletes queue """
    session = prepare_session(user=user, password=password)
    full_host = 'http://{}:15672'.format(host)
    res = session.delete('{0}{1}'.format(full_host, _QUEUE_ITEM.format(name=queue_name)))
    return True if res.status_code == 204 else False

def info_queue(queue_name, host='localhost', user=None, password=None):
    """ Info queue """
    session = prepare_session(user=user, password=password)
    full_host = 'http://{}:15672'.format(host)
    res = session.get('{0}{1}'.format(full_host, _QUEUE_ITEM.format(name=queue_name)))
    return loads(res.text) if res.status_code == 200 else None

def purge_queue(queue_name, host='localhost', user=None, password=None):
    """ Purge queue """
    session = prepare_session(user=user, password=password)
    full_host = 'http://{}:15672'.format(host)
    res = session.delete('{0}{1}/contents'.format(full_host, _QUEUE_ITEM.format(name=queue_name)))
    return True if res.status_code == 204 else False

def list_queues(host='localhost', user=None, password=None):
    """ List queues"""
    session = prepare_session(user=user, password=password)
    full_host = 'http://{}:15672'.format(host)
    res = session.get('{0}{1}'.format(full_host, _QUEUES))
    return [queue['name'] for queue in loads(res.text)] if res.status_code == 200 else None

def create_queue(queue_name, host='localhost', user=None, password=None):
    """ Adds a new queue.

    Returns the attributes of the new queue, or False if the insertion went wrong """
    session = prepare_session(user=user, password=password)
    body = {
        # add here future body params
    }
    full_host = 'http://{}:15672'.format(host)
    res = session.put('{0}{1}'.format(full_host, _QUEUE_ITEM.format(name=queue_name)),
                      data=dumps(body))

    return True if res.status_code == 204 else False

def delete_exchange(exchange_name, host='localhost', user=None, password=None):
    """ Deletes exchange """
    session = prepare_session(user=user, password=password)
    base_uri = 'http://{}:15672'.format(host)
    res = session.delete('{0}{1}'.format(base_uri, _EXCHANGE_ITEM.format(name=exchange_name)))
    return {'deleted': 'success'} if res.status_code == 204 else False

def create_exchange(name, _type, auto_delete=None, durable=None, internal=None, host='localhost', user=None, password=None):
    """ Adds a new exchange.

    Returns the attributes of the new exchange, or False if the insertion went wrong """
    session = prepare_session(user=user, password=password)
    body = {
        'type': _type
    }

    # See default values in http://localhost:15672/api
    if auto_delete is not None:
        body['auto_delete'] = auto_delete
    if durable is not None:
        body['durable'] = durable
    if internal is not None:
        body['internal'] = internal

    base_uri = 'http://{}:15672'.format(host)
    res = session.put('{0}{1}'.format(base_uri, _EXCHANGE_ITEM.format(name=name)),
                      data=dumps(body))
    return True if res.status_code == 204 else False


def set_binding(source, dest, dest_type, routing_key=None, host='localhost', user=None, password=None):
    """ Sets a binding between source, which must be an exchange, and dest, which
    can be either an exchange or a queue.

    :param source: Exchange from which the messages come
    :type source: Str.
    :param dest: Destination of the messages. Can be either an exchange or a queue.
    :type dest: Str.
    :param dest_type: Defines the type of destination. Accepts either "exchange" or "queue"
    :type dest_type: Str.
    :rtype: Dict or False
    :param routing_key: topic through which route the messages, use None for fanout
    :type routing_key: Str.
    """
    _DEST_TYPES = {'exchange': 'e', 'queue': 'q'}
    try:
        _dest_type = _DEST_TYPES[dest_type]
    except KeyError:
        raise ValueError('Error setting binding between {0} and {1}.\n'
                         'Destination type must be either "exchange" or "queue".'
                         ' Current: {2}'.format(source, dest, dest_type))
    session = prepare_session(user=user, password=password)
    body = {'routing_key': routing_key if routing_key else None}
    base_uri = 'http://{}:15672'.format(host)
    res = session.post('{0}{1}'.format(base_uri, _BINDING_POST.format(source=source,
                                                                      dest=dest,
                                                                      dest_type=_dest_type)),
                       data=dumps(body))
    return True if res.status_code == 201 else False


def bind_exchange(dest, source, routing_key):
    """ Helper function to bind one exchange to another """
    return set_binding(routing_key, source, dest, 'exchange')


def delete_bind_exchange(dest, source, routing_key):
    """ Helper function to delete one existing binding between one exchange to another """
    return delete_binding(routing_key, source, dest, 'exchange')


def bind_queue(queue, exchange, routing_key):
    """ Helper function to bind a queue to an exchange """
    return set_binding(routing_key, exchange, queue, 'queue')


def list_bindings_between_entities(source, dest, dest_type):
    """ List all bindings between source, which must be an exchange, and dest, which
    can be either an exchange or a queue.

    Returns a list of all bindings.

    :param source: Exchange from which the messages come
    :type source: Str.
    :param dest: Destination of the messages. Can be either an exchange or a queue.
    :type dest: Str.
    :param dest_type: Defines the type of destination. Accepts either "exchange" or "queue"
    :type dest_type: Str.
    :rtype: List or False

    """
    _DEST_TYPES = {'exchange': 'e', 'queue': 'q'}
    try:
        _dest_type = _DEST_TYPES[dest_type]
    except KeyError:
        raise RuntimeError('Error setting binding between {0} and {1}.\n'
                           'Destination type must be either "exchange" or "queue".'
                           ' Current: {2}'.format(source, dest, dest_type))
    session = _prepare_session()
    _SERVER_HOST = 'http://{}:15672'.format(get_settings().AMQP_HOST)
    res = session.get('{0}{1}'.format(_SERVER_HOST, _BINDING_POST.format(source=source,
                                                                         dest=dest,
                                                                         dest_type=_dest_type)))
    return loads(res.text) if res.status_code == 200 else False


def list_bindings():
    """ list all bindings.

    The returned list is actually a list of dicts with all the attributes that
    the plugin API returns

    """
    session = _prepare_session()
    _SERVER_HOST = 'http://{}:15672'.format(get_settings().AMQP_HOST)
    res = session.get('{0}{1}'.format(_SERVER_HOST, _BINDINGS))
    return loads(res.text)


if __name__ == "__main__":
   import sys
   print info_queue(sys.argv[1])['messages']
   print purge_queue(sys.argv[1]) 
