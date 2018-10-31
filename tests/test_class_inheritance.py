import nose
from nose.tools import ok_, eq_
from testCommons import neq_, exceptionExpected_
from parameterized import parameterized
import re

from codeableModels import CMetaclass, CStereotype, CClass, CObject, CAttribute, CException, CEnum

class TestClassInheritance():
    def setUp(self):
        self.mcl = CMetaclass("MCL")

    def testClassNoInheritance(self):
        t = CClass(self.mcl, "T")
        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), set())
        eq_(set(t.allSuperclasses), set())
        eq_(set(t.allSubclasses), set())

    def testClassSuperclassesEmptyInput(self):
        m1 = CClass(self.mcl, "M1", superclasses = [])
        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set())

    def testClassSuperclassesNoneInput(self):
        m1 = CClass(self.mcl, "M1", superclasses = None)
        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set())

    def testClassSimpleInheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses = t)
        m2 = CClass(self.mcl, "M2", superclasses = t)
        b1 = CClass(self.mcl, "B1", superclasses = m1)
        b2 = CClass(self.mcl, "B2", superclasses = m1)
        b3 = CClass(self.mcl, "B3", superclasses = t)

        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), set([m1, m2, b3]))
        eq_(set(t.allSuperclasses), set())
        eq_(set(t.allSubclasses), set([m1, m2, b1, b2, b3]))

        eq_(set(m1.superclasses), set([t]))
        eq_(set(m1.subclasses), set([b1, b2]))
        eq_(set(m1.allSuperclasses), set([t]))
        eq_(set(m1.allSubclasses), set([b1, b2]))

        eq_(set(m2.superclasses), set([t]))
        eq_(set(m2.subclasses), set())
        eq_(set(m2.allSuperclasses), set([t]))
        eq_(set(m2.allSubclasses), set())

        eq_(set(b1.superclasses), set([m1]))
        eq_(set(b1.subclasses), set())
        eq_(set(b1.allSuperclasses), set([t, m1]))
        eq_(set(b1.allSubclasses), set())

        eq_(set(b2.superclasses), set([m1]))
        eq_(set(b2.subclasses), set())
        eq_(set(b2.allSuperclasses), set([t, m1]))
        eq_(set(b2.allSubclasses), set())

        eq_(set(b3.superclasses), set([t]))
        eq_(set(b3.subclasses), set())
        eq_(set(b3.allSuperclasses), set([t]))
        eq_(set(b3.allSubclasses), set())

    def testClassInheritanceDoubleAssignment(self):
        t = CClass(self.mcl, "T")
        try:
            CClass(self.mcl, "C1", superclasses = [t, t])
            exceptionExpected_()
        except CException as e: 
            eq_("'T' is already a superclass of 'C1'", e.value) 
        c1 = self.mcl.getClass("C1")
        eq_(c1.metaclass, self.mcl)
        eq_(c1.name, "C1")
        eq_(t.name, "T")
        eq_(set(c1.superclasses), set([t]))

    def testClassInheritanceDeleteTopClass(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses = [t])
        m2 = CClass(self.mcl, "M2", superclasses = [t])
        b1 = CClass(self.mcl, "B1", superclasses = [m1])
        b2 = CClass(self.mcl, "B2", superclasses = [m1])
        b3 = CClass(self.mcl, "B3", superclasses = [t])

        t.delete()

        eq_(t.name, None)
        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), set())
        eq_(set(t.allSuperclasses), set())
        eq_(set(t.allSubclasses), set())

        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set([b1, b2]))
        eq_(set(m1.allSuperclasses), set())
        eq_(set(m1.allSubclasses), set([b1, b2]))

        eq_(set(m2.superclasses), set())
        eq_(set(m2.subclasses), set())
        eq_(set(m2.allSuperclasses), set())
        eq_(set(m2.allSubclasses), set())

        eq_(set(b1.superclasses), set([m1]))
        eq_(set(b1.subclasses), set())
        eq_(set(b1.allSuperclasses), set([m1]))
        eq_(set(b1.allSubclasses), set())

        eq_(set(b2.superclasses), set([m1]))
        eq_(set(b2.subclasses), set())
        eq_(set(b2.allSuperclasses), set([m1]))
        eq_(set(b2.allSubclasses), set())

        eq_(set(b3.superclasses), set())
        eq_(set(b3.subclasses), set())
        eq_(set(b3.allSuperclasses), set())
        eq_(set(b3.allSubclasses), set())

    def testClassInheritanceDeleteInnerClass(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses = [t])
        m2 = CClass(self.mcl, "M2", superclasses = [t])
        b1 = CClass(self.mcl, "B1", superclasses = [m1])
        b2 = CClass(self.mcl, "B2", superclasses = [m1])
        b3 = CClass(self.mcl, "B3", superclasses = [t])

        m1.delete()

        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), set([m2, b3]))
        eq_(set(t.allSuperclasses), set())
        eq_(set(t.allSubclasses), set([m2, b3]))

        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set())
        eq_(set(m1.allSuperclasses), set())
        eq_(set(m1.allSubclasses), set())

        eq_(set(m2.superclasses), set([t]))
        eq_(set(m2.subclasses), set())
        eq_(set(m2.allSuperclasses), set([t]))
        eq_(set(m2.allSubclasses), set())

        eq_(set(b1.superclasses), set())
        eq_(set(b1.subclasses), set())
        eq_(set(b1.allSuperclasses), set())
        eq_(set(b1.allSubclasses), set())

        eq_(set(b2.superclasses), set())
        eq_(set(b2.subclasses), set())
        eq_(set(b2.allSuperclasses), set())
        eq_(set(b2.allSubclasses), set())

        eq_(set(b3.superclasses), set([t]))
        eq_(set(b3.subclasses), set())
        eq_(set(b3.allSuperclasses), set([t]))
        eq_(set(b3.allSubclasses), set())

    def testClassSuperclassesReassignment(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses = [t])
        m2 = CClass(self.mcl, "M2", superclasses = [t])
        b1 = CClass(self.mcl, "B1", superclasses = [m1])
        b2 = CClass(self.mcl, "B2", superclasses = [m1])
        b3 = CClass(self.mcl, "B3", superclasses = [t])

        m1.superclasses = []
        b1.superclasses = []
        b2.superclasses = []

        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), set([m2, b3]))
        eq_(set(t.allSuperclasses), set())
        eq_(set(t.allSubclasses), set([m2, b3]))

        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set())
        eq_(set(m1.allSuperclasses), set())
        eq_(set(m1.allSubclasses), set())

        eq_(set(m2.superclasses), set([t]))
        eq_(set(m2.subclasses), set())
        eq_(set(m2.allSuperclasses), set([t]))
        eq_(set(m2.allSubclasses), set())

        eq_(set(b1.superclasses), set())
        eq_(set(b1.subclasses), set())
        eq_(set(b1.allSuperclasses), set())
        eq_(set(b1.allSubclasses), set())

        eq_(set(b2.superclasses), set())
        eq_(set(b2.subclasses), set())
        eq_(set(b2.allSuperclasses), set())
        eq_(set(b2.allSubclasses), set())

        eq_(set(b3.superclasses), set([t]))
        eq_(set(b3.subclasses), set())
        eq_(set(b3.allSuperclasses), set([t]))
        eq_(set(b3.allSubclasses), set())

    def testClassMultipleInheritance(self):
        t1 = CClass(self.mcl, "T1")
        t2 = CClass(self.mcl, "T2")
        t3 = CClass(self.mcl, "T3")
        m1 = CClass(self.mcl, "M1", superclasses = [t1, t3])
        m2 = CClass(self.mcl, "M2", superclasses = [t2, t3])
        b1 = CClass(self.mcl, "B1", superclasses = [m1])
        b2 = CClass(self.mcl, "B2", superclasses = [m1, m2])
        b3 = CClass(self.mcl, "B3", superclasses = [m2, m1])

        eq_(set(t1.superclasses), set())
        eq_(set(t1.subclasses), set([m1]))
        eq_(set(t1.allSuperclasses), set())
        eq_(set(t1.allSubclasses), set([m1, b1, b2, b3]))

        eq_(set(t2.superclasses), set())
        eq_(set(t2.subclasses), set([m2]))
        eq_(set(t2.allSuperclasses), set())
        eq_(set(t2.allSubclasses), set([m2, b3, b2]))

        eq_(set(t3.superclasses), set())
        eq_(set(t3.subclasses), set([m2, m1]))
        eq_(set(t3.allSuperclasses), set())
        eq_(set(t3.allSubclasses), set([m2, m1, b1, b2, b3]))

        eq_(set(m1.superclasses), set([t1, t3]))
        eq_(set(m1.subclasses), set([b1, b2, b3]))
        eq_(set(m1.allSuperclasses), set([t1, t3]))
        eq_(set(m1.allSubclasses), set([b1, b2, b3]))

        eq_(set(m2.superclasses), set([t2, t3]))
        eq_(set(m2.subclasses), set([b2, b3]))
        eq_(set(m2.allSuperclasses), set([t2, t3]))
        eq_(set(m2.allSubclasses), set([b2, b3]))

        eq_(set(b1.superclasses), set([m1]))
        eq_(set(b1.subclasses), set())
        eq_(set(b1.allSuperclasses), set([m1, t1, t3]))
        eq_(set(b1.allSubclasses), set())

        eq_(set(b2.superclasses), set([m1, m2]))
        eq_(set(b2.subclasses), set())
        eq_(set(b2.allSuperclasses), set([m1, m2, t1, t2, t3]))
        eq_(set(b2.allSubclasses), set())

        eq_(set(b3.superclasses), set([m1, m2]))
        eq_(set(b3.subclasses), set())
        eq_(set(b3.allSuperclasses), set([m1, m2, t1, t2, t3]))
        eq_(set(b3.allSubclasses), set())       

    def testClassAsWrongTypeOfSuperclass(self):
        t = CClass(self.mcl, "C") 
        try:
            CMetaclass("M", superclasses = [t])
            exceptionExpected_()
        except CException as e: 
            ok_(re.match("^cannot add superclass 'C' to 'M': not of type([ <a-zA-Z.']+)CMetaclass'>$", e.value))
        try:
            CStereotype("S", superclasses = [t])
            exceptionExpected_()
        except CException as e: 
            ok_(re.match("^cannot add superclass 'C' to 'S': not of type([ <a-zA-Z.']+)CStereotype'>$", e.value))

    def testClassPathNoInheritance(self):
        t = CClass(self.mcl)
        eq_(set(t.classPath), set([t]))
    
    def testClassPathSimpleInheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses = [t])
        m2 = CClass(self.mcl, "M2", superclasses = [t])
        b1 = CClass(self.mcl, "B1", superclasses = [m1])
        b2 = CClass(self.mcl, "B2", superclasses = [m1])
        b3 = CClass(self.mcl, "B3", superclasses = [t])
        eq_(b1.classPath, [b1, m1, t])
        eq_(b2.classPath, [b2, m1, t])
        eq_(b3.classPath, [b3, t])
        eq_(m1.classPath, [m1, t])
        eq_(m2.classPath, [m2, t])
        eq_(t.classPath, [t])

    def testClassPathMultipleInheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses = [t])
        m2 = CClass(self.mcl, "M2", superclasses = [t])
        b1 = CClass(self.mcl, "B1", superclasses = [m1, m2])
        b2 = CClass(self.mcl, "B2", superclasses = [t, m1])
        b3 = CClass(self.mcl, "B3", superclasses = [t, m1, m2])
        eq_(b1.classPath, [b1, m1, t, m2])
        eq_(b2.classPath, [b2, t, m1])
        eq_(b3.classPath, [b3, t, m1, m2])
        eq_(m1.classPath, [m1, t])
        eq_(m2.classPath, [m2, t])
        eq_(t.classPath, [t])

    def testClassInstanceOf(self):
        a = CClass(self.mcl)
        b = CClass(self.mcl, superclasses = [a])
        c = CClass(self.mcl)
        o = CObject(b, "o")

        eq_(o.instanceOf(a), True)
        eq_(o.instanceOf(b), True)
        eq_(o.instanceOf(c), False)

        try:
            o.instanceOf(o)
            exceptionExpected_()
        except CException as e: 
            eq_("'o' is not a class", e.value)

        o.delete()
        eq_(o.instanceOf(a), False)
    
    def testClassGetAllInstances(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses = [t])
        m2 = CClass(self.mcl, "M2", superclasses = [t])
        b1 = CClass(self.mcl, "B1", superclasses = [m1, m2])
        to1 = CObject(t)
        to2 = CObject(t)
        m1o1 = CObject(m1)
        m1o2 = CObject(m1)
        m2o = CObject(m2)
        b1o1 = CObject(b1)
        b1o2 = CObject(b1)

        eq_(set(t.objects), set([to1, to2]))
        eq_(set(t.allObjects), set([to1, to2, m1o1, m1o2, b1o1, b1o2, m2o]))
        eq_(set(m1.objects), set([m1o1, m1o2]))
        eq_(set(m1.allObjects), set([m1o1, m1o2, b1o1, b1o2]))
        eq_(set(m2.objects), set([m2o]))
        eq_(set(m2.allObjects), set([m2o, b1o1, b1o2]))
        eq_(set(b1.objects), set([b1o1, b1o2]))
        eq_(set(b1.allObjects), set([b1o1, b1o2]))

    def testClassHasSuperclassHasSubclass(self):
        c1 = CClass(self.mcl, "C1")
        c2 = CClass(self.mcl, "C2", superclasses = [c1])
        c3 = CClass(self.mcl, "C3", superclasses = [c2])
        c4 = CClass(self.mcl, "C4", superclasses = [c2])
        c5 = CClass(self.mcl, "C5", superclasses = [])

        eq_(c1.hasSuperclass(c2), False)
        eq_(c5.hasSuperclass(c2), False)
        eq_(c1.hasSuperclass(None), False)
        eq_(c5.hasSuperclass(None), False)
        eq_(c2.hasSuperclass(c1), True)
        eq_(c3.hasSuperclass(c2), True)
        eq_(c3.hasSuperclass(c2), True)  
        eq_(c4.hasSuperclass(c2), True)
        eq_(c3.hasSubclass(c2), False)
        eq_(c3.hasSubclass(None), False)
        eq_(c5.hasSubclass(c2), False)
        eq_(c5.hasSubclass(None), False)
        eq_(c1.hasSubclass(c3), True)
        eq_(c1.hasSubclass(c2), True)

    def testClassUnknownNonPositionalArgument(self):
        t = CClass(self.mcl, "T")
        try:
            CClass(self.mcl, "ST", superclass = t)
            exceptionExpected_()
        except CException as e: 
            eq_("unknown keyword argument 'superclass', should be one of: ['stereotypeInstances', 'values', 'taggedValues', 'attributes', 'superclasses', 'bundles']", e.value)

    def testSuperclassesThatAreDeleted(self):
        c1 = CClass(self.mcl, "C1")
        c1.delete()
        try:
            CClass(self.mcl, superclasses = [c1])
            exceptionExpected_()
        except CException as e: 
            eq_(e.value, "cannot access named element that has been deleted")

    def testSuperclassesThatAreNone(self):
        try:
            CClass(self.mcl, "C", superclasses = [None])
            exceptionExpected_()
        except CException as e: 
            ok_(e.value.startswith("cannot add superclass 'None' to 'C': not of type"))

if __name__ == "__main__":
    nose.main()



