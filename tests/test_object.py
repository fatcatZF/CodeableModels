
import pytest
from codeable_models import CMetaclass, CClass, CObject, CException, CBundle, add_links


class TestObject:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.cl = CClass(self.mcl, "CL", attributes={"i": 1})

    def test_creation_of_one_object(self):
        assert self.cl.objects == []
        o1 = CObject(self.cl, "o")
        o2 = self.cl.objects[0]
        assert o1.name == "o"
        assert o1 == o2
        assert o2.classifier == self.cl

    def test_create_object_wrong_arg_types(self):
        with pytest.raises(CException) as exc_info:
            CObject("CL", "o1")
        e = exc_info.value
        assert "'CL' is not a class" == e.value
        with pytest.raises(CException) as exc_info:
            CObject(self.mcl, "o1")
        e = exc_info.value
        assert "'MCL' is not a class" == e.value

    def test_creation_of_3_objects(self):
        o1 = CObject(self.cl, "o1")
        o2 = CObject(self.cl, "o2")
        o3 = CObject(self.cl, "o3")
        assert set(self.cl.objects) == {o1, o2, o3}

    def test_creation_of_unnamed_object(self):
        o1 = CObject(self.cl)
        o2 = CObject(self.cl)
        o3 = CObject(self.cl, "x")
        assert set(self.cl.objects) == {o1, o2, o3}
        assert o1.name == None
        assert o2.name == None
        assert o3.name == "x"

    def test_delete_object(self):
        o = CObject(self.cl, "o")
        o.delete()
        assert set(self.cl.objects) == set()

        o1 = CObject(self.cl, "o1")
        o2 = CObject(self.cl, "o2")
        o3 = CObject(self.cl, "o3")
        o3.set_value("i", 7)

        o1.delete()
        assert set(self.cl.objects) == {o2, o3}
        o3.delete()
        assert set(self.cl.objects) == {o2}

        assert o3.classifier == None
        assert set(self.cl.objects) == {o2}
        assert o3.name == None
        assert o3.bundles == []
        with pytest.raises(CException) as exc_info:
            o3.get_value("i")
        e = exc_info.value
        assert "can't get value 'i' on deleted object" == e.value

    def test_class_instance_relation(self):
        cl1 = CClass(self.mcl, "CL1")
        cl2 = CClass(self.mcl, "CL2")
        assert set(cl1.objects) == set()

        o1 = CObject(cl1, "O1")
        o2 = CObject(cl1, "O2")
        o3 = CObject(cl2, "O3")
        assert set(cl1.objects) == {o1, o2}
        assert set(cl2.objects) == {o3}
        assert o1.classifier == cl1
        assert o2.classifier == cl1
        assert o3.classifier == cl2

    def test_class_instance_relation_deletion_from_object(self):
        cl1 = CClass(self.mcl, "CL1")
        o1 = CObject(cl1, "O1")
        o1.delete()
        assert set(cl1.objects) == set()

        o1 = CObject(cl1, "O1")
        o2 = CObject(cl1, "O2")
        o3 = CObject(cl1, "O3")

        assert set(cl1.objects) == {o1, o2, o3}
        o1.delete()
        assert set(cl1.objects) == {o2, o3}
        o3.delete()
        assert set(cl1.objects) == {o2}
        assert o1.classifier == None
        assert o2.classifier == cl1
        assert o3.classifier == None
        o2.delete()
        assert set(cl1.objects) == set()
        assert o1.classifier == None
        assert o2.classifier == None
        assert o3.classifier == None

    def test_classifier_change(self):
        cl1 = CClass(self.mcl, "CL1")
        cl2 = CClass(self.mcl, "CL2")
        o1 = CObject(cl1, "O1")
        o1.classifier = cl2
        assert o1.classifier == cl2
        assert cl1.objects == []
        assert cl2.objects == [o1]

    def test_classifier_change_null_input(self):
        cl1 = CClass(self.mcl, "CL1")
        o1 = CObject(cl1, "O1")
        with pytest.raises(CException) as exc_info:
            o1.classifier = None
        e = exc_info.value
        assert "'None' is not a class" == e.value

    def test_classifier_change_wrong_input_type(self):
        cl1 = CClass(self.mcl, "CL1")
        o1 = CObject(cl1, "O1")
        with pytest.raises(CException) as exc_info:
            o1.classifier = self.mcl
        e = exc_info.value
        assert e.value.endswith("' is not a class")

    def test_class_is_deleted_in_constructor(self):
        c1 = CClass(self.mcl, "CL1")
        c1.delete()
        with pytest.raises(CException) as exc_info:
            CObject(c1, "O1")
        e = exc_info.value
        assert e.value.endswith("cannot access named element that has been deleted")

    def test_class_is_deleted_in_classifier_method(self):
        c1 = CClass(self.mcl, "CL1")
        c2 = CClass(self.mcl, "CL2")
        o1 = CObject(c2, "O1")
        c1.delete()
        with pytest.raises(CException) as exc_info:
            o1.classifier = c1
        e = exc_info.value
        assert e.value.endswith("cannot access named element that has been deleted")

    def test_class_is_none_in_constructor(self):
        with pytest.raises(CException) as exc_info:
            CObject(None, "O1")
        e = exc_info.value
        assert e.value.endswith("'None' is not a class")

    def test_get_connected_elements_wrong_keyword_arg(self):
        o1 = CObject(self.cl, "o1")
        with pytest.raises(CException) as exc_info:
            o1.get_connected_elements(a="o1")
        e = exc_info.value
        assert e.value == "unknown keyword argument 'a', should be one of: " + "['add_links', 'add_bundles', 'process_bundles', " + "'stop_elements_inclusive', 'stop_elements_exclusive']"

    def test_get_connected_elements_empty(self):
        o1 = CObject(self.cl, "o1")
        assert set(o1.get_connected_elements()) == {o1}

    mcl = CMetaclass("MCL")
    cl1 = CClass(mcl, "C")
    cl2 = CClass(mcl, "C")
    cl1.association(cl2, "*->*")
    o1 = CObject(cl1, "o1")
    o2 = CObject(cl2, "o2")
    o3 = CObject(cl2, "o3")
    o4 = CObject(cl2, "o4")
    o5 = CObject(cl2, "o5")
    add_links({o1: [o2, o3, o4, o5]})
    o6 = CObject(cl2, "o6")
    add_links({o6: o1})
    o7 = CObject(cl1, "o7")
    o8 = CObject(cl2, "o8")
    o9 = CObject(cl2, "o9")
    add_links({o7: [o8, o9]})
    o10 = CObject(cl1, "o10")
    o11 = CObject(cl2, "o11")
    add_links({o10: o11})
    o12 = CObject(cl1, "o12")
    o13 = CObject(cl2, "o13")
    add_links({o12: o11})
    b_sub = CBundle("b_sub", elements=[o13])
    b1 = CBundle("b1", elements=[o1, o2, o3, b_sub, o7])
    b2 = CBundle("b2", elements=[o7, o10, o11, o12])

    all_test_elements = [o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, b1, b2, b_sub]

    @pytest.mark.parametrize("test_elements, kwargs_dict, connected_elements_result", [
        (all_test_elements, {"process_bundles": True}, {o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13}),
        (all_test_elements, {"process_bundles": True, "add_bundles": True},
         {o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, b1, b2, b_sub}),
        ([o1], {"process_bundles": True}, {o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13}),
        ([o1], {"process_bundles": True, "add_bundles": True},
         {o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, b1, b2, b_sub}),
        ([o7], {}, {o7, o8, o9}),
        ([o7], {"add_bundles": True}, {o7, o8, o9, b1, b2}),
    ])
    def test_get_connected_elements(self, test_elements, kwargs_dict, connected_elements_result):
        for elt in test_elements:
            assert set(elt.get_connected_elements(**kwargs_dict)) == connected_elements_result

    def test_get_connected_elements_stop_elements_inclusive_wrong_types(self):
        o1 = CObject(self.cl, "o1")
        with pytest.raises(CException) as exc_info:
            o1.get_connected_elements(stop_elements_inclusive="o1")
        e = exc_info.value
        assert e.value == "expected one element or a list of stop elements, but got: 'o1'"
        with pytest.raises(CException) as exc_info:
            o1.get_connected_elements(stop_elements_inclusive=["o1"])
        e = exc_info.value
        assert e.value == "expected one element or a list of stop elements, but got: '['o1']' with element of wrong type: 'o1'"

    @pytest.mark.parametrize("test_elements, kwargs_dict, connected_elements_result", [
        ([o1], {"stop_elements_exclusive": [o1]}, set()),
        ([o1], {"stop_elements_inclusive": [o3, o6]}, {o1, o2, o3, o4, o5, o6}),
        ([o1], {"stop_elements_exclusive": [o3, o6]}, {o1, o2, o4, o5}),
        ([o1], {"stop_elements_inclusive": [o3, o6], "stop_elements_exclusive": [o3]}, {o1, o2, o4, o5, o6}),
        ([o7], {"stop_elements_inclusive": [b2], "stop_elements_exclusive": [b1], "process_bundles": True,
                "add_bundles": True}, {o7, b2, o8, o9}),
        ([o7], {"stop_elements_exclusive": [b1, b2], "process_bundles": True, "add_bundles": True}, {o7, o8, o9}),
    ])
    def test_get_connected_elements_stop_elements_inclusive(self, test_elements, kwargs_dict,
                                                            connected_elements_result):
        for elt in test_elements:
            assert set(elt.get_connected_elements(**kwargs_dict)) == connected_elements_result

    def test_class_object_class_is_none(self):
        o1 = CObject(self.cl, "o")
        assert o1.class_object_class == None


