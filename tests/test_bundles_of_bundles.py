
import pytest
from codeable_models import CBundle, CMetaclass, CClass, CException, CEnum


class TestBundlesOfBundles:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.b1 = CBundle("B1")
        self.b2 = CBundle("B2")

    def test_bundle_defined_bundles(self):
        assert set(self.b1.get_elements()) == set()
        b1 = CBundle("B1", bundles=self.b1)
        assert set(self.b1.get_elements()) == {b1}
        b2 = CBundle("B2", bundles=[self.b1])
        b3 = CBundle("B3", bundles=[self.b1, self.b2])
        mcl = CMetaclass("MCL", bundles=self.b1)
        assert set(self.b1.get_elements(type=CBundle)) == {b1, b2, b3}
        assert set(self.b1.elements) == {b1, b2, b3, mcl}
        assert set(self.b2.get_elements(type=CBundle)) == {b3}
        assert set(self.b2.elements) == {b3}

    def test_bundle_defined_by_bundle_list(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        b3 = CBundle("P3")
        assert set(self.b1.get_elements(type=CBundle)) == set()
        ba = CBundle("PA", elements=[b1, b2, b3])
        assert set(ba.elements) == {b1, b2, b3}
        self.mcl.bundles = ba
        assert set(ba.elements) == {b1, b2, b3, self.mcl}
        assert set(ba.get_elements(type=CBundle)) == {b1, b2, b3}
        bb = CBundle("PB")
        bb.elements = [b2, b3]
        assert set(bb.get_elements(type=CBundle)) == {b2, b3}
        assert set(b1.bundles) == {ba}
        assert set(b2.bundles) == {ba, bb}
        assert set(b3.bundles) == {ba, bb}
        assert set(ba.bundles) == set()
        assert set(bb.bundles) == set()
        assert set(b1.elements) == set()
        assert set(b2.elements) == set()
        assert set(b3.elements) == set()

    def test_get_bundles_by_name(self):
        assert set(self.b1.get_elements(name="B1")) == set()
        b1 = CBundle("B1", bundles=self.b1)
        m = CMetaclass("B1", bundles=self.b1)
        assert self.b1.get_elements(type=CMetaclass) == [m]
        assert set(self.b1.get_elements(name="B1", type=CBundle)) == {b1}
        b2 = CBundle("B1", bundles=self.b1)
        assert set(self.b1.get_elements(name="B1", type=CBundle)) == {b1, b2}
        assert b1 != b2
        b3 = CBundle("B1", bundles=self.b1)
        assert set(self.b1.get_elements(name="B1", type=CBundle)) == {b1, b2, b3}
        assert self.b1.get_element(name="B1", type=CBundle) == b1

    def test_get_bundle_elements_by_name(self):
        assert set(self.b1.get_elements(name="B1")) == set()
        b1 = CBundle("B1", bundles=self.b1)
        assert set(self.b1.get_elements(name="B1")) == {b1}
        m = CMetaclass("B1", bundles=self.b1)
        assert set(self.b1.get_elements(name="B1")) == {m, b1}
        b2 = CBundle("B1", bundles=self.b1)
        assert set(self.b1.get_elements(name="B1")) == {m, b1, b2}
        assert b1 != b2
        b3 = CBundle("B1", bundles=self.b1)
        assert set(self.b1.get_elements(name="B1")) == {m, b1, b2, b3}
        assert self.b1.get_element(name="B1") == b1

    def test_bundle_defined_bundle_change(self):
        b1 = CBundle("B1", bundles=self.b1)
        b2 = CBundle("B2", bundles=self.b1)
        b3 = CBundle("P3", bundles=self.b1)
        mcl = CMetaclass("MCL", bundles=self.b1)
        b = CBundle()
        b2.bundles = b
        b3.bundles = None
        self.mcl.bundles = b
        assert set(self.b1.elements) == {mcl, b1}
        assert set(self.b1.get_elements(type=CBundle)) == {b1}
        assert set(b.elements) == {b2, self.mcl}
        assert set(b.get_elements(type=CBundle)) == {b2}
        assert b1.bundles == [self.b1]
        assert b2.bundles == [b]
        assert b3.bundles == []

    def test_bundle_delete_bundle(self):
        b1 = CBundle("B1", bundles=self.b1)
        b2 = CBundle("B2", bundles=self.b1)
        b3 = CBundle("P3", bundles=self.b1)
        self.b1.delete()
        assert set(self.b1.elements) == set()
        assert b1.get_elements(type=CBundle) == []
        assert b1.elements == []
        assert b2.get_elements(type=CBundle) == []
        assert b3.get_elements(type=CBundle) == []

    def test_creation_of_unnamed_bundle_in_bundle(self):
        b1 = CBundle()
        b2 = CBundle()
        b3 = CBundle("x")
        mcl = CMetaclass()
        self.b1.elements = [b1, b2, b3, mcl]
        assert set(self.b1.get_elements(type=CBundle)) == {b1, b2, b3}
        assert self.b1.get_element(name=None, type=CBundle) == b1
        assert set(self.b1.get_elements(name=None, type=CBundle)) == {b1, b2}
        assert set(self.b1.get_elements(name=None)) == {b1, b2, mcl}

    def test_remove_bundle_from_bundle(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        ba = CBundle("A", bundles=b1)
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
            b2.remove(ba)
        e = exc_info.value
        assert "'A' is not an element of the bundle" == e.value
        b1.remove(ba)
        assert set(b1.get_elements(type=CBundle)) == set()

        mcl1 = CMetaclass("MCL")
        cl1 = CClass(mcl1, "CL")

        ba = CBundle("PA", bundles=b1)
        bb = CBundle("PB", bundles=b1)
        bc = CBundle("PC", bundles=b1, elements=[mcl1, cl1])

        b1.remove(ba)
        with pytest.raises(CException) as exc_info:
            b1.remove(CBundle("PB", bundles=b2))
        e = exc_info.value
        assert "'PB' is not an element of the bundle" == e.value
        with pytest.raises(CException) as exc_info:
            b1.remove(ba)
        e = exc_info.value
        assert "'PA' is not an element of the bundle" == e.value

        assert set(b1.get_elements(type=CBundle)) == {bb, bc}
        b1.remove(bc)
        assert set(b1.get_elements(type=CBundle)) == {bb}

        assert bc.get_elements(type=CBundle) == []
        assert bc.get_elements(type=CBundle) == []
        assert bc.elements == [mcl1, cl1]

    def test_delete_bundle_from_bundle(self):
        b1 = CBundle("B1")
        ba = CBundle("A", bundles=b1)
        ba.delete()
        assert set(b1.get_elements(type=CBundle)) == set()

        mcl1 = CMetaclass("MCL")
        cl1 = CClass(mcl1, "CL")

        ba = CBundle("PA", bundles=b1)
        bb = CBundle("PB", bundles=b1)
        bc = CBundle("PC", bundles=b1, elements=[mcl1, cl1])

        ba.delete()
        assert set(b1.get_elements(type=CBundle)) == {bb, bc}
        bc.delete()
        assert set(b1.get_elements(type=CBundle)) == {bb}

        assert bc.get_elements(type=CBundle) == []
        assert bc.get_elements(type=CBundle) == []
        assert bc.elements == []

    def test_remove_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        ba = CBundle("ba", bundles=[b1, b2])
        b1.remove(ba)
        assert set(b1.get_elements(type=CBundle)) == set()
        assert set(b2.get_elements(type=CBundle)) == {ba}
        assert set(ba.bundles) == {b2}

    def test_delete_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        ba = CBundle("ba", bundles=[b1, b2])
        b1.delete()
        assert set(b1.get_elements(type=CBundle)) == set()
        assert set(b2.get_elements(type=CBundle)) == {ba}
        assert set(ba.bundles) == {b2}

    def test_delete_bundle_having_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        ba = CBundle("ba", bundles=[b1, b2])
        bb = CBundle("bb", bundles=[b2])
        ba.delete()
        assert set(b1.get_elements(type=CBundle)) == set()
        assert set(b2.get_elements(type=CBundle)) == {bb}
        assert set(ba.bundles) == set()
        assert set(bb.bundles) == {b2}

    def test_delete_top_level_bundle(self):
        b1 = CBundle("B1")
        ba = CBundle("A", bundles=b1)
        b1.delete()
        assert b1.get_elements(type=CBundle) == []
        assert ba.get_elements(type=CBundle) == []

        b1 = CBundle("B1")
        mcl1 = CMetaclass("MCL")
        cl1 = CClass(mcl1, "CL")

        ba = CBundle("BA", bundles=b1)
        bb = CBundle("BB", bundles=b1)
        bc = CBundle("BC", bundles=b1, elements=[mcl1, cl1])

        b1.delete()
        assert b1.get_elements(type=CBundle) == []
        assert b1.elements == []
        assert ba.get_elements(type=CBundle) == []
        assert bb.get_elements(type=CBundle) == []
        assert bc.get_elements(type=CBundle) == []
        assert bc.elements == [mcl1, cl1]
        assert bc.get_elements(type=CBundle) == []
        assert mcl1.classes == [cl1]
        assert mcl1.bundles == [bc]
        assert cl1.metaclass == mcl1
        assert cl1.bundles == [bc]

    def test_bundle_that_is_deleted(self):
        b1 = CBundle("B1")
        b1.delete()
        with pytest.raises(CException) as exc_info:
            CBundle("A", bundles=b1)
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_set_bundle_to_none(self):
        p = CBundle("A", bundles=None)
        assert p.get_elements(type=CBundle) == []
        assert p.name == "A"


