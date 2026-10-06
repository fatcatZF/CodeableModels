import re


import pytest
from codeable_models import CMetaclass, CStereotype, CClass, CObject, CException


class TestClassInheritance:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")

    def test_class_no_inheritance(self):
        t = CClass(self.mcl, "T")
        assert set(t.superclasses) == set()
        assert set(t.subclasses) == set()
        assert set(t.all_superclasses) == set()
        assert set(t.all_subclasses) == set()

    def test_class_superclasses_empty_input(self):
        m1 = CClass(self.mcl, "M1", superclasses=[])
        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == set()

    def test_class_superclasses_none_input(self):
        m1 = CClass(self.mcl, "M1", superclasses=None)
        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == set()

    def test_class_simple_inheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=t)
        m2 = CClass(self.mcl, "M2", superclasses=t)
        b1 = CClass(self.mcl, "B1", superclasses=m1)
        b2 = CClass(self.mcl, "B2", superclasses=m1)
        b3 = CClass(self.mcl, "B3", superclasses=t)

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

    def test_class_inheritance_double_assignment(self):
        t = CClass(self.mcl, "T")
        with pytest.raises(CException) as exc_info:
            CClass(self.mcl, "C1", superclasses=[t, t])
        e = exc_info.value
        assert "'T' is already a superclass of 'C1'" == e.value
        c1 = self.mcl.get_class("C1")
        assert c1.metaclass == self.mcl
        assert c1.name == "C1"
        assert t.name == "T"
        assert set(c1.superclasses) == {t}

    def test_class_inheritance_delete_top_class(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t])

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

    def test_class_inheritance_delete_inner_class(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t])

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

    def test_class_superclasses_reassignment(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t])

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

    def test_class_multiple_inheritance(self):
        t1 = CClass(self.mcl, "T1")
        t2 = CClass(self.mcl, "T2")
        t3 = CClass(self.mcl, "T3")
        m1 = CClass(self.mcl, "M1", superclasses=[t1, t3])
        m2 = CClass(self.mcl, "M2", superclasses=[t2, t3])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1, m2])
        b3 = CClass(self.mcl, "B3", superclasses=[m2, m1])

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

    def test_class_as_wrong_type_of_superclass(self):
        t = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            CMetaclass("M", superclasses=[t])
        e = exc_info.value
        assert re.match("^cannot add superclass 'C' to 'M': not of type([_ <a-zA-Z.']+)CMetaclass'>$", e.value)
        with pytest.raises(CException) as exc_info:
            CStereotype("S", superclasses=[t])
        e = exc_info.value
        assert re.match("^cannot add superclass 'C' to 'S': not of type([_ <a-zA-Z.']+)CStereotype'>$", e.value)

    def test_class_path_no_inheritance(self):
        t = CClass(self.mcl)
        assert set(t.class_path) == {t}

    def test_class_path_simple_inheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t])
        assert b1.class_path == [b1, m1, t]
        assert b2.class_path == [b2, m1, t]
        assert b3.class_path == [b3, t]
        assert m1.class_path == [m1, t]
        assert m2.class_path == [m2, t]
        assert t.class_path == [t]

    def test_class_path_multiple_inheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1, m2])
        b2 = CClass(self.mcl, "B2", superclasses=[t, m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t, m1, m2])
        assert b1.class_path == [b1, m1, t, m2]
        assert b2.class_path == [b2, t, m1]
        assert b3.class_path == [b3, t, m1, m2]
        assert m1.class_path == [m1, t]
        assert m2.class_path == [m2, t]
        assert t.class_path == [t]

    def test_class_instance_of(self):
        a = CClass(self.mcl)
        b = CClass(self.mcl, superclasses=[a])
        c = CClass(self.mcl)
        o = CObject(b, "o")

        assert o.instance_of(a) == True
        assert o.instance_of(b) == True
        assert o.instance_of(c) == False

        with pytest.raises(CException) as exc_info:
            o.instance_of(o)
        e = exc_info.value
        assert "'o' is not a class" == e.value

        o.delete()
        assert o.instance_of(a) == False

    def test_class_get_all_instances(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1, m2])
        to1 = CObject(t)
        to2 = CObject(t)
        m1o1 = CObject(m1)
        m1o2 = CObject(m1)
        m2o = CObject(m2)
        b1o1 = CObject(b1)
        b1o2 = CObject(b1)

        assert set(t.objects) == {to1, to2}
        assert set(t.all_objects) == {to1, to2, m1o1, m1o2, b1o1, b1o2, m2o}
        assert set(m1.objects) == {m1o1, m1o2}
        assert set(m1.all_objects) == {m1o1, m1o2, b1o1, b1o2}
        assert set(m2.objects) == {m2o}
        assert set(m2.all_objects) == {m2o, b1o1, b1o2}
        assert set(b1.objects) == {b1o1, b1o2}
        assert set(b1.all_objects) == {b1o1, b1o2}

    def test_class_has_superclass_has_subclass(self):
        c1 = CClass(self.mcl, "C1")
        c2 = CClass(self.mcl, "C2", superclasses=[c1])
        c3 = CClass(self.mcl, "C3", superclasses=[c2])
        c4 = CClass(self.mcl, "C4", superclasses=[c2])
        c5 = CClass(self.mcl, "C5", superclasses=[])

        assert c1.has_superclass(c2) == False
        assert c5.has_superclass(c2) == False
        assert c1.has_superclass(None) == False
        assert c5.has_superclass(None) == False
        assert c2.has_superclass(c1) == True
        assert c3.has_superclass(c2) == True
        assert c3.has_superclass(c2) == True
        assert c4.has_superclass(c2) == True
        assert c3.has_subclass(c2) == False
        assert c3.has_subclass(None) == False
        assert c5.has_subclass(c2) == False
        assert c5.has_subclass(None) == False
        assert c1.has_subclass(c3) == True
        assert c1.has_subclass(c2) == True

    def test_class_unknown_non_positional_argument(self):
        t = CClass(self.mcl, "T")
        with pytest.raises(CException) as exc_info:
            CClass(self.mcl, "ST", superclass=t)
        e = exc_info.value
        assert "unknown keyword argument 'superclass', should be one of: " + "['stereotype_instances', 'values', 'tagged_values', 'attributes', 'superclasses', 'bundles']" == e.value

    def test_superclasses_that_are_deleted(self):
        c1 = CClass(self.mcl, "C1")
        c1.delete()
        with pytest.raises(CException) as exc_info:
            CClass(self.mcl, superclasses=[c1])
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_superclasses_that_are_none(self):
        with pytest.raises(CException) as exc_info:
            CClass(self.mcl, "C", superclasses=[None])
        e = exc_info.value
        assert e.value.startswith("cannot add superclass 'None' to 'C': not of type")


