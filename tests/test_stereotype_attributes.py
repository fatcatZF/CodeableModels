import re


import pytest
from codeable_models import CMetaclass, CClass, CObject, CAttribute, CException, CEnum, CStereotype


class TestStereotypeAttributes:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.stereotype = CStereotype("S", extended=self.mcl)

    def test_primitive_empty_input(self):
        cl = CStereotype("S", extended=self.mcl, attributes={})
        assert len(cl.attributes) == 0
        assert len(cl.attribute_names) == 0

    def test_primitive_none_input(self):
        cl = CStereotype("S", extended=self.mcl, attributes=None)
        assert len(cl.attributes) == 0
        assert len(cl.attribute_names) == 0

    def test_primitive_type_attributes(self):
        cl = CStereotype("S", extended=self.mcl, attributes={
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
        cl = CStereotype("S", attributes={"isBoolean": True})
        a = cl.get_attribute("isBoolean")
        assert a.name == "isBoolean"
        assert a.classifier == cl
        cl.delete()
        assert a.name == None
        assert a.classifier == None

    def test_primitive_attributes_no_default(self):
        self.stereotype.attributes = {"a": bool, "b": int, "c": str, "d": float, "e": list}
        a1 = self.stereotype.get_attribute("a")
        a2 = self.stereotype.get_attribute("b")
        a3 = self.stereotype.get_attribute("c")
        a4 = self.stereotype.get_attribute("d")
        a5 = self.stereotype.get_attribute("e")
        assert {a1, a2, a3, a4, a5}.issubset(self.stereotype.attributes)
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
        assert self.stereotype.get_attribute("x") == None
        self.stereotype.attributes = {"a": bool, "b": int, "c": str, "d": float}
        assert self.stereotype.get_attribute("x") == None

    def test_same_named_arguments_cattributes(self):
        a1 = CAttribute(default="")
        a2 = CAttribute(type=str)
        n1 = "a"
        self.stereotype.attributes = {n1: a1, "a": a2}
        assert set(self.stereotype.attributes) == {a2}
        assert self.stereotype.attribute_names == ["a"]

    def test_same_named_arguments_defaults(self):
        n1 = "a"
        self.stereotype.attributes = {n1: "", "a": 1}
        assert len(self.stereotype.attributes), 1
        assert self.stereotype.get_attribute("a").default == 1
        assert self.stereotype.attribute_names == ["a"]

    def test_object_type_attribute(self):
        attribute_type = CClass(self.mcl, "AttrType")
        attribute_value = CObject(attribute_type, "attribute_value")
        self.stereotype.attributes = {"attrTypeObj": attribute_value}
        object_attribute = self.stereotype.get_attribute("attrTypeObj")
        attributes = self.stereotype.attributes
        assert set(attributes) == {object_attribute}

        bool_attr = CAttribute(default=True)
        self.stereotype.attributes = {"attrTypeObj": object_attribute, "isBoolean": bool_attr}
        attributes = self.stereotype.attributes
        assert set(attributes) == {object_attribute, bool_attr}
        assert self.stereotype.attribute_names == ["attrTypeObj", "isBoolean"]
        object_attribute = self.stereotype.get_attribute("attrTypeObj")
        assert object_attribute.type == attribute_type
        default = object_attribute.default
        assert isinstance(default, CObject)
        assert default == attribute_value

        self.stereotype.attributes = {"attrTypeObj": attribute_value, "isBoolean": bool_attr}
        assert self.stereotype.attribute_names == ["attrTypeObj", "isBoolean"]
        # using the CObject in attributes causes a new CAttribute to be created != object_attribute
        assert self.stereotype.get_attribute("attrTypeObj") != object_attribute

    def test_class_type_attribute(self):
        attribute_type = CMetaclass("AttrType")
        attribute_value = CClass(attribute_type, "attribute_value")
        self.stereotype.attributes = {"attrTypeCl": attribute_type}
        class_attribute = self.stereotype.get_attribute("attrTypeCl")
        class_attribute.default = attribute_value
        attributes = self.stereotype.attributes
        assert set(attributes) == {class_attribute}

        bool_attr = CAttribute(default=True)
        self.stereotype.attributes = {"attrTypeCl": class_attribute, "isBoolean": bool_attr}
        attributes = self.stereotype.attributes
        assert set(attributes) == {class_attribute, bool_attr}
        assert self.stereotype.attribute_names == ["attrTypeCl", "isBoolean"]
        class_attribute = self.stereotype.get_attribute("attrTypeCl")
        assert class_attribute.type == attribute_type
        default = class_attribute.default
        assert isinstance(default, CClass)
        assert default == attribute_value

        self.stereotype.attributes = {"attrTypeCl": attribute_value, "isBoolean": bool_attr}
        assert self.stereotype.attribute_names == ["attrTypeCl", "isBoolean"]
        # using the CClass in attributes causes a new CAttribute to be created != class_attribute
        assert self.stereotype.get_attribute("attrTypeCl") != class_attribute

    def test_use_enum_type_attribute(self):
        enum_values = ["A", "B", "C"]
        enum_obj = CEnum("ABCEnum", values=enum_values)
        ea1 = CAttribute(type=enum_obj, default="A")
        ea2 = CAttribute(type=enum_obj)
        self.stereotype.attributes = {"letters1": ea1, "letters2": ea2}
        assert set(self.stereotype.attributes) == {ea1, ea2}
        assert isinstance(ea1.type, CEnum)

        self.stereotype.attributes = {"letters1": ea1, "isBool": True, "letters2": ea2}
        bool_attr = self.stereotype.get_attribute("isBool")
        l1 = self.stereotype.get_attribute("letters1")
        assert set(self.stereotype.attributes) == {l1, ea2, bool_attr}
        assert l1.default == "A"
        assert ea2.default == None

    def test_unknown_attribute_type(self):
        with pytest.raises(CException) as exc_info:
            self.stereotype.attributes = {"x": CEnum, "b": bool}
        e = exc_info.value
        assert re.match("^(unknown attribute type: '<class ).*(CEnum'>')$", e.value)

    def test_set_attribute_default_value(self):
        enum_obj = CEnum("ABCEnum", values=["A", "B", "C"])
        self.stereotype.attributes = {"letters": enum_obj, "b": bool}
        letters = self.stereotype.get_attribute("letters")
        b = self.stereotype.get_attribute("b")
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

        self.stereotype.attributes = {"a": cl_a, "b": obj_b}
        a = self.stereotype.get_attribute("a")
        b = self.stereotype.get_attribute("b")
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
        self.stereotype.attributes = {"a": type_to_check}
        attr = self.stereotype.get_attribute("a")
        with pytest.raises(CException) as exc_info:
            attr.default = wrong_default
        e = exc_info.value
        assert f"default value '{wrong_default!s}' incompatible with attribute's type '{type_to_check!s}'" == e.value

    def test_delete_attributes(self):
        self.stereotype.attributes = {
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc"}
        assert len(set(self.stereotype.attributes)) == 4
        self.stereotype.attributes = {}
        assert set(self.stereotype.attributes) == set()
        self.stereotype.attributes = {
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc"}
        assert len(set(self.stereotype.attributes)) == 4
        self.stereotype.attributes = {}
        assert set(self.stereotype.attributes) == set()

    def test_type_object_attribute_class_is_deleted_in_constructor(self):
        attribute_class = CClass(self.mcl, "AC")
        attribute_class.delete()
        with pytest.raises(CException) as exc_info:
            CStereotype("S", attributes={"ac": attribute_class})
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_type_object_attribute_class_is_none(self):
        s1 = CStereotype("S", attributes={"ac": None})
        ac = s1.get_attribute("ac")
        assert ac.default == None
        assert ac.type == None

    def test_default_object_attribute_is_deleted_in_constructor(self):
        attribute_class = CClass(self.mcl, "AC")
        default_object = CObject(attribute_class)
        default_object.delete()
        with pytest.raises(CException) as exc_info:
            CStereotype("S", attributes={"ac": default_object})
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"


