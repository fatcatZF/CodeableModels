
import pytest
from codeable_models import CBundle, CStereotype, CMetaclass, CClass, CException, CEnum


class TestBundlesOfStereotypes:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.b1 = CBundle("B1")
        self.b2 = CBundle("B2")
        self.m1 = CMetaclass("M1")
        self.m2 = CMetaclass("M2")
        self.a = self.m1.association(self.m2, name="A", multiplicity="1", role_name="m1",
                                     source_multiplicity="*", source_role_name="m2")

    def test_stereotype_name_fail(self):
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            CStereotype(self.b1)
        e = exc_info.value
        assert e.value.startswith("is not a name string: '")
        assert e.value.endswith(" B1'")

    def test_stereotype_defined_bundles(self):
        assert set(self.b1.get_elements(type=CStereotype)) == set()
        s1 = CStereotype("s1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CStereotype)) == {s1}
        s2 = CStereotype("s2", bundles=[self.b1])
        s3 = CStereotype("s3", bundles=[self.b1, self.b2])
        cl = CClass(self.mcl, "C", bundles=self.b1)
        assert set(self.b1.get_elements(type=CStereotype)) == {s1, s2, s3}
        assert set(self.b1.elements) == {s1, s2, s3, cl}
        assert set(self.b2.get_elements(type=CStereotype)) == {s3}
        assert set(self.b2.elements) == {s3}

    def test_bundle_defined_stereotype(self):
        s1 = CStereotype("s1")
        s2 = CStereotype("s2")
        s3 = CStereotype("s3")
        assert set(self.b1.get_elements(type=CStereotype)) == set()
        b1 = CBundle("B1", elements=[s1, s2, s3])
        assert set(b1.elements) == {s1, s2, s3}
        cl = CClass(self.mcl, "C", bundles=b1)
        assert set(b1.elements) == {s1, s2, s3, cl}
        assert set(b1.get_elements(type=CStereotype)) == {s1, s2, s3}
        b2 = CBundle("B2")
        b2.elements = [s2, s3]
        assert set(b2.get_elements(type=CStereotype)) == {s2, s3}
        assert set(s1.bundles) == {b1}
        assert set(s2.bundles) == {b1, b2}
        assert set(s3.bundles) == {b1, b2}

    def test_get_stereotypes_by_name(self):
        assert set(self.b1.get_elements(type=CStereotype, name="s1")) == set()
        s1 = CStereotype("s1", bundles=self.b1)
        c1 = CClass(self.mcl, "C1", bundles=self.b1)
        assert self.b1.get_elements(type=CClass) == [c1]
        assert set(self.b1.get_elements(type=CStereotype, name="s1")) == {s1}
        s2 = CStereotype("s1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CStereotype, name="s1")) == {s1, s2}
        assert s1 != s2
        s3 = CStereotype("s1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CStereotype, name="s1")) == {s1, s2, s3}
        assert self.b1.get_element(type=CStereotype, name="s1") == s1

    def test_get_stereotype_elements_by_name(self):
        assert set(self.b1.get_elements(name="s1")) == set()
        s1 = CStereotype("s1", bundles=self.b1)
        assert set(self.b1.get_elements(name="s1")) == {s1}
        c1 = CClass(self.mcl, "s1", bundles=self.b1)
        assert set(self.b1.get_elements(name="s1")) == {s1, c1}
        s2 = CStereotype("s1", bundles=self.b1)
        assert set(self.b1.get_elements(name="s1")) == {s1, c1, s2}
        assert s1 != s2
        s3 = CStereotype("s1", bundles=self.b1)
        assert set(self.b1.get_elements(name="s1")) == {s1, c1, s2, s3}
        assert self.b1.get_element(name="s1") == s1

    def test_stereotype_defined_bundle_change(self):
        s1 = CStereotype("s1", bundles=self.b1)
        s2 = CStereotype("s2", bundles=self.b1)
        s3 = CStereotype("s3", bundles=self.b1)
        cl1 = CClass(self.mcl, "C1", bundles=self.b1)
        cl2 = CClass(self.mcl, "C2", bundles=self.b1)
        b = CBundle()
        s2.bundles = b
        s3.bundles = None
        cl2.bundles = b
        assert set(self.b1.elements) == {cl1, s1}
        assert set(self.b1.get_elements(type=CStereotype)) == {s1}
        assert set(b.elements) == {s2, cl2}
        assert set(b.get_elements(type=CStereotype)) == {s2}
        assert s1.bundles == [self.b1]
        assert s2.bundles == [b]
        assert s3.bundles == []

    def test_bundle_delete_stereotype_metaclass(self):
        s1 = CStereotype("s1", bundles=self.b1, extended=self.mcl)
        assert s1.extended == [self.mcl]
        s2 = CStereotype("s2", bundles=self.b1)
        s3 = CStereotype("s3", bundles=self.b1)
        self.b1.delete()
        assert set(self.b1.elements) == set()
        assert s1.bundles == []
        assert s1.extended == [self.mcl]
        assert s2.bundles == []
        assert s3.bundles == []

    def test_bundle_delete_stereotype_association(self):
        s1 = CStereotype("s1", bundles=self.b1, extended=self.a)
        assert s1.extended == [self.a]
        s2 = CStereotype("s2", bundles=self.b1)
        s3 = CStereotype("s3", bundles=self.b1)
        self.b1.delete()
        assert set(self.b1.elements) == set()
        assert s1.bundles == []
        assert s1.extended == [self.a]
        assert s2.bundles == []
        assert s3.bundles == []

    def test_creation_of_unnamed_stereotype_in_bundle(self):
        cl = CClass(self.mcl)
        s1 = CStereotype()
        s2 = CStereotype()
        s3 = CStereotype("x")
        self.b1.elements = [s1, s2, s3, cl]
        assert set(self.b1.get_elements(type=CStereotype)) == {s1, s2, s3}
        assert self.b1.get_element(name=None) == s1
        assert set(self.b1.get_elements(type=CStereotype, name=None)) == {s1, s2}
        assert self.b1.get_element(name=None) == s1
        assert set(self.b1.get_elements(name=None)) == {s1, s2, cl}

    def test_remove_stereotype_from_bundle(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        s1 = CStereotype("s1", bundles=b1)
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            b1.remove(None)
        e = exc_info.value
        assert "'None' is not an element of the bundle" == e.value
        with pytest.raises(CException) as exc_info:
            b1.remove(CEnum("A"))
        e = exc_info.value
        assert "'A' is not an element of the bundle" == e.value
        with pytest.raises(CException) as exc_info:
            b2.remove(s1)
        e = exc_info.value
        assert "'s1' is not an element of the bundle" == e.value
        b1.remove(s1)
        assert set(b1.get_elements(type=CStereotype)) == set()

        s1 = CStereotype("s1", bundles=b1)
        s2 = CStereotype("s1", bundles=b1)
        s3 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, bundles=b1, extended=self.mcl)
        s4 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, bundles=b1, extended=self.a)

        b1.remove(s1)
        with pytest.raises(CException) as exc_info:
            b1.remove(CStereotype("s2", bundles=b2))
        e = exc_info.value
        assert "'s2' is not an element of the bundle" == e.value
        with pytest.raises(CException) as exc_info:
            b1.remove(s1)
        e = exc_info.value
        assert "'s1' is not an element of the bundle" == e.value

        assert set(b1.get_elements(type=CStereotype)) == {s2, s3, s4}
        b1.remove(s3)
        b1.remove(s4)
        assert set(b1.get_elements(type=CStereotype)) == {s2}

        assert s3.superclasses == [s2]
        assert s2.subclasses == [s3, s4]
        assert s3.attribute_names == ["i"]
        assert s3.extended == [self.mcl]
        assert s3.name == "s1"
        assert s3.bundles == []
        assert s4.superclasses == [s2]
        assert s4.attribute_names == ["i"]
        assert s4.extended == [self.a]
        assert s4.name == "s1"
        assert s4.bundles == []

    def test_delete_stereotype_from_bundle(self):
        b1 = CBundle("B1")
        s1 = CStereotype("s1", bundles=b1)
        s1.delete()
        assert set(b1.get_elements(type=CStereotype)) == set()

        s1 = CStereotype("s1", bundles=b1)
        s2 = CStereotype("s1", bundles=b1)
        s3 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, bundles=b1, extended=self.mcl)
        s4 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, bundles=b1, extended=self.a)

        s1.delete()
        assert set(b1.get_elements(type=CStereotype)) == {s2, s3, s4}
        s3.delete()
        s4.delete()
        assert set(b1.get_elements(type=CStereotype)) == {s2}

        assert s3.superclasses == []
        assert s2.subclasses == []
        assert s3.attributes == []
        assert s3.attribute_names == []
        assert s3.extended == []
        assert s3.name == None
        assert s3.bundles == []

        assert s4.superclasses == []
        assert s4.attributes == []
        assert s4.attribute_names == []
        assert s4.extended == []
        assert s4.name == None
        assert s4.bundles == []

    def test_remove_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        s1 = CStereotype("s1", bundles=[b1, b2])
        b1.remove(s1)
        assert set(b1.get_elements(type=CStereotype)) == set()
        assert set(b2.get_elements(type=CStereotype)) == {s1}
        assert set(s1.bundles) == {b2}

    def test_delete_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        s1 = CStereotype("s1", bundles=[b1, b2])
        b1.delete()
        assert set(b1.get_elements(type=CStereotype)) == set()
        assert set(b2.get_elements(type=CStereotype)) == {s1}
        assert set(s1.bundles) == {b2}

    def test_delete_stereotype_having_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        s1 = CStereotype("s1", bundles=[b1, b2])
        s2 = CStereotype("s2", bundles=[b2])
        s1.delete()
        assert set(b1.get_elements(type=CStereotype)) == set()
        assert set(b2.get_elements(type=CStereotype)) == {s2}
        assert set(s1.bundles) == set()
        assert set(s2.bundles) == {b2}

    def test_stereotype_remove_stereotype_or_metaclass(self):
        mcl = CMetaclass("MCL1")
        s1 = CStereotype("S1", extended=[mcl])
        s2 = CStereotype("S2", extended=[mcl])
        s3 = CStereotype("S3", extended=[mcl])
        s4 = CStereotype("S4", extended=[mcl])
        self.b1.elements = [mcl, s1, s2, s3, s4]
        assert set(self.b1.get_elements(type=CStereotype)) == {s1, s2, s3, s4}
        s2.delete()
        assert set(self.b1.get_elements(type=CStereotype)) == {s1, s3, s4}
        assert set(s2.extended) == set()
        assert set(s1.extended) == {mcl}
        mcl.delete()
        assert set(mcl.stereotypes) == set()
        assert set(s1.extended) == set()
        assert set(self.b1.get_elements(type=CStereotype)) == {s1, s3, s4}

    def test_double_assignment_stereotype_extension_metaclass(self):
        with pytest.raises(CException) as exc_info:
            CStereotype("S1", bundles=self.b1, extended=[self.mcl, self.mcl])
        e = exc_info.value
        assert "'MCL' is already extended by stereotype 'S1'" == e.value
        s1 = self.b1.get_element(type=CStereotype, name="S1")
        assert s1.name == "S1"
        assert set(self.b1.get_elements(type=CStereotype)) == {s1}
        assert s1.bundles == [self.b1]
        assert self.mcl.stereotypes == [s1]

    def test_double_assignment_stereotype_extension_association(self):
        with pytest.raises(CException) as exc_info:
            CStereotype("S1", bundles=self.b1, extended=[self.a, self.a])
        e = exc_info.value
        assert "'A' is already extended by stereotype 'S1'" == e.value
        s1 = self.b1.get_element(type=CStereotype, name="S1")
        assert s1.name == "S1"
        assert set(self.b1.get_elements(type=CStereotype)) == {s1}
        assert s1.bundles == [self.b1]
        assert self.a.stereotypes == [s1]

    def test_double_assignment_metaclass_stereotype(self):
        with pytest.raises(CException) as exc_info:
            s1 = CStereotype("S1", bundles=self.b1)
            self.mcl.stereotypes = [s1, s1]
        e = exc_info.value
        assert "'S1' is already a stereotype of 'MCL'" == e.value
        s1 = self.b1.get_element(type=CStereotype, name="S1")
        assert s1.name == "S1"
        assert set(self.b1.get_elements(type=CStereotype)) == {s1}

    def test_double_assignment_association_stereotype(self):
        with pytest.raises(CException) as exc_info:
            s1 = CStereotype("S1", bundles=self.b1)
            self.a.stereotypes = [s1, s1]
        e = exc_info.value
        assert "'S1' is already a stereotype of 'A'" == e.value
        s1 = self.b1.get_element(type=CStereotype, name="S1")
        assert s1.name == "S1"
        assert set(self.b1.get_elements(type=CStereotype)) == {s1}

    def test_bundle_that_is_deleted(self):
        b1 = CBundle("B1")
        b1.delete()
        with pytest.raises(CException) as exc_info:
            CStereotype("S1", bundles=b1)
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_set_bundle_to_none(self):
        s = CStereotype("S1", bundles=None)
        assert s.bundles == []
        assert s.name == "S1"


