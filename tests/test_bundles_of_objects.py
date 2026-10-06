
import pytest
from codeable_models import CBundle, CMetaclass, CClass, CObject, CException, CEnum


class TestBundlesOfClasses:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.cl = CClass(self.mcl, "C", attributes={"i": 1})
        self.b1 = CBundle("B1")
        self.b2 = CBundle("B2")

    def test_object_name_fail(self):
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            CObject(self.cl, self.b1)
        e = exc_info.value
        assert e.value.startswith("is not a name string: '")
        assert e.value.endswith(" B1'")

    def test_object_defined_bundles(self):
        assert set(self.b1.get_elements(type=CObject)) == set()
        o1 = CObject(self.cl, "O1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CObject)) == {o1}
        o2 = CObject(self.cl, "O2", bundles=[self.b1])
        o3 = CObject(self.cl, "O3", bundles=[self.b1, self.b2])
        mcl = CMetaclass("MCL", bundles=self.b1)
        assert set(self.b1.get_elements(type=CObject)) == {o1, o2, o3}
        assert set(self.b1.elements) == {o1, o2, o3, mcl}
        assert set(self.b2.get_elements(type=CObject)) == {o3}
        assert set(self.b2.elements) == {o3}

    def test_bundle_defined_objects(self):
        o1 = CObject(self.cl, "O1")
        o2 = CObject(self.cl, "O2")
        o3 = CObject(self.cl, "O3")
        assert set(self.b1.get_elements(type=CObject)) == set()
        b1 = CBundle("B1", elements=[o1, o2, o3])
        assert set(b1.elements) == {o1, o2, o3}
        self.mcl.bundles = b1
        assert set(b1.elements) == {o1, o2, o3, self.mcl}
        assert set(b1.get_elements(type=CObject)) == {o1, o2, o3}
        b2 = CBundle("B2")
        b2.elements = [o2, o3]
        assert set(b2.get_elements(type=CObject)) == {o2, o3}
        assert set(o1.bundles) == {b1}
        assert set(o2.bundles) == {b1, b2}
        assert set(o3.bundles) == {b1, b2}

    def test_get_objects_by_name(self):
        assert set(self.b1.get_elements(type=CObject, name="O1")) == set()
        o1 = CObject(self.cl, "O1", bundles=self.b1)
        m = CMetaclass("O1", bundles=self.b1)
        assert self.b1.get_elements(type=CMetaclass) == [m]
        assert set(self.b1.get_elements(type=CObject, name="O1")) == {o1}
        o2 = CObject(self.cl, "O1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CObject, name="O1")) == {o1, o2}
        assert o1 != o2
        o3 = CObject(self.cl, "O1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CObject, name="O1")) == {o1, o2, o3}
        assert self.b1.get_element(type=CObject, name="O1") == o1

    def test_get_object_elements_by_name(self):
        assert set(self.b1.get_elements(type=CObject, name="O1")) == set()
        o1 = CObject(self.cl, "O1", bundles=self.b1)
        assert set(self.b1.get_elements(type=CObject, name="O1")) == {o1}
        m = CMetaclass("O1", bundles=self.b1)
        assert set(self.b1.get_elements(name="O1")) == {m, o1}
        o2 = CObject(self.cl, "O1", bundles=self.b1)
        assert set(self.b1.get_elements(name="O1")) == {m, o1, o2}
        assert o1 != o2
        o3 = CObject(self.cl, "O1", bundles=self.b1)
        assert set(self.b1.get_elements(name="O1")) == {m, o1, o2, o3}
        assert self.b1.get_element(type=CObject, name="O1") == o1

    def test_object_defined_bundle_change(self):
        o1 = CObject(self.cl, "O1", bundles=self.b1)
        o2 = CObject(self.cl, "O2", bundles=self.b1)
        o3 = CObject(self.cl, "O3", bundles=self.b1)
        mcl = CMetaclass("MCL", bundles=self.b1)
        b = CBundle()
        o2.bundles = b
        o3.bundles = None
        self.mcl.bundles = b
        assert set(self.b1.elements) == {mcl, o1}
        assert set(self.b1.get_elements(type=CObject)) == {o1}
        assert set(b.elements) == {o2, self.mcl}
        assert set(b.get_elements(type=CObject)) == {o2}
        assert o1.bundles == [self.b1]
        assert o2.bundles == [b]
        assert o3.bundles == []

    def test_bundle_delete_object(self):
        o1 = CObject(self.cl, "O1", bundles=self.b1)
        o2 = CObject(self.cl, "O2", bundles=self.b1)
        o3 = CObject(self.cl, "O3", bundles=self.b1)
        self.b1.delete()
        assert set(self.b1.elements) == set()
        assert o1.bundles == []
        assert o1.classifier == self.cl
        assert o2.bundles == []
        assert o3.bundles == []

    def test_creation_of_unnamed_object_in_bundle(self):
        o1 = CObject(self.cl)
        o2 = CObject(self.cl)
        o3 = CObject(self.cl, "x")
        mcl = CMetaclass()
        self.b1.elements = [o1, o2, o3, mcl]
        assert set(self.b1.get_elements(type=CObject)) == {o1, o2, o3}
        assert self.b1.get_element(type=CObject, name=None) == o1
        assert set(self.b1.get_elements(type=CObject, name=None)) == {o1, o2}
        assert self.b1.get_element(name=None) == o1
        assert set(self.b1.get_elements(name=None)) == {o1, o2, mcl}

    def test_remove_object_from_bundle(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        o = CObject(self.cl, "O", bundles=b1)
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
            b2.remove(o)
        e = exc_info.value
        assert "'O' is not an element of the bundle" == e.value
        b1.remove(o)
        assert set(b1.get_elements(type=CObject)) == set()

        o1 = CObject(self.cl, "O1", bundles=b1)
        o2 = CObject(self.cl, "O2", bundles=b1)
        o3 = CObject(self.cl, "O3", bundles=b1)
        o3.set_value("i", 7)

        b1.remove(o1)
        with pytest.raises(CException) as exc_info:
            b1.remove(CObject(CClass(self.mcl), "Obj2", bundles=b2))
        e = exc_info.value
        assert "'Obj2' is not an element of the bundle" == e.value
        with pytest.raises(CException) as exc_info:
            b1.remove(o1)
        e = exc_info.value
        assert "'O1' is not an element of the bundle" == e.value

        assert set(b1.get_elements(type=CObject)) == {o2, o3}
        b1.remove(o3)
        assert b1.get_elements(type=CObject) == [o2]

        assert o3.classifier == self.cl
        assert set(self.cl.objects) == {o, o1, o2, o3}
        assert o3.get_value("i") == 7
        assert o3.name == "O3"
        assert o3.bundles == []

    def test_delete_object_from_bundle(self):
        b1 = CBundle("B1")
        o = CObject(self.cl, "O1", bundles=b1)
        o.delete()
        assert set(b1.get_elements(type=CObject)) == set()

        o1 = CObject(self.cl, "O1", bundles=b1)
        o2 = CObject(self.cl, "O2", bundles=b1)
        o3 = CObject(self.cl, "O3", bundles=b1)
        o3.set_value("i", 7)

        o1.delete()
        assert set(b1.get_elements(type=CObject)) == {o2, o3}
        o3.delete()
        assert set(b1.get_elements(type=CObject)) == {o2}

        assert o3.classifier == None
        with pytest.raises(CException) as exc_info:
            o3.get_value("i")
        e = exc_info.value
        assert "can't get value 'i' on deleted object" == e.value
        assert o3.name == None
        assert o3.bundles == []

    def test_remove_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        o1 = CObject(self.cl, "o", bundles=[b1, b2])
        b1.remove(o1)
        assert set(b1.get_elements(type=CObject)) == set()
        assert set(b2.get_elements(type=CObject)) == {o1}
        assert set(o1.bundles) == {b2}

    def test_delete_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        o1 = CObject(self.cl, "o1", bundles=[b1, b2])
        b1.delete()
        assert set(b1.get_elements(type=CObject)) == set()
        assert set(b2.get_elements(type=CObject)) == {o1}
        assert set(o1.bundles) == {b2}

    def test_delete_object_having_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        o1 = CObject(self.cl, "o1", bundles=[b1, b2])
        o2 = CObject(self.cl, "o2", bundles=[b2])
        o1.delete()
        assert set(b1.get_elements(type=CObject)) == set()
        assert set(b2.get_elements(type=CObject)) == {o2}
        assert set(o1.bundles) == set()
        assert set(o2.bundles) == {b2}

    def test_bundle_that_is_deleted(self):
        b1 = CBundle("B1")
        b1.delete()
        with pytest.raises(CException) as exc_info:
            CObject(self.cl, "O1", bundles=b1)
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_set_bundle_to_none(self):
        o = CObject(self.cl, "O1", bundles=None)
        assert o.bundles == []
        assert o.name == "O1"


