
import pytest
from codeable_models import CBundle, CMetaclass, CClass, CObject, CAttribute, CException, CEnum


class TestBundlesOfMetaclasses:
    def setup_method(self):
        self.b1 = CBundle("B1")
        self.b2 = CBundle("B2")

    def test_metaclass_name_fail(self):
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            CMetaclass(self.b1)
        e = exc_info.value
        assert e.value.startswith("is not a name string: '")
        assert e.value.endswith(" B1'")

    def test_metaclass_defined_bundles(self):
        assert set(self.b1.get_elements()) == set()
        m1 = CMetaclass("M1", bundles=self.b1)
        assert set(self.b1.get_elements()) == {m1}
        m2 = CMetaclass("M2", bundles=[self.b1])
        m3 = CMetaclass("M3", bundles=[self.b1, self.b2])
        cl = CClass(m1, "C", bundles=[self.b1, self.b2])
        assert set(self.b1.get_elements(type=CMetaclass)) == {m1, m2, m3}
        assert set(self.b1.elements) == {m1, m2, m3, cl}
        assert set(self.b2.get_elements(type=CMetaclass)) == {m3}
        assert set(self.b2.elements) == {m3, cl}

    def test_bundle_defined_metaclasses(self):
        m1 = CMetaclass("M1")
        m2 = CMetaclass("M2")
        m3 = CMetaclass("M3")
        assert set(self.b1.get_elements(type=CMetaclass)) == set()
        b1 = CBundle("B1", elements=[m1, m2, m3])
        assert set(b1.elements) == {m1, m2, m3}
        cl = CClass(m1, "C", bundles=b1)
        assert set(b1.elements) == {m1, m2, m3, cl}
        assert set(b1.get_elements(type=CMetaclass)) == {m1, m2, m3}
        b2 = CBundle("B2")
        b2.elements = [m2, m3]
        assert set(b2.get_elements(type=CMetaclass)) == {m2, m3}
        assert set(m1.bundles) == {b1}
        assert set(m2.bundles) == {b1, b2}
        assert set(m3.bundles) == {b1, b2}

    def test_get_metaclasses_by_name(self):
        assert set(self.b1.get_elements(type=CMetaclass, name="m1")) == set()
        m1 = CMetaclass("M1", bundles=self.b1)
        c1 = CClass(m1, "C1", bundles=self.b1)
        assert self.b1.get_elements(type=CClass) == [c1]
        assert set(self.b1.get_elements(type=CMetaclass, name="M1")) == {m1}
        m2 = CMetaclass("M1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CMetaclass, name="M1")) == {m1, m2}
        assert m1 != m2
        m3 = CMetaclass("M1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CMetaclass, name="M1")) == {m1, m2, m3}
        assert self.b1.get_element(type=CMetaclass, name="M1") == m1

    def test_get_metaclass_elements_by_name(self):
        assert set(self.b1.get_elements(name="M1")) == set()
        m1 = CMetaclass("M1", bundles=self.b1)
        assert set(self.b1.get_elements(name="M1")) == {m1}
        c1 = CClass(m1, "M1", bundles=self.b1)
        assert set(self.b1.get_elements(name="M1")) == {m1, c1}
        m2 = CMetaclass("M1", bundles=self.b1)
        assert set(self.b1.get_elements(name="M1")) == {m1, c1, m2}
        assert m1 != m2
        m3 = CMetaclass("M1", bundles=self.b1)
        assert set(self.b1.get_elements(name="M1")) == {m1, c1, m2, m3}
        assert self.b1.get_element(name="M1") == m1

    def test_metaclass_defined_bundle_change(self):
        m1 = CMetaclass("M1", bundles=self.b1)
        m2 = CMetaclass("M2", bundles=self.b1)
        m3 = CMetaclass("M3", bundles=self.b1)
        cl1 = CClass(m1, "C1", bundles=self.b1)
        cl2 = CClass(m1, "C2", bundles=self.b1)
        b = CBundle()
        m2.bundles = b
        m3.bundles = None
        cl2.bundles = b
        assert set(self.b1.elements) == {cl1, m1}
        assert set(self.b1.get_elements(type=CMetaclass)) == {m1}
        assert set(b.elements) == {m2, cl2}
        assert set(b.get_elements(type=CMetaclass)) == {m2}
        assert m1.bundles == [self.b1]
        assert m2.bundles == [b]
        assert m3.bundles == []

    def test_bundle_delete_metaclass(self):
        m1 = CMetaclass("M1", bundles=self.b1)
        c = CClass(m1)
        assert m1.classes == [c]
        m2 = CMetaclass("M2", bundles=self.b1)
        m3 = CMetaclass("M3", bundles=self.b1)
        self.b1.delete()
        assert set(self.b1.elements) == set()
        assert m1.bundles == []
        assert m1.classes == [c]
        assert m2.bundles == []
        assert m3.bundles == []

    def test_creation_of_unnamed_metaclass_in_bundle(self):
        m1 = CMetaclass()
        m2 = CMetaclass()
        m3 = CMetaclass("x")
        cl = CClass(m1)
        self.b1.elements = [m1, m2, m3, cl]
        assert set(self.b1.get_elements(type=CMetaclass)) == {m1, m2, m3}
        assert self.b1.get_element(name=None) == m1
        assert set(self.b1.get_elements(type=CMetaclass, name=None)) == {m1, m2}
        assert set(self.b1.get_elements(name=None)) == {m1, m2, cl}

    def test_remove_metaclass_from_bundle(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        m1 = CMetaclass("M1", bundles=b1)
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
            b2.remove(m1)
        e = exc_info.value
        assert "'M1' is not an element of the bundle" == e.value
        b1.remove(m1)
        assert set(b1.get_elements(type=CMetaclass)) == set()

        m1 = CMetaclass("M1", bundles=b1)
        m2 = CMetaclass("M1", bundles=b1)
        m3 = CMetaclass("M1", superclasses=m2, attributes={"i": 1}, bundles=b1)
        c = CClass(m3, bundles=b1)

        b1.remove(m1)
        with pytest.raises(CException) as exc_info:
            b1.remove(CMetaclass("M2", bundles=b2))
        e = exc_info.value
        assert "'M2' is not an element of the bundle" == e.value
        with pytest.raises(CException) as exc_info:
            b1.remove(m1)
        e = exc_info.value
        assert "'M1' is not an element of the bundle" == e.value

        assert set(b1.get_elements(type=CMetaclass)) == {m2, m3}
        b1.remove(m3)
        assert set(b1.get_elements(type=CMetaclass)) == {m2}

        assert m3.superclasses == [m2]
        assert m2.subclasses == [m3]
        assert m3.attribute_names == ["i"]
        assert m3.classes == [c]
        assert m3.name == "M1"
        assert m3.bundles == []
        assert b1.get_elements(type=CClass) == [c]

    def test_delete_metaclass_from_bundle(self):
        b1 = CBundle("B1")
        CBundle("B2")
        m1 = CMetaclass("M1", bundles=b1)
        m1.delete()
        assert set(b1.get_elements(type=CMetaclass)) == set()

        m1 = CMetaclass("M1", bundles=b1)
        m2 = CMetaclass("M1", bundles=b1)
        m3 = CMetaclass("M1", superclasses=m2, attributes={"i": 1}, bundles=b1)
        CClass(m3, bundles=b1)
        m1.delete()
        assert set(b1.get_elements(type=CMetaclass)) == {m2, m3}
        m3.delete()
        assert set(b1.get_elements(type=CMetaclass)) == {m2}

        assert m3.superclasses == []
        assert m2.subclasses == []
        assert m3.attributes == []
        assert m3.attribute_names == []
        assert m3.classes == []
        assert m3.name == None
        assert m3.bundles == []
        assert b1.get_elements(type=CClass) == []

    def test_remove_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        m1 = CMetaclass("m1", bundles=[b1, b2])
        b1.remove(m1)
        assert set(b1.get_elements(type=CMetaclass)) == set()
        assert set(b2.get_elements(type=CMetaclass)) == {m1}
        assert set(m1.bundles) == {b2}

    def test_delete_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        m1 = CMetaclass("m1", bundles=[b1, b2])
        b1.delete()
        assert set(b1.get_elements(type=CMetaclass)) == set()
        assert set(b2.get_elements(type=CMetaclass)) == {m1}
        assert set(m1.bundles) == {b2}

    def test_delete_metaclass_having_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        m1 = CMetaclass("m1", bundles=[b1, b2])
        m2 = CMetaclass("m2", bundles=[b2])
        m1.delete()
        assert set(b1.get_elements(type=CMetaclass)) == set()
        assert set(b2.get_elements(type=CMetaclass)) == {m2}
        assert set(m1.bundles) == set()
        assert set(m2.bundles) == {b2}

    def test_delete_class_that_is_an_attribute_type(self):
        b1 = CBundle("B1")
        mcl = CMetaclass("MCL")
        cl1 = CClass(mcl, "CL1", bundles=b1)
        cl2 = CClass(mcl, "CL2", bundles=b1)
        cl3 = CClass(mcl, "CL3", bundles=b1)
        o3 = CObject(cl3, "O3")

        ea1 = CAttribute(type=cl3, default=o3)
        m = CMetaclass("M", bundles=b1, attributes={"o": ea1})
        c = CClass(m)
        cl1.delete()
        cl3.delete()
        with pytest.raises(CException) as exc_info:
            # we just use list here, in order to not get a warning that ea1.default has no effect
            list([ea1.default])
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            # we just use list here, in order to not get a warning that ea1.type has no effect
            list([ea1.type])
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            ea1.default = "3"
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            ea1.type = cl1
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            ea1.type = cl2
        e = exc_info.value
        assert "default value '' incompatible with attribute's type 'CL2'" == e.value
        with pytest.raises(CException) as exc_info:
            c.set_value("o", CObject(cl2))
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            c.get_value("o")
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value

    def test_bundle_that_is_deleted(self):
        b1 = CBundle("B1")
        b1.delete()
        with pytest.raises(CException) as exc_info:
            CMetaclass("M", bundles=b1)
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_set_bundle_to_none(self):
        c = CMetaclass("M", bundles=None)
        assert c.bundles == []
        assert c.name == "M"


