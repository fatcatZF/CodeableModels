
import pytest
from codeable_models import CBundle, CMetaclass, CClass, CObject, CAttribute, CException, CEnum


class TestBundlesOfEnums:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.b1 = CBundle("B1")
        self.b2 = CBundle("B2")

    def test_enum_name_fail(self):
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            CEnum(self.mcl)
        e = exc_info.value
        assert e.value.startswith("is not a name string: '")
        assert e.value.endswith(" MCL'")

    def test_enum_defined_bundles(self):
        assert set(self.b1.get_elements()) == set()
        e1 = CEnum("E1", values=["A", "B", "C"], bundles=self.b1)
        assert set(self.b1.get_elements()) == {e1}
        e2 = CEnum("E2", values=["A", "B", "C"], bundles=[self.b1])
        e3 = CEnum("E3", values=["A", "B", "C"], bundles=[self.b1, self.b2])
        mcl = CMetaclass("MCL", bundles=self.b1)
        assert set(self.b1.get_elements(type=CEnum)) == {e1, e2, e3}
        assert set(self.b1.elements) == {e1, e2, e3, mcl}
        assert set(self.b2.get_elements(type=CEnum)) == {e3}
        assert set(self.b2.elements) == {e3}

    def test_bundle_defined_enums(self):
        e1 = CEnum("E1", values=["A", "B", "C"])
        e2 = CEnum("E2", values=["A", "B", "C"])
        e3 = CEnum("E3", values=["A", "B", "C"])
        assert set(self.b1.get_elements(type=CEnum)) == set()
        b1 = CBundle("B1", elements=[e1, e2, e3])
        assert set(b1.elements) == {e1, e2, e3}
        self.mcl.bundles = b1
        assert set(b1.elements) == {e1, e2, e3, self.mcl}
        assert set(b1.get_elements(type=CEnum)) == {e1, e2, e3}
        b2 = CBundle("B2")
        b2.elements = [e2, e3]
        assert set(b2.get_elements(type=CEnum)) == {e2, e3}
        assert set(e1.bundles) == {b1}
        assert set(e2.bundles) == {b1, b2}
        assert set(e3.bundles) == {b1, b2}

    def test_get_enums_by_name(self):
        assert set(self.b1.get_elements(type=CEnum, name="E1")) == set()
        e1 = CEnum("E1", bundles=self.b1)
        m = CMetaclass("E1", bundles=self.b1)
        assert self.b1.get_elements(type=CMetaclass) == [m]
        assert set(self.b1.get_elements(type=CEnum, name="E1")) == {e1}
        e2 = CEnum("E1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CEnum, name="E1")) == {e1, e2}
        assert e1 != e2
        e3 = CEnum("E1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CEnum, name="E1")) == {e1, e2, e3}
        assert self.b1.get_element(type=CEnum, name="E1") == e1

    def test_get_enum_elements_by_name(self):
        assert set(self.b1.get_elements(name="E1")) == set()
        e1 = CEnum("E1", bundles=self.b1)
        assert set(self.b1.get_elements(name="E1")) == {e1}
        m = CMetaclass("E1", bundles=self.b1)
        assert set(self.b1.get_elements(name="E1")) == {m, e1}
        e2 = CEnum("E1", bundles=self.b1)
        assert set(self.b1.get_elements(name="E1")) == {m, e1, e2}
        assert e1 != e2
        e3 = CEnum("E1", bundles=self.b1)
        assert set(self.b1.get_elements(name="E1")) == {m, e1, e2, e3}
        assert self.b1.get_element(name="E1") == e1

    def test_enum_defined_bundle_change(self):
        e1 = CEnum("E1", bundles=self.b1)
        e2 = CEnum("E2", bundles=self.b1)
        e3 = CEnum("E3", bundles=self.b1)
        mcl = CMetaclass("MCL", bundles=self.b1)
        b = CBundle()
        e2.bundles = b
        e3.bundles = None
        self.mcl.bundles = b
        assert set(self.b1.elements) == {mcl, e1}
        assert set(self.b1.get_elements(type=CEnum)) == {e1}
        assert set(b.elements) == {e2, self.mcl}
        assert set(b.get_elements(type=CEnum)) == {e2}
        assert e1.bundles == [self.b1]
        assert e2.bundles == [b]
        assert e3.bundles == []

    def test_bundle_delete_enum(self):
        e1 = CEnum("E1", bundles=self.b1)
        e2 = CEnum("E2", bundles=self.b1)
        e3 = CEnum("E3", bundles=self.b1)
        self.b1.delete()
        assert set(self.b1.elements) == set()
        assert e1.bundles == []
        assert e1.name == "E1"
        assert e2.bundles == []
        assert e3.bundles == []

    def test_creation_of_unnamed_enum_in_bundle(self):
        e1 = CEnum()
        e2 = CEnum()
        e3 = CEnum("x")
        mcl = CMetaclass()
        self.b1.elements = [e1, e2, e3, mcl]
        assert set(self.b1.get_elements(type=CEnum)) == {e1, e2, e3}
        assert self.b1.get_element(type=CEnum, name=None) == e1
        assert set(self.b1.get_elements(type=CEnum, name=None)) == {e1, e2}
        assert set(self.b1.get_elements(name=None)) == {e1, e2, mcl}

    def test_remove_enum_from_bundle(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        e1 = CEnum("E1", bundles=b1)
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
            b2.remove(e1)
        e = exc_info.value
        assert "'E1' is not an element of the bundle" == e.value
        b1.remove(e1)
        assert set(b1.get_elements(type=CEnum)) == set()

        e1 = CEnum("E1", bundles=b1)
        e2 = CEnum("E2", bundles=b1)
        e3 = CEnum("E3", values=["1", "2"], bundles=b1)

        b1.remove(e1)
        with pytest.raises(CException) as exc_info:
            b1.remove(CEnum("E2", bundles=b2))
        e = exc_info.value
        assert "'E2' is not an element of the bundle" == e.value
        with pytest.raises(CException) as exc_info:
            b1.remove(e1)
        e = exc_info.value
        assert "'E1' is not an element of the bundle" == e.value

        assert set(b1.get_elements(type=CEnum)) == {e2, e3}
        b1.remove(e3)
        assert set(b1.get_elements(type=CEnum)) == {e2}

        assert e3.name == "E3"
        assert e3.bundles == []
        assert e3.values == ["1", "2"]

    def test_delete_enum_from_bundle(self):
        b1 = CBundle("B1")
        e1 = CEnum("E1", bundles=b1)
        e1.delete()
        assert set(b1.get_elements(type=CEnum)) == set()

        e1 = CEnum("E1", bundles=b1)
        e2 = CEnum("E2", bundles=b1)
        e3 = CEnum("E3", values=["1", "2"], bundles=b1)
        ea1 = CAttribute(type=e3, default="1")
        ea2 = CAttribute(type=e3)
        cl = CClass(self.mcl, attributes={"letters1": ea1, "letters2": ea2})
        o = CObject(cl, "o")

        e1.delete()
        assert set(b1.get_elements(type=CEnum)) == {e2, e3}
        e3.delete()
        assert set(b1.get_elements(type=CEnum)) == {e2}

        assert e3.name == None
        assert e3.bundles == []
        assert e3.values == []
        assert set(cl.attributes) == {ea1, ea2}
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
            ea1.type = e1
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            ea1.type = e2
        e = exc_info.value
        assert "default value '1' incompatible with attribute's type 'E2'" == e.value
        with pytest.raises(CException) as exc_info:
            o.set_value("letters1", "1")
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            o.get_value("letters1")
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value

    def test_remove_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        e1 = CEnum("e1", bundles=[b1, b2])
        b1.remove(e1)
        assert set(b1.get_elements(type=CEnum)) == set()
        assert set(b2.get_elements(type=CEnum)) == {e1}
        assert set(e1.bundles) == {b2}

    def test_delete_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        e1 = CEnum("e1", bundles=[b1, b2])
        b1.delete()
        assert set(b1.get_elements(type=CEnum)) == set()
        assert set(b2.get_elements(type=CEnum)) == {e1}
        assert set(e1.bundles) == {b2}

    def test_delete_enum_having_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        e1 = CEnum("e1", bundles=[b1, b2])
        e2 = CEnum("e2", bundles=[b2])
        e1.delete()
        assert set(b1.get_elements(type=CEnum)) == set()
        assert set(b2.get_elements(type=CEnum)) == {e2}
        assert set(e1.bundles) == set()
        assert set(e2.bundles) == {b2}

    def test_delete_enum_that_is_an_attribute_type(self):
        b1 = CBundle("B1")
        CBundle("B2")
        e1 = CEnum("E1", bundles=b1)
        e2 = CEnum("E2", bundles=b1)
        e3 = CEnum("E3", values=["1", "2"], bundles=b1)
        ea1 = CAttribute(type=e3, default="1")
        ea2 = CAttribute(type=e3)
        cl = CClass(self.mcl, attributes={"letters1": ea1, "letters2": ea2})
        o = CObject(cl, "o")
        e1.delete()
        e3.delete()
        with pytest.raises(CException) as exc_info:
            ea1.default = "3"
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            ea1.type = e1
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            ea1.default = "3"
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            ea1.type = e1
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            ea1.type = e2
        e = exc_info.value
        assert "default value '1' incompatible with attribute's type 'E2'" == e.value
        with pytest.raises(CException) as exc_info:
            o.set_value("letters1", "1")
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            o.get_value("letters1")
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value

    def test_bundle_that_is_deleted(self):
        b1 = CBundle("B1")
        b1.delete()
        with pytest.raises(CException) as exc_info:
            CEnum("E1", bundles=b1)
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_set_bundle_to_none(self):
        c = CEnum("E1", bundles=None)
        assert c.bundles == []
        assert c.name == "E1"


