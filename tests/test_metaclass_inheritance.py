import re


import pytest
from codeable_models import CMetaclass, CStereotype, CClass, CException


class TestMetaclassInheritance:
    def test_metaclass_no_inheritance(self):
        t = CMetaclass("T")
        assert set(t.superclasses) == set()
        assert set(t.subclasses) == set()
        assert set(t.all_superclasses) == set()
        assert set(t.all_subclasses) == set()

    def test_metaclass_superclasses_empty_input(self):
        m1 = CMetaclass("M1", superclasses=[])
        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == set()

    def test_metaclass_superclasses_none_input(self):
        m1 = CMetaclass("M1", superclasses=None)
        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == set()

    def test_metaclass_simple_inheritance(self):
        t = CMetaclass("T")
        m1 = CMetaclass("M1", superclasses=t)
        m2 = CMetaclass("M2", superclasses=t)
        b1 = CMetaclass("B1", superclasses=m1)
        b2 = CMetaclass("B2", superclasses=m1)
        b3 = CMetaclass("B3", superclasses=t)

        assert set(t.superclasses) == set()
        assert set(t.subclasses) == {m1, m2, b3}
        assert set(t.all_superclasses) == set()
        assert set(t.all_subclasses) == {m1, m2, b1, b2, b3}

        assert set(m1.superclasses) == {t}
        assert set(m1.subclasses) == {b1, b2}
        assert set(m1.all_superclasses) == {t}
        assert set(m1.all_subclasses) == {b1, b2}

        assert set(m2.superclasses) == {t}
        assert set(m2.subclasses) == set()
        assert set(m2.all_superclasses) == {t}
        assert set(m2.all_subclasses) == set()

        assert set(b1.superclasses) == {m1}
        assert set(b1.subclasses) == set()
        assert set(b1.all_superclasses) == {t, m1}
        assert set(b1.all_subclasses) == set()

        assert set(b2.superclasses) == {m1}
        assert set(b2.subclasses) == set()
        assert set(b2.all_superclasses) == {t, m1}
        assert set(b2.all_subclasses) == set()

        assert set(b3.superclasses) == {t}
        assert set(b3.subclasses) == set()
        assert set(b3.all_superclasses) == {t}
        assert set(b3.all_subclasses) == set()

    def test_metaclass_inheritance_double_assignment(self):
        t = CMetaclass("T")
        m1 = CMetaclass("M1")
        with pytest.raises(CException) as exc_info:
            m1.superclasses = [t, t]
        e = exc_info.value
        assert "'T' is already a superclass of 'M1'" == e.value
        assert m1.name == "M1"
        assert t.name == "T"
        assert set(m1.superclasses) == {t}

    def test_metaclass_inheritance_delete_top_class(self):
        t = CMetaclass("T")
        m1 = CMetaclass("M1", superclasses=[t])
        m2 = CMetaclass("M2", superclasses=[t])
        b1 = CMetaclass("B1", superclasses=[m1])
        b2 = CMetaclass("B2", superclasses=[m1])
        b3 = CMetaclass("B3", superclasses=[t])

        t.delete()

        assert t.name == None
        assert set(t.superclasses) == set()
        assert set(t.subclasses) == set()
        assert set(t.all_superclasses) == set()
        assert set(t.all_subclasses) == set()

        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == {b1, b2}
        assert set(m1.all_superclasses) == set()
        assert set(m1.all_subclasses) == {b1, b2}

        assert set(m2.superclasses) == set()
        assert set(m2.subclasses) == set()
        assert set(m2.all_superclasses) == set()
        assert set(m2.all_subclasses) == set()

        assert set(b1.superclasses) == {m1}
        assert set(b1.subclasses) == set()
        assert set(b1.all_superclasses) == {m1}
        assert set(b1.all_subclasses) == set()

        assert set(b2.superclasses) == {m1}
        assert set(b2.subclasses) == set()
        assert set(b2.all_superclasses) == {m1}
        assert set(b2.all_subclasses) == set()

        assert set(b3.superclasses) == set()
        assert set(b3.subclasses) == set()
        assert set(b3.all_superclasses) == set()
        assert set(b3.all_subclasses) == set()

    def test_metaclass_inheritance_delete_inner_class(self):
        t = CMetaclass("T")
        m1 = CMetaclass("M1", superclasses=[t])
        m2 = CMetaclass("M2", superclasses=[t])
        b1 = CMetaclass("B1", superclasses=[m1])
        b2 = CMetaclass("B2", superclasses=[m1])
        b3 = CMetaclass("B3", superclasses=[t])

        m1.delete()

        assert set(t.superclasses) == set()
        assert set(t.subclasses) == {m2, b3}
        assert set(t.all_superclasses) == set()
        assert set(t.all_subclasses) == {m2, b3}

        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == set()
        assert set(m1.all_superclasses) == set()
        assert set(m1.all_subclasses) == set()

        assert set(m2.superclasses) == {t}
        assert set(m2.subclasses) == set()
        assert set(m2.all_superclasses) == {t}
        assert set(m2.all_subclasses) == set()

        assert set(b1.superclasses) == set()
        assert set(b1.subclasses) == set()
        assert set(b1.all_superclasses) == set()
        assert set(b1.all_subclasses) == set()

        assert set(b2.superclasses) == set()
        assert set(b2.subclasses) == set()
        assert set(b2.all_superclasses) == set()
        assert set(b2.all_subclasses) == set()

        assert set(b3.superclasses) == {t}
        assert set(b3.subclasses) == set()
        assert set(b3.all_superclasses) == {t}
        assert set(b3.all_subclasses) == set()

    def test_metaclass_superclasses_reassignment(self):
        t = CMetaclass("T")
        m1 = CMetaclass("M1", superclasses=[t])
        m2 = CMetaclass("M2", superclasses=[t])
        b1 = CMetaclass("B1", superclasses=[m1])
        b2 = CMetaclass("B2", superclasses=[m1])
        b3 = CMetaclass("B3", superclasses=[t])

        m1.superclasses = []
        b1.superclasses = []
        b2.superclasses = []

        assert set(t.superclasses) == set()
        assert set(t.subclasses) == {m2, b3}
        assert set(t.all_superclasses) == set()
        assert set(t.all_subclasses) == {m2, b3}

        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == set()
        assert set(m1.all_superclasses) == set()
        assert set(m1.all_subclasses) == set()

        assert set(m2.superclasses) == {t}
        assert set(m2.subclasses) == set()
        assert set(m2.all_superclasses) == {t}
        assert set(m2.all_subclasses) == set()

        assert set(b1.superclasses) == set()
        assert set(b1.subclasses) == set()
        assert set(b1.all_superclasses) == set()
        assert set(b1.all_subclasses) == set()

        assert set(b2.superclasses) == set()
        assert set(b2.subclasses) == set()
        assert set(b2.all_superclasses) == set()
        assert set(b2.all_subclasses) == set()

        assert set(b3.superclasses) == {t}
        assert set(b3.subclasses) == set()
        assert set(b3.all_superclasses) == {t}
        assert set(b3.all_subclasses) == set()

    def test_metaclass_multiple_inheritance(self):
        t1 = CMetaclass("T1")
        t2 = CMetaclass("T2")
        t3 = CMetaclass("T3")
        m1 = CMetaclass("M1", superclasses=[t1, t3])
        m2 = CMetaclass("M2", superclasses=[t2, t3])
        b1 = CMetaclass("B1", superclasses=[m1])
        b2 = CMetaclass("B2", superclasses=[m1, m2])
        b3 = CMetaclass("B3", superclasses=[m2, m1])

        assert set(t1.superclasses) == set()
        assert set(t1.subclasses) == {m1}
        assert set(t1.all_superclasses) == set()
        assert set(t1.all_subclasses) == {m1, b1, b2, b3}

        assert set(t2.superclasses) == set()
        assert set(t2.subclasses) == {m2}
        assert set(t2.all_superclasses) == set()
        assert set(t2.all_subclasses) == {m2, b3, b2}

        assert set(t3.superclasses) == set()
        assert set(t3.subclasses) == {m2, m1}
        assert set(t3.all_superclasses) == set()
        assert set(t3.all_subclasses) == {m2, m1, b1, b2, b3}

        assert set(m1.superclasses) == {t1, t3}
        assert set(m1.subclasses) == {b1, b2, b3}
        assert set(m1.all_superclasses) == {t1, t3}
        assert set(m1.all_subclasses) == {b1, b2, b3}

        assert set(m2.superclasses) == {t2, t3}
        assert set(m2.subclasses) == {b2, b3}
        assert set(m2.all_superclasses) == {t2, t3}
        assert set(m2.all_subclasses) == {b2, b3}

        assert set(b1.superclasses) == {m1}
        assert set(b1.subclasses) == set()
        assert set(b1.all_superclasses) == {m1, t1, t3}
        assert set(b1.all_subclasses) == set()

        assert set(b2.superclasses) == {m1, m2}
        assert set(b2.subclasses) == set()
        assert set(b2.all_superclasses) == {m1, m2, t1, t2, t3}
        assert set(b2.all_subclasses) == set()

        assert set(b3.superclasses) == {m1, m2}
        assert set(b3.subclasses) == set()
        assert set(b3.all_superclasses) == {m1, m2, t1, t2, t3}
        assert set(b3.all_subclasses) == set()

    def test_metaclass_as_wrong_type_of_superclass(self):
        t = CMetaclass("M")
        with pytest.raises(CException) as exc_info:
            CClass(t, "C", superclasses=[t])
        e = exc_info.value
        assert re.match("^cannot add superclass 'M' to 'C': not of type([_ <a-zA-Z.']+)CClass'>$", e.value)
        with pytest.raises(CException) as exc_info:
            CStereotype("S", superclasses=[t])
        e = exc_info.value
        assert re.match("^cannot add superclass 'M' to 'S': not of type([_ <a-zA-Z.']+)CStereotype'>$", e.value)

    def test_metaclass_path_no_inheritance(self):
        t = CMetaclass()
        assert set(t.class_path) == {t}

    def test_metaclass_path_simple_inheritance(self):
        t = CMetaclass("T")
        m1 = CMetaclass("M1", superclasses=[t])
        m2 = CMetaclass("M2", superclasses=[t])
        b1 = CMetaclass("B1", superclasses=[m1])
        b2 = CMetaclass("B2", superclasses=[m1])
        b3 = CMetaclass("B3", superclasses=[t])
        assert b1.class_path == [b1, m1, t]
        assert b2.class_path == [b2, m1, t]
        assert b3.class_path == [b3, t]
        assert m1.class_path == [m1, t]
        assert m2.class_path == [m2, t]
        assert t.class_path == [t]

    def test_metaclass_path_multiple_inheritance(self):
        t = CMetaclass("T")
        m1 = CMetaclass("M1", superclasses=[t])
        m2 = CMetaclass("M2", superclasses=[t])
        b1 = CMetaclass("B1", superclasses=[m1, m2])
        b2 = CMetaclass("B2", superclasses=[t, m1])
        b3 = CMetaclass("B3", superclasses=[t, m1, m2])
        assert b1.class_path == [b1, m1, t, m2]
        assert b2.class_path == [b2, t, m1]
        assert b3.class_path == [b3, t, m1, m2]
        assert m1.class_path == [m1, t]
        assert m2.class_path == [m2, t]
        assert t.class_path == [t]

    def test_metaclass_instance_of(self):
        a = CMetaclass()
        b = CMetaclass(superclasses=[a])
        c = CMetaclass()
        cl = CClass(b, "C")

        assert cl.instance_of(a) == True
        assert cl.instance_of(b) == True
        assert cl.instance_of(c) == False

        with pytest.raises(CException) as exc_info:
            cl.instance_of(cl)
        e = exc_info.value
        assert "'C' is not a metaclass" == e.value

        cl.delete()
        assert cl.instance_of(a) == False

    def test_metaclass_get_all_instances(self):
        t = CMetaclass("T")
        m1 = CMetaclass("M1", superclasses=[t])
        m2 = CMetaclass("M2", superclasses=[t])
        b1 = CMetaclass("B1", superclasses=[m1, m2])
        to1 = CClass(t)
        to2 = CClass(t)
        m1o1 = CClass(m1)
        m1o2 = CClass(m1)
        m2o = CClass(m2)
        b1o1 = CClass(b1)
        b1o2 = CClass(b1)

        assert set(t.classes) == {to1, to2}
        assert set(t.all_classes) == {to1, to2, m1o1, m1o2, b1o1, b1o2, m2o}
        assert set(m1.classes) == {m1o1, m1o2}
        assert set(m1.all_classes) == {m1o1, m1o2, b1o1, b1o2}
        assert set(m2.classes) == {m2o}
        assert set(m2.all_classes) == {m2o, b1o1, b1o2}
        assert set(b1.classes) == {b1o1, b1o2}
        assert set(b1.all_classes) == {b1o1, b1o2}

    def test_metaclass_has_superclass_has_subclass(self):
        m1 = CMetaclass("M1")
        m2 = CMetaclass("M2", superclasses=[m1])
        m3 = CMetaclass("M3", superclasses=[m2])
        m4 = CMetaclass("M4", superclasses=[m2])
        m5 = CMetaclass("M5", superclasses=[])

        assert m1.has_superclass(m2) == False
        assert m5.has_superclass(m2) == False
        assert m1.has_superclass(None) == False
        assert m5.has_superclass(None) == False
        assert m2.has_superclass(m1) == True
        assert m3.has_superclass(m2) == True
        assert m3.has_superclass(m2) == True
        assert m4.has_superclass(m2) == True
        assert m3.has_subclass(m2) == False
        assert m3.has_subclass(None) == False
        assert m5.has_subclass(m2) == False
        assert m5.has_subclass(None) == False
        assert m1.has_subclass(m3) == True
        assert m1.has_subclass(m2) == True

    def test_metaclass_unknown_non_positional_argument(self):
        t = CMetaclass("T")
        with pytest.raises(CException) as exc_info:
            CMetaclass("ST", superclass=t)
        e = exc_info.value
        assert "unknown keyword argument 'superclass', should be one of: " + "['stereotypes', 'attributes', 'superclasses', 'bundles']" == e.value

    def test_super_metaclasses_that_are_deleted(self):
        m1 = CMetaclass("M1")
        m1.delete()
        with pytest.raises(CException) as exc_info:
            CMetaclass(superclasses=[m1])
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_super_metaclasses_that_are_none(self):
        with pytest.raises(CException) as exc_info:
            CMetaclass("M", superclasses=[None])
        e = exc_info.value
        assert e.value.startswith("cannot add superclass 'None' to 'M': not of type")


