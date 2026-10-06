
import pytest
from codeable_models import CMetaclass, CClass, CObject, CException, CEnum


class TestClassAttributeValues:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")

    def test_values_on_primitive_type_attributes(self):
        mcl = CMetaclass("M", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"]})
        cl = CClass(mcl, "C")

        assert cl.get_value("isBoolean") == True
        assert cl.get_value("intVal") == 1
        assert cl.get_value("floatVal") == 1.1
        assert cl.get_value("string") == "abc"
        assert cl.get_value("list") == ["a", "b"]

        cl.set_value("isBoolean", False)
        cl.set_value("intVal", 2)
        cl.set_value("floatVal", 2.1)
        cl.set_value("string", "y")

        assert cl.get_value("isBoolean") == False
        assert cl.get_value("intVal") == 2
        assert cl.get_value("floatVal") == 2.1
        assert cl.get_value("string") == "y"

        cl.set_value("list", [])
        assert cl.get_value("list") == []
        cl.set_value("list", [1, 2, 3])
        assert cl.get_value("list") == [1, 2, 3]

    def test_attribute_of_value_unknown(self):
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.get_value("x")
        e = exc_info.value
        assert e.value == "attribute 'x' unknown for 'C'"

        self.mcl.attributes = {"isBoolean": True, "intVal": 1}
        with pytest.raises(CException) as exc_info:
            cl.set_value("x", 1)
        e = exc_info.value
        assert e.value == "attribute 'x' unknown for 'C'"

    def test_integers_as_floats(self):
        mcl = CMetaclass("C", attributes={
            "floatVal": float})
        cl = CClass(mcl, "C")
        cl.set_value("floatVal", 15)
        assert cl.get_value("floatVal") == 15

    def test_attribute_defined_after_instance(self):
        mcl = CMetaclass("C")
        cl = CClass(mcl, "C")
        mcl.attributes = {"floatVal": float}
        cl.set_value("floatVal", 15)
        assert cl.get_value("floatVal") == 15

    def test_object_type_attribute_values(self):
        attr_type = CClass(self.mcl, "AttrType")
        attr_value = CObject(attr_type, "attribute_value")
        self.mcl.attributes = {"attrTypeObj": attr_value}
        obj_attr = self.mcl.get_attribute("attrTypeObj")
        assert obj_attr.type == attr_type
        cl = CClass(self.mcl, "C")
        assert cl.get_value("attrTypeObj") == attr_value

        non_attr_value = CObject(CClass(self.mcl), "non_attribute_value")
        with pytest.raises(CException) as exc_info:
            cl.set_value("attrTypeObj", non_attr_value)
        e = exc_info.value
        assert e.value == "type of 'non_attribute_value' is not matching type of attribute 'attrTypeObj'"

    def test_class_type_attribute_values(self):
        attr_type = CMetaclass("AttrType")
        attr_value = CClass(attr_type, "attribute_value")
        self.mcl.attributes = {"attrTypeCl": attr_type}
        cl_attr = self.mcl.get_attribute("attrTypeCl")
        cl_attr.default = attr_value
        assert cl_attr.type == attr_type
        cl = CClass(self.mcl, "C")
        assert cl.get_value("attrTypeCl") == attr_value

        non_attr_value = CClass(CMetaclass("MX"), "non_attribute_value")
        with pytest.raises(CException) as exc_info:
            cl.set_value("attrTypeCl", non_attr_value)
        e = exc_info.value
        assert e.value == "type of 'non_attribute_value' is not matching type of attribute 'attrTypeCl'"

    def test_add_object_attribute_get_set_value(self):
        attr_type = CClass(self.mcl, "AttrType")
        attr_value = CObject(attr_type, "attribute_value")
        cl = CClass(self.mcl)
        self.mcl.attributes = {
            "attrTypeObj1": attr_type, "attrTypeObj2": attr_value
        }
        assert cl.get_value("attrTypeObj1") == None
        assert cl.get_value("attrTypeObj2") == attr_value

    def test_object_attribute_of_superclass_type(self):
        attr_super_type = CClass(self.mcl, "AttrSuperType")
        attr_type = CClass(self.mcl, "AttrType", superclasses=attr_super_type)
        attr_value = CObject(attr_type, "attribute_value")
        cl = CClass(self.mcl)
        self.mcl.attributes = {
            "attrTypeObj1": attr_super_type, "attrTypeObj2": attr_value
        }
        cl.set_value("attrTypeObj1", attr_value)
        cl.set_value("attrTypeObj2", attr_value)
        assert cl.get_value("attrTypeObj1") == attr_value
        assert cl.get_value("attrTypeObj2") == attr_value

    def test_values_on_attributes_with_no_default_values(self):
        attr_type = CClass(self.mcl, "AttrType")
        enum_type = CEnum("EnumT", values=["A", "B", "C"])
        mcl = CMetaclass("M", attributes={
            "b": bool,
            "i": int,
            "f": float,
            "s": str,
            "l": list,
            "C": attr_type,
            "e": enum_type})
        cl = CClass(mcl, "C")
        for n in ["b", "i", "f", "s", "l", "C", "e"]:
            assert cl.get_value(n) == None

    def test_values_defined_in_constructor(self):
        obj_val_type = CClass(CMetaclass())
        obj_val = CObject(obj_val_type, "object_value")

        mcl = CMetaclass("M", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"],
            "obj": obj_val_type})
        cl = CClass(mcl, "C", values={
            "isBoolean": False, "intVal": 2, "floatVal": 2.1,
            "string": "y", "list": [], "obj": obj_val})

        assert cl.get_value("isBoolean") == False
        assert cl.get_value("intVal") == 2
        assert cl.get_value("floatVal") == 2.1
        assert cl.get_value("string") == "y"
        assert cl.get_value("list") == []
        assert cl.get_value("obj") == obj_val

        assert cl.values == {"isBoolean": False, "intVal": 2, "floatVal": 2.1, "string": "y", "list": [], "obj": obj_val}

    def test_values_setter_overwrite(self):
        mcl = CMetaclass("M", attributes={
            "isBoolean": True,
            "intVal": 1})
        cl = CClass(mcl, "C", values={
            "isBoolean": False, "intVal": 2})
        cl.values = {"isBoolean": True, "intVal": 20}
        assert cl.get_value("isBoolean") == True
        assert cl.get_value("intVal") == 20
        assert cl.values == {'isBoolean': True, 'intVal': 20}
        cl.values = {}
        # values should not delete existing values
        assert cl.values == {"isBoolean": True, "intVal": 20}

    def test_values_setter_with_superclass(self):
        mcl_super = CMetaclass("S_MCL", attributes={
            "intVal": 20, "intVal2": 30})
        mcl = CMetaclass("M", superclasses=mcl_super, attributes={
            "isBoolean": True,
            "intVal": 1})
        cl = CClass(mcl, "C", values={
            "isBoolean": False})
        assert cl.values == {"isBoolean": False, "intVal": 1, "intVal2": 30}
        cl.set_value("intVal", 12, mcl_super)
        cl.set_value("intVal", 15, mcl)
        cl.set_value("intVal2", 16, mcl_super)
        assert cl.values == {"isBoolean": False, "intVal": 15, "intVal2": 16}
        assert cl.get_value("intVal", mcl_super) == 12
        assert cl.get_value("intVal", mcl) == 15

    def test_values_setter_malformed_description(self):
        mcl = CMetaclass("M", attributes={
            "isBoolean": True,
            "intVal": 1})
        cl = CClass(mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.values = [1, 2, 3]
        e = exc_info.value
        assert e.value == "malformed attribute values description: '[1, 2, 3]'"

    def test_enum_type_attribute_values(self):
        enum_type = CEnum("EnumT", values=["A", "B", "C"])
        mcl = CMetaclass(attributes={
            "e1": enum_type,
            "e2": enum_type})
        e2 = mcl.get_attribute("e2")
        e2.default = "A"
        cl = CClass(mcl, "C")
        assert cl.get_value("e1") == None
        assert cl.get_value("e2") == "A"
        cl.set_value("e1", "B")
        cl.set_value("e2", "C")
        assert cl.get_value("e1") == "B"
        assert cl.get_value("e2") == "C"
        with pytest.raises(CException) as exc_info:
            cl.set_value("e1", "X")
        e = exc_info.value
        assert e.value == "value 'X' is not element of enumeration"

    def test_default_init_after_instance_creation(self):
        enum_type = CEnum("EnumT", values=["A", "B", "C"])
        mcl = CMetaclass(attributes={
            "e1": enum_type,
            "e2": enum_type})
        cl = CClass(mcl, "C")
        e2 = mcl.get_attribute("e2")
        e2.default = "A"
        assert cl.get_value("e1") == None
        assert cl.get_value("e2") == "A"

    def test_attribute_value_type_check_bool1(self):
        self.mcl.attributes = {"t": bool}
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.set_value("t", self.mcl)
        e = exc_info.value
        assert f"value for attribute 't' is not a known attribute type" == e.value

    def test_attribute_value_type_check_bool2(self):
        self.mcl.attributes = {"t": bool}
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.set_value("t", 1)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_int(self):
        self.mcl.attributes = {"t": int}
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.set_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_float(self):
        self.mcl.attributes = {"t": float}
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.set_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_str(self):
        self.mcl.attributes = {"t": str}
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.set_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_list(self):
        self.mcl.attributes = {"t": list}
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.set_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_object(self):
        attr_type = CMetaclass("AttrType")
        self.mcl.attributes = {"t": attr_type}
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.set_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_enum(self):
        enum_type = CEnum("EnumT", values=["A", "B", "C"])
        self.mcl.attributes = {"t": enum_type}
        cl = CClass(self.mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.set_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_deleted(self):
        mcl = CMetaclass(attributes={
            "isBoolean": True,
            "intVal": 15})
        cl = CClass(mcl, "C")
        assert cl.get_value("intVal") == 15
        mcl.attributes = {
            "isBoolean": False}
        assert cl.get_value("isBoolean") == True
        with pytest.raises(CException) as exc_info:
            cl.get_value("intVal")
        e = exc_info.value
        assert e.value == "attribute 'intVal' unknown for 'C'"
        with pytest.raises(CException) as exc_info:
            cl.set_value("intVal", 1)
        e = exc_info.value
        assert e.value == "attribute 'intVal' unknown for 'C'"

    def test_attribute_deleted_no_default(self):
        mcl = CMetaclass(attributes={
            "isBoolean": bool,
            "intVal": int})
        mcl.attributes = {"isBoolean": bool}
        cl = CClass(mcl, "C")
        assert cl.get_value("isBoolean") == None
        with pytest.raises(CException) as exc_info:
            cl.get_value("intVal")
        e = exc_info.value
        assert e.value == "attribute 'intVal' unknown for 'C'"
        with pytest.raises(CException) as exc_info:
            cl.set_value("intVal", 1)
        e = exc_info.value
        assert e.value == "attribute 'intVal' unknown for 'C'"

    def test_attributes_overwrite(self):
        mcl = CMetaclass(attributes={
            "isBoolean": True,
            "intVal": 15})
        cl = CClass(mcl, "C")
        assert cl.get_value("intVal") == 15
        with pytest.raises(CException) as exc_info:
            cl.get_value("floatVal")
        e = exc_info.value
        assert e.value == "attribute 'floatVal' unknown for 'C'"
        cl.set_value("intVal", 18)
        mcl.attributes = {
            "isBoolean": False,
            "intVal": 19,
            "floatVal": 25.1}
        assert cl.get_value("isBoolean") == True
        assert cl.get_value("floatVal") == 25.1
        assert cl.get_value("intVal") == 18
        cl.set_value("floatVal", 1.2)
        assert cl.get_value("floatVal") == 1.2

    def test_attributes_overwrite_no_defaults(self):
        mcl = CMetaclass(attributes={
            "isBoolean": bool,
            "intVal": int})
        cl = CClass(mcl, "C")
        assert cl.get_value("isBoolean") == None
        cl.set_value("isBoolean", False)
        mcl.attributes = {
            "isBoolean": bool,
            "intVal": int,
            "floatVal": float}
        assert cl.get_value("isBoolean") == False
        assert cl.get_value("floatVal") == None
        assert cl.get_value("intVal") == None
        cl.set_value("floatVal", 1.2)
        assert cl.get_value("floatVal") == 1.2

    def test_attributes_deleted_on_subclass(self):
        mcl = CMetaclass("M", attributes={
            "isBoolean": True,
            "intVal": 1})
        mcl2 = CMetaclass("M2", attributes={
            "isBoolean": False}, superclasses=mcl)

        cl = CClass(mcl2, "C")

        assert cl.get_value("isBoolean") == False
        assert cl.get_value("isBoolean", mcl) == True
        assert cl.get_value("isBoolean", mcl2) == False

        mcl2.attributes = {}

        assert cl.get_value("isBoolean") == True
        assert cl.get_value("intVal") == 1
        assert cl.get_value("isBoolean", mcl) == True
        with pytest.raises(CException) as exc_info:
            cl.get_value("isBoolean", mcl2)
        e = exc_info.value
        assert e.value == "attribute 'isBoolean' unknown for 'M2'"

    def test_attributes_deleted_on_subclass_no_defaults(self):
        mcl = CMetaclass("M", attributes={
            "isBoolean": bool,
            "intVal": int})
        mcl2 = CMetaclass("M2", attributes={
            "isBoolean": bool}, superclasses=mcl)

        cl = CClass(mcl2, "C")

        assert cl.get_value("isBoolean") == None
        assert cl.get_value("isBoolean", mcl) == None
        assert cl.get_value("isBoolean", mcl2) == None

        mcl2.attributes = {}

        assert cl.get_value("isBoolean") == None
        assert cl.get_value("intVal") == None
        assert cl.get_value("isBoolean", mcl) == None
        with pytest.raises(CException) as exc_info:
            cl.get_value("isBoolean", mcl2)
        e = exc_info.value
        assert e.value == "attribute 'isBoolean' unknown for 'M2'"

    def test_attribute_values_inheritance(self):
        t1 = CMetaclass("T1")
        t2 = CMetaclass("T2")
        c = CMetaclass("C", superclasses=[t1, t2])
        sc = CMetaclass("C", superclasses=c)

        t1.attributes = {"i0": 0}
        t2.attributes = {"i1": 1}
        c.attributes = {"i2": 2}
        sc.attributes = {"i3": 3}

        cl = CClass(sc, "C")

        for name, value in {"i0": 0, "i1": 1, "i2": 2, "i3": 3}.items():
            assert cl.get_value(name) == value

        assert cl.get_value("i0", t1) == 0
        assert cl.get_value("i1", t2) == 1
        assert cl.get_value("i2", c) == 2
        assert cl.get_value("i3", sc) == 3

        for name, value in {"i0": 10, "i1": 11, "i2": 12, "i3": 13}.items():
            cl.set_value(name, value)

        for name, value in {"i0": 10, "i1": 11, "i2": 12, "i3": 13}.items():
            assert cl.get_value(name) == value

        assert cl.get_value("i0", t1) == 10
        assert cl.get_value("i1", t2) == 11
        assert cl.get_value("i2", c) == 12
        assert cl.get_value("i3", sc) == 13

    def test_attribute_values_inheritance_after_delete_superclass(self):
        t1 = CMetaclass("T1")
        t2 = CMetaclass("T2")
        c = CMetaclass("C", superclasses=[t1, t2])
        sc = CMetaclass("C", superclasses=c)

        t1.attributes = {"i0": 0}
        t2.attributes = {"i1": 1}
        c.attributes = {"i2": 2}
        sc.attributes = {"i3": 3}

        cl = CClass(sc, "C")

        t2.delete()

        for name, value in {"i0": 0, "i2": 2, "i3": 3}.items():
            assert cl.get_value(name) == value
        with pytest.raises(CException) as exc_info:
            cl.get_value("i1")
        e = exc_info.value
        assert e.value == "attribute 'i1' unknown for 'C'"

        assert cl.get_value("i0", t1) == 0
        with pytest.raises(CException) as exc_info:
            cl.get_value("i1", t2)
        e = exc_info.value
        assert e.value == "attribute 'i1' unknown for ''"
        assert cl.get_value("i2", c) == 2
        assert cl.get_value("i3", sc) == 3

        for name, value in {"i0": 10, "i2": 12, "i3": 13}.items():
            cl.set_value(name, value)
        with pytest.raises(CException) as exc_info:
            cl.set_value("i1", 11)
        e = exc_info.value
        assert e.value == "attribute 'i1' unknown for 'C'"

        for name, value in {"i0": 10, "i2": 12, "i3": 13}.items():
            assert cl.get_value(name) == value
        with pytest.raises(CException) as exc_info:
            cl.get_value("i1")
        e = exc_info.value
        assert e.value == "attribute 'i1' unknown for 'C'"

        assert cl.get_value("i0", t1) == 10
        with pytest.raises(CException) as exc_info:
            cl.get_value("i1", t2)
        e = exc_info.value
        assert e.value == "attribute 'i1' unknown for ''"
        assert cl.get_value("i2", c) == 12
        assert cl.get_value("i3", sc) == 13

    def test_attribute_values_same_name_inheritance(self):
        t1 = CMetaclass("T1")
        t2 = CMetaclass("T2")
        c = CMetaclass("C", superclasses=[t1, t2])
        sc = CMetaclass("C", superclasses=c)

        t1.attributes = {"i": 0}
        t2.attributes = {"i": 1}
        c.attributes = {"i": 2}
        sc.attributes = {"i": 3}

        cl1 = CClass(sc)
        cl2 = CClass(c)
        cl3 = CClass(t1)

        assert cl1.get_value("i") == 3
        assert cl2.get_value("i") == 2
        assert cl3.get_value("i") == 0

        assert cl1.get_value("i", sc) == 3
        assert cl1.get_value("i", c) == 2
        assert cl1.get_value("i", t2) == 1
        assert cl1.get_value("i", t1) == 0
        assert cl2.get_value("i", c) == 2
        assert cl2.get_value("i", t2) == 1
        assert cl2.get_value("i", t1) == 0
        assert cl3.get_value("i", t1) == 0

        cl1.set_value("i", 10)
        cl2.set_value("i", 11)
        cl3.set_value("i", 12)

        assert cl1.get_value("i") == 10
        assert cl2.get_value("i") == 11
        assert cl3.get_value("i") == 12

        assert cl1.get_value("i", sc) == 10
        assert cl1.get_value("i", c) == 2
        assert cl1.get_value("i", t2) == 1
        assert cl1.get_value("i", t1) == 0
        assert cl2.get_value("i", c) == 11
        assert cl2.get_value("i", t2) == 1
        assert cl2.get_value("i", t1) == 0
        assert cl3.get_value("i", t1) == 12

        cl1.set_value("i", 130, sc)
        cl1.set_value("i", 100, t1)
        cl1.set_value("i", 110, t2)
        cl1.set_value("i", 120, c)

        assert cl1.get_value("i") == 130

        assert cl1.get_value("i", sc) == 130
        assert cl1.get_value("i", c) == 120
        assert cl1.get_value("i", t2) == 110
        assert cl1.get_value("i", t1) == 100

    def test_values_multiple_inheritance(self):
        t1 = CMetaclass("T1")
        t2 = CMetaclass("T2")
        st_a = CMetaclass("STA", superclasses=[t1, t2])
        sub_a = CMetaclass("SubA", superclasses=[st_a])
        st_b = CMetaclass("STB", superclasses=[t1, t2])
        sub_b = CMetaclass("SubB", superclasses=[st_b])
        st_c = CMetaclass("STC")
        sub_c = CMetaclass("SubC", superclasses=[st_c])

        mcl = CMetaclass("M", superclasses=[sub_a, sub_b, sub_c])
        cl = CClass(mcl, "C")

        t1.attributes = {"i0": 0}
        t2.attributes = {"i1": 1}
        st_a.attributes = {"i2": 2}
        sub_a.attributes = {"i3": 3}
        st_b.attributes = {"i4": 4}
        sub_b.attributes = {"i5": 5}
        st_c.attributes = {"i6": 6}
        sub_c.attributes = {"i7": 7}

        assert cl.get_value("i0") == 0
        assert cl.get_value("i1") == 1
        assert cl.get_value("i2") == 2
        assert cl.get_value("i3") == 3
        assert cl.get_value("i4") == 4
        assert cl.get_value("i5") == 5
        assert cl.get_value("i6") == 6
        assert cl.get_value("i7") == 7

        assert cl.get_value("i0", t1) == 0
        assert cl.get_value("i1", t2) == 1
        assert cl.get_value("i2", st_a) == 2
        assert cl.get_value("i3", sub_a) == 3
        assert cl.get_value("i4", st_b) == 4
        assert cl.get_value("i5", sub_b) == 5
        assert cl.get_value("i6", st_c) == 6
        assert cl.get_value("i7", sub_c) == 7

        cl.set_value("i0", 10)
        cl.set_value("i1", 11)
        cl.set_value("i2", 12)
        cl.set_value("i3", 13)
        cl.set_value("i4", 14)
        cl.set_value("i5", 15)
        cl.set_value("i6", 16)
        cl.set_value("i7", 17)

        assert cl.get_value("i0") == 10
        assert cl.get_value("i1") == 11
        assert cl.get_value("i2") == 12
        assert cl.get_value("i3") == 13
        assert cl.get_value("i4") == 14
        assert cl.get_value("i5") == 15
        assert cl.get_value("i6") == 16
        assert cl.get_value("i7") == 17

    def test_delete_attribute_values(self):
        mcl = CMetaclass("M", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"]})
        cl = CClass(mcl, "C")
        cl.delete_value("isBoolean")
        cl.delete_value("intVal")
        value_of_list = cl.delete_value("list")
        assert cl.values == {'floatVal': 1.1, 'string': 'abc'}
        assert value_of_list == ['a', 'b']

    def test_delete_attribute_values_with_superclass(self):
        mcl_super = CMetaclass("SCL_M", attributes={
            "intVal": 20, "intVal2": 30})
        mcl = CMetaclass("M", superclasses=mcl_super, attributes={
            "isBoolean": True,
            "intVal": 1})
        cl = CClass(mcl, "C", values={
            "isBoolean": False})
        cl.delete_value("isBoolean")
        cl.delete_value("intVal2")
        assert cl.values == {"intVal": 1}

        cl.set_value("intVal", 2, mcl_super)
        cl.set_value("intVal", 3, mcl)
        assert cl.values == {"intVal": 3}
        cl.delete_value("intVal")
        assert cl.values == {"intVal": 2}

        cl.set_value("intVal", 2, mcl_super)
        cl.set_value("intVal", 3, mcl)
        cl.delete_value("intVal", mcl)
        assert cl.values == {"intVal": 2}

        cl.set_value("intVal", 2, mcl_super)
        cl.set_value("intVal", 3, mcl)
        cl.delete_value("intVal", mcl_super)
        assert cl.values == {"intVal": 3}

    def test_attribute_values_exceptional_cases(self):
        mcl = CMetaclass("M", attributes={"b": True})
        cl1 = CClass(mcl, "C")
        cl1.delete()

        with pytest.raises(CException) as exc_info:
            cl1.get_value("b")
        e = exc_info.value
        assert e.value == "can't get value 'b' on deleted class"

        with pytest.raises(CException) as exc_info:
            cl1.set_value("b", 1)
        e = exc_info.value
        assert e.value == "can't set value 'b' on deleted class"

        with pytest.raises(CException) as exc_info:
            cl1.delete_value("b")
        e = exc_info.value
        assert e.value == "can't delete value 'b' on deleted class"

        with pytest.raises(CException) as exc_info:
            cl1.values = {"b": 1}
        e = exc_info.value
        assert e.value == "can't set values on deleted class"

        with pytest.raises(CException) as exc_info:
            # we just use list here, in order to not get a warning that cl1.values has no effect
            list(cl1.values)
        e = exc_info.value
        assert e.value == "can't get values on deleted class"

        cl = CClass(mcl, "C")
        with pytest.raises(CException) as exc_info:
            cl.delete_value("x")
        e = exc_info.value
        assert e.value == "attribute 'x' unknown for 'C'"


