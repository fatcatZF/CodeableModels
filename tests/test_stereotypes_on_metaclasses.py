
import pytest
from codeable_models import CStereotype, CMetaclass, CClass, CException, CBundle


class TestStereotypesOnMetaclasses:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.mcl = CMetaclass("MCL")

    def test_creation_of_one_stereotype(self):
        s = CStereotype("S", extended=self.mcl)
        assert s.name == "S"
        assert self.mcl.stereotypes == [s]
        assert s.extended == [self.mcl]

    def test_wrongs_types_in_list_of_extended_element_types(self):
        with pytest.raises(CException) as exc_info:
            CStereotype("S", extended=[self.mcl, self.mcl.association(self.mcl, name="A")])
        e = exc_info.value
        assert "'A' is not a metaclass" == e.value
        with pytest.raises(CException) as exc_info:
            CStereotype("S", extended=[self.mcl, CBundle("P")])
        e = exc_info.value
        assert "'P' is not a metaclass" == e.value
        with pytest.raises(CException) as exc_info:
            CStereotype("S", extended=[CBundle("P"), self.mcl])
        e = exc_info.value
        assert "unknown type of extend element: 'P'" == e.value

    def test_creation_of_3_stereotypes(self):
        s1 = CStereotype("S1")
        s2 = CStereotype("S2")
        s3 = CStereotype("S3")
        self.mcl.stereotypes = [s1, s2, s3]
        assert s1.extended == [self.mcl]
        assert s2.extended == [self.mcl]
        assert s3.extended == [self.mcl]
        assert set(self.mcl.stereotypes) == {s1, s2, s3}

    def test_creation_of_unnamed_stereotype(self):
        s = CStereotype()
        assert s.name == None
        assert self.mcl.stereotypes == []
        assert s.extended == []

    def test_delete_stereotype(self):
        s1 = CStereotype("S1")
        s1.delete()
        assert s1.name == None
        assert self.mcl.stereotypes == []
        s1 = CStereotype("S1", extended=self.mcl)
        s1.delete()
        assert s1.name == None
        assert self.mcl.stereotypes == []

        s1 = CStereotype("S1", extended=self.mcl)
        s2 = CStereotype("S2", extended=self.mcl)
        s3 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, extended=self.mcl)

        s1.delete()
        assert set(self.mcl.stereotypes) == {s2, s3}
        s3.delete()
        assert set(self.mcl.stereotypes) == {s2}

        assert s3.superclasses == []
        assert s2.subclasses == []
        assert s3.attributes == []
        assert s3.attribute_names == []
        assert s3.extended == []
        assert s3.name == None
        assert s3.bundles == []

    def test_stereotype_extension_add_remove(self):
        s1 = CStereotype("S1")
        assert set(s1.extended) == set()
        mcl1 = CMetaclass(stereotypes=[s1])
        assert set(s1.extended) == {mcl1}
        assert set(mcl1.stereotypes) == {s1}
        mcl2 = CMetaclass(stereotypes=s1)
        assert set(s1.extended) == {mcl1, mcl2}
        assert set(mcl1.stereotypes) == {s1}
        assert set(mcl2.stereotypes) == {s1}
        s1.extended = [mcl2]
        assert set(s1.extended) == {mcl2}
        assert set(mcl1.stereotypes) == set()
        assert set(mcl2.stereotypes) == {s1}
        s2 = CStereotype("S2", extended=[mcl2])
        assert set(mcl2.stereotypes) == {s2, s1}
        assert set(s1.extended) == {mcl2}
        assert set(s2.extended) == {mcl2}
        mcl2.stereotypes = []
        assert set(mcl2.stereotypes) == set()
        assert set(s1.extended) == set()
        assert set(s2.extended) == set()

    def test_stereotype_remove_stereotype_or_metaclass(self):
        mcl = CMetaclass("MCL1")
        s1 = CStereotype("S1", extended=[mcl])
        s2 = CStereotype("S2", extended=[mcl])
        s3 = CStereotype("S3", extended=[mcl])
        s4 = CStereotype("S4", extended=[mcl])
        assert set(mcl.stereotypes) == {s1, s2, s3, s4}
        s2.delete()
        assert set(mcl.stereotypes) == {s1, s3, s4}
        assert set(s2.extended) == set()
        assert set(s1.extended) == {mcl}
        mcl.delete()
        assert set(mcl.stereotypes) == set()
        assert set(s1.extended) == set()

    def test_stereotypes_wrong_type(self):
        with pytest.raises(CException) as exc_info:
            self.mcl.stereotypes = [self.mcl]
        e = exc_info.value
        assert "'MCL' is not a stereotype" == e.value

    def test_extended_wrong_type(self):
        with pytest.raises(CException) as exc_info:
            cl = CClass(self.mcl)
            CStereotype("S1", extended=[cl])
        e = exc_info.value
        assert "unknown type of extend element: ''" == e.value

    def test_metaclass_stereotypes_null_input(self):
        s = CStereotype()
        m = CMetaclass(stereotypes=None)
        assert m.stereotypes == []
        assert s.extended == []

    def test_metaclass_stereotypes_non_list_input(self):
        s = CStereotype()
        m = CMetaclass(stereotypes=s)
        assert m.stereotypes == [s]
        assert s.extended == [m]

    def test_metaclass_stereotypes_non_list_input_wrong_type(self):
        with pytest.raises(CException) as exc_info:
            CMetaclass(stereotypes=self.mcl)
        e = exc_info.value
        assert "a list or a stereotype is required as input" == e.value

    def test_metaclass_stereotypes_append(self):
        s1 = CStereotype()
        s2 = CStereotype()
        m = CMetaclass(stereotypes=[s1])
        # should have no effect, as setter must be used
        m.stereotypes.append(s2)
        assert m.stereotypes == [s1]
        assert s1.extended == [m]
        assert s2.extended == []

    def test_stereotype_extended_null_input(self):
        m = CMetaclass()
        s = CStereotype(extended=None)
        assert m.stereotypes == []
        assert s.extended == []

    def test_stereotype_extended_non_list_input(self):
        m = CMetaclass()
        s = CStereotype(extended=m)
        assert m.stereotypes == [s]
        assert s.extended == [m]

    def test_stereotype_extended_non_list_input_wrong_type(self):
        with pytest.raises(CException) as exc_info:
            CStereotype(extended=CClass(self.mcl))
        e = exc_info.value
        assert "extended requires a list, a metaclass, an association as input" == e.value

    def test_stereotype_extended_append(self):
        m1 = CMetaclass()
        m2 = CMetaclass()
        s = CStereotype(extended=[m1])
        # should have no effect, as setter must be used
        s.extended.append(m2)
        assert m1.stereotypes == [s]
        assert m2.stereotypes == []
        assert s.extended == [m1]

    def test_extended_metaclass_that_is_deleted(self):
        m1 = CMetaclass("M1")
        m1.delete()
        with pytest.raises(CException) as exc_info:
            CStereotype(extended=[m1])
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_extended_metaclass_that_are_none(self):
        with pytest.raises(CException) as exc_info:
            CStereotype(extended=[None])
        e = exc_info.value
        assert e.value == "unknown type of extend element: 'None'"


