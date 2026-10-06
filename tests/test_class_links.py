
import pytest
from codeable_models import CMetaclass, CClass, CObject, CException, set_links, add_links, delete_links


class TestClassLinks:
    def setup_method(self):
        self.m1 = CMetaclass("M1")
        self.m2 = CMetaclass("M2")
        self.mcl = CMetaclass("MCL")

    def test_link_methods_wrong_keyword_args(self):
        c1 = CClass(self.m1, "C1")
        with pytest.raises(CException) as exc_info:
            add_links({c1: c1}, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            c1.add_links(c1, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            set_links({c1: c1}, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            c1.delete_links(c1, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            delete_links({c1: c1}, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            c1.get_linked(associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            delete_links({c1: c1}, stereotype_instances=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"

    def test_set_one_to_one_link(self):
        self.m1.association(self.m2, name="l", multiplicity="1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")

        assert c1.linked == []

        set_links({c1: c2})
        assert c1.linked == [c2]
        assert c2.linked == [c1]

        set_links({c1: c3})
        assert c1.linked == [c3]
        assert c2.linked == []
        assert c3.linked == [c1]

    def test_add_one_to_one_link(self):
        self.m1.association(self.m2, "l: 1 -> [target] 0..1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")

        assert c1.linked == []

        add_links({c1: c3})
        assert c1.linked == [c3]
        assert c3.linked == [c1]

        set_links({c1: []}, role_name="target")
        assert c1.linked == []

        c1.add_links(c2)
        assert c1.linked == [c2]
        assert c2.linked == [c1]

        with pytest.raises(CException) as exc_info:
            add_links({c1: c3})
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '2': should be '0..1'"
        assert c1.linked == [c2]
        assert c2.linked == [c1]
        assert c3.linked == []

    def test_wrong_types_add_links(self):
        self.m1.association(self.m2, name="l", multiplicity="1")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        with pytest.raises(CException) as exc_info:
            add_links({c1: self.mcl})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            c1.add_links([c2, self.mcl])
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"

    def test_wrong_types_set_links(self):
        self.m1.association(self.m2, name="l", multiplicity="1")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        with pytest.raises(CException) as exc_info:
            set_links({c1: self.mcl})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            set_links({c1: [c2, self.mcl]})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            set_links({c1: [c2, None]})
        e = exc_info.value
        assert e.value == "link target 'None' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            set_links({self.mcl: c2})
        e = exc_info.value
        assert e.value == "link source 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            set_links({None: c2})
        e = exc_info.value
        assert e.value == "link should not contain an empty source"

    def test_wrong_format_set_links(self):
        self.m1.association(self.m2, name="l", multiplicity="1")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            set_links([c1, c2])
        e = exc_info.value
        assert e.value == "link definitions should be of the form {<link source 1>: " + "<link target(s) 1>, ..., <link source n>: <link target(s) n>}"

    def test_remove_one_to_one_link(self):
        a = self.m1.association(self.m2, "l: 1 -> [c2] 0..1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m1, "c3")
        c4 = CClass(self.m2, "c4")

        links = set_links({c1: c2, c3: c4})
        assert c1.linked == [c2]
        assert c2.linked == [c1]
        assert c3.linked == [c4]
        assert c4.linked == [c3]
        assert c1.links == [links[0]]
        assert c2.links == [links[0]]
        assert c3.links == [links[1]]
        assert c4.links == [links[1]]

        with pytest.raises(CException) as exc_info:
            links = set_links({c1: None})
        e = exc_info.value
        assert e.value == "matching association not found for source 'c1' and targets '[]'"

        set_links({c1: None}, association=a)
        assert c1.linked == []
        assert c2.linked == []
        assert c3.linked == [c4]
        assert c4.linked == [c3]
        assert c1.links == []
        assert c2.links == []
        assert c3.links == [links[1]]
        assert c4.links == [links[1]]

    def test_set_links_one_to_n_link(self):
        self.m1.association(self.m2, name="l")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")

        set_links({c1: [c2, c3]})
        assert c1.linked == [c2, c3]
        assert c2.linked == [c1]
        assert c3.linked == [c1]
        set_links({c1: c2})
        assert c1.linked == [c2]
        assert c2.linked == [c1]
        assert c3.linked == []
        set_links({c3: c1, c2: c1})
        assert c1.linked == [c3, c2]
        assert c2.linked == [c1]
        assert c3.linked == [c1]

    def test_add_links_one_to_n_link(self):
        self.m1.association(self.m2, name="l")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")
        c5 = CClass(self.m2, "c5")
        c6 = CClass(self.m2, "c6")

        add_links({c1: [c2, c3]})
        assert c1.linked == [c2, c3]
        assert c2.linked == [c1]
        assert c3.linked == [c1]
        add_links({c1: c4})
        assert c1.linked == [c2, c3, c4]
        assert c2.linked == [c1]
        assert c3.linked == [c1]
        assert c4.linked == [c1]
        c1.add_links([c5, c6])
        assert c1.linked == [c2, c3, c4, c5, c6]
        assert c2.linked == [c1]
        assert c3.linked == [c1]
        assert c4.linked == [c1]
        assert c5.linked == [c1]
        assert c6.linked == [c1]

    def test_remove_one_to_n_link(self):
        a = self.m1.association(self.m2, name="l", multiplicity="*")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        set_links({c1: [c2, c3]})
        set_links({c1: c2})
        assert c1.linked == [c2]
        assert c2.linked == [c1]
        assert c3.linked == []
        with pytest.raises(CException) as exc_info:
            set_links({c1: []})
        e = exc_info.value
        assert e.value == "matching association not found for source 'c1' and targets '[]'"
        set_links({c1: []}, association=a)
        assert c1.linked == []
        assert c2.linked == []
        assert c3.linked == []

    def test_n_to_n_link(self):
        a = self.m1.association(self.m2, name="l", source_multiplicity="*")
        c1a = CClass(self.m1, "c1a")
        c1b = CClass(self.m1, "c1b")
        c1c = CClass(self.m1, "c1c")
        c2a = CClass(self.m2, "c2a")
        c2b = CClass(self.m2, "c2b")

        set_links({c1a: [c2a, c2b], c1b: [c2a], c1c: [c2b]})

        assert c1a.linked == [c2a, c2b]
        assert c1b.linked == [c2a]
        assert c1c.linked == [c2b]
        assert c2a.linked == [c1a, c1b]
        assert c2b.linked == [c1a, c1c]

        set_links({c2a: [c1a, c1b]})
        with pytest.raises(CException) as exc_info:
            set_links({c2b: []})
        e = exc_info.value
        assert e.value == "matching association not found for source 'c2b' and targets '[]'"
        set_links({c2b: []}, association=a)

        assert c1a.linked == [c2a]
        assert c1b.linked == [c2a]
        assert c1c.linked == []
        assert c2a.linked == [c1a, c1b]
        assert c2b.linked == []

    def test_remove_n_to_n_link(self):
        self.m1.association(self.m2, name="l", source_multiplicity="*", multiplicity="*")
        c1 = CClass(self.m1, "c2")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m1, "c4")
        set_links({c1: [c2, c3], c4: c2})
        set_links({c1: c2, c4: [c3, c2]})
        assert c1.linked == [c2]
        assert c2.linked == [c1, c4]
        assert c3.linked == [c4]
        assert c4.linked == [c3, c2]

    def test_n_to_n_set_self_link(self):
        self.m1.association(self.m1, name="a", source_multiplicity="*", multiplicity="*", source_role_name="super",
                            role_name="sub")

        top = CClass(self.m1, "Top")
        mid1 = CClass(self.m1, "Mid1")
        mid2 = CClass(self.m1, "Mid2")
        mid3 = CClass(self.m1, "Mid3")
        bottom1 = CClass(self.m1, "Bottom1")
        bottom2 = CClass(self.m1, "Bottom2")

        set_links({top: [mid1, mid2, mid3]}, role_name="sub")
        mid1.add_links([bottom1, bottom2], role_name="sub")

        assert top.linked == [mid1, mid2, mid3]
        assert mid1.linked == [top, bottom1, bottom2]
        assert mid2.linked == [top]
        assert mid3.linked == [top]
        assert bottom1.linked == [mid1]
        assert bottom2.linked == [mid1]

        assert top.get_linked(role_name="sub") == [mid1, mid2, mid3]
        assert mid1.get_linked(role_name="sub") == [bottom1, bottom2]
        assert mid2.get_linked(role_name="sub") == []
        assert mid3.get_linked(role_name="sub") == []
        assert bottom1.get_linked(role_name="sub") == []
        assert bottom2.get_linked(role_name="sub") == []

        assert top.get_linked(role_name="super") == []
        assert mid1.get_linked(role_name="super") == [top]
        assert mid2.get_linked(role_name="super") == [top]
        assert mid3.get_linked(role_name="super") == [top]
        assert bottom1.get_linked(role_name="super") == [mid1]
        assert bottom2.get_linked(role_name="super") == [mid1]

    def test_n_to_n_set_self_link_delete_links(self):
        self.m1.association(self.m1, name="a", source_multiplicity="*", multiplicity="*", source_role_name="super",
                            role_name="sub")

        top = CClass(self.m1, "Top")
        mid1 = CClass(self.m1, "Mid1")
        mid2 = CClass(self.m1, "Mid2")
        mid3 = CClass(self.m1, "Mid3")
        bottom1 = CClass(self.m1, "Bottom1")
        bottom2 = CClass(self.m1, "Bottom2")

        set_links({top: [mid1, mid2, mid3], mid1: [bottom1, bottom2]}, role_name="sub")
        # delete links
        set_links({top: []}, role_name="sub")
        assert top.linked == []
        assert mid1.linked == [bottom1, bottom2]
        # change links
        set_links({mid1: top, mid3: top, bottom1: mid1, bottom2: mid1}, role_name="super")

        assert top.linked == [mid1, mid3]
        assert mid1.linked == [top, bottom1, bottom2]
        assert mid2.linked == []
        assert mid3.linked == [top]
        assert bottom1.linked == [mid1]
        assert bottom2.linked == [mid1]

        assert top.get_linked(role_name="sub") == [mid1, mid3]
        assert mid1.get_linked(role_name="sub") == [bottom1, bottom2]
        assert mid2.get_linked(role_name="sub") == []
        assert mid3.get_linked(role_name="sub") == []
        assert bottom1.get_linked(role_name="sub") == []
        assert bottom2.get_linked(role_name="sub") == []

        assert top.get_linked(role_name="super") == []
        assert mid1.get_linked(role_name="super") == [top]
        assert mid2.get_linked(role_name="super") == []
        assert mid3.get_linked(role_name="super") == [top]
        assert bottom1.get_linked(role_name="super") == [mid1]
        assert bottom2.get_linked(role_name="super") == [mid1]

    def test_incompatible_classifier(self):
        self.m1.association(self.m2, name="l", multiplicity="*")
        cl = CClass(self.mcl, "CLX")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CObject(cl, "c3")
        with pytest.raises(CException) as exc_info:
            set_links({c1: [c2, c3]})
        e = exc_info.value
        assert e.value == "link target 'c3' is an object, but source is a class"
        with pytest.raises(CException) as exc_info:
            set_links({c1: c3})
        e = exc_info.value
        assert e.value == "link target 'c3' is an object, but source is a class"

    def test_duplicate_assignment(self):
        a = self.m1.association(self.m2, "l: *->*")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        with pytest.raises(CException) as exc_info:
            set_links({c1: [c2, c2]})
        e = exc_info.value
        assert e.value == "trying to link the same link twice 'c1 -> c2'' twice for the same association"
        assert c1.get_linked() == []
        assert c2.get_linked() == []

        b = self.m1.association(self.m2, "l: *->*")
        c1.add_links(c2, association=a)
        c1.add_links(c2, association=b)
        assert c1.get_linked() == [c2, c2]
        assert c2.get_linked() == [c1, c1]

    def test_non_existing_role_name(self):
        self.m1.association(self.m1, role_name="next", source_role_name="prior",
                            source_multiplicity="1", multiplicity="1")
        c1 = CClass(self.m1, "c1")
        with pytest.raises(CException) as exc_info:
            set_links({c1: c1}, role_name="target")
        e = exc_info.value
        assert e.value == "matching association not found for source 'c1' and targets '['c1']'"

    def test_link_association_ambiguous(self):
        self.m1.association(self.m2, name="a1", role_name="c2", multiplicity="*")
        self.m1.association(self.m2, name="a2", role_name="c2", multiplicity="*")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        with pytest.raises(CException) as exc_info:
            set_links({c1: c2})
        e = exc_info.value
        assert e.value == "link specification ambiguous, multiple matching associations found " + "for source 'c1' and targets '['c2']'"
        with pytest.raises(CException) as exc_info:
            set_links({c1: c2}, role_name="c2")
        e = exc_info.value
        assert e.value == "link specification ambiguous, multiple matching associations found " + "for source 'c1' and targets '['c2']'"

    def test_link_and_get_links_by_association(self):
        a1 = self.m1.association(self.m2, name="a1", multiplicity="*")
        a2 = self.m1.association(self.m2, name="a2", multiplicity="*")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")

        links_a1 = set_links({c1: c2}, association=a1)
        links_a2 = set_links({c1: [c2, c3]}, association=a2)

        assert c1.get_linked() == [c2, c2, c3]
        assert c1.linked == [c2, c2, c3]

        assert c1.get_linked(association=a1) == [c2]
        assert c1.get_linked(association=a2) == [c2, c3]

        assert c1.get_links_for_association(a1) == links_a1
        assert c1.get_links_for_association(a2) == links_a2

    def test_link_with_inheritance_in_classifier_targets(self):
        sub_class = CMetaclass(superclasses=self.m2)
        a1 = self.m1.association(sub_class, name="a1", multiplicity="*")
        a2 = self.m1.association(self.m2, name="a2", multiplicity="*")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c_sub_1 = CClass(sub_class, "c_sub_1")
        c_sub_2 = CClass(sub_class, "c_sub_2")
        c_super_1 = CClass(self.m2, "c_super_1")
        c_super_2 = CClass(self.m2, "c_super_2")
        with pytest.raises(CException) as exc_info:
            # ambiguous, list works for both associations 
            set_links({c1: [c_sub_1, c_sub_2]})
        e = exc_info.value
        assert e.value == "link specification ambiguous, multiple matching associations found " + "for source 'c1' and targets '['c_sub_1', 'c_sub_2']'"
        set_links({c1: [c_sub_1, c_sub_2]}, association=a1)
        set_links({c1: [c_sub_1]}, association=a2)
        set_links({c2: [c_super_1, c_super_2]})

        assert c1.linked == [c_sub_1, c_sub_2, c_sub_1]
        assert c1.get_linked() == [c_sub_1, c_sub_2, c_sub_1]
        assert c2.get_linked() == [c_super_1, c_super_2]
        assert c1.get_linked(association=a1) == [c_sub_1, c_sub_2]
        assert c1.get_linked(association=a2) == [c_sub_1]
        assert c2.get_linked(association=a1) == []
        assert c2.get_linked(association=a2) == [c_super_1, c_super_2]

        # this mixed list is applicable only for a2
        set_links({c2: [c_sub_1, c_super_1]})
        assert c2.get_linked(association=a1) == []
        assert c2.get_linked(association=a2) == [c_sub_1, c_super_1]

    def test_link_with_inheritance_in_classifier_targets_using_role_names(self):
        sub_class = CMetaclass(superclasses=self.m2)
        a1 = self.m1.association(sub_class, "a1: * -> [sub_class] *")
        a2 = self.m1.association(self.m2, "a2: * -> [c2] *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c_sub_1 = CClass(sub_class, "c_sub_1")
        c_sub_2 = CClass(sub_class, "c_sub_2")
        c_super_1 = CClass(self.m2, "c_super_1")
        c_super_2 = CClass(self.m2, "c_super_2")
        set_links({c1: [c_sub_1, c_sub_2]}, role_name="sub_class")
        set_links({c1: [c_sub_1]}, role_name="c2")
        set_links({c2: [c_super_1, c_super_2]})

        assert c1.linked == [c_sub_1, c_sub_2, c_sub_1]
        assert c1.get_linked() == [c_sub_1, c_sub_2, c_sub_1]
        assert c2.get_linked() == [c_super_1, c_super_2]
        assert c1.get_linked(association=a1) == [c_sub_1, c_sub_2]
        assert c1.get_linked(association=a2) == [c_sub_1]
        assert c2.get_linked(association=a1) == []
        assert c2.get_linked(association=a2) == [c_super_1, c_super_2]
        assert c1.get_linked(role_name="sub_class") == [c_sub_1, c_sub_2]
        assert c1.get_linked(role_name="c2") == [c_sub_1]
        assert c2.get_linked(role_name="sub_class") == []
        assert c2.get_linked(role_name="c2") == [c_super_1, c_super_2]

    def test_link_delete_association(self):
        a = self.m1.association(self.m2, name="l", source_multiplicity="*", multiplicity="*")
        c1 = CClass(self.m1, "c2")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m1, "c4")
        set_links({c1: [c2, c3]})
        set_links({c4: [c2]})
        set_links({c1: [c2]})
        set_links({c4: [c3, c2]})
        a.delete()
        assert c1.linked == []
        assert c2.linked == []
        assert c3.linked == []
        assert c4.linked == []
        with pytest.raises(CException) as exc_info:
            set_links({c1: [c2, c3]})
        e = exc_info.value
        assert e.value == "matching association not found for source 'c2' and targets '['c2', 'c3']'"

    def test_link_delete_class_object(self):
        self.m1.association(self.m2, name="l", source_multiplicity="*", multiplicity="*")
        c1 = CClass(self.m1, "c2")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m1, "c4")
        add_links({c1: [c2, c3]})
        add_links({c4: [c3, c2]})

        c2.delete()
        assert c1.linked == [c3]
        assert c3.linked == [c1, c4]
        assert c4.linked == [c3]
        with pytest.raises(CException) as exc_info:
            add_links({c1: [c2]})
        e = exc_info.value
        assert e.value == "cannot link to deleted target"
        with pytest.raises(CException) as exc_info:
            add_links({c2: [c1]})
        e = exc_info.value
        assert e.value == "cannot link to deleted source"

    def test_one_to_one_link_multiplicity(self):
        a = self.m1.association(self.m2, name="l", multiplicity="1", source_multiplicity="1..1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m1, "c4")

        with pytest.raises(CException) as exc_info:
            set_links({c1: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '0': should be '1'"
        with pytest.raises(CException) as exc_info:
            set_links({c1: [c2, c3]})
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '2': should be '1'"

        with pytest.raises(CException) as exc_info:
            set_links({c2: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'c2' have wrong multiplicity '0': should be '1..1'"
        with pytest.raises(CException) as exc_info:
            set_links({c2: [c1, c4]})
        e = exc_info.value
        assert e.value == "links of object 'c2' have wrong multiplicity '2': should be '1..1'"

    def test_one_to_n_link_multiplicity(self):
        a = self.m1.association(self.m2, name="l", source_multiplicity="1", multiplicity="1..*")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m1, "c4")

        with pytest.raises(CException) as exc_info:
            set_links({c1: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '0': should be '1..*'"

        set_links({c1: [c2, c3]})
        assert c1.get_linked(association=a) == [c2, c3]

        with pytest.raises(CException) as exc_info:
            set_links({c2: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'c2' have wrong multiplicity '0': should be '1'"
        with pytest.raises(CException) as exc_info:
            set_links({c2: [c1, c4]})
        e = exc_info.value
        assert e.value == "links of object 'c2' have wrong multiplicity '2': should be '1'"

    def test_specific_n_to_n_link_multiplicity(self):
        a = self.m1.association(self.m2, name="l", source_multiplicity="1..2", multiplicity="2")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m1, "c4")
        c5 = CClass(self.m1, "c5")
        c6 = CClass(self.m2, "c6")

        with pytest.raises(CException) as exc_info:
            set_links({c1: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '0': should be '2'"
        with pytest.raises(CException) as exc_info:
            set_links({c1: [c2]}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '1': should be '2'"
        with pytest.raises(CException) as exc_info:
            set_links({c1: [c2, c3, c6]}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '3': should be '2'"

        set_links({c1: [c2, c3]})
        assert c1.get_linked(association=a) == [c2, c3]
        set_links({c2: [c1, c4], c1: c3, c4: c3})
        assert c2.get_linked(association=a) == [c1, c4]

        with pytest.raises(CException) as exc_info:
            set_links({c2: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'c2' have wrong multiplicity '0': should be '1..2'"
        with pytest.raises(CException) as exc_info:
            set_links({c2: [c1, c4, c5]})
        e = exc_info.value
        assert e.value == "links of object 'c2' have wrong multiplicity '3': should be '1..2'"

    def test_get_links(self):
        c1_sub_class = CMetaclass("C1Sub", superclasses=self.m1)
        c2_sub_class = CMetaclass("C2Sub", superclasses=self.m2)
        a1 = self.m1.association(self.m2, role_name="c2", source_role_name="c1",
                                 source_multiplicity="*", multiplicity="*")
        a2 = self.m1.association(self.m1, role_name="next", source_role_name="prior",
                                 source_multiplicity="1", multiplicity="0..1")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c1_sub_class = CClass(c1_sub_class, "c1_sub_class")
        c2_sub_class = CClass(c2_sub_class, "c2_sub_class")

        links1 = set_links({c1: c2})
        assert links1 == c1.links
        link1 = c1.links[0]
        link2 = [o for o in c1.links if o.association == a1][0]
        assert link1 == link2
        assert link1.association == a1
        assert link1.source == c1
        assert link1.target == c2

        links2 = set_links({c1: c2_sub_class})
        assert links2 == c1.links
        assert len(c1.links) == 1
        link1 = c1.links[0]
        link2 = [o for o in c1.links if o.association == a1][0]
        assert link1 == link2
        assert link1.association == a1
        assert link1.source == c1
        assert link1.target == c2_sub_class

        links3 = set_links({c1: c2})
        assert links3 == c1.links
        assert len(c1.links) == 1
        link1 = c1.links[0]
        link2 = [o for o in c1.links if o.association == a1][0]
        assert link1 == link2
        assert link1.association == a1
        assert link1.source == c1
        assert link1.target == c2

        links4 = set_links({c1: c1}, role_name="next")
        assert links3 + links4 == c1.links
        assert len(c1.links) == 2
        link1 = c1.links[1]
        link2 = [o for o in c1.links if o.association == a2][0]
        assert link1 == link2
        assert link1.association == a2
        assert link1.source == c1
        assert link1.target == c1

        links5 = set_links({c1: c1_sub_class}, role_name="next")
        assert links3 + links5 == c1.links
        assert len(c1.links) == 2
        link1 = c1.links[1]
        link2 = [o for o in c1.links if o.association == a2][0]
        assert link1 == link2
        assert link1.association == a2
        assert link1.source == c1
        assert link1.target == c1_sub_class

        set_links({c1: c1}, role_name="next")
        assert len(c1.links) == 2
        link1 = c1.links[1]
        link2 = [o for o in c1.links if o.association == a2][0]
        assert link1 == link2
        assert link1.association == a2
        assert link1.source == c1
        assert link1.target == c1

        set_links({c1: []}, association=a1)
        set_links({c1: []}, association=a2)
        assert len(c1.links) == 0

        set_links({c1_sub_class: c1}, role_name="next")
        assert len(c1_sub_class.links) == 1
        link1 = c1_sub_class.links[0]
        link2 = [o for o in c1_sub_class.links if o.association == a2][0]
        assert link1 == link2
        assert link1.association == a2
        assert link1.source == c1_sub_class
        assert link1.target == c1

    def test_get_links_self_link(self):
        a1 = self.m1.association(self.m1, role_name="to", source_role_name="from",
                                 source_multiplicity="*", multiplicity="*")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m1, "c3")
        c4 = CClass(self.m1, "c4")

        set_links({c1: [c2, c3, c1]})
        add_links({c4: [c1, c3]})
        link1 = c1.links[0]
        link2 = [o for o in c1.links if o.association == a1][0]
        link3 = [o for o in c1.links if o.role_name == "to"][0]
        link4 = [o for o in c1.links if o.source_role_name == "from"][0]
        assert link1 == link2
        assert link1 == link3
        assert link1 == link4
        assert link1.association == a1
        assert link1.source == c1
        assert link1.target == c2

        assert len(c1.links) == 4
        assert len(c2.links) == 1
        assert len(c3.links) == 2
        assert len(c4.links) == 2

    def test_add_links(self):
        self.m1.association(self.m2, "1 -> [role1] *")
        self.m1.association(self.m2, "* -> [role2] *")
        self.m1.association(self.m2, "1 -> [role3] 1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")

        add_links({c1: c2}, role_name="role1")
        assert c1.get_linked(role_name="role1") == [c2]
        add_links({c1: [c3, c4]}, role_name="role1")
        c1.get_linked(role_name="role1")
        assert c1.get_linked(role_name="role1") == [c2, c3, c4]

        c1.add_links(c2, role_name="role2")
        assert c1.get_linked(role_name="role2") == [c2]
        c1.add_links([c3, c4], role_name="role2")
        c1.get_linked(role_name="role2")
        assert c1.get_linked(role_name="role2") == [c2, c3, c4]

        c1.add_links(c2, role_name="role3")
        assert c1.get_linked(role_name="role3") == [c2]
        with pytest.raises(CException) as exc_info:
            add_links({c1: [c3, c4]}, role_name="role3")
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '3': should be '1'"

        with pytest.raises(CException) as exc_info:
            add_links({c1: [c3]}, role_name="role3")
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '2': should be '1'"
        assert c1.get_linked(role_name="role3") == [c2]

    def test_link_source_multiplicity(self):
        self.m1.association(self.m2, "[sourceRole1] 1 -> [role1] *")
        self.m1.association(self.m2, "[sourceRole2] 1 -> [role2] 1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m2, "c3")
        CClass(self.m2, "c4")
        CClass(self.m2, "c5")

        set_links({c1: c3}, role_name="role1")
        set_links({c2: c3}, role_name="role1")

        assert c3.get_linked(role_name="sourceRole1") == [c2]

    def test_add_links_source_multiplicity(self):
        self.m1.association(self.m2, "[sourceRole1] 1 -> [role1] *")
        self.m1.association(self.m2, "[sourceRole2] 1 -> [role2] 1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")
        c5 = CClass(self.m2, "c5")
        c6 = CClass(self.m2, "c6")

        add_links({c2: c3}, role_name="role1")
        add_links({c2: c4}, role_name="role1")

        assert c3.get_linked(role_name="sourceRole1") == [c2]

        add_links({c2: c5}, role_name="role1")
        assert c2.get_linked(role_name="role1") == [c3, c4, c5]

        with pytest.raises(CException) as exc_info:
            add_links({c1: [c4]}, role_name="role1")
        e = exc_info.value
        assert e.value == "links of object 'c4' have wrong multiplicity '2': should be '1'"

        add_links({c1: c6}, role_name="role2")
        assert c1.get_linked(role_name="role2") == [c6]
        with pytest.raises(CException) as exc_info:
            add_links({c1: [c3, c4]}, role_name="role2")
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '3': should be '1'"
        assert c1.get_linked(role_name="role2") == [c6]

    def test_set_links_multiple_links_in_definition(self):
        self.m1.association(self.m2, "[sourceRole1] * -> [role1] *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m1, "c3")
        c4 = CClass(self.m2, "c4")
        c5 = CClass(self.m2, "c5")

        set_links({c1: c4, c2: [c4], c5: [c1, c2, c3]})
        assert c1.get_linked() == [c4, c5]
        assert c2.get_linked() == [c4, c5]
        assert c3.get_linked() == [c5]
        assert c4.get_linked() == [c1, c2]
        assert c5.get_linked() == [c1, c2, c3]

    def test_add_links_multiple_links_in_definition(self):
        self.m1.association(self.m2, "[sourceRole1] * -> [role1] *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m1, "c3")
        c4 = CClass(self.m2, "c4")
        c5 = CClass(self.m2, "c5")

        add_links({c1: c4, c2: [c4], c5: [c1, c2, c3]})
        assert c1.get_linked() == [c4, c5]
        assert c2.get_linked() == [c4, c5]
        assert c3.get_linked() == [c5]
        assert c4.get_linked() == [c1, c2]
        assert c5.get_linked() == [c1, c2, c3]

    def test_wrong_types_delete_links(self):
        self.m1.association(self.m2, name="l", multiplicity="1")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            delete_links(c1)
        e = exc_info.value
        assert e.value == "link definitions should be of the form " + "{<link source 1>: <link target(s) 1>, ..., <link source n>: <link target(s) n>}"
        with pytest.raises(CException) as exc_info:
            delete_links({c1: self.mcl})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            delete_links({c1: [c2, self.mcl]})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            delete_links({c1: [c2, None]})
        e = exc_info.value
        assert e.value == "link target 'None' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            delete_links({self.mcl: c2})
        e = exc_info.value
        assert e.value == "link source 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            delete_links({None: c2})
        e = exc_info.value
        assert e.value == "link should not contain an empty source"

    def test_delete_one_to_one_link(self):
        self.m1.association(self.m2, "l: 1 -> [c2] 0..1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m1, "c3")
        c4 = CClass(self.m2, "c4")

        links = add_links({c1: c2, c3: c4})
        c1.delete_links(c2)
        assert c1.linked == []
        assert c2.linked == []
        assert c3.linked == [c4]
        assert c4.linked == [c3]
        assert c1.links == []
        assert c2.links == []
        assert c3.links == [links[1]]
        assert c4.links == [links[1]]
        delete_links({c3: c4})
        assert c1.linked == []
        assert c2.linked == []
        assert c3.linked == []
        assert c4.linked == []
        assert c1.links == []
        assert c2.links == []
        assert c3.links == []
        assert c4.links == []

    def test_delete_one_to_one_link_wrong_multiplicity(self):
        self.m1.association(self.m2, "l: 1 -> [c2] 1")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        add_links({c1: c2})
        with pytest.raises(CException) as exc_info:
            c1.delete_links(c2)
        e = exc_info.value
        assert e.value == "links of object 'c1' have wrong multiplicity '0': should be '1'"
        assert c1.linked == [c2]
        assert c2.linked == [c1]

    def test_delete_one_to_n_links(self):
        self.m1.association(self.m2, "l: 0..1 -> *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")
        c5 = CClass(self.m2, "c5")

        add_links({c1: [c3, c4], c2: [c5]})
        c4.delete_links([c1])
        assert c1.linked == [c3]
        assert c2.linked == [c5]
        assert c3.linked == [c1]
        assert c4.linked == []
        assert c5.linked == [c2]

        c4.add_links([c2])
        assert c2.linked == [c5, c4]
        delete_links({c1: c3, c2: c2.linked})
        assert c1.linked == []
        assert c2.linked == []
        assert c3.linked == []
        assert c4.linked == []
        assert c5.linked == []

    def test_delete_one_to_n_links_wrong_multiplicity(self):
        self.m1.association(self.m2, "l: 1 -> *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")
        c5 = CClass(self.m2, "c5")

        add_links({c1: [c3, c4], c2: [c5]})

        with pytest.raises(CException) as exc_info:
            c4.delete_links([c1])
        e = exc_info.value
        assert e.value == "links of object 'c4' have wrong multiplicity '0': should be '1'"

    def test_delete_n_to_n_links(self):
        self.m1.association(self.m2, "l: * -> *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")
        c5 = CClass(self.m2, "c5")
        c6 = CClass(self.m2, "c6")

        add_links({c1: [c3, c4], c2: [c4, c5]})
        c4.delete_links([c1, c2])
        assert c1.linked == [c3]
        assert c2.linked == [c5]
        assert c3.linked == [c1]
        assert c4.linked == []
        assert c5.linked == [c2]

        add_links({c4: [c1, c2], c6: [c2, c1]})
        delete_links({c1: c6, c2: [c4, c5]})
        assert c1.linked == [c3, c4]
        assert c2.linked == [c6]
        assert c3.linked == [c1]
        assert c4.linked == [c1]
        assert c5.linked == []
        assert c6.linked == [c2]

    def test_delete_link_no_matching_link(self):
        a = self.m1.association(self.m2, "l: 0..1 -> *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")
        c5 = CClass(self.m2, "c5")

        add_links({c1: [c3, c4], c2: [c5]}, association=a)

        with pytest.raises(CException) as exc_info:
            delete_links({c1: c5})
        e = exc_info.value
        assert e.value == "no link found for 'c1 -> c5' in delete links"

        b = self.m1.association(self.m2, "l: 0..1 -> *")
        with pytest.raises(CException) as exc_info:
            delete_links({c1: c5})
        e = exc_info.value
        assert e.value == "no link found for 'c1 -> c5' in delete links"

        with pytest.raises(CException) as exc_info:
            c4.delete_links([c1], association=b)
        e = exc_info.value
        assert e.value == "no link found for 'c4 -> c1' in delete links for given association"

    def test_delete_link_select_by_association(self):
        a = self.m1.association(self.m2, "a: * -> *")
        b = self.m1.association(self.m2, "b: * -> *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")

        add_links({c1: [c3], c2: [c3, c4]}, association=b)
        delete_links({c2: c3})
        assert c1.linked == [c3]
        assert c2.linked == [c4]
        assert c3.linked == [c1]
        assert c4.linked == [c2]
        add_links({c1: [c3], c2: [c3, c4]}, association=a)

        with pytest.raises(CException) as exc_info:
            delete_links({c1: c3})
        e = exc_info.value
        assert e.value == "link definition in delete links ambiguous for link 'c1->c3': found multiple matches"

        delete_links({c1: c3, c2: c4}, association=b)
        assert c1.linked == [c3]
        assert c2.linked == [c3, c4]
        assert c3.linked == [c1, c2]
        assert c4.linked == [c2]
        for o in [c1, c2, c3, c4]:
            for lo in o.links:
                assert lo.association == a

        c1.add_links(c3, association=b)
        with pytest.raises(CException) as exc_info:
            c1.delete_links(c3)
        e = exc_info.value
        assert e.value == "link definition in delete links ambiguous for link 'c1->c3': found multiple matches"

        assert c1.linked == [c3, c3]
        assert c2.linked == [c3, c4]
        assert c3.linked == [c1, c2, c1]
        assert c4.linked == [c2]

        c1.delete_links(c3, association=a)
        assert c1.linked == [c3]
        assert c2.linked == [c3, c4]
        assert c3.linked == [c2, c1]
        assert c4.linked == [c2]

    def test_delete_link_select_by_role_name(self):
        a = self.m1.association(self.m2, "a: [sourceA] * -> [targetA] *")
        self.m1.association(self.m2, "b: [sourceB] * -> [targetB] *")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m1, "c2")
        c3 = CClass(self.m2, "c3")
        c4 = CClass(self.m2, "c4")

        add_links({c1: [c3], c2: [c3, c4]}, role_name="targetB")
        delete_links({c2: c3})
        assert c1.linked == [c3]
        assert c2.linked == [c4]
        assert c3.linked == [c1]
        assert c4.linked == [c2]
        add_links({c1: [c3], c2: [c3, c4]}, role_name="targetA")

        delete_links({c1: c3, c2: c4}, role_name="targetB")
        assert c1.linked == [c3]
        assert c2.linked == [c3, c4]
        assert c3.linked == [c1, c2]
        assert c4.linked == [c2]
        for o in [c1, c2, c3, c4]:
            for lo in o.links:
                assert lo.association == a

        add_links({c1: [c3], c2: [c3, c4]}, role_name="targetB")
        c3.delete_links([c1, c2], role_name="sourceB")
        delete_links({c4: c2}, role_name="sourceB")

        assert c1.linked == [c3]
        assert c2.linked == [c3, c4]
        assert c3.linked == [c1, c2]
        assert c4.linked == [c2]
        for o in [c1, c2, c3, c4]:
            for lo in o.links:
                assert lo.association == a

    def test_delete_links_wrong_role_name(self):
        self.m1.association(self.m2, "a: [sourceA] * -> [targetA] *")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c1.add_links(c2)
        with pytest.raises(CException) as exc_info:
            c1.delete_links(c2, role_name="target")
        e = exc_info.value
        assert e.value == "no link found for 'c1 -> c2' in delete links for given role name 'target'"

    def test_delete_links_wrong_association(self):
        self.m1.association(self.m2, "a: [sourceA] * -> [targetA] *")
        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c1.add_links(c2)
        with pytest.raises(CException) as exc_info:
            c1.delete_links(c2, association=c1)
        e = exc_info.value
        assert e.value == "'c1' is not a association"
        b = self.m1.association(self.m2, "b: [sourceB] * -> [targetB] *")
        with pytest.raises(CException) as exc_info:
            c1.delete_links(c2, association=b)
        e = exc_info.value
        assert e.value == "no link found for 'c1 -> c2' in delete links for given association"
        with pytest.raises(CException) as exc_info:
            c1.delete_links(c2, association=b, role_name="x")
        e = exc_info.value
        assert e.value == "no link found for 'c1 -> c2' in delete links for given role name 'x' and for given association"

    def test_link_label_none_default(self):
        a1 = self.m1.association(self.m2, name="a1", multiplicity="*")
        a2 = self.m1.association(self.m2, multiplicity="*")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")

        l1 = set_links({c1: c2}, association=a1)
        l2 = set_links({c1: [c2, c3]}, association=a2)

        assert l1[0].label == None
        assert l2[0].label == None
        assert l2[1].label == None

    def test_link_label_get_set(self):
        a1 = self.m1.association(self.m2, name="a1", multiplicity="*")
        a2 = self.m1.association(self.m2, multiplicity="*")

        c1 = CClass(self.m1, "c1")
        c2 = CClass(self.m2, "c2")
        c3 = CClass(self.m2, "c3")

        l1 = set_links({c1: c2}, association=a1, label="l1")
        l2 = add_links({c1: [c2, c3]}, association=a2, label="l2")

        assert l1[0].label == "l1"
        assert l2[0].label == "l2"
        assert l2[1].label == "l2"

        l2[1].label = "l3"
        assert l2[0].label == "l2"
        assert l2[1].label == "l3"

        l3 = c1.add_links(c3, association=a1, label="x1")
        assert l3[0].label == "x1"

    def test_add_links_with_inherited_common_classifiers(self):
        super_a = CMetaclass("SuperA")
        super_b = CMetaclass("SuperB")
        super_a.association(super_b, "[a] 1 -> [b] *")

        sub_b1 = CMetaclass("SubB1", superclasses=[super_b])
        sub_b2 = CMetaclass("SubB2", superclasses=[super_b])
        sub_a = CMetaclass("SubA", superclasses=[super_a])

        cl_a = CClass(sub_a, "a")
        cl_b1 = CClass(sub_b1, "b1")
        cl_b2 = CClass(sub_b2, "b2")

        add_links({cl_a: [cl_b1, cl_b2]}, role_name="b")
        assert set(cl_a.get_linked(role_name="b")) == {cl_b1, cl_b2}


