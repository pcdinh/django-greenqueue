# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

import logging, os
log = logging.getLogger('greenqueue')

from greenqueue.utils import Singleton

from .base import BaseService
from .. import settings


class ZMQService(BaseService):
    def __init__(self):
        super(ZMQService, self).__init__()
        self.socket = None

    @classmethod
    def setup_gevent_spawn(cls):
        # posible, but untested gevent enable for this backend
        # this is incomplete, need zmq gevent patching.
        # import gevent
        # cls._back_process_callable = cls.process_callable
        # def _wrapped_process_callable(self, uuid, _callable, args, kwargs)::
        #     gevent.spawn(self._back_process_callable, *args, **kwargs)
        # cls.process_callable = _wrapped_process_callable
        pass
    
    def zmq(self):
        return import_module('zmq')

    def start(self):
        # load all modules
        self.load_modules()
        
        # bind socket if need
        if self.socket is None:
            ctx = self.zmq().Context.instance()
            self.socket = ctx.socket(self.zmq().PULL)
            self.socket.bind(settings.GREENQUEUE_BIND_ADDRESS)
            log.info("greenqueue: now listening on %s. (pid %s)",
                settings.GREENQUEUE_BIND_ADDRESS, os.getpid())

        # recv loop
        while True:
            message = self.socket.recv_pyobj()
            self.handle_message(message)

    def close(self):
        if self.socket is not None:
            self.socket.close()

    def send(self, name, args=[], kwargs={}):
        ctx = self.zmq.Context.instance()
        socket = ctx.socket(self.zmq.PUSH)
        socket.connect(settings.GREENQUEUE_BIND_ADDRESS)

        new_uuid = self.create_new_uuid()

        socket.send_pyobj({
            'name': name, 
            'args': args, 
            'kwargs':kwargs,
            'uuid': new_uuid,
        })

        return new_uuid
