
import pytest
from codeable_models import CStereotype, CMetaclass, CException, CBundle, CClass


class TestStereotypesOnAssociations:
    def setup_method(self):
        self.m1 = CMetaclass("M1")
        self.m2 = CMetaclass("M2")
        self.a = self.m1.association(self.m2, name="A", multiplicity="1", role_name="m1",
                                     source_multiplicity="*", source_role_name="m2")

    def test_creation_of_one_stereotype(self):
        s = CStereotype("S", extended=self.a)
        assert s.name == "S"
        assert self.a.stereotypes == [s]
        assert s.extended == [self.a]

    def test_wrongs_types_in_list_of_extended_element_types(self):
        with pytest.raises(CException) as exc_info:
            CStereotype("S", extended=[self.a, self.m1])
        e = exc_info.value
        assert "'M1' is not a association" == e.value
        with pytest.raises(CException) as exc_info:
            CStereotype("S", extended=[self.a, CBundle("P")])
        e = exc_info.value
        assert "'P' is not a association" == e.value
        with pytest.raises(CException) as exc_info:
            CStereotype("S", extended=[CBundle("P"), self.a])
        e = exc_info.value
        assert "unknown type of extend element: 'P'" == e.value

    def test_attempt_to_define_stereotypes_on_class_association(self):
        a_class = CClass(self.m1, "AClass")
        b_class = CClass(self.m1, "BClass")
        s = CStereotype("S")
        with pytest.raises(CException) as exc_info:
            a_class.association(b_class, "1 -> 1", stereotypes=s)
        e = exc_info.value
        assert "stereotypes on associations can only be defined for metaclass associations" == e.value

        association = a_class.association(b_class, "1 -> 1")
        with pytest.raises(CException) as exc_info:
            association.stereotypes = s
        e = exc_info.value
        assert "stereotypes on associations can only be defined for metaclass associations" == e.value

    def test_creation_of_3_stereotypes(self):
        s1 = CStereotype("S1")
        s2 = CStereotype("S2")
        s3 = CStereotype("S3")
        self.a.stereotypes = [s1, s2, s3]
        assert s1.extended == [self.a]
        assert s2.extended == [self.a]
        assert s3.extended == [self.a]
        assert set(self.a.stereotypes) == {s1, s2, s3}

    def test_creation_of_unnamed_stereotype(self):
        s = CStereotype()
        assert s.name == None
        assert self.a.stereotypes == []
        assert s.extended == []

    def test_delete_stereotype(self):
        s1 = CStereotype("S1")
        s1.delete()
        assert s1.name == None
        assert self.a.stereotypes == []
        s1 = CStereotype("S1", extended=self.a)
        s1.delete()
        assert s1.name == None
        assert self.a.stereotypes == []

        s1 = CStereotype("S1", extended=self.a)
        s2 = CStereotype("S2", extended=self.a)
        s3 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, extended=self.a)

        s1.delete()
        assert set(self.a.stereotypes) == {s2, s3}
        s3.delete()
        assert set(self.a.stereotypes) == {s2}

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
        a1 = self.m1.association(self.m2, multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2", stereotypes=[s1])
        assert set(s1.extended) == {a1}
        assert set(a1.stereotypes) == {s1}
        a2 = self.m1.association(self.m2, multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2", stereotypes=s1)
        assert set(s1.extended) == {a1, a2}
        assert set(a1.stereotypes) == {s1}
        assert set(a2.stereotypes) == {s1}
        s1.extended = [a2]
        assert set(s1.extended) == {a2}
        assert set(a1.stereotypes) == set()
        assert set(a2.stereotypes) == {s1}
        s2 = CStereotype("S2", extended=[a2])
        assert set(a2.stereotypes) == {s2, s1}
        assert set(s1.extended) == {a2}
        assert set(s2.extended) == {a2}
        a2.stereotypes = []
        assert set(a2.stereotypes) == set()
        assert set(s1.extended) == set()
        assert set(s2.extended) == set()

    def test_stereotype_remove_stereotype_or_association(self):
        a1 = self.m1.association(self.m2, multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2")
        s1 = CStereotype("S1", extended=[a1])
        s2 = CStereotype("S2", extended=[a1])
        s3 = CStereotype("S3", extended=[a1])
        s4 = CStereotype("S4", extended=[a1])
        assert set(a1.stereotypes) == {s1, s2, s3, s4}
        s2.delete()
        assert set(a1.stereotypes) == {s1, s3, s4}
        assert set(s2.extended) == set()
        assert set(s1.extended) == {a1}
        a1.delete()
        assert set(a1.stereotypes) == set()
        assert set(s1.extended) == set()

    def test_stereotypes_wrong_type(self):
        a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2")
        with pytest.raises(CException) as exc_info:
            a1.stereotypes = [a1]
        e = exc_info.value
        assert "'a1' is not a stereotype" == e.value

    def test_association_stereotypes_null_input(self):
        s = CStereotype()
        a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2", stereotypes=None)
        assert a1.stereotypes == []
        assert s.extended == []

    def test_association_stereotypes_non_list_input(self):
        s = CStereotype()
        a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2", stereotypes=s)
        assert a1.stereotypes == [s]
        assert s.extended == [a1]

    def test_association_stereotypes_non_list_input_wrong_type(self):
        with pytest.raises(CException) as exc_info:
            a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                     source_multiplicity="*", source_role_name="m2")
            a1.stereotypes = a1
        e = exc_info.value
        assert "a list or a stereotype is required as input" == e.value

    def test_metaclass_stereotypes_append(self):
        s1 = CStereotype()
        s2 = CStereotype()
        a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2", stereotypes=s1)
        # should have no effect, as setter must be used
        a1.stereotypes.append(s2)
        assert a1.stereotypes == [s1]
        assert s1.extended == [a1]
        assert s2.extended == []

    def test_stereotype_extended_null_input(self):
        a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2")
        s = CStereotype(extended=None)
        assert a1.stereotypes == []
        assert s.extended == []

    def test_stereotype_extended_non_list_input(self):
        a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2")
        s = CStereotype(extended=a1)
        assert a1.stereotypes == [s]
        assert s.extended == [a1]

    def test_stereotype_extended_append(self):
        a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2")
        a2 = self.m1.association(self.m2, name="a2", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2")
        s = CStereotype(extended=[a1])
        # should have no effect, as setter must be used
        s.extended.append(a2)
        assert a1.stereotypes == [s]
        assert a2.stereotypes == []
        assert s.extended == [a1]

    def test_extended_association_that_is_deleted(self):
        a1 = self.m1.association(self.m2, name="a1", multiplicity="1", role_name="m1",
                                 source_multiplicity="*", source_role_name="m2")
        a1.delete()
        with pytest.raises(CException) as exc_info:
            CStereotype(extended=[a1])
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"


