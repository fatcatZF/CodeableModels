
import pytest
from codeable_models import CMetaclass, CStereotype, CClass, CException, set_links, add_links


class TestStereotypeInstancesOnLinks:
    def setup_method(self):
        self.m1 = CMetaclass("M1")
        self.m2 = CMetaclass("M2")
        self.a = self.m1.association(self.m2, name="a", multiplicity="*", role_name="m2",
                                     source_multiplicity="1", source_role_name="m1")

    def test_stereotype_instances_on_association_link(self):
        s1 = CStereotype("S1", extended=self.a)
        s2 = CStereotype("S2", extended=self.a)
        s3 = CStereotype("S3", extended=self.a)

        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        c3 = CClass(self.m2, "C3")
        links = set_links({c1: [c2, c3]})
        l1 = links[0]

        assert l1.stereotype_instances == []
        assert s1.extended_instances == []
        l1.stereotype_instances = [s1]
        assert s1.extended_instances == [l1]
        assert l1.stereotype_instances == [s1]
        l1.stereotype_instances = [s1, s2, s3]
        assert s1.extended_instances == [l1]
        assert s2.extended_instances == [l1]
        assert s3.extended_instances == [l1]
        assert set(l1.stereotype_instances) == {s1, s2, s3}
        l1.stereotype_instances = s2
        assert l1.stereotype_instances == [s2]
        assert s1.extended_instances == []
        assert s2.extended_instances == [l1]
        assert s3.extended_instances == []

        assert c1.get_links_for_association(self.a) == links
        assert c2.get_links_for_association(self.a) == [l1]
        assert c3.get_links_for_association(self.a) == [links[1]]

    def test_stereotype_instances_double_assignment(self):
        s1 = CStereotype("S1", extended=self.a)

        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        links = set_links({c1: c2})[0]

        with pytest.raises(CException) as exc_info:
            links.stereotype_instances = [s1, s1]
        e = exc_info.value
        assert e.value == "'S1' is already a stereotype instance on link from 'C1' to 'C2'"
        assert links.stereotype_instances == [s1]

    def test_stereotype_instances_none_assignment(self):
        CStereotype("S1", extended=self.a)

        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        links = set_links({c1: [c2]})[0]

        with pytest.raises(CException) as exc_info:
            links.stereotype_instances = [None]
        e = exc_info.value
        assert e.value == "'None' is not a stereotype"
        assert links.stereotype_instances == []

    def test_stereotype_instances_wrong_type_in_assignment(self):
        CStereotype("S1", extended=self.a)
        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        links = c1.add_links(c2)[0]
        with pytest.raises(CException) as exc_info:
            links.stereotype_instances = self.a
        e = exc_info.value
        assert e.value == "a list or a stereotype is required as input"
        assert links.stereotype_instances == []

    def test_multiple_extended_instances(self):
        s1 = CStereotype("S1", extended=self.a)
        s2 = CStereotype("S2", extended=self.a)
        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        c3 = CClass(self.m2, "C3")
        c4 = CClass(self.m2, "C4")
        links = set_links({c1: [c2, c3, c4]})
        links[0].stereotype_instances = [s1]
        assert s1.extended_instances == [links[0]]
        links[1].stereotype_instances = [s1]
        assert set(s1.extended_instances) == {links[0], links[1]}
        links[2].stereotype_instances = [s1, s2]
        assert set(s1.extended_instances) == {links[0], links[1], links[2]}
        assert set(s2.extended_instances) == {links[2]}

        assert c1.get_links_for_association(self.a) == links

    def test_delete_stereotype_of_extended_instances(self):
        s1 = CStereotype("S1", extended=self.a)
        s1.delete()
        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        links = set_links({c1: c2})[0]
        with pytest.raises(CException) as exc_info:
            links.stereotype_instances = [s1]
        e = exc_info.value
        assert e.value == "cannot access named element that has been deleted"

    def test_delete_stereotyped_element_instance(self):
        s1 = CStereotype("S1", extended=self.a)
        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        links = set_links({c1: c2}, stereotype_instances=[s1])[0]
        assert s1.extended_instances == [links]
        assert links.stereotype_instances == [s1]
        links.delete()
        assert s1.extended_instances == []
        assert links.stereotype_instances == []

    def test_add_stereotype_instance_wrong_association(self):
        other_association = self.m1.association(self.m2, name="b", multiplicity="*", role_name="m1",
                                                source_multiplicity="1", source_role_name="m2")
        s1 = CStereotype("S1", extended=self.a)
        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        links = set_links({c1: c2}, association=other_association)[0]
        with pytest.raises(CException) as exc_info:
            links.stereotype_instances = [s1]
        e = exc_info.value
        assert e.value == "stereotype 'S1' cannot be added to link from 'C1' to 'C2': no extension by this stereotype found"

    def test_add_stereotype_of_inherited_metaclass(self):
        sub1 = CMetaclass("Sub1", superclasses=self.m1)
        sub2 = CMetaclass("Sub2", superclasses=self.m2)
        s = CStereotype("S1", extended=self.a)
        c1 = CClass(sub1, "C1")
        c2 = CClass(sub2, "C2")
        links = add_links({c1: c2}, stereotype_instances=s)[0]
        assert s.extended_instances == [links]
        assert links.stereotype_instances == [s]

    def test_add_stereotype_instance_correct_by_inheritance_of_stereotype(self):
        s1 = CStereotype("S1", extended=self.a)
        s2 = CStereotype("S2", superclasses=s1)
        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        links = c1.add_links(c2, stereotype_instances=[s2])[0]
        assert s2.extended_instances == [links]
        assert links.stereotype_instances == [s2]

    def test_all_extended_instances(self):
        s1 = CStereotype("S1", extended=self.a)
        s2 = CStereotype("S2", superclasses=s1)
        c1 = CClass(self.m1, "C1")
        c2 = CClass(self.m2, "C2")
        c3 = CClass(self.m2, "C3")
        links = set_links({c1: [c2, c3]})
        links[0].stereotype_instances = s1
        links[1].stereotype_instances = s2
        assert s1.extended_instances == [links[0]]
        assert s2.extended_instances == [links[1]]
        assert s1.all_extended_instances == [links[0], links[1]]
        assert s2.all_extended_instances == [links[1]]


