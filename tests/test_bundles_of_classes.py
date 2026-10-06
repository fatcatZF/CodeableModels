
import pytest
from codeable_models import CBundle, CMetaclass, CClass, CObject, CAttribute, CException, CEnum


class TestBundlesOfClasses:
    def setup_method(self):
        self.mcl = CMetaclass("MCL", attributes={"i": 1})
        self.b1 = CBundle("B1")
        self.b2 = CBundle("B2")

    def test_class_name_fail(self):
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            CClass(self.mcl, self.mcl)
        e = exc_info.value
        assert e.value.startswith("is not a name string: '")
        assert e.value.endswith(" MCL'")

    def test_class_defined_bundles(self):
        assert set(self.b1.get_elements()) == set()
        cl1 = CClass(self.mcl, "Class1", bundles=self.b1)
        assert set(self.b1.get_elements()) == {cl1}
        cl2 = CClass(self.mcl, "Class2", bundles=[self.b1])
        cl3 = CClass(self.mcl, "Class3", bundles=[self.b1, self.b2])
        mcl = CMetaclass("MCL", bundles=self.b1)
        assert set(self.b1.get_elements(type=CClass)) == {cl1, cl2, cl3}
        assert set(self.b1.elements) == {cl1, cl2, cl3, mcl}
        assert set(self.b2.get_elements(type=CClass)) == {cl3}
        assert set(self.b2.elements) == {cl3}

    def test_bundle_defined_classes(self):
        cl1 = CClass(self.mcl, "Class1")
        cl2 = CClass(self.mcl, "Class2")
        cl3 = CClass(self.mcl, "Class3")
        assert set(self.b1.get_elements(type=CClass)) == set()
        b1 = CBundle("B1", elements=[cl1, cl2, cl3])
        assert set(b1.elements) == {cl1, cl2, cl3}
        self.mcl.bundles = b1
        assert set(b1.elements) == {cl1, cl2, cl3, self.mcl}
        assert set(b1.get_elements(type=CClass)) == {cl1, cl2, cl3}
        b2 = CBundle("B2")
        b2.elements = [cl2, cl3]
        assert set(b2.get_elements(type=CClass)) == {cl2, cl3}
        assert set(cl1.bundles) == {b1}
        assert set(cl2.bundles) == {b1, b2}
        assert set(cl3.bundles) == {b1, b2}

    def test_get_classes_by_name(self):
        assert set(self.b1.get_elements(type=CClass, name="CL1")) == set()
        c1 = CClass(self.mcl, "CL1", bundles=self.b1)
        m = CMetaclass("CL1", bundles=self.b1)
        assert self.b1.get_elements(type=CMetaclass) == [m]
        assert set(self.b1.get_elements(type=CClass, name="CL1")) == {c1}
        c2 = CClass(self.mcl, "CL1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CClass, name="CL1")) == {c1, c2}
        assert c1 != c2
        c3 = CClass(self.mcl, "CL1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CClass, name="CL1")) == {c1, c2, c3}
        assert self.b1.get_element(type=CClass, name="CL1") == c1

    def test_get_class_elements_by_name(self):
        assert set(self.b1.get_elements(name="CL1")) == set()
        c1 = CClass(self.mcl, "CL1", bundles=self.b1)
        assert set(self.b1.get_elements(name="CL1")) == {c1}
        m = CMetaclass("CL1", bundles=self.b1)
        assert set(self.b1.get_elements(name="CL1")) == {m, c1}
        c2 = CClass(self.mcl, "CL1", bundles=self.b1)
        assert set(self.b1.get_elements(name="CL1")) == {m, c1, c2}
        assert c1 != c2
        c3 = CClass(self.mcl, "CL1", bundles=self.b1)
        assert set(self.b1.get_elements(name="CL1")) == {m, c1, c2, c3}
        assert self.b1.get_element(name="CL1") == c1

    def test_class_defined_bundle_change(self):
        cl1 = CClass(self.mcl, "Class1", bundles=self.b1)
        cl2 = CClass(self.mcl, "Class2", bundles=self.b1)
        cl3 = CClass(self.mcl, "Class3", bundles=self.b1)
        mcl = CMetaclass("MCL", bundles=self.b1)
        b = CBundle()
        cl2.bundles = b
        cl3.bundles = None
        self.mcl.bundles = b
        assert set(self.b1.elements) == {mcl, cl1}
        assert set(self.b1.get_elements(type=CClass)) == {cl1}
        assert set(b.elements) == {cl2, self.mcl}
        assert set(b.get_elements(type=CClass)) == {cl2}
        assert cl1.bundles == [self.b1]
        assert cl2.bundles == [b]
        assert cl3.bundles == []

    def test_bundle_delete_class(self):
        cl1 = CClass(self.mcl, "Class1", bundles=self.b1)
        cl2 = CClass(self.mcl, "Class2", bundles=self.b1)
        cl3 = CClass(self.mcl, "Class3", bundles=self.b1)
        self.b1.delete()
        assert set(self.b1.elements) == set()
        assert cl1.bundles == []
        assert cl1.metaclass == self.mcl
        assert cl2.bundles == []
        assert cl3.bundles == []

    def test_creation_of_unnamed_class_in_bundle(self):
        c1 = CClass(self.mcl)
        c2 = CClass(self.mcl)
        c3 = CClass(self.mcl, "x")
        mcl = CMetaclass()
        self.b1.elements = [c1, c2, c3, mcl]
        assert set(self.b1.get_elements(type=CClass)) == {c1, c2, c3}
        assert self.b1.get_element(type=CClass, name=None) == c1
        assert set(self.b1.get_elements(type=CClass, name=None)) == {c1, c2}
        assert set(self.b1.get_elements(name=None)) == {c1, c2, mcl}

    def test_remove_class_from_bundle(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        cl1 = CClass(self.mcl, "CL1", bundles=b1)
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
            b2.remove(cl1)
        e = exc_info.value
        assert "'CL1' is not an element of the bundle" == e.value
        b1.remove(cl1)
        assert set(b1.get_elements(type=CClass)) == set()

        cl1 = CClass(self.mcl, "CL1", bundles=b1)
        cl2 = CClass(self.mcl, "CL2", bundles=b1)
        cl3 = CClass(self.mcl, "CL3", superclasses=cl2, attributes={"i": 1}, bundles=b1)
        cl3.set_value("i", 7)
        o = CObject(cl3, bundles=b1)

        b1.remove(cl1)
        with pytest.raises(CException) as exc_info:
            b1.remove(CClass(CMetaclass("MCL", bundles=b2), "CL2", bundles=b2))
        e = exc_info.value
        assert "'CL2' is not an element of the bundle" == e.value
        with pytest.raises(CException) as exc_info:
            b1.remove(cl1)
        e = exc_info.value
        assert "'CL1' is not an element of the bundle" == e.value

        assert set(b1.get_elements(type=CClass)) == {cl2, cl3}
        b1.remove(cl3)
        assert set(b1.get_elements(type=CClass)) == {cl2}

        assert cl3.superclasses == [cl2]
        assert cl2.subclasses == [cl3]
        assert cl3.attribute_names == ["i"]
        assert cl3.metaclass == self.mcl
        assert cl3.objects == [o]
        assert cl3.name == "CL3"
        assert cl3.bundles == []
        assert b1.get_elements(type=CObject) == [o]
        assert cl3.get_value("i") == 7

    def test_delete_class_from_bundle(self):
        b1 = CBundle("B1")
        cl1 = CClass(self.mcl, "CL1", bundles=b1)
        cl1.delete()
        assert set(b1.get_elements(type=CClass)) == set()

        cl1 = CClass(self.mcl, "CL1", bundles=b1)
        cl2 = CClass(self.mcl, "CL2", bundles=b1)
        cl3 = CClass(self.mcl, "CL3", superclasses=cl2, attributes={"i": 1}, bundles=b1)
        cl3.set_value("i", 7)
        CObject(cl3, bundles=b1)
        cl1.delete()
        assert set(b1.get_elements(type=CClass)) == {cl2, cl3}
        cl3.delete()
        assert set(b1.get_elements(type=CClass)) == {cl2}

        assert cl3.superclasses == []
        assert cl2.subclasses == []
        assert cl3.attributes == []
        assert cl3.attribute_names == []
        assert cl3.metaclass == None
        assert cl3.objects == []
        assert cl3.name == None
        assert cl3.bundles == []
        assert b1.get_elements(type=CObject) == []
        with pytest.raises(CException) as exc_info:
            cl3.get_value("i")
        e = exc_info.value
        assert "can't get value 'i' on deleted class" == e.value

    def test_remove_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        c1 = CClass(self.mcl, "c1", bundles=[b1, b2])
        b1.remove(c1)
        assert set(b1.get_elements(type=CClass)) == set()
        assert set(b2.get_elements(type=CClass)) == {c1}
        assert set(c1.bundles) == {b2}

    def test_delete_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        c1 = CClass(self.mcl, "c1", bundles=[b1, b2])
        b1.delete()
        assert set(b1.get_elements(type=CClass)) == set()
        assert set(b2.get_elements(type=CClass)) == {c1}
        assert set(c1.bundles) == {b2}

    def test_delete_class_having_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        c1 = CClass(self.mcl, "c1", bundles=[b1, b2])
        c2 = CClass(self.mcl, "c2", bundles=[b2])
        c1.delete()
        assert set(b1.get_elements(type=CClass)) == set()
        assert set(b2.get_elements(type=CClass)) == {c2}
        assert set(c1.bundles) == set()
        assert set(c2.bundles) == {b2}

    def test_delete_class_that_is_an_attribute_type(self):
        b1 = CBundle("B1")
        cl1 = CClass(self.mcl, "CL1", bundles=b1)
        cl2 = CClass(self.mcl, "CL2", bundles=b1)
        cl3 = CClass(self.mcl, "CL3", bundles=b1)
        o3 = CObject(cl3, "O3")

        ea1 = CAttribute(type=cl3, default=o3)
        c = CClass(self.mcl, "C", bundles=b1, attributes={"o": ea1})
        o = CObject(c)
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
            o.set_value("o", CObject(cl2))
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value
        with pytest.raises(CException) as exc_info:
            o.get_value("o")
        e = exc_info.value
        assert "cannot access named element that has been deleted" == e.value

    def test_bundle_that_is_deleted(self):
        b1 = CBundle("B1")
        CBundle("B2")
        b1.delete()
        with pytest.raises(CException) as exc_info:
            CClass(self.mcl, "CL1", bundles=b1)
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_set_bundle_to_none(self):
        c = CClass(self.mcl, "C", bundles=None)
        assert c.bundles == []
        assert c.name == "C"

    def test_bundle_elements_that_are_deleted(self):
        c = CClass(self.mcl, "C")
        c.delete()
        with pytest.raises(CException) as exc_info:
            CBundle("B1", elements=[c])
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_bundle_elements_that_are_none(self):
        with pytest.raises(CException) as exc_info:
            CBundle("B1", elements=[None])
        e = exc_info.value
        assert e.value == "'None' cannot be an element of bundle"


