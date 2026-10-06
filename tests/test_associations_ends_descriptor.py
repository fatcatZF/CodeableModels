
import pytest
from codeable_models import CMetaclass, CClass, CException


class TestAssociationsEndsDescriptor:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.c1 = CClass(self.mcl, "C1")
        self.c2 = CClass(self.mcl, "C2")
        self.c3 = CClass(self.mcl, "C3")
        self.c4 = CClass(self.mcl, "C4")
        self.c5 = CClass(self.mcl, "C5")

    def test_ends_string_malformed(self):
        with pytest.raises(CException) as exc_info:
            self.c1.association(self.c2, '')
        e = exc_info.value
        assert "association descriptor malformed: ''" == e.value
        with pytest.raises(CException) as exc_info:
            self.c1.association(self.c2, '->->')
        e = exc_info.value
        assert "malformed multiplicity: ''" == e.value
        with pytest.raises(CException) as exc_info:
            self.c1.association(self.c2, 'a->b')
        e = exc_info.value
        assert "malformed multiplicity: 'a'" == e.value
        with pytest.raises(CException) as exc_info:
            self.c1.association(self.c2, '[]->[]')
        e = exc_info.value
        assert "malformed multiplicity: '[]'" == e.value
        with pytest.raises(CException) as exc_info:
            self.c1.association(self.c2, '[]1->[]*')
        e = exc_info.value
        assert "malformed multiplicity: '[]1'" == e.value
        with pytest.raises(CException) as exc_info:
            self.c1.association(self.c2, '::1->1')
        e = exc_info.value
        assert "malformed multiplicity: ':1'" == e.value
        with pytest.raises(CException) as exc_info:
            self.c1.association(self.c2, '1->1:')
        e = exc_info.value
        assert "association descriptor malformed: ''" == e.value

    def test_ends_string_association(self):
        a1 = self.c1.association(self.c2, '[a]1->[b]*')
        assert a1.role_name == "b"
        assert a1.source_role_name == "a"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == False

        a1 = self.c1.association(self.c2, ' [a b]  1   ->  [ b c_()-] * ')
        assert a1.role_name == " b c_()-"
        assert a1.source_role_name == "a b"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == False

        a1 = self.c1.association(self.c2, '1..3->    4..*  ')
        assert a1.role_name == None
        assert a1.source_role_name == None
        assert a1.multiplicity == "4..*"
        assert a1.source_multiplicity == "1..3"
        assert a1.composition == False
        assert a1.aggregation == False

        a1 = self.c1.association(self.c2, '[ax] -> [bx]')
        assert a1.role_name == "bx"
        assert a1.source_role_name == "ax"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == False

    def test_ends_string_aggregation(self):
        a1 = self.c1.association(self.c2, '[a]1<>-[b]*')
        assert a1.role_name == "b"
        assert a1.source_role_name == "a"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == True

        a1 = self.c1.association(self.c2, ' [a b]  1   <>-  [ b c_()-] * ')
        assert a1.role_name == " b c_()-"
        assert a1.source_role_name == "a b"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == True

        a1 = self.c1.association(self.c2, '1..3<>-    4..*  ')
        assert a1.role_name == None
        assert a1.source_role_name == None
        assert a1.multiplicity == "4..*"
        assert a1.source_multiplicity == "1..3"
        assert a1.composition == False
        assert a1.aggregation == True

        a1 = self.c1.association(self.c2, '[ax] <>- [bx]')
        assert a1.role_name == "bx"
        assert a1.source_role_name == "ax"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == True

    def test_ends_string_composition(self):
        a1 = self.c1.association(self.c2, '[a]1<*>-[b]*')
        assert a1.role_name == "b"
        assert a1.source_role_name == "a"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == True
        assert a1.aggregation == False

        a1 = self.c1.association(self.c2, ' [a b]  1   <*>-  [ b c_()-] * ')
        assert a1.role_name == " b c_()-"
        assert a1.source_role_name == "a b"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == True
        assert a1.aggregation == False

        a1 = self.c1.association(self.c2, '1..3<*>-    4..*  ')
        assert a1.role_name == None
        assert a1.source_role_name == None
        assert a1.multiplicity == "4..*"
        assert a1.source_multiplicity == "1..3"
        assert a1.composition == True
        assert a1.aggregation == False

        a1 = self.c1.association(self.c2, '[ax] <*>- [bx]')
        assert a1.role_name == "bx"
        assert a1.source_role_name == "ax"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == True
        assert a1.aggregation == False

    def test_ends_string_association_with_name(self):
        a1 = self.c1.association(self.c2, ' assoc a : [a]1->[b]*')
        assert a1.role_name == "b"
        assert a1.source_role_name == "a"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == False
        assert a1.name == "assoc a"

        a1 = self.c1.association(self.c2, 'a: [a b]  1   ->  [ b c_()-] * ')
        assert a1.role_name == " b c_()-"
        assert a1.source_role_name == "a b"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == False
        assert a1.name == "a"

        a1 = self.c1.association(self.c2, '"legal_name":1..3->    4..*  ')
        assert a1.role_name == None
        assert a1.source_role_name == None
        assert a1.multiplicity == "4..*"
        assert a1.source_multiplicity == "1..3"
        assert a1.composition == False
        assert a1.aggregation == False
        assert a1.name == '"legal_name"'

        a1 = self.c1.association(self.c2, '[ax] -> [bx]:[ax] -> [bx]')
        assert a1.role_name == "bx"
        assert a1.source_role_name == "ax"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == False
        assert a1.name == '[ax] -> [bx]'

    def test_ends_string_aggregation_with_name(self):
        a1 = self.c1.association(self.c2, ' assoc a : [a]1<>-[b]*')
        assert a1.role_name == "b"
        assert a1.source_role_name == "a"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == True
        assert a1.name == "assoc a"

        a1 = self.c1.association(self.c2, ': [a b]  1   <>-  [ b c_()-] * ')
        assert a1.role_name == " b c_()-"
        assert a1.source_role_name == "a b"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.name == ""

        a1 = self.c1.association(self.c2, '"legal_name":1..3<>-    4..*  ')
        assert a1.role_name == None
        assert a1.source_role_name == None
        assert a1.multiplicity == "4..*"
        assert a1.source_multiplicity == "1..3"
        assert a1.composition == False
        assert a1.aggregation == True
        assert a1.name == '"legal_name"'

        a1 = self.c1.association(self.c2, '[ax] <>- [bx]:[ax] <>- [bx]')
        assert a1.role_name == "bx"
        assert a1.source_role_name == "ax"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == False
        assert a1.aggregation == True
        assert a1.name == '[ax] <>- [bx]'

    def test_ends_string_composition_with_name(self):
        a1 = self.c1.association(self.c2, ' assoc a : [a]1<*>-[b]*')
        assert a1.role_name == "b"
        assert a1.source_role_name == "a"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == True
        assert a1.aggregation == False
        assert a1.name == "assoc a"

        a1 = self.c1.association(self.c2, 'a: [a b]  1   <*>-  [ b c_()-] * ')
        assert a1.role_name == " b c_()-"
        assert a1.source_role_name == "a b"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == True
        assert a1.aggregation == False
        assert a1.name == "a"

        a1 = self.c1.association(self.c2, '"legal_name":1..3<*>-    4..*  ')
        assert a1.role_name == None
        assert a1.source_role_name == None
        assert a1.multiplicity == "4..*"
        assert a1.source_multiplicity == "1..3"
        assert a1.composition == True
        assert a1.aggregation == False
        assert a1.name == '"legal_name"'

        a1 = self.c1.association(self.c2, '[ax] <*>- [bx]:[ax] <*>- [bx]')
        assert a1.role_name == "bx"
        assert a1.source_role_name == "ax"
        assert a1.multiplicity == "*"
        assert a1.source_multiplicity == "1"
        assert a1.composition == True
        assert a1.aggregation == False
        assert a1.name == '[ax] <*>- [bx]'


