
import pytest
from codeable_models import CMetaclass, CClass, CException, CStereotype


class TestStereotypeDefaultValues:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.stereotype = CStereotype("S", extended=self.mcl)
        self.m1 = CMetaclass("M1")
        self.m2 = CMetaclass("M2")
        self.a = self.m1.association(self.m2, name="a", multiplicity="*", role_name="m1",
                                     source_multiplicity="1", source_role_name="m2")

    def test_default_values_on_stereotype(self):
        mcl = CMetaclass("MCL", attributes={
            "aStr1": str, "aList1": list, "aStr2": "def", "aList2": ["d1", "d2"], "b": bool
        })
        s1 = CStereotype("S1", extended=mcl, default_values={
            "aStr1": "a", "aList1": ["a"], "aStr2": "def2", "aList2": []
        })
        assert s1.default_values == {"aStr1": "a", "aList1": ["a"], "aStr2": "def2", "aList2": []}
        assert s1.get_default_value("aStr1") == "a"
        s1.set_default_value("aStr1", "b")
        assert s1.get_default_value("aStr1") == "b"

        s1.default_values = {}
        # default_values should not delete existing values
        assert s1.default_values == {'aStr1': 'b', 'aList1': ['a'], 'aStr2': 'def2', 'aList2': []}

        s1.default_values = {"b": True}
        assert s1.default_values == {'aStr1': 'b', 'aList1': ['a'], 'aStr2': 'def2', 'aList2': [], 'b': True}
        assert s1.get_default_value("b") == True

    def test_default_values_on_stereotype__initialized_in_class_constructor(self):
        mcl = CMetaclass("MCL", attributes={
            "aStr1": str, "aList1": list, "aStr2": "def", "aList2": ["d1", "d2"], "b": True
        })
        s = CStereotype("S", extended=mcl, default_values={
            "aStr1": "a", "aList1": ["a"], "aStr2": "def2", "aList2": []
        })
        c1 = CClass(mcl, "C1", stereotype_instances=s)
        # metaclass defaults are initialized at the end of construction, stereotype_instances runs before
        # and thus overwrites metaclass defaults
        assert c1.values == {"aStr1": "a", "aList1": ["a"], "aStr2": "def2", "aList2": [], "b": True}

    def test_default_values_on_stereotype__initialize_after_class_constructor(self):
        mcl = CMetaclass("MCL", attributes={
            "aStr1": str, "aList1": list, "aStr2": "def", "aList2": ["d1", "d2"], "b": True
        })
        s = CStereotype("S", extended=mcl, default_values={
            "aStr1": "a", "aList1": ["a"], "aStr2": "def2", "aList2": []
        })
        c1 = CClass(mcl, "C1")
        c1.stereotype_instances = s
        # after construction, metaclass defaults are set. The stereotype defaults are set only for 
        # values not yet set
        assert c1.values == {'aStr2': 'def', 'aList2': ['d1', 'd2'], 'b': True, 'aStr1': 'a', 'aList1': ['a']}

    def test_default_values_on_stereotype_exceptions(self):
        mcl = CMetaclass("MCL", attributes={
            "aStr1": str, "aList1": list, "aStr2": "def", "aList2": ["d1", "d2"], "b": bool
        })
        s1 = CStereotype("S1", extended=mcl, default_values={
            "aStr1": "a", "aList1": ["a"], "aStr2": "def2", "aList2": []
        })
        with pytest.raises(CException) as exc_info:
            s1.default_values = {"x": bool}
        e = exc_info.value
        assert e.value == "attribute 'x' unknown for metaclasses extended by stereotype 'S1'"

        with pytest.raises(CException) as exc_info:
            s1.default_values = {"b": bool}
        e = exc_info.value
        assert e.value == "value for attribute 'b' is not a known attribute type"

        with pytest.raises(CException) as exc_info:
            s1.default_values = {"b": []}
        e = exc_info.value
        assert e.value == "value type for attribute 'b' does not match attribute type"

        with pytest.raises(CException) as exc_info:
            s1.default_values = []
        e = exc_info.value
        assert e.value == "malformed default values description: '[]'"

    def test_default_values_on_stereotype_inheritance1(self):
        mcl = CMetaclass("MCL", attributes={
            "aStr2": "def", "aList2": ["d1", "d2"], "b": bool
        })
        mcl2 = CMetaclass("MCL2", superclasses=mcl, attributes={
            "aStr1": str, "aList1": list
        })
        s1 = CStereotype("S1", extended=mcl2, default_values={
            "aStr1": "a", "aList2": []
        })
        s2 = CStereotype("S2", superclasses=s1, extended=mcl2, default_values={
            "aList1": ["a"], "aStr2": "def2"
        })

        assert s1.default_values == {"aStr1": "a", "aList2": []}
        assert s2.default_values == {"aList1": ["a"], "aStr2": "def2"}
        assert s1.get_default_value("aStr1") == "a"
        assert s2.get_default_value("aStr2") == "def2"
        assert s2.get_default_value("aStr1") == None
        assert s1.get_default_value("aStr2") == None

    def test_default_values_on_stereotype_inheritance2(self):
        mcl = CMetaclass("MCL", attributes={
            "aStr2": "def", "aList2": ["d1", "d2"], "b": bool
        })
        mcl2 = CMetaclass("MCL2", superclasses=mcl, attributes={
            "aStr1": str, "aList1": list
        })
        with pytest.raises(CException) as exc_info:
            CStereotype("S1", extended=mcl, default_values={
                "aStr1": "a", "aList2": []
            })
        e = exc_info.value
        assert e.value == "attribute 'aStr1' unknown for metaclasses extended by stereotype 'S1'"

        s2 = CStereotype("S2", extended=mcl2, default_values={
            "aList1": ["a"], "aStr2": "def2"
        })
        assert s2.default_values == {"aList1": ["a"], "aStr2": "def2"}

    def test_default_values_on_stereotype__metaclass_delete(self):
        mcl = CMetaclass("MCL", attributes={
            "aStr2": "def", "aList2": ["d1", "d2"], "b": bool
        })
        mcl2 = CMetaclass("MCL2", superclasses=mcl, attributes={
            "aStr1": str, "aList1": list
        })
        s1 = CStereotype("S1", extended=mcl2, default_values={
            "aStr1": "a", "aList2": []
        })
        s2 = CStereotype("S2", superclasses=s1, extended=mcl2, default_values={
            "aList1": ["a"], "aStr2": "def2"
        })
        mcl.delete()

        assert s1.default_values == {"aStr1": "a"}
        assert s2.default_values == {"aList1": ["a"]}
        assert s1.get_default_value("aStr1") == "a"
        with pytest.raises(CException) as exc_info:
            assert s2.get_default_value("aStr2") == "def2"
        e = exc_info.value
        assert e.value == "attribute 'aStr2' unknown for metaclasses extended by stereotype 'S2'"
        assert s2.get_default_value("aStr1") == None

    def test_delete_default_values(self):
        mcl = CMetaclass("MCL", attributes={
            "isBoolean": True,
            "intVal": int,
            "floatVal": 1.1,
            "string": "def",
            "list": list})
        s = CStereotype("S", extended=mcl, default_values={
            "isBoolean": False,
            "intVal": 1,
            "string": "abc",
            "list": ["a", "b"]})
        c1 = CClass(mcl, "C1", stereotype_instances=s)
        s.delete_default_value("isBoolean")
        s.delete_default_value("intVal")
        list_value = s.delete_default_value("list")
        assert s.default_values == {"string": "abc"}
        assert list_value == ['a', 'b']
        c2 = CClass(mcl, "C2", stereotype_instances=s)
        assert c1.values == {'isBoolean': False, 'floatVal': 1.1, 'string': 'abc', 'intVal': 1, 'list': ['a', 'b']}
        assert c2.values == {'isBoolean': True, 'floatVal': 1.1, 'string': 'abc'}

    def test_delete_default_values_with_superclass(self):
        mcl_super = CMetaclass("MCLSuper", attributes={
            "isBoolean": False,
            "intVal": int,
            "intVal2": int})
        mcl = CMetaclass("MCL", superclasses=mcl_super, attributes={
            "isBoolean": False,
            "intVal": int,
            "intVal2": int})
        sst = CStereotype("SST", extended=mcl, default_values={
            "intVal": 20, "intVal2": 30})
        st = CStereotype("ST", superclasses=sst, default_values={
            "isBoolean": True,
            "intVal": 1})
        c1 = CClass(mcl, "C1", stereotype_instances=st)
        assert c1.values == {'isBoolean': True, 'intVal': 1, 'intVal2': 30}
        st.delete_default_value("isBoolean")
        sst.delete_default_value("intVal2")
        st.delete_default_value("intVal")
        assert st.default_values == {}
        assert sst.default_values == {"intVal": 20}
        c2 = CClass(mcl, "C2", stereotype_instances=st)
        assert c1.values == {'isBoolean': True, 'intVal': 1, 'intVal2': 30}
        assert c2.values == {'isBoolean': False, 'intVal': 20}

        sst.set_default_value("intVal", 2, mcl_super)
        sst.set_default_value("intVal", 3, mcl)
        assert sst.default_values == {"intVal": 3}
        sst.delete_default_value("intVal")
        assert sst.default_values == {"intVal": 2}

        sst.set_default_value("intVal", 2, mcl_super)
        sst.set_default_value("intVal", 3, mcl)
        sst.delete_default_value("intVal", mcl)
        assert sst.default_values == {"intVal": 2}

        sst.set_default_value("intVal", 2, mcl_super)
        sst.set_default_value("intVal", 3, mcl)
        sst.delete_default_value("intVal", mcl_super)
        assert sst.default_values == {"intVal": 3}

    def test_default_values_exceptional_cases(self):
        mcl = CMetaclass("MCL", attributes={
            "isBoolean": True,
            "intVal": int,
            "floatVal": 1.1,
            "string": "def",
            "list": list})
        s1 = CStereotype("S", extended=mcl, default_values={
            "isBoolean": False,
            "intVal": 1,
            "string": "abc",
            "list": ["a", "b"]})
        s1.delete()

        with pytest.raises(CException) as exc_info:
            s1.get_default_value("b")
        e = exc_info.value
        assert e.value == "can't get default value 'b' on deleted stereotype"

        with pytest.raises(CException) as exc_info:
            s1.set_default_value("b", 1)
        e = exc_info.value
        assert e.value == "can't set default value 'b' on deleted stereotype"

        with pytest.raises(CException) as exc_info:
            s1.delete_default_value("b")
        e = exc_info.value
        assert e.value == "can't delete default value 'b' on deleted stereotype"

        with pytest.raises(CException) as exc_info:
            s1.default_values = {"b": 1}
        e = exc_info.value
        assert e.value == "can't set default values on deleted stereotype"

        with pytest.raises(CException) as exc_info:
            # we just use list here, in order to not get a warning that s1.default_values has no effect
            list(s1.default_values)
        e = exc_info.value
        assert e.value == "can't get default values on deleted stereotype"

        s = CStereotype("S", extended=mcl, default_values={
            "isBoolean": False,
            "intVal": 1,
            "string": "abc",
            "list": ["a", "b"]})
        with pytest.raises(CException) as exc_info:
            s.delete_default_value("x")
        e = exc_info.value
        assert e.value == "attribute 'x' unknown for metaclasses extended by stereotype 'S'"

    def test_default_values_from_stereotype_on_association_fails(self):
        with pytest.raises(CException) as exc_info:
            CStereotype("S1", extended=self.a, default_values={
                "aStr1": "a", "aList1": ["a"], "aStr2": "def2", "aList2": []
            })
        e = exc_info.value
        assert e.value == "default values can only be used on a stereotype that extends metaclasses"

    def test_set_default_value_from_stereotype_on_association_fails(self):
        with pytest.raises(CException) as exc_info:
            s1 = CStereotype("S1", extended=self.a)
            s1.set_default_value("a", "1")
        e = exc_info.value
        assert e.value == "default values can only be used on a stereotype that extends metaclasses"

    def test_get_default_value_from_stereotype_on_association_fails(self):
        with pytest.raises(CException) as exc_info:
            s1 = CStereotype("S1", extended=self.a)
            s1.get_default_value("a")
        e = exc_info.value
        assert e.value == "default values can only be used on a stereotype that extends metaclasses"

    def test_delete_default_value_from_stereotype_on_association_fails(self):
        with pytest.raises(CException) as exc_info:
            s1 = CStereotype("S1", extended=self.a)
            s1.delete_default_value("a")
        e = exc_info.value
        assert e.value == "default values can only be used on a stereotype that extends metaclasses"

    def test_default_values_from_stereotype_on_no_extension_fails(self):
        with pytest.raises(CException) as exc_info:
            CStereotype("S1", default_values={
                "aStr1": "a", "aList1": ["a"], "aStr2": "def2", "aList2": []
            })
        e = exc_info.value
        assert e.value == "default values can only be used on a stereotype that extends metaclasses"

    def test_set_default_value_from_stereotype_on_no_extension_fails(self):
        with pytest.raises(CException) as exc_info:
            s1 = CStereotype("S1")
            s1.set_default_value("a", "1")
        e = exc_info.value
        assert e.value == "default values can only be used on a stereotype that extends metaclasses"

    def test_get_default_value_from_stereotype_on_no_extension_fails(self):
        with pytest.raises(CException) as exc_info:
            s1 = CStereotype("S1")
            s1.get_default_value("a")
        e = exc_info.value
        assert e.value == "default values can only be used on a stereotype that extends metaclasses"

    def test_delete_default_value_from_stereotype_on_no_extension_fails(self):
        with pytest.raises(CException) as exc_info:
            s1 = CStereotype("S1")
            s1.delete_default_value("a")
        e = exc_info.value
        assert e.value == "default values can only be used on a stereotype that extends metaclasses"


