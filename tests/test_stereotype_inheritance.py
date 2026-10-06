import re


import pytest
from codeable_models import CMetaclass, CStereotype, CClass, CException


class TestStereotypeInheritance:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")

    def test_stereotype_no_inheritance(self):
        t = CStereotype("T")
        assert set(t.superclasses) == set()
        assert set(t.subclasses) == set()
        assert set(t.all_superclasses) == set()
        assert set(t.all_subclasses) == set()

    def test_stereotype_superclasses_empty_input(self):
        m1 = CStereotype("M1", superclasses=[])
        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == set()

    def test_stereotype_superclasses_none_input(self):
        m1 = CStereotype("M1", superclasses=None)
        assert set(m1.superclasses) == set()
        assert set(m1.subclasses) == set()

    def test_stereotype_simple_inheritance(self):
        t = CStereotype("T")
        m1 = CStereotype("M1", superclasses=t)
        m2 = CStereotype("M2", superclasses=t)
        b1 = CStereotype("B1", superclasses=m1)
        b2 = CStereotype("B2", superclasses=m1)
        b3 = CStereotype("B3", superclasses=t)

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

    def test_stereotype_inheritance_double_assignment(self):
        m = CMetaclass("M")
        t = CStereotype("T")
        with pytest.raises(CException) as exc_info:
            CStereotype("S1", extended=m, superclasses=[t, t])
        e = exc_info.value
        assert "'T' is already a superclass of 'S1'" == e.value
        s1 = m.get_stereotype("S1")
        assert s1.name == "S1"
        assert set(s1.superclasses) == {t}

    def test_stereotype_inheritance_delete_top_class(self):
        t = CStereotype("T")
        m1 = CStereotype("M1", superclasses=[t])
        m2 = CStereotype("M2", superclasses=[t])
        b1 = CStereotype("B1", superclasses=[m1])
        b2 = CStereotype("B2", superclasses=[m1])
        b3 = CStereotype("B3", superclasses=[t])

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

    def test_stereotype_inheritance_delete_inner_class(self):
        t = CStereotype("T")
        m1 = CStereotype("M1", superclasses=[t])
        m2 = CStereotype("M2", superclasses=[t])
        b1 = CStereotype("B1", superclasses=[m1])
        b2 = CStereotype("B2", superclasses=[m1])
        b3 = CStereotype("B3", superclasses=[t])

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

    def test_stereotype_superclasses_reassignment(self):
        t = CStereotype("T")
        m1 = CStereotype("M1", superclasses=[t])
        m2 = CStereotype("M2", superclasses=[t])
        b1 = CStereotype("B1", superclasses=[m1])
        b2 = CStereotype("B2", superclasses=[m1])
        b3 = CStereotype("B3", superclasses=[t])

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

    def test_stereotype_multiple_inheritance(self):
        t1 = CStereotype("T1")
        t2 = CStereotype("T2")
        t3 = CStereotype("T3")
        m1 = CStereotype("M1", superclasses=[t1, t3])
        m2 = CStereotype("M2", superclasses=[t2, t3])
        b1 = CStereotype("B1", superclasses=[m1])
        b2 = CStereotype("B2", superclasses=[m1, m2])
        b3 = CStereotype("B3", superclasses=[m2, m1])

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

    def test_stereotype_as_wrong_type_of_superclass(self):
        t = CStereotype("S")
        with pytest.raises(CException) as exc_info:
            CMetaclass("M", superclasses=[t])
        e = exc_info.value
        assert re.match("^cannot add superclass 'S' to 'M': not of type([_ <a-zA-Z.']+)CMetaclass'>$", e.value)
        with pytest.raises(CException) as exc_info:
            CClass(CMetaclass(), "C", superclasses=[t])
        e = exc_info.value
        assert re.match("^cannot add superclass 'S' to 'C': not of type([_ <a-zA-Z.']+)CClass'>$", e.value)

    def test_extended_classes_of_inheriting_stereotypes__superclass_has_none(self):
        m1 = CMetaclass()
        m2 = CMetaclass(superclasses=[m1])
        s1 = CStereotype()
        s2 = CStereotype(superclasses=[s1])
        m2.stereotypes = s2
        assert len(s1.extended) == 0
        assert set(m2.stereotypes) == {s2}

    def test_extended_classes_of_inheriting_stereotypes__superclass_has_the_same(self):
        m1 = CMetaclass()
        s1 = CStereotype(extended=[m1])
        s2 = CStereotype(superclasses=[s1], extended=[m1])
        assert set(s1.extended) == {m1}
        assert set(s2.extended) == {m1}
        assert set(m1.stereotypes) == {s2, s1}

    def test_extended_classes_of_inheriting_stereotypes__remove_superclass_stereotype(self):
        m1 = CMetaclass()
        s1 = CStereotype(extended=[m1])
        s2 = CStereotype(superclasses=[s1], extended=[m1])
        m1.stereotypes = s2
        assert set(s1.extended) == set()
        assert set(s2.extended) == {m1}
        assert set(m1.stereotypes) == {s2}

    def test_extended_classes_of_inheriting_stereotypes__superclass_is_set_to_the_same(self):
        m1 = CMetaclass("M1")
        s1 = CStereotype("S1")
        s2 = CStereotype("S2", extended=[m1], superclasses=[s1])
        m1.stereotypes = [s2, s1]
        assert set(s1.extended) == {m1}
        assert set(s2.extended) == {m1}
        assert set(m1.stereotypes) == {s2, s1}

    def test_extended_classes_of_inheriting_stereotypes__superclass_has_metaclasses_superclass(self):
        m1 = CMetaclass()
        m2 = CMetaclass(superclasses=[m1])
        s1 = CStereotype(extended=[m1])
        s2 = CStereotype(superclasses=[s1], extended=[m2])
        assert set(s1.extended) == {m1}
        assert set(s2.extended) == {m2}
        assert set(m1.stereotypes) == {s1}
        assert set(m2.stereotypes) == {s2}

    def test_extended_classes_of_inheriting_stereotypes__superclass_has_metaclasses_superclass_indirectly(self):
        m1 = CMetaclass()
        m2 = CMetaclass(superclasses=[m1])
        m3 = CMetaclass(superclasses=[m2])
        s1 = CStereotype(extended=[m1])
        s2 = CStereotype(superclasses=[s1], extended=[m3])
        assert set(s1.extended) == {m1}
        assert set(s2.extended) == {m3}
        assert set(m1.stereotypes) == {s1}
        assert set(m3.stereotypes) == {s2}

    def test_extended_classes_of_inheriting_stereotypes__superclass_is_set_to_metaclasses_superclass_indirectly(self):
        m1 = CMetaclass()
        m2 = CMetaclass(superclasses=[m1])
        m3 = CMetaclass(superclasses=[m2])
        s1 = CStereotype()
        s2 = CStereotype(superclasses=[s1], extended=[m3])
        m1.stereotypes = s1
        assert set(s1.extended) == {m1}
        assert set(s2.extended) == {m3}
        assert set(m1.stereotypes) == {s1}
        assert set(m3.stereotypes) == {s2}

    def test_stereotype_has_superclass_has_subclass(self):
        c1 = CStereotype("C1")
        c2 = CStereotype("C2", superclasses=[c1])
        c3 = CStereotype("C3", superclasses=[c2])
        c4 = CStereotype("C4", superclasses=[c2])
        c5 = CStereotype("C5", superclasses=[])

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

    def test_stereotype_unknown_non_positional_argument(self):
        t = CStereotype("T")
        with pytest.raises(CException) as exc_info:
            CStereotype("ST", superclass=t)
        e = exc_info.value
        assert "unknown keyword argument 'superclass', should be one of: " + "['extended', 'default_values', 'attributes', 'superclasses', 'bundles']" == e.value

    def test_super_stereotypes_that_are_deleted(self):
        s1 = CStereotype("S1")
        s1.delete()
        with pytest.raises(CException) as exc_info:
            CStereotype(superclasses=[s1])
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_super_stereotypes_that_are_none(self):
        with pytest.raises(CException) as exc_info:
            CStereotype("S", superclasses=[None])
        e = exc_info.value
        assert e.value.startswith("cannot add superclass 'None' to 'S': not of type")


