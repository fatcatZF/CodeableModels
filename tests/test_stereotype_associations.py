
import pytest
from codeable_models import CMetaclass, CStereotype, CClass, CException, CBundle


class TestStereotypeAssociations:

    def setup_method(self):
        self.stereotypeBundle = CBundle("Elements")
        self.s1 = CStereotype("S1", bundles=self.stereotypeBundle)
        self.s2 = CStereotype("S2", bundles=self.stereotypeBundle)
        self.s3 = CStereotype("S3", bundles=self.stereotypeBundle)
        self.s4 = CStereotype("S4", bundles=self.stereotypeBundle)
        self.s5 = CStereotype("S5", bundles=self.stereotypeBundle)

    def get_all_associations_in_bundle(self):
        associations = []
        for c in self.stereotypeBundle.get_elements(type=CStereotype):
            for a in c.all_associations:
                if a not in associations:
                    associations.append(a)
        return associations

    def test_association_creation(self):
        a1 = self.s1.association(self.s2, multiplicity="1", role_name="t",
                                 source_multiplicity="*", source_role_name="i")
        a2 = self.s1.association(self.s2, "[o]*->[s]1")
        a3 = self.s1.association(self.s3, "[a] 0..1 <*>- [n]*")
        a4 = self.s1.association(self.s3, multiplicity="*", role_name="e",
                                 source_multiplicity="0..1", source_role_name="a", composition=True)
        a5 = self.s4.association(self.s3, multiplicity="*", role_name="n",
                                 source_multiplicity="0..1", source_role_name="a", aggregation=True)
        a6 = self.s3.association(self.s2, '[a] 0..3 <>- [e]*')

        assert len(self.get_all_associations_in_bundle()) == 6

        assert self.s1.associations[0].role_name == "t"
        assert a5.role_name == "n"
        assert a2.role_name == "s"
        assert a1.multiplicity == "1"
        assert a1.source_multiplicity == "*"
        assert a4.source_multiplicity == "0..1"
        assert a6.source_multiplicity == "0..3"

        assert a1.composition == False
        assert a1.aggregation == False
        assert a3.composition == True
        assert a3.aggregation == False
        assert a5.composition == False
        assert a5.aggregation == True

        a1.aggregation = True
        assert a1.composition == False
        assert a1.aggregation == True
        a1.composition = True
        assert a1.composition == True
        assert a1.aggregation == False

    def test_mixed_association_types(self):
        m1 = CMetaclass("M1")
        c1 = CClass(m1, "C1")
        with pytest.raises(CException) as exc_info:
            self.s1.association(c1, multiplicity="1", role_name="t",
                                source_multiplicity="*", source_role_name="i")
        e = exc_info.value
        assert "stereotype 'S1' is not compatible with association target 'C1'" == e.value

        with pytest.raises(CException) as exc_info:
            self.s1.association(m1, multiplicity="1", role_name="t",
                                source_multiplicity="*", source_role_name="i")
        e = exc_info.value
        assert "stereotype 'S1' is not compatible with association target 'M1'" == e.value

    def test_get_association_by_role_name(self):
        self.s1.association(self.s2, multiplicity="1", role_name="t",
                            source_multiplicity="*", source_role_name="i")
        self.s1.association(self.s2, multiplicity="1", role_name="s",
                            source_multiplicity="*", source_role_name="o")
        self.s1.association(self.s3, multiplicity="*", role_name="n",
                            source_multiplicity="0..1", source_role_name="a", composition=True)

        a_2 = next(a for a in self.s1.associations if a.role_name == "s")
        assert a_2.multiplicity == "1"
        assert a_2.source_role_name == "o"
        assert a_2.source_multiplicity == "*"

    def test_get_association_by_name(self):
        self.s1.association(self.s2, name="n1", multiplicity="1", role_name="t",
                            source_multiplicity="*", source_role_name="i")
        self.s1.association(self.s2, name="n2", multiplicity="1", role_name="s",
                            source_multiplicity="*", source_role_name="o")
        self.s1.association(self.s3, "n3: [a] 0..1 <*>- [n] *")

        a_2 = next(a for a in self.s1.associations if a.name == "n2")
        assert a_2.multiplicity == "1"
        assert a_2.source_role_name == "o"
        assert a_2.source_multiplicity == "*"

        a_3 = next(a for a in self.s1.associations if a.name == "n3")
        assert a_3.multiplicity == "*"
        assert a_3.role_name == "n"
        assert a_3.source_multiplicity == "0..1"
        assert a_3.source_role_name == "a"
        assert a_3.composition == True

    def test_get_associations(self):
        a1 = self.s1.association(self.s2, multiplicity="1", role_name="t",
                                 source_multiplicity="*", source_role_name="i")
        a2 = self.s1.association(self.s2, multiplicity="1", role_name="s",
                                 source_multiplicity="*", source_role_name="o")
        a3 = self.s1.association(self.s3, multiplicity="*", role_name="n",
                                 source_multiplicity="0..1", source_role_name="a", composition=True)
        a4 = self.s1.association(self.s3, multiplicity="*", role_name="e",
                                 source_multiplicity="0..1", source_role_name="a", composition=True)
        a5 = self.s4.association(self.s3, multiplicity="*", role_name="n",
                                 source_multiplicity="0..1", source_role_name="a", aggregation=True)
        a6 = self.s3.association(self.s2, multiplicity="*", role_name="e",
                                 source_multiplicity="1..3", source_role_name="a", aggregation=True)
        assert self.s1.associations == [a1, a2, a3, a4]
        assert self.s2.associations == [a1, a2, a6]
        assert self.s3.associations == [a3, a4, a5, a6]
        assert self.s4.associations == [a5]
        assert self.s5.associations == []

    def test_delete_associations(self):
        a1 = self.s1.association(self.s2, multiplicity="1", role_name="t",
                                 source_multiplicity="*", source_role_name="i")
        a2 = self.s1.association(self.s2, multiplicity="1", role_name="s",
                                 source_multiplicity="*", source_role_name="o")
        a3 = self.s1.association(self.s3, multiplicity="*", role_name="n",
                                 source_multiplicity="0..1", source_role_name="a", composition=True)
        a4 = self.s1.association(self.s3, multiplicity="*", role_name="e",
                                 source_multiplicity="0..1", source_role_name="a", composition=True)
        a5 = self.s4.association(self.s3, multiplicity="*", role_name="n",
                                 source_multiplicity="0..1", source_role_name="a", aggregation=True)
        a6 = self.s3.association(self.s2, multiplicity="*", role_name="e",
                                 source_multiplicity="0..3", source_role_name="a", aggregation=True)
        a7 = self.s1.association(self.s1, multiplicity="*", role_name="x",
                                 source_multiplicity="1..3", source_role_name="y")

        assert len(self.get_all_associations_in_bundle()) == 7

        a2.delete()
        a4.delete()

        assert len(self.get_all_associations_in_bundle()) == 5

        assert self.s1.associations == [a1, a3, a7]
        assert self.s2.associations == [a1, a6]
        assert self.s3.associations == [a3, a5, a6]
        assert self.s4.associations == [a5]
        assert self.s5.associations == []

    def test_delete_class_and_get_associations(self):
        self.s1.association(self.s2, multiplicity="1", role_name="t",
                            source_multiplicity="*", source_role_name="i")
        self.s1.association(self.s2, multiplicity="1", role_name="s",
                            source_multiplicity="*", source_role_name="o")
        self.s1.association(self.s3, multiplicity="*", role_name="n",
                            source_multiplicity="0..1", source_role_name="a", composition=True)
        self.s1.association(self.s3, multiplicity="*", role_name="e",
                            source_multiplicity="0..1", source_role_name="a", composition=True)
        a5 = self.s4.association(self.s3, multiplicity="*", role_name="n",
                                 source_multiplicity="0..1", source_role_name="a", aggregation=True)
        a6 = self.s3.association(self.s2, multiplicity="*", role_name="e",
                                 source_multiplicity="0..3", source_role_name="a", aggregation=True)
        self.s1.association(self.s1, multiplicity="*", role_name="x",
                            source_multiplicity="1..3", source_role_name="y")

        assert len(self.get_all_associations_in_bundle()) == 7

        self.s1.delete()

        assert len(self.get_all_associations_in_bundle()) == 2

        assert self.s1.associations == []
        assert self.s2.associations == [a6]
        assert self.s3.associations == [a5, a6]
        assert self.s4.associations == [a5]
        assert self.s5.associations == []

    def test_all_associations(self):
        s = CStereotype("S")
        d = CStereotype("D", superclasses=s)
        a = s.association(d, "is next: [prior s] * -> [next d] *")
        assert d.all_associations == [a]
        assert s.all_associations == [a]

    def test_get_opposite_classifier(self):
        a = self.s1.association(self.s2, "[o]*->[s]1")
        assert a.get_opposite_classifier(self.s1) == self.s2
        assert a.get_opposite_classifier(self.s2) == self.s1
        with pytest.raises(CException) as exc_info:
            a.get_opposite_classifier(self.s3)
        e = exc_info.value
        assert "can only get opposite if either source or target classifier is provided" == e.value


