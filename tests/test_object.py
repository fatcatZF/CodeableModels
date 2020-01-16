import nose
from nose.tools import ok_, eq_
from testCommons import neq_, exceptionExpected_
from parameterized import parameterized

from codeable_models import CMetaclass, CClass, CObject, CAttribute, CException, CEnum, CBundle, add_links

class TestObject():
    def setUp(self):
        self.mcl = CMetaclass("MCL")
        self.cl = CClass(self.mcl, "CL", attributes = {"i" : 1})

    def testCreationOfOneObject(self):
        eq_(self.cl.objects, [])
        o1 = CObject(self.cl, "o")
        o2 = self.cl.objects[0]
        eq_(o1.name, "o")
        eq_(o1, o2)
        eq_(o2.classifier, self.cl)

    def testCreateObjectWrongArgTypes(self):
        try:
            CObject("CL", "o1")
            exceptionExpected_()
        except CException as e: 
            eq_("'CL' is not a class", e.value)
        try:
            CObject(self.mcl, "o1")
            exceptionExpected_()
        except CException as e: 
            eq_("'MCL' is not a class", e.value)
    
    def testCreationOf3Objects(self):
        o1 = CObject(self.cl, "o1")
        o2 = CObject(self.cl, "o2")
        o3 = CObject(self.cl, "o3")
        eq_(set(self.cl.objects), set([o1, o2, o3]))
  
    def testCreationOfUnnamedObject(self):
        o1 = CObject(self.cl)
        o2 = CObject(self.cl)
        o3 = CObject(self.cl, "x")
        eq_(set(self.cl.objects), set([o1, o2, o3]))
        eq_(o1.name, None)
        eq_(o2.name, None)
        eq_(o3.name, "x")

    def testDeleteObject(self):
        o = CObject(self.cl, "o")
        o.delete()
        eq_(set(self.cl.objects), set())

        o1 = CObject(self.cl, "o1")
        o2 = CObject(self.cl, "o2")
        o3 = CObject(self.cl, "o3")
        o3.set_value("i", 7)

        o1.delete()
        eq_(set(self.cl.objects), set([o2, o3]))
        o3.delete()
        eq_(set(self.cl.objects), set([o2]))

        eq_(o3.classifier, None)
        eq_(set(self.cl.objects), set([o2]))
        eq_(o3.name, None)
        eq_(o3.bundles, [])
        try:
            o3.get_value("i")
            exceptionExpected_()
        except CException as e: 
            eq_("can't get value 'i' on deleted object", e.value)

    def testClassInstanceRelation(self):
        cl1 = CClass(self.mcl, "CL1")
        cl2 = CClass(self.mcl, "CL2")
        eq_(set(cl1.objects), set())

        o1 = CObject(cl1, "O1")
        o2 = CObject(cl1, "O2")
        o3 = CObject(cl2, "O3")
        eq_(set(cl1.objects), set([o1, o2]))
        eq_(set(cl2.objects), set([o3]))
        eq_(o1.classifier, cl1)
        eq_(o2.classifier, cl1)
        eq_(o3.classifier, cl2)

    def testClassInstanceRelationDeletionFromObject(self):
        cl1 = CClass(self.mcl, "CL1")
        o1 = CObject(cl1, "O1")
        o1.delete()
        eq_(set(cl1.objects), set())

        o1 = CObject(cl1, "O1")
        o2 = CObject(cl1, "O2")
        o3 = CObject(cl1, "O3")

        eq_(set(cl1.objects), set([o1, o2, o3]))
        o1.delete()
        eq_(set(cl1.objects), set([o2, o3]))
        o3.delete()
        eq_(set(cl1.objects), set([o2]))
        eq_(o1.classifier, None)
        eq_(o2.classifier, cl1)
        eq_(o3.classifier, None)
        o2.delete()
        eq_(set(cl1.objects), set())
        eq_(o1.classifier, None)
        eq_(o2.classifier, None)
        eq_(o3.classifier, None)

    def testClassifierChange(self):
        cl1 = CClass(self.mcl, "CL1")
        cl2 = CClass(self.mcl, "CL2")
        o1 = CObject(cl1, "O1")
        o1.classifier = cl2
        eq_(o1.classifier, cl2)
        eq_(cl1.objects, [])
        eq_(cl2.objects, [o1])

    def testClassifierChangeNullInput(self):
        cl1 = CClass(self.mcl, "CL1")
        o1 = CObject(cl1, "O1")
        try:
            o1.classifier = None
            exceptionExpected_()
        except CException as e: 
            eq_("'None' is not a class", e.value)

    def testClassifierChangeWrongInputType(self):
        cl1 = CClass(self.mcl, "CL1")
        o1 = CObject(cl1, "O1")
        try:
            o1.classifier = self.mcl
            exceptionExpected_()
        except CException as e: 
            ok_(e.value.endswith("' is not a class"))


    def testClassIsDeletedInConstructor(self):
        c1 = CClass(self.mcl, "CL1")
        c1.delete()
        try:
            CObject(c1, "O1")
            exceptionExpected_()
        except CException as e: 
            ok_(e.value.endswith("cannot access named element that has been deleted"))

    def testClassIsDeletedInClassifierMethod(self):
        c1 = CClass(self.mcl, "CL1")
        c2 = CClass(self.mcl, "CL2")
        o1 = CObject(c2, "O1")
        c1.delete()
        try:
            o1.classifier = c1
            exceptionExpected_()
        except CException as e: 
            ok_(e.value.endswith("cannot access named element that has been deleted"))

    def testClassIsNoneInConstructor(self):
        try:
            CObject(None, "O1")
            exceptionExpected_()
        except CException as e: 
            ok_(e.value.endswith("'None' is not a class"))



    def testGetConnectedElements_WrongKeywordArg(self):
        o1 = CObject(self.cl, "o1")
        try:
            o1.get_connected_elements(a ="o1")
            exceptionExpected_()
        except CException as e: 
            eq_(e.value, "unknown keyword argument 'a', should be one of: ['add_bundles', 'process_bundles', 'stop_elements_inclusive', 'stop_elements_exclusive']")

    def testGetConnectedElementsEmpty(self):
        o1 = CObject(self.cl, "o1")
        eq_(set(o1.get_connected_elements()), set([o1]))

    mcl = CMetaclass("MCL")
    cl1 = CClass(mcl, "C")
    cl2 = CClass(mcl, "C")
    cl1.association(cl2, "*->*")
    o1 = CObject(cl1, "o1")
    o2 = CObject(cl2, "o2")
    o3 = CObject(cl2, "o3")
    o4 = CObject(cl2, "o4")
    o5 = CObject(cl2, "o5")
    add_links({o1: [o2, o3, o4, o5]})
    o6 = CObject(cl2, "o6")
    add_links({o6: o1})
    o7 = CObject(cl1, "o7")
    o8 = CObject(cl2, "o8")
    o9 = CObject(cl2, "o9")
    add_links({o7: [o8, o9]})
    o10 = CObject(cl1, "o10")
    o11 = CObject(cl2, "o11")
    add_links({o10: o11})
    o12 = CObject(cl1, "o12")
    o13 = CObject(cl2, "o13")
    add_links({o12: o11})
    bsub = CBundle("bsub", elements = [o13])
    b1 = CBundle("b1", elements = [o1, o2, o3, bsub, o7])
    b2 = CBundle("b2", elements = [o7, o10, o11, o12])

    allTestElts = [o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, b1, b2, bsub]

    @parameterized.expand([
        (allTestElts, {"process_bundles": True}, set([o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13])),
        (allTestElts, {"process_bundles": True, "add_bundles": True}, set([o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, b1, b2, bsub])),
        ([o1], {"process_bundles": True}, set([o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13])),
        ([o1], {"process_bundles": True, "add_bundles": True}, set([o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, b1, b2, bsub])),
        ([o7], {}, set([o7, o8, o9])),
        ([o7], {"add_bundles": True}, set([o7, o8, o9, b1, b2])),
    ])
    def testGetConnectedElements(self, testElements, kwargsDict, connectedElementsResult):
        for elt in testElements:
             eq_(set(elt.get_connected_elements(**kwargsDict)), connectedElementsResult)

    def testGetConnectedElements_stop_elements_inclusiveWrongTypes(self):
        o1 = CObject(self.cl, "o1")
        try:
            o1.get_connected_elements(stop_elements_inclusive ="o1")
            exceptionExpected_()
        except CException as e: 
            eq_(e.value, "expected one element or a list of stop elements, but got: 'o1'")
        try:
            o1.get_connected_elements(stop_elements_inclusive = ["o1"])
            exceptionExpected_()
        except CException as e: 
            eq_(e.value, "expected one element or a list of stop elements, but got: '['o1']' with element of wrong type: 'o1'")

    @parameterized.expand([
        ([o1], {"stop_elements_exclusive" : [o1]}, set()),
        ([o1], {"stop_elements_inclusive" : [o3, o6]}, set([o1, o2, o3, o4, o5, o6])),
        ([o1], {"stop_elements_exclusive" : [o3, o6]}, set([o1, o2, o4, o5])),
        ([o1], {"stop_elements_inclusive" : [o3, o6], "stop_elements_exclusive" : [o3]}, set([o1, o2, o4, o5, o6])),
        ([o7], {"stop_elements_inclusive" : [b2], "stop_elements_exclusive" : [b1], "process_bundles": True, "add_bundles": True}, set([o7, b2, o8, o9])),
        ([o7], {"stop_elements_exclusive" : [b1, b2], "process_bundles": True, "add_bundles": True}, set([o7, o8, o9])),
    ])
    def testGetConnectedElements_stop_elements_inclusive(self, testElements, kwargsDict, connectedElementsResult):
        for elt in testElements:
             eq_(set(elt.get_connected_elements(**kwargsDict)), connectedElementsResult)


if __name__ == "__main__":
    nose.main()