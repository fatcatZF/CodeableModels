
import pytest
from codeable_models import *


class TestStereotypeTagValuesOnLinks:
    def setup_method(self):
        self.st = CStereotype("ST")
        self.m1 = CMetaclass("M1")
        self.m2 = CMetaclass("M2")
        self.a = self.m1.association(self.m2, name="a", multiplicity="*", role_name="m1",
                                     source_multiplicity="1", source_role_name="m2")
        self.a.stereotypes = self.st
        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        c3 = CClass(self.m2, "C3")
        c4 = CClass(self.m2, "C4")
        self.links = set_links({c1: [c2, c3, c4]})
        self.link1 = self.links[0]
        self.link2 = self.links[1]
        self.link3 = self.links[2]
        self.link1.stereotype_instances = self.st

    def test_tagged_values_on_primitive_type_attributes(self):
        s = CStereotype("S", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"]})
        self.a.stereotypes = s
        self.link1.stereotype_instances = s

        assert self.link1.get_tagged_value("isBoolean") == True
        assert self.link1.get_tagged_value("intVal") == 1
        assert self.link1.get_tagged_value("floatVal") == 1.1
        assert self.link1.get_tagged_value("string") == "abc"
        assert self.link1.get_tagged_value("list") == ["a", "b"]

        self.link1.set_tagged_value("isBoolean", False)
        self.link1.set_tagged_value("intVal", 2)
        self.link1.set_tagged_value("floatVal", 2.1)
        self.link1.set_tagged_value("string", "y")

        assert self.link1.get_tagged_value("isBoolean") == False
        assert self.link1.get_tagged_value("intVal") == 2
        assert self.link1.get_tagged_value("floatVal") == 2.1
        assert self.link1.get_tagged_value("string") == "y"

        self.link1.set_tagged_value("list", [])
        assert self.link1.get_tagged_value("list") == []
        self.link1.set_tagged_value("list", [1, 2, 3])
        assert self.link1.get_tagged_value("list") == [1, 2, 3]

    def test_attribute_of_tagged_value_unknown(self):
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("x")
        e = exc_info.value
        assert e.value == "tagged value 'x' unknown"

    def test_integers_as_float_tagged_values(self):
        self.st.attributes = {"floatVal": float}
        self.link1.set_tagged_value("floatVal", 15)
        assert self.link1.get_tagged_value("floatVal") == 15

    def test_object_type_attribute_tagged_values(self):
        attribute_type = CClass(self.m1, "AttrType")
        attribute_value = CObject(attribute_type, "attribute_value")
        self.st.attributes = {"attrTypeObj": attribute_value}
        object_attribute = self.st.get_attribute("attrTypeObj")
        assert object_attribute.type == attribute_type
        assert self.link1.get_tagged_value("attrTypeObj") == attribute_value

        non_attribute_value = CObject(CClass(self.m1), "non_attribute_value")
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("attrTypeObj", non_attribute_value)
        e = exc_info.value
        assert e.value == "type of 'non_attribute_value' is not matching type of attribute 'attrTypeObj'"

    def test_class_type_attribute_tagged_values(self):
        attribute_type = CMetaclass("AttrType")
        attribute_value = CClass(attribute_type, "attribute_value")
        self.st.attributes = {"attrTypeCl": attribute_type}
        class_attribute = self.st.get_attribute("attrTypeCl")
        class_attribute.default = attribute_value
        assert class_attribute.type == attribute_type
        assert self.link1.get_tagged_value("attrTypeCl") == attribute_value

        non_attribute_value = CClass(CMetaclass("MX"), "non_attribute_value")
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("attrTypeCl", non_attribute_value)
        e = exc_info.value
        assert e.value == "type of 'non_attribute_value' is not matching type of attribute 'attrTypeCl'"

    def test_add_object_attribute_get_set_tagged_value(self):
        attribute_type = CClass(self.m1, "AttrType")
        attribute_value = CObject(attribute_type, "attribute_value")
        self.st.attributes = {
            "attrTypeObj1": attribute_type, "attrTypeObj2": attribute_value
        }
        assert self.link1.get_tagged_value("attrTypeObj1") == None
        assert self.link1.get_tagged_value("attrTypeObj2") == attribute_value

    def test_object_attribute_tagged_value_of_superclass_type(self):
        attribute_super_type = CClass(self.m1, "AttrSuperType")
        attribute_type = CClass(self.m1, "AttrType", superclasses=attribute_super_type)
        attribute_value = CObject(attribute_type, "attribute_value")
        self.st.attributes = {
            "attrTypeObj1": attribute_super_type, "attrTypeObj2": attribute_value
        }
        self.link1.set_tagged_value("attrTypeObj1", attribute_value)
        self.link1.set_tagged_value("attrTypeObj2", attribute_value)
        assert self.link1.get_tagged_value("attrTypeObj1") == attribute_value
        assert self.link1.get_tagged_value("attrTypeObj2") == attribute_value

    def test_tagged_values_on_attributes_with_no_default_values(self):
        attribute_type = CClass(self.m1, "AttrType")
        enum_type = CEnum("EnumT", values=["A", "B", "C"])
        st = CStereotype("S", attributes={
            "b": bool,
            "i": int,
            "f": float,
            "s": str,
            "l": list,
            "C": attribute_type,
            "e": enum_type})
        self.a.stereotypes = st
        self.link1.stereotype_instances = st
        for n in ["b", "i", "f", "s", "l", "C", "e"]:
            assert self.link1.get_tagged_value(n) == None

    def test_tagged_values_setter(self):
        object_value_type = CClass(CMetaclass())
        object_value = CObject(object_value_type, "object_value")

        st = CStereotype("S", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"],
            "obj": object_value_type})
        self.a.stereotypes = st
        self.link1.stereotype_instances = st
        self.link1.tagged_values = {
            "isBoolean": False, "intVal": 2, "floatVal": 2.1,
            "string": "y", "list": [], "obj": object_value}

        assert self.link1.get_tagged_value("isBoolean") == False
        assert self.link1.get_tagged_value("intVal") == 2
        assert self.link1.get_tagged_value("floatVal") == 2.1
        assert self.link1.get_tagged_value("string") == "y"
        assert self.link1.get_tagged_value("list") == []
        assert self.link1.get_tagged_value("obj") == object_value

        assert self.link1.tagged_values == {"isBoolean": False, "intVal": 2, "floatVal": 2.1, "string": "y", "list": [], "obj": object_value}

    def test_tagged_values_setter_overwrite(self):
        st = CStereotype("S", attributes={
            "isBoolean": True,
            "intVal": 1})
        self.a.stereotypes = st
        self.link1.stereotype_instances = st
        self.link1.tagged_values = {"isBoolean": False, "intVal": 2}
        self.link1.tagged_values = {"isBoolean": True, "intVal": 20}
        assert self.link1.get_tagged_value("isBoolean") == True
        assert self.link1.get_tagged_value("intVal") == 20
        assert self.link1.tagged_values == {'isBoolean': True, 'intVal': 20}
        self.link1.tagged_values = {}
        # tagged values should not delete existing values
        assert self.link1.tagged_values == {"isBoolean": True, "intVal": 20}

    def test_tagged_values_setter_with_superclass(self):
        sst = CStereotype("SST", attributes={
            "intVal": 20, "intVal2": 30})
        st = CStereotype("S", superclasses=sst, attributes={
            "isBoolean": True,
            "intVal": 1})
        self.a.stereotypes = st
        self.link1.stereotype_instances = st
        self.link1.tagged_values = {"isBoolean": False}
        assert self.link1.tagged_values == {"isBoolean": False, "intVal": 1, "intVal2": 30}
        self.link1.set_tagged_value("intVal", 12, sst)
        self.link1.set_tagged_value("intVal", 15, st)
        self.link1.set_tagged_value("intVal2", 16, sst)
        assert self.link1.tagged_values == {"isBoolean": False, "intVal": 15, "intVal2": 16}
        assert self.link1.get_tagged_value("intVal", sst) == 12
        assert self.link1.get_tagged_value("intVal", st) == 15

    def test_tagged_values_setter_malformed_description(self):
        with pytest.raises(CException) as exc_info:
            self.link1.tagged_values = [1, 2, 3]
        e = exc_info.value
        assert e.value == "malformed tagged values description: '[1, 2, 3]'"

    def test_enum_type_attribute_values(self):
        enum_type = CEnum("EnumT", values=["A", "B", "C"])
        self.st.attributes = {
            "e1": enum_type,
            "e2": enum_type}
        e2 = self.st.get_attribute("e2")
        e2.default = "A"
        assert self.link1.get_tagged_value("e1") == None
        assert self.link1.get_tagged_value("e2") == "A"
        self.link1.set_tagged_value("e1", "B")
        self.link1.set_tagged_value("e2", "C")
        assert self.link1.get_tagged_value("e1") == "B"
        assert self.link1.get_tagged_value("e2") == "C"
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("e1", "X")
        e = exc_info.value
        assert e.value == "value 'X' is not element of enumeration"

    def test_default_init_after_instance_creation(self):
        enum_type = CEnum("EnumT", values=["A", "B", "C"])
        self.st.attributes = {
            "e1": enum_type,
            "e2": enum_type}
        e2 = self.st.get_attribute("e2")
        e2.default = "A"
        assert self.link1.get_tagged_value("e1") == None
        assert self.link1.get_tagged_value("e2") == "A"

    def test_attribute_value_type_check_bool1(self):
        self.st.attributes = {"t": bool}
        self.stereotype_instances = self.st
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("t", self.m1)
        e = exc_info.value
        assert f"value for attribute 't' is not a known attribute type" == e.value

    def test_attribute_value_type_check_bool2(self):
        self.st.attributes = {"t": bool}
        self.link1.stereotype_instances = self.st
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("t", 1)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_int(self):
        self.st.attributes = {"t": int}
        self.link1.stereotype_instances = self.st
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_float(self):
        self.st.attributes = {"t": float}
        self.link1.stereotype_instances = self.st
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_str(self):
        self.st.attributes = {"t": str}
        self.link1.stereotype_instances = self.st
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_list(self):
        self.st.attributes = {"t": list}
        self.link1.stereotype_instances = self.st
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_object(self):
        attribute_type = CClass(CMetaclass(), "AttrType")
        self.st.attributes = {"t": attribute_type}
        self.link1.stereotype_instances = self.st
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_value_type_check_enum(self):
        enum_type = CEnum("EnumT", values=["A", "B", "C"])
        self.st.attributes = {"t": enum_type}
        self.link1.stereotype_instances = self.st
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("t", True)
        e = exc_info.value
        assert f"value type for attribute 't' does not match attribute type" == e.value

    def test_attribute_deleted(self):
        self.st.attributes = {
            "isBoolean": True,
            "intVal": 15}
        self.link1.stereotype_instances = self.st
        assert self.link1.get_tagged_value("intVal") == 15
        self.st.attributes = {
            "isBoolean": False}
        assert self.link1.get_tagged_value("isBoolean") == True
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("intVal")
        e = exc_info.value
        assert e.value == "tagged value 'intVal' unknown"
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("intVal", 1)
        e = exc_info.value
        assert e.value == "tagged value 'intVal' unknown"

    def test_attribute_deleted_no_default(self):
        self.st.attributes = {
            "isBoolean": bool,
            "intVal": int}
        self.st.attributes = {"isBoolean": bool}
        assert self.link1.get_tagged_value("isBoolean") == None
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("intVal")
        e = exc_info.value
        assert e.value == "tagged value 'intVal' unknown"
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("intVal", 1)
        e = exc_info.value
        assert e.value == "tagged value 'intVal' unknown"

    def test_attributes_overwrite(self):
        self.st.attributes = {
            "isBoolean": True,
            "intVal": 15}
        self.link1.stereotype_instances = self.st
        assert self.link1.get_tagged_value("intVal") == 15
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("floatVal")
        e = exc_info.value
        assert e.value == "tagged value 'floatVal' unknown"
        self.link1.set_tagged_value("intVal", 18)
        self.st.attributes = {
            "isBoolean": False,
            "intVal": 19,
            "floatVal": 25.1}
        assert self.link1.get_tagged_value("isBoolean") == True
        assert self.link1.get_tagged_value("floatVal") == 25.1
        assert self.link1.get_tagged_value("intVal") == 18
        self.link1.set_tagged_value("floatVal", 1.2)
        assert self.link1.get_tagged_value("floatVal") == 1.2

    def test_attributes_overwrite_no_defaults(self):
        self.st.attributes = {
            "isBoolean": bool,
            "intVal": int}
        assert self.link1.get_tagged_value("isBoolean") == None
        self.link1.set_tagged_value("isBoolean", False)
        self.st.attributes = {
            "isBoolean": bool,
            "intVal": int,
            "floatVal": float}
        assert self.link1.get_tagged_value("isBoolean") == False
        assert self.link1.get_tagged_value("floatVal") == None
        assert self.link1.get_tagged_value("intVal") == None
        self.link1.set_tagged_value("floatVal", 1.2)
        assert self.link1.get_tagged_value("floatVal") == 1.2

    def test_attributes_deleted_on_subclass(self):
        self.st.attributes = {
            "isBoolean": True,
            "intVal": 1}
        st2 = CStereotype("S2", attributes={
            "isBoolean": False}, superclasses=self.st)
        self.a.stereotypes = st2
        self.link1.stereotype_instances = st2

        assert self.link1.get_tagged_value("isBoolean") == False
        assert self.link1.get_tagged_value("isBoolean", self.st) == True
        assert self.link1.get_tagged_value("isBoolean", st2) == False

        st2.attributes = {}

        assert self.link1.get_tagged_value("isBoolean") == True
        assert self.link1.get_tagged_value("intVal") == 1
        assert self.link1.get_tagged_value("isBoolean", self.st) == True
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("isBoolean", st2)
        e = exc_info.value
        assert e.value == "tagged value 'isBoolean' unknown for 'S2'"

    def test_attributes_deleted_on_subclass_no_defaults(self):
        self.st.attributes = {
            "isBoolean": bool,
            "intVal": int}
        st2 = CStereotype("S2", attributes={
            "isBoolean": bool}, superclasses=self.st)
        self.a.stereotypes = st2
        self.link1.stereotype_instances = st2

        assert self.link1.get_tagged_value("isBoolean") == None
        assert self.link1.get_tagged_value("isBoolean", self.st) == None
        assert self.link1.get_tagged_value("isBoolean", st2) == None

        st2.attributes = {}

        assert self.link1.get_tagged_value("isBoolean") == None
        assert self.link1.get_tagged_value("intVal") == None
        assert self.link1.get_tagged_value("isBoolean", self.st) == None
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("isBoolean", st2)
        e = exc_info.value
        assert e.value == "tagged value 'isBoolean' unknown for 'S2'"

    def test_wrong_stereotype_in_tagged_value(self):
        self.st.attributes = {
            "isBoolean": True}
        st2 = CStereotype("S2", attributes={
            "isBoolean": True})
        self.link1.stereotype_instances = self.st

        self.link1.set_tagged_value("isBoolean", False)

        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("isBoolean", False, st2)
        e = exc_info.value
        assert e.value == "stereotype 'S2' is not a stereotype of element"

        assert self.link1.get_tagged_value("isBoolean") == False

        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("isBoolean", st2)
        e = exc_info.value
        assert e.value == "stereotype 'S2' is not a stereotype of element"

    def test_attribute_values_inheritance(self):
        t1 = CStereotype("T1")
        t2 = CStereotype("T2")
        c = CStereotype("C", superclasses=[t1, t2])
        sc = CStereotype("C", superclasses=c)

        t1.attributes = {"i0": 0}
        t2.attributes = {"i1": 1}
        c.attributes = {"i2": 2}
        sc.attributes = {"i3": 3}

        self.a.stereotypes = sc
        self.link1.stereotype_instances = sc

        for name, value in {"i0": 0, "i1": 1, "i2": 2, "i3": 3}.items():
            assert self.link1.get_tagged_value(name) == value

        assert self.link1.get_tagged_value("i0", t1) == 0
        assert self.link1.get_tagged_value("i1", t2) == 1
        assert self.link1.get_tagged_value("i2", c) == 2
        assert self.link1.get_tagged_value("i3", sc) == 3

        for name, value in {"i0": 10, "i1": 11, "i2": 12, "i3": 13}.items():
            self.link1.set_tagged_value(name, value)

        for name, value in {"i0": 10, "i1": 11, "i2": 12, "i3": 13}.items():
            assert self.link1.get_tagged_value(name) == value

        assert self.link1.get_tagged_value("i0", t1) == 10
        assert self.link1.get_tagged_value("i1", t2) == 11
        assert self.link1.get_tagged_value("i2", c) == 12
        assert self.link1.get_tagged_value("i3", sc) == 13

    def test_attribute_values_inheritance_after_delete_superclass(self):
        t1 = CStereotype("T1")
        t2 = CStereotype("T2")
        c = CStereotype("C", superclasses=[t1, t2])
        sc = CStereotype("C", superclasses=c)

        t1.attributes = {"i0": 0}
        t2.attributes = {"i1": 1}
        c.attributes = {"i2": 2}
        sc.attributes = {"i3": 3}

        self.a.stereotypes = sc
        self.link1.stereotype_instances = sc

        t2.delete()

        for name, value in {"i0": 0, "i2": 2, "i3": 3}.items():
            assert self.link1.get_tagged_value(name) == value
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("i1")
        e = exc_info.value
        assert e.value == "tagged value 'i1' unknown"

        assert self.link1.get_tagged_value("i0", t1) == 0
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("i1", t2)
        e = exc_info.value
        assert e.value == "tagged value 'i1' unknown for ''"
        assert self.link1.get_tagged_value("i2", c) == 2
        assert self.link1.get_tagged_value("i3", sc) == 3

        for name, value in {"i0": 10, "i2": 12, "i3": 13}.items():
            self.link1.set_tagged_value(name, value)
        with pytest.raises(CException) as exc_info:
            self.link1.set_tagged_value("i1", 11)
        e = exc_info.value
        assert e.value == "tagged value 'i1' unknown"

        for name, value in {"i0": 10, "i2": 12, "i3": 13}.items():
            assert self.link1.get_tagged_value(name) == value
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("i1")
        e = exc_info.value
        assert e.value == "tagged value 'i1' unknown"

        assert self.link1.get_tagged_value("i0", t1) == 10
        with pytest.raises(CException) as exc_info:
            self.link1.get_tagged_value("i1", t2)
        e = exc_info.value
        assert e.value == "tagged value 'i1' unknown for ''"
        assert self.link1.get_tagged_value("i2", c) == 12
        assert self.link1.get_tagged_value("i3", sc) == 13

    def test_attribute_values_same_name_inheritance(self):
        t1 = CStereotype("T1")
        t2 = CStereotype("T2")
        c = CStereotype("C", superclasses=[t1, t2])
        sc = CStereotype("C", superclasses=c)

        t1.attributes = {"i": 0}
        t2.attributes = {"i": 1}
        c.attributes = {"i": 2}
        sc.attributes = {"i": 3}

        self.a.stereotypes = t1
        self.link1.stereotype_instances = sc
        self.link2.stereotype_instances = c
        self.link3.stereotype_instances = t1

        assert self.link1.get_tagged_value("i") == 3
        assert self.link2.get_tagged_value("i") == 2
        assert self.link3.get_tagged_value("i") == 0

        assert self.link1.get_tagged_value("i", sc) == 3
        assert self.link1.get_tagged_value("i", c) == 2
        assert self.link1.get_tagged_value("i", t2) == 1
        assert self.link1.get_tagged_value("i", t1) == 0
        assert self.link2.get_tagged_value("i", c) == 2
        assert self.link2.get_tagged_value("i", t2) == 1
        assert self.link2.get_tagged_value("i", t1) == 0
        assert self.link3.get_tagged_value("i", t1) == 0

        self.link1.set_tagged_value("i", 10)
        self.link2.set_tagged_value("i", 11)
        self.link3.set_tagged_value("i", 12)

        assert self.link1.get_tagged_value("i") == 10
        assert self.link2.get_tagged_value("i") == 11
        assert self.link3.get_tagged_value("i") == 12

        assert self.link1.get_tagged_value("i", sc) == 10
        assert self.link1.get_tagged_value("i", c) == 2
        assert self.link1.get_tagged_value("i", t2) == 1
        assert self.link1.get_tagged_value("i", t1) == 0
        assert self.link2.get_tagged_value("i", c) == 11
        assert self.link2.get_tagged_value("i", t2) == 1
        assert self.link2.get_tagged_value("i", t1) == 0
        assert self.link3.get_tagged_value("i", t1) == 12

        self.link1.set_tagged_value("i", 130, sc)
        self.link1.set_tagged_value("i", 100, t1)
        self.link1.set_tagged_value("i", 110, t2)
        self.link1.set_tagged_value("i", 120, c)

        assert self.link1.get_tagged_value("i") == 130

        assert self.link1.get_tagged_value("i", sc) == 130
        assert self.link1.get_tagged_value("i", c) == 120
        assert self.link1.get_tagged_value("i", t2) == 110
        assert self.link1.get_tagged_value("i", t1) == 100

    def test_tagged_values_inheritance_multiple_stereotypes(self):
        t1 = CStereotype("T1")
        t2 = CStereotype("T2")
        st_a = CStereotype("STA", superclasses=[t1, t2])
        sub_a = CStereotype("SubA", superclasses=[st_a])
        st_b = CStereotype("STB", superclasses=[t1, t2])
        sub_b = CStereotype("SubB", superclasses=[st_b])
        st_c = CStereotype("STC")
        sub_c = CStereotype("SubC", superclasses=[st_c])

        self.a.stereotypes = [t1, st_c]
        self.link1.stereotype_instances = [sub_a, sub_b, sub_c]

        t1.attributes = {"i0": 0}
        t2.attributes = {"i1": 1}
        st_a.attributes = {"i2": 2}
        sub_a.attributes = {"i3": 3}
        st_b.attributes = {"i4": 4}
        sub_b.attributes = {"i5": 5}
        st_c.attributes = {"i6": 6}
        sub_c.attributes = {"i7": 7}

        assert self.link1.get_tagged_value("i0") == 0
        assert self.link1.get_tagged_value("i1") == 1
        assert self.link1.get_tagged_value("i2") == 2
        assert self.link1.get_tagged_value("i3") == 3
        assert self.link1.get_tagged_value("i4") == 4
        assert self.link1.get_tagged_value("i5") == 5
        assert self.link1.get_tagged_value("i6") == 6
        assert self.link1.get_tagged_value("i7") == 7

        assert self.link1.get_tagged_value("i0", t1) == 0
        assert self.link1.get_tagged_value("i1", t2) == 1
        assert self.link1.get_tagged_value("i2", st_a) == 2
        assert self.link1.get_tagged_value("i3", sub_a) == 3
        assert self.link1.get_tagged_value("i4", st_b) == 4
        assert self.link1.get_tagged_value("i5", sub_b) == 5
        assert self.link1.get_tagged_value("i6", st_c) == 6
        assert self.link1.get_tagged_value("i7", sub_c) == 7

        self.link1.set_tagged_value("i0", 10)
        self.link1.set_tagged_value("i1", 11)
        self.link1.set_tagged_value("i2", 12)
        self.link1.set_tagged_value("i3", 13)
        self.link1.set_tagged_value("i4", 14)
        self.link1.set_tagged_value("i5", 15)
        self.link1.set_tagged_value("i6", 16)
        self.link1.set_tagged_value("i7", 17)

        assert self.link1.get_tagged_value("i0") == 10
        assert self.link1.get_tagged_value("i1") == 11
        assert self.link1.get_tagged_value("i2") == 12
        assert self.link1.get_tagged_value("i3") == 13
        assert self.link1.get_tagged_value("i4") == 14
        assert self.link1.get_tagged_value("i5") == 15
        assert self.link1.get_tagged_value("i6") == 16
        assert self.link1.get_tagged_value("i7") == 17

        self.link1.set_tagged_value("i0", 210, t1)
        self.link1.set_tagged_value("i1", 211, t2)
        self.link1.set_tagged_value("i2", 212, st_a)
        self.link1.set_tagged_value("i3", 213, sub_a)
        self.link1.set_tagged_value("i4", 214, st_b)
        self.link1.set_tagged_value("i5", 215, sub_b)
        self.link1.set_tagged_value("i6", 216, st_c)
        self.link1.set_tagged_value("i7", 217, sub_c)

        assert self.link1.get_tagged_value("i0") == 210
        assert self.link1.get_tagged_value("i1") == 211
        assert self.link1.get_tagged_value("i2") == 212
        assert self.link1.get_tagged_value("i3") == 213
        assert self.link1.get_tagged_value("i4") == 214
        assert self.link1.get_tagged_value("i5") == 215
        assert self.link1.get_tagged_value("i6") == 216
        assert self.link1.get_tagged_value("i7") == 217

    def test_tagged_values_non_pos_argument_object_add_links(self):
        s = CStereotype("S", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"]})
        self.a.stereotypes = s

        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        c3 = CClass(self.m2, "C3")

        links = c1.add_links([c2, c3], stereotype_instances=s, tagged_values={
            "isBoolean": True, "intVal": 1, "floatVal": 1.1, "string": "abc", "list": ["a", "b"]
        })
        link = links[0]

        assert link.stereotype_instances == [s]
        assert link.get_tagged_value("isBoolean") == True
        assert link.get_tagged_value("intVal") == 1
        assert link.get_tagged_value("floatVal") == 1.1
        assert link.get_tagged_value("string") == "abc"
        assert link.get_tagged_value("list") == ["a", "b"]

    def test_tagged_values_non_pos_argument_add_links_function(self):
        s = CStereotype("S", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"]})
        self.a.stereotypes = s

        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        c3 = CClass(self.m2, "C3")

        links = add_links({c1: [c2, c3]}, stereotype_instances=s, tagged_values={
            "isBoolean": True, "intVal": 1, "floatVal": 1.1, "string": "abc", "list": ["a", "b"]
        })
        link = links[0]

        assert link.stereotype_instances == [s]
        assert link.get_tagged_value("isBoolean") == True
        assert link.get_tagged_value("intVal") == 1
        assert link.get_tagged_value("floatVal") == 1.1
        assert link.get_tagged_value("string") == "abc"
        assert link.get_tagged_value("list") == ["a", "b"]

    def test_delete_tagged_values(self):
        s = CStereotype("S", attributes={
            "isBoolean": True,
            "intVal": 1,
            "floatVal": 1.1,
            "string": "abc",
            "list": ["a", "b"]})
        self.a.stereotypes = s
        self.link1.stereotype_instances = s
        self.link1.delete_tagged_value("isBoolean")
        self.link1.delete_tagged_value("intVal")
        list_value = self.link1.delete_tagged_value("list")
        assert self.link1.tagged_values == {'floatVal': 1.1, 'string': 'abc'}
        assert list_value == ['a', 'b']

    def test_delete_tagged_values_with_superclass(self):
        sst = CStereotype("SST", attributes={
            "intVal": 20, "intVal2": 30})
        st = CStereotype("ST", superclasses=sst, attributes={
            "isBoolean": True,
            "intVal": 1})
        self.a.stereotypes = st
        self.link1.stereotype_instances = st

        self.link1.delete_tagged_value("isBoolean")
        self.link1.delete_tagged_value("intVal2")
        assert self.link1.tagged_values == {"intVal": 1}

        self.link1.set_tagged_value("intVal", 2, sst)
        self.link1.set_tagged_value("intVal", 3, st)
        assert self.link1.tagged_values == {"intVal": 3}
        self.link1.delete_tagged_value("intVal")
        assert self.link1.tagged_values == {"intVal": 2}

        self.link1.set_tagged_value("intVal", 2, sst)
        self.link1.set_tagged_value("intVal", 3, st)
        self.link1.delete_tagged_value("intVal", st)
        assert self.link1.tagged_values == {"intVal": 2}

        self.link1.set_tagged_value("intVal", 2, sst)
        self.link1.set_tagged_value("intVal", 3, st)
        self.link1.delete_tagged_value("intVal", sst)
        assert self.link1.tagged_values == {"intVal": 3}

    def test_delete_tagged_values_exceptional_cases(self):
        s = CStereotype("S", attributes={"b": True})
        self.a.stereotypes = s
        self.link1.stereotype_instances = s
        self.link2.delete()

        with pytest.raises(CException) as exc_info:
            self.link2.get_tagged_value("b")
        e = exc_info.value
        assert e.value == "can't get tagged value 'b' on deleted link"

        with pytest.raises(CException) as exc_info:
            self.link2.set_tagged_value("b", 1)
        e = exc_info.value
        assert e.value == "can't set tagged value 'b' on deleted link"

        with pytest.raises(CException) as exc_info:
            self.link2.delete_tagged_value("b")
        e = exc_info.value
        assert e.value == "can't delete tagged value 'b' on deleted link"

        with pytest.raises(CException) as exc_info:
            self.link2.tagged_values = {"b": 1}
        e = exc_info.value
        assert e.value == "can't set tagged values on deleted link"

        with pytest.raises(CException) as exc_info:
            # we just use list here, in order to not get a warning that self.l2.tagged_values has no effect
            list(self.link2.tagged_values)
        e = exc_info.value
        assert e.value == "can't get tagged values on deleted link"

        self.link1.stereotype_instances = s
        with pytest.raises(CException) as exc_info:
            self.link1.delete_tagged_value("x")
        e = exc_info.value
        assert e.value == "tagged value 'x' unknown"


