##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Object Event Tests
"""
import doctest
import unittest

import zope.component.testing
from zope.lifecycleevent import ObjectCreatedEvent, created
from zope.lifecycleevent import Attributes, Sequence
from zope.lifecycleevent import ObjectModifiedEvent, modified
from zope.lifecycleevent import ObjectCopiedEvent, copied


class TestSequence(unittest.TestCase):

    def testSequence(self):

        from zope.interface import Interface, Attribute

        class ISample(Interface):
            field1 = Attribute("A test field")
            field2 = Attribute("A test field")
            field3 = Attribute("A test field")

        desc = Sequence(ISample, 'field1', 'field2')
        self.assertEqual(desc.interface, ISample)
        self.assertEqual(desc.keys, ('field1', 'field2'))


class TestAttributes(unittest.TestCase):
    def testAttributes(self):
        from zope.lifecycleevent.interfaces import IObjectMovedEvent
        desc = Attributes(IObjectMovedEvent, "newName", "newParent")
        self.assertEqual(desc.interface, IObjectMovedEvent)
        self.assertEqual(desc.attributes, ('newName', 'newParent'))


class TestObjectCreatedEvent(unittest.TestCase):

    klass = ObjectCreatedEvent
    object = object()

    def setUp(self):
        from zope.event import subscribers
        self._old_subscribers = subscribers[:]
        self.listener = []
        subscribers[:] = [self.listener.append]
        self.event = self.klass(self.object)

    def tearDown(self):
        from zope.event import subscribers
        subscribers[:] = self._old_subscribers

    def testGetObject(self):
        self.assertEqual(self.event.object, self.object)

    def testCreated(self):
        created(self.object)
        self.assertEqual(len(self.listener), 1)
        self.assertEqual(self.listener[-1].object, self.object)


class TestObjectModifiedEvent(unittest.TestCase):

    klass = ObjectModifiedEvent
    object = object()

    def setUp(self):
        from zope.event import subscribers
        self._old_subscribers = subscribers[:]
        self.listener = []
        subscribers[:] = [self.listener.append]
        self.event = self.klass(self.object)

    def tearDown(self):
        from zope.event import subscribers
        subscribers[:] = self._old_subscribers

    def testGetObject(self):
        self.assertEqual(self.event.object, self.object)

    def testModified(self):
        modified(self.object)
        self.assertEqual(len(self.listener), 1)
        self.assertEqual(self.listener[-1].object, self.object)

    def testAttributes(self):
        from zope.interface import implementer, Interface, Attribute

        class ISample(Interface):
            field = Attribute("A test field")

        @implementer(ISample)
        class Sample(object):
            pass
        obj = Sample()
        obj.field = 42
        attrs = Attributes(ISample, "field")

        modified(obj, attrs)
        self.assertEqual(self.listener[-1].object, obj)
        self.assertEqual(self.listener[-1].descriptions, (attrs,))


class TestObjectCopiedEvent(unittest.TestCase):

    klass = ObjectCopiedEvent
    original = object()
    object = object()

    def setUp(self):
        from zope.event import subscribers
        self._old_subscribers = subscribers[:]
        self.listener = []
        subscribers[:] = [self.listener.append]
        self.event = self.klass(self.object, self.original)

    def tearDown(self):
        from zope.event import subscribers
        subscribers[:] = self._old_subscribers

    def testGetObject(self):
        self.assertEqual(self.event.object, self.object)

    def testCopied(self):
        copied(self.object, self.original)
        self.assertEqual(len(self.listener), 1)
        self.assertEqual(self.listener[-1].object, self.object)
        self.assertEqual(self.listener[-1].original, self.original)


class TestObjectMovedEvent(unittest.TestCase):

    def _getTargetClass(self):
        from zope.lifecycleevent import ObjectMovedEvent
        return ObjectMovedEvent

    def _makeOne(self, *arg):
        return self._getTargetClass()(*arg)

    def test_it(self):
        ob = Context()
        old_parent = Context()
        new_parent = Context()
        event = self._makeOne(ob, old_parent, 'old_name', new_parent,
                              'new_name')
        self.assertEqual(event.object, ob)
        self.assertEqual(event.oldParent, old_parent)
        self.assertEqual(event.newParent, new_parent)
        self.assertEqual(event.newName, 'new_name')
        self.assertEqual(event.oldName, 'old_name')

    def test_verifyClass(self):
        from zope.interface.verify import verifyClass
        from zope.lifecycleevent.interfaces import IObjectMovedEvent
        verifyClass(IObjectMovedEvent, self._getTargetClass())

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        from zope.lifecycleevent.interfaces import IObjectMovedEvent
        verifyObject(IObjectMovedEvent,
                     self._makeOne(None, None, None, None, None))


class TestObjectAddedEvent(unittest.TestCase):

    def _getTargetClass(self):
        from zope.lifecycleevent import ObjectAddedEvent
        return ObjectAddedEvent

    def _makeOne(self, *arg):
        return self._getTargetClass()(*arg)

    def test_it(self):
        ob = Context()
        new_parent = Context()
        event = self._makeOne(ob, new_parent, 'new_name')
        self.assertEqual(event.object, ob)
        self.assertEqual(event.newParent, new_parent)
        self.assertEqual(event.newName, 'new_name')
        self.assertEqual(event.oldParent, None)
        self.assertEqual(event.oldName, None)

    def test_it_Nones(self):
        ob = Context()
        new_parent = Context()
        ob.__parent__ = new_parent
        ob.__name__ = 'new_name'
        event = self._makeOne(ob, None, None)
        self.assertEqual(event.object, ob)
        self.assertEqual(event.newParent, new_parent)
        self.assertEqual(event.newName, 'new_name')
        self.assertEqual(event.oldParent, None)
        self.assertEqual(event.oldName, None)

    def test_verifyClass(self):
        from zope.interface.verify import verifyClass
        from zope.lifecycleevent.interfaces import IObjectAddedEvent
        verifyClass(IObjectAddedEvent, self._getTargetClass())

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        from zope.lifecycleevent.interfaces import IObjectAddedEvent
        parent = Context()
        ob = Context()
        verifyObject(IObjectAddedEvent, self._makeOne(ob, parent, 'new_name'))


class TestObjectRemovedEvent(unittest.TestCase):

    def _getTargetClass(self):
        from zope.lifecycleevent import ObjectRemovedEvent
        return ObjectRemovedEvent

    def _makeOne(self, *arg):
        return self._getTargetClass()(*arg)

    def test_it(self):
        ob = Context()
        parent = Context()
        event = self._makeOne(ob, parent, 'name')
        self.assertEqual(event.object, ob)
        self.assertEqual(event.newParent, None)
        self.assertEqual(event.newName, None)
        self.assertEqual(event.oldParent, parent)
        self.assertEqual(event.oldName, 'name')

    def test_it_Nones(self):
        ob = Context()
        parent = Context()
        ob.__parent__ = parent
        ob.__name__ = 'name'
        event = self._makeOne(ob, None, None)
        self.assertEqual(event.object, ob)
        self.assertEqual(event.newParent, None)
        self.assertEqual(event.newName,  None)
        self.assertEqual(event.oldParent, parent)
        self.assertEqual(event.oldName, 'name')

    def test_verifyClass(self):
        from zope.interface.verify import verifyClass
        from zope.lifecycleevent.interfaces import IObjectRemovedEvent
        verifyClass(IObjectRemovedEvent, self._getTargetClass())

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        from zope.lifecycleevent.interfaces import IObjectRemovedEvent
        parent = object()
        ob = object()
        verifyObject(IObjectRemovedEvent, self._makeOne(ob, parent, 'new_name'))


class Context:
    pass


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestAttributes),
        unittest.makeSuite(TestSequence),
        unittest.makeSuite(TestObjectCreatedEvent),
        unittest.makeSuite(TestObjectModifiedEvent),
        unittest.makeSuite(TestObjectCopiedEvent),
        unittest.makeSuite(TestObjectMovedEvent),
        unittest.makeSuite(TestObjectAddedEvent),
        unittest.makeSuite(TestObjectRemovedEvent),
        doctest.DocFileSuite('README.txt',
                             tearDown=zope.component.testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
