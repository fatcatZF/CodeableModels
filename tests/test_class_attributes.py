import re


import pytest
from codeable_models import CMetaclass, CClass, CObject, CAttribute, CException, CEnum


class TestClassAttributes:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.cl = CClass(self.mcl, "CL")

    def test_primitive_empty_input(self):
        cl = CClass(self.mcl, "C", attributes={})
        assert len(cl.attributes) == 0
        assert len(cl.attribute_names) == 0

    def test_primitive_none_input(self):
        cl = CClass(self.mcl, "C", attributes=None)
        assert len(cl.attributes) == 0
        assert len(cl.attribute_names) == 0

    def test_primitive_type_attributes(self):
        cl = CClass(self.mcl, "C", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"]})
        assert len(cl.attributes) == 5
        assert len(cl.attribute_names) == 5

        assert {"isBoolean", "intVal", "floatVal", "string", "list"}.issubset(cl.attribute_names)

        a1 = cl.get_attribute("isBoolean")
        a2 = cl.get_attribute("intVal")
        a3 = cl.get_attribute("floatVal")
        a4 = cl.get_attribute("string")
        a5 = cl.get_attribute("list")
        assert {a1, a2, a3, a4, a5}.issubset(cl.attributes)
        assert None == cl.get_attribute("X")

        assert a1.type == bool
        assert a2.type == int
        assert a3.type == float
        assert a4.type == str
        assert a5.type == list

        d1 = a1.default
        d2 = a2.default
        d3 = a3.default
        d4 = a4.default
        d5 = a5.default

        assert isinstance(d1, bool)
        assert isinstance(d2, int)
        assert isinstance(d3, float)
        assert isinstance(d4, str)
        assert isinstance(d5, list)

        assert d1 == True
        assert d2 == 1
        assert d3 == 1.1
        assert d4 == "abc"
        assert d5 == ["a", "b"]

    def test_attribute_get_name_and_classifier(self):
        cl = CClass(self.mcl, "C", attributes={"isBoolean": True})
        a = cl.get_attribute("isBoolean")
        assert a.name == "isBoolean"
        assert a.classifier == cl
        cl.delete()
        assert a.name == None
        assert a.classifier == None

    def test_primitive_attributes_no_default(self):
        self.cl.attributes = {"a": bool, "b": int, "c": str, "d": float, "e": list}
        a1 = self.cl.get_attribute("a")
        a2 = self.cl.get_attribute("b")
        a3 = self.cl.get_attribute("c")
        a4 = self.cl.get_attribute("d")
        a5 = self.cl.get_attribute("e")
        assert {a1, a2, a3, a4, a5}.issubset(self.cl.attributes)
        assert a1.default == None
        assert a1.type == bool
        assert a2.default == None
        assert a2.type == int
        assert a3.default == None
        assert a3.type == str
        assert a4.default == None
        assert a4.type == float
        assert a5.default == None
        assert a5.type == list

    def test_get_attribute_not_found(self):
        assert self.cl.get_attribute("x") == None
        self.cl.attributes = {"a": bool, "b": int, "c": str, "d": float}
        assert self.cl.get_attribute("x") == None

    def test_type_and_default_on_attribute(self):
        CAttribute(default="", type=str)
        CAttribute(type=str, default="")
        with pytest.raises(CException) as exc_info:
            CAttribute(default=1, type=str)
        e = exc_info.value
        assert "default value '1' incompatible with attribute's type '<class 'str'>'" == e.value
        with pytest.raises(CException) as exc_info:
            CAttribute(type=str, default=1)
        e = exc_info.value
        assert "default value '1' incompatible with attribute's type '<class 'str'>'" == e.value
        a5 = CAttribute(type=int)
        assert a5.default == None

    def test_same_named_attributes(self):
        a1 = CAttribute(default="")
        a2 = CAttribute(type=str)
        n1 = "a"
        self.cl.attributes = {n1: a1, "a": a2}
        assert set(self.cl.attributes) == {a2}
        assert self.cl.attribute_names == ["a"]

    def test_same_named_arguments_defaults(self):
        n1 = "a"
        self.cl.attributes = {n1: "", "a": 1}
        assert len(self.cl.attributes), 1
        assert self.cl.get_attribute("a").default == 1
        assert self.cl.attribute_names == ["a"]

    def test_object_type_attribute(self):
        attr_type = CClass(self.mcl, "AttrType")
        attr_value = CObject(attr_type, "attribute_value")
        self.cl.attributes = {"attrTypeObj": attr_value}
        obj_attr = self.cl.get_attribute("attrTypeObj")
        attributes = self.cl.attributes
        assert set(attributes) == {obj_attr}

        bool_attr = CAttribute(default=True)
        self.cl.attributes = {"attrTypeObj": obj_attr, "isBoolean": bool_attr}
        attributes = self.cl.attributes
        assert set(attributes) == {obj_attr, bool_attr}
        assert self.cl.attribute_names == ["attrTypeObj", "isBoolean"]
        obj_attr = self.cl.get_attribute("attrTypeObj")
        assert obj_attr.type == attr_type
        default = obj_attr.default
        assert isinstance(default, CObject)
        assert default == attr_value

        self.cl.attributes = {"attrTypeObj": attr_value, "isBoolean": bool_attr}
        assert self.cl.attribute_names == ["attrTypeObj", "isBoolean"]
        # using the CObject in attributes causes a new CAttribute to be created != obj_attr
        assert self.cl.get_attribute("attrTypeObj") != obj_attr

    def test_class_type_attribute(self):
        attr_type = CMetaclass("AttrType")
        attr_value = CClass(attr_type, "attribute_value")
        self.cl.attributes = {"attrTypeCl": attr_type}
        cl_attr = self.cl.get_attribute("attrTypeCl")
        cl_attr.default = attr_value
        attributes = self.cl.attributes
        assert set(attributes) == {cl_attr}

        bool_attr = CAttribute(default=True)
        self.cl.attributes = {"attrTypeCl": cl_attr, "isBoolean": bool_attr}
        attributes = self.cl.attributes
        assert set(attributes) == {cl_attr, bool_attr}
        assert self.cl.attribute_names == ["attrTypeCl", "isBoolean"]
        cl_attr = self.cl.get_attribute("attrTypeCl")
        assert cl_attr.type == attr_type
        default = cl_attr.default
        assert isinstance(default, CClass)
        assert default == attr_value

        self.cl.attributes = {"attrTypeCl": attr_value, "isBoolean": bool_attr}
        assert self.cl.attribute_names == ["attrTypeCl", "isBoolean"]
        # using the CClass in attributes causes a new CAttribute to be created != cl_attr
        assert self.cl.get_attribute("attrTypeCl") != cl_attr

    def test_enum_get_values(self):
        enum_values = ["A", "B", "C"]
        enum_obj = CEnum("ABCEnum", values=enum_values)
        assert ["A", "B", "C"] == enum_obj.values
        assert "A" in enum_obj.values
        assert not ("X" in enum_obj.values)
        enum_values = [1, 2, 3]
        enum_obj = CEnum("123Enum", values=enum_values)
        assert [1, 2, 3] == enum_obj.values

    def test_enum_empty(self):
        enum_obj = CEnum("ABCEnum", values=[])
        assert enum_obj.values == []
        enum_obj = CEnum("ABCEnum", values=None)
        assert enum_obj.values == []

    def test_enum_no_list(self):
        enum_values = {"A", "B", "C"}
        with pytest.raises(CException) as exc_info:
            CEnum("ABCEnum", values=enum_values)
        e = exc_info.value
        assert re.match("^an enum needs to be initialized with a list of values, but got:([ {}'CAB,]+)$", e.value)

    def test_enum_name(self):
        enum_values = ["A", "B", "C"]
        enum_obj = CEnum("ABCEnum", values=enum_values)
        assert "ABCEnum" == enum_obj.name

    def test_define_enum_type_attribute(self):
        enum_values = ["A", "B", "C"]
        enum_obj = CEnum("ABCEnum", values=enum_values)
        CAttribute(type=enum_obj, default="A")
        CAttribute(default="A", type=enum_obj)
        with pytest.raises(CException) as exc_info:
            CAttribute(type=enum_obj, default="X")
        e = exc_info.value
        assert "default value 'X' incompatible with attribute's type 'ABCEnum'" == e.value
        with pytest.raises(CException) as exc_info:
            CAttribute(default="X", type=enum_obj)
        e = exc_info.value
        assert "default value 'X' incompatible with attribute's type 'ABCEnum'" == e.value

    def test_use_enum_type_attribute(self):
        enum_values = ["A", "B", "C"]
        enum_obj = CEnum("ABCEnum", values=enum_values)
        ea1 = CAttribute(type=enum_obj, default="A")
        ea2 = CAttribute(type=enum_obj)
        self.cl.attributes = {"letters1": ea1, "letters2": ea2}
        assert set(self.cl.attributes) == {ea1, ea2}
        assert isinstance(ea1.type, CEnum)

        self.cl.attributes = {"letters1": ea1, "isBool": True, "letters2": ea2}
        bool_attr = self.cl.get_attribute("isBool")
        l1 = self.cl.get_attribute("letters1")
        assert set(self.cl.attributes) == {l1, ea2, bool_attr}
        assert l1.default == "A"
        assert ea2.default == None

    def test_unknown_attribute_type(self):
        with pytest.raises(CException) as exc_info:
            self.cl.attributes = {"x": CEnum, "b": bool}
        e = exc_info.value
        assert re.match("^(unknown attribute type: '<class ).*(CEnum'>')$", e.value)

    def test_set_attribute_default_value(self):
        enum_obj = CEnum("ABCEnum", values=["A", "B", "C"])
        self.cl.attributes = {"letters": enum_obj, "b": bool}
        letters = self.cl.get_attribute("letters")
        b = self.cl.get_attribute("b")
        assert letters.default == None
        assert b.default == None
        letters.default = "B"
        b.default = False
        assert letters.default == "B"
        assert b.default == False
        assert letters.type == enum_obj
        assert b.type == bool

    def test_cclass_vs_cobject(self):
        cl_a = CClass(self.mcl, "A")
        cl_b = CClass(self.mcl, "B")
        obj_b = CObject(cl_b, "obj_b")

        self.cl.attributes = {"a": cl_a, "b": obj_b}
        a = self.cl.get_attribute("a")
        b = self.cl.get_attribute("b")
        assert a.type == cl_a
        assert a.default == None
        assert b.type == cl_b
        assert b.default == obj_b

    testMetaclass = CMetaclass("A")
    testEnum = CEnum("AEnum", values=[1, 2])
    testClass = CClass(testMetaclass, "CL")

    @pytest.mark.parametrize("type_to_check, wrong_default", [
        (bool, testMetaclass),
        (bool, 1.1),
        (int, testMetaclass),
        (int, "abc"),
        (float, "1"),
        (float, testMetaclass),
        (str, 1),
        (str, testMetaclass),
        (testEnum, "1"),
        (testEnum, testMetaclass),
        (testClass, "1"),
        (testClass, testMetaclass)])
    def test_attribute_type_check(self, type_to_check, wrong_default):
        self.cl.attributes = {"a": type_to_check}
        attr = self.cl.get_attribute("a")
        with pytest.raises(CException) as exc_info:
            attr.default = wrong_default
        e = exc_info.value
        assert f"default value '{wrong_default!s}' incompatible with attribute's type '{type_to_check!s}'" == e.value

    def test_delete_attributes(self):
        self.cl.attributes = {
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc"}
        assert len(set(self.cl.attributes)) == 4
        self.cl.attributes = {}
        assert set(self.cl.attributes) == set()
        self.cl.attributes = {
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc"}
        assert len(set(self.cl.attributes)) == 4
        self.cl.attributes = {}
        assert set(self.cl.attributes) == set()

    def test_type_object_attribute_class_is_deleted_in_constructor(self):
        attr_cl = CClass(self.mcl, "AC")
        attr_cl.delete()
        with pytest.raises(CException) as exc_info:
            CClass(self.mcl, "C", attributes={"ac": attr_cl})
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_type_object_attribute_class_is_deleted_in_type_method(self):
        attr_cl = CClass(self.mcl, "AC")
        attr_cl.delete()
        with pytest.raises(CException) as exc_info:
            a = CAttribute()
            a.type = attr_cl
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_set_cattribute_method_to_none(self):
        # setting the type/default to their default value (None) should work
        a = CAttribute()
        a.type = None
        a.default = None
        assert a.type == None
        assert a.default == None

    def test_type_object_attribute_class_is_none(self):
        c = CClass(self.mcl, "C", attributes={"ac": None})
        ac = c.get_attribute("ac")
        assert ac.default == None
        assert ac.type == None

    def test_default_object_attribute_is_deleted_in_constructor(self):
        attr_cl = CClass(self.mcl, "AC")
        default_obj = CObject(attr_cl)
        default_obj.delete()
        with pytest.raises(CException) as exc_info:
            CClass(self.mcl, "C", attributes={"ac": default_obj})
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_default_object_attribute_is_deleted_in_default_method(self):
        attr_cl = CClass(self.mcl, "AC")
        default_obj = CObject(attr_cl)
        default_obj.delete()
        with pytest.raises(CException) as exc_info:
            a = CAttribute()
            a.default = default_obj
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"


