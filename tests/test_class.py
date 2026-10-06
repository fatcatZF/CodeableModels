
import pytest
from codeable_models import CMetaclass, CClass, CObject, CException, CBundle


class TestClass:
    def setup_method(self):
        self.mcl = CMetaclass("MCL", attributes={"i": 1})

    def test_creation_of_one_class(self):
        assert self.mcl.classes == []
        cl = CClass(self.mcl, "CL")
        cl2 = self.mcl.classes[0]
        assert cl2.name == "CL"
        assert cl == cl2
        assert cl2.metaclass == self.mcl

    def test_create_class_wrong_arg_types(self):
        with pytest.raises(CException) as exc_info:
            CClass("MCL", "CL")
        e = exc_info.value
        assert "'MCL' is not a metaclass" == e.value
        with pytest.raises(CException) as exc_info:
            cl = CClass(self.mcl, "TC")
            CClass(cl, "CL")
        e = exc_info.value
        assert "'TC' is not a metaclass" == e.value

    def test_creation_of_3_classes(self):
        c1 = CClass(self.mcl, "CL1")
        c2 = CClass(self.mcl, "CL2")
        c3 = CClass(self.mcl, "CL3")
        assert set(self.mcl.classes) == {c1, c2, c3}

    def test_creation_of_unnamed_class(self):
        c1 = CClass(self.mcl)
        c2 = CClass(self.mcl)
        c3 = CClass(self.mcl, "x")
        assert set(self.mcl.classes) == {c1, c2, c3}
        assert c1.name == None
        assert c2.name == None
        assert c3.name == "x"

    def test_get_objects_by_name(self):
        c1 = CClass(self.mcl)
        assert set(c1.get_objects("o1")) == set()
        o1 = CObject(c1, "o1")
        assert c1.objects == [o1]
        assert set(c1.get_objects("o1")) == {o1}
        o2 = CObject(c1, "o1")
        assert set(c1.get_objects("o1")) == {o1, o2}
        assert o1 != o2
        o3 = CObject(c1, "o1")
        assert set(c1.get_objects("o1")) == {o1, o2, o3}
        assert c1.get_object("o1") == o1

    def test_delete_class(self):
        cl1 = CClass(self.mcl, "CL1")
        cl1.delete()
        assert set(self.mcl.classes) == set()

        cl1 = CClass(self.mcl, "CL1")
        cl2 = CClass(self.mcl, "CL2")
        cl3 = CClass(self.mcl, "CL3", superclasses=cl2, attributes={"i": 1})
        cl3.set_value("i", 7)
        CObject(cl3)

        cl1.delete()
        assert set(self.mcl.classes) == {cl2, cl3}
        cl3.delete()
        assert set(self.mcl.classes) == {cl2}

        assert cl3.superclasses == []
        assert cl2.subclasses == []
        assert cl3.attributes == []
        assert cl3.attribute_names == []
        assert cl3.metaclass == None
        assert cl3.objects == []
        assert cl3.name == None
        assert cl3.bundles == []
        with pytest.raises(CException) as exc_info:
            cl3.get_value("i")
        e = exc_info.value
        assert "can't get value 'i' on deleted class" == e.value

    def test_delete_class_instance_relation(self):
        cl1 = CClass(self.mcl, "CL1")
        cl2 = CClass(self.mcl, "CL2")
        obj1 = CObject(cl1, "O1")
        obj2 = CObject(cl1, "O2")
        obj3 = CObject(cl2, "O3")

        cl1.delete()

        assert obj1.classifier == None
        assert obj2.classifier == None
        assert obj3.classifier == cl2
        assert set(cl2.objects) == {obj3}
        assert cl1.objects == []

    def test_metaclass_change(self):
        m1 = CMetaclass("M1")
        m2 = CMetaclass("M2")
        c1 = CClass(m1, "C1")
        c1.metaclass = m2
        assert c1.metaclass == m2
        assert m1.classes == []
        assert m2.classes == [c1]

    def test_metaclass_change_none_input(self):
        m1 = CMetaclass("M1")
        CMetaclass("M2")
        c1 = CClass(m1, "C1")
        with pytest.raises(CException) as exc_info:
            c1.metaclass = None
        e = exc_info.value
        assert "'None' is not a metaclass" == e.value

    def test_metaclass_change_wrong_input_type(self):
        m1 = CMetaclass("M1")
        CMetaclass("M2")
        c1 = CClass(m1, "C1")
        with pytest.raises(CException) as exc_info:
            c1.metaclass = CClass(m1)
        e = exc_info.value
        assert e.value.endswith("' is not a metaclass")

    def test_metaclass_is_deleted_in_constructor(self):
        m1 = CMetaclass("M1")
        m1.delete()
        with pytest.raises(CException) as exc_info:
            CClass(m1, "C1")
        e = exc_info.value
        assert e.value.endswith("cannot access named element that has been deleted")

    def test_metaclass_is_deleted_in_metaclass_method(self):
        m1 = CMetaclass("M1")
        m2 = CMetaclass("M2")
        c1 = CClass(m2, "C1")
        m1.delete()
        with pytest.raises(CException) as exc_info:
            c1.metaclass = m1
        e = exc_info.value
        assert e.value.endswith("cannot access named element that has been deleted")

    def test_metaclass_is_none_in_constructor(self):
        with pytest.raises(CException) as exc_info:
            CClass(None, "C1")
        e = exc_info.value
        assert e.value.endswith("'None' is not a metaclass")

    def test_class_object(self):
        cl = CClass(self.mcl, "CX")
        assert cl.class_object.name == cl.name
        assert cl.class_object.classifier == self.mcl
        assert cl.class_object.class_object_class == cl

    def test_get_connected_elements__wrong_keyword_arg(self):
        c1 = CClass(self.mcl, "c1")
        with pytest.raises(CException) as exc_info:
            c1.get_connected_elements(a="c1")
        e = exc_info.value
        assert e.value == "unknown keyword argument 'a', should be one of: " + "['add_associations', 'add_bundles', 'process_bundles', 'stop_elements_inclusive'," + " 'stop_elements_exclusive']"

    def test_get_connected_elements_empty(self):
        c1 = CClass(self.mcl, "c1")
        assert set(c1.get_connected_elements()) == {c1}

    mcl = CMetaclass("MCL")
    c1 = CClass(mcl, "c1")
    c2 = CClass(mcl, "c2", superclasses=c1)
    c3 = CClass(mcl, "c3", superclasses=c2)
    c4 = CClass(mcl, "c4", superclasses=c2)
    c5 = CClass(mcl, "c5", superclasses=c4)
    c6 = CClass(mcl, "c6")
    a1 = c1.association(c6)
    c7 = CClass(mcl, "c7")
    c8 = CClass(mcl, "c8")
    a3 = c8.association(c7)
    c9 = CClass(mcl, "c9")
    a4 = c7.association(c9)
    c10 = CClass(mcl, "c10")
    c11 = CClass(mcl, "c11", superclasses=c10)
    c12 = CClass(mcl, "c12")
    c13 = CClass(mcl, "c13")
    c12.association(c11)
    b_sub = CBundle("b_sub", elements=[c13])
    b1 = CBundle("b1", elements=[c1, c2, c3, b_sub, c7])
    b2 = CBundle("b2", elements=[c7, c10, c11, c12])

    all_test_elements = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, b1, b2, b_sub]

    @pytest.mark.parametrize("test_elements, kwargs_dict, connected_elements_result", [
        (all_test_elements, {"process_bundles": True}, {c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13}),
        (all_test_elements, {"process_bundles": True, "add_bundles": True},
         {c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, b1, b2, b_sub}),
        ([c1], {"process_bundles": True}, {c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13}),
        ([c1], {"process_bundles": True, "add_bundles": True},
         {c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, b1, b2, b_sub}),
        ([c7], {}, {c7, c8, c9}),
        ([c7], {"add_bundles": True}, {c7, c8, c9, b1, b2}),
    ])
    def test_get_connected_elements(self, test_elements, kwargs_dict, connected_elements_result):
        for elt in test_elements:
            assert set(elt.get_connected_elements(**kwargs_dict)) == connected_elements_result

    def test_get_connected_elements_stop_elements_inclusive_wrong_types(self):
        c1 = CClass(self.mcl, "c1")
        with pytest.raises(CException) as exc_info:
            c1.get_connected_elements(stop_elements_inclusive="c1")
        e = exc_info.value
        assert e.value == "expected one element or a list of stop elements, but got: 'c1'"
        with pytest.raises(CException) as exc_info:
            c1.get_connected_elements(stop_elements_inclusive=["c1"])
        e = exc_info.value
        assert e.value == "expected one element or a list of stop elements, but got: '['c1']' with element of wrong type: 'c1'"

    @pytest.mark.parametrize("test_elements, kwargs_dict, connected_elements_result", [
        ([c1], {"stop_elements_exclusive": [c1]}, set()),
        ([c1], {"stop_elements_inclusive": [c3, c6]}, {c1, c2, c3, c4, c5, c6}),
        ([c1], {"stop_elements_exclusive": [c3, c6]}, {c1, c2, c4, c5}),
        ([c1], {"stop_elements_inclusive": [c3, c6], "stop_elements_exclusive": [c3]}, {c1, c2, c4, c5, c6}),
        ([c7], {"stop_elements_inclusive": [b2], "stop_elements_exclusive": [b1], "process_bundles": True,
                "add_bundles": True}, {c7, b2, c8, c9}),
        ([c7], {"stop_elements_exclusive": [b1, b2], "process_bundles": True, "add_bundles": True}, {c7, c8, c9}),
    ])
    def test_get_connected_elements_stop_elements_inclusive(self, test_elements, kwargs_dict,
                                                            connected_elements_result):
        for elt in test_elements:
            assert set(elt.get_connected_elements(**kwargs_dict)) == connected_elements_result


