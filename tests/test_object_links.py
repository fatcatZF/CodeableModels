
import pytest
from codeable_models import CMetaclass, CClass, CObject, CException, set_links, add_links, delete_links


class TestObjectLinks:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.c1 = CClass(self.mcl, "C1")
        self.c2 = CClass(self.mcl, "C2")

    def test_link_methods_wrong_keyword_args(self):
        o1 = CObject(self.c1, "o1")
        with pytest.raises(CException) as exc_info:
            add_links({o1: o1}, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            o1.add_links(o1, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            set_links({o1: o1}, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            delete_links({o1: o1}, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            o1.delete_links(o1, associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            o1.get_linked(associationX=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            delete_links({o1: o1}, stereotype_instances=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"
        with pytest.raises(CException) as exc_info:
            delete_links({o1: o1}, tagged_values=None)
        e = exc_info.value
        assert e.value == "unknown keywords argument"

    def test_set_one_to_one_link(self):
        self.c1.association(self.c2, name="l", multiplicity="1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")

        assert o1.linked == []

        set_links({o1: o2})
        assert o1.linked == [o2]
        assert o2.linked == [o1]

        set_links({o1: o3})
        assert o1.linked == [o3]
        assert o2.linked == []
        assert o3.linked == [o1]

    def test_add_one_to_one_link(self):
        self.c1.association(self.c2, "l: 1 -> [target] 0..1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")

        assert o1.linked == []

        add_links({o1: o3})
        assert o1.linked == [o3]
        assert o3.linked == [o1]

        set_links({o1: []}, role_name="target")
        assert o1.linked == []

        o1.add_links(o2)
        assert o1.linked == [o2]
        assert o2.linked == [o1]

        with pytest.raises(CException) as exc_info:
            add_links({o1: o3})
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '2': should be '0..1'"
        assert o1.linked == [o2]
        assert o2.linked == [o1]
        assert o3.linked == []

    def test_wrong_types_add_links(self):
        self.c1.association(self.c2, name="l", multiplicity="1")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        with pytest.raises(CException) as exc_info:
            add_links({o1: self.mcl})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            o1.add_links([o2, self.mcl])
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"

    def test_wrong_types_set_links(self):
        self.c1.association(self.c2, name="l", multiplicity="1")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        with pytest.raises(CException) as exc_info:
            set_links({o1: self.mcl})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            set_links({o1: [o2, self.mcl]})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            set_links({o1: [o2, None]})
        e = exc_info.value
        assert e.value == "link target 'None' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            set_links({self.mcl: o2})
        e = exc_info.value
        assert e.value == "link source 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            set_links({None: o2})
        e = exc_info.value
        assert e.value == "link should not contain an empty source"

    def test_wrong_format_set_links(self):
        self.c1.association(self.c2, name="l", multiplicity="1")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            set_links([o1, o2])
        e = exc_info.value
        assert e.value == "link definitions should be of the form {<link source 1>: " + "<link target(s) 1>, ..., <link source n>: <link target(s) n>}"

    def test_remove_one_to_one_link(self):
        a = self.c1.association(self.c2, "l: 1 -> [c2] 0..1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c1, "o3")
        o4 = CObject(self.c2, "o4")

        links = set_links({o1: o2, o3: o4})
        assert o1.linked == [o2]
        assert o2.linked == [o1]
        assert o3.linked == [o4]
        assert o4.linked == [o3]
        assert o1.links == [links[0]]
        assert o2.links == [links[0]]
        assert o3.links == [links[1]]
        assert o4.links == [links[1]]

        with pytest.raises(CException) as exc_info:
            links = set_links({o1: None})
        e = exc_info.value
        assert e.value == "matching association not found for source 'o1' and targets '[]'"

        set_links({o1: None}, association=a)
        assert o1.linked == []
        assert o2.linked == []
        assert o3.linked == [o4]
        assert o4.linked == [o3]
        assert o1.links == []
        assert o2.links == []
        assert o3.links == [links[1]]
        assert o4.links == [links[1]]

    def test_set_links_one_to_n_link(self):
        self.c1.association(self.c2, name="l")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")

        set_links({o1: [o2, o3]})
        assert o1.linked == [o2, o3]
        assert o2.linked == [o1]
        assert o3.linked == [o1]
        set_links({o1: o2})
        assert o1.linked == [o2]
        assert o2.linked == [o1]
        assert o3.linked == []
        set_links({o3: o1, o2: o1})
        assert o1.linked == [o3, o2]
        assert o2.linked == [o1]
        assert o3.linked == [o1]

    def test_add_links_one_to_n_link(self):
        self.c1.association(self.c2, name="l")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")
        o5 = CObject(self.c2, "o5")
        o6 = CObject(self.c2, "o6")

        add_links({o1: [o2, o3]})
        assert o1.linked == [o2, o3]
        assert o2.linked == [o1]
        assert o3.linked == [o1]
        add_links({o1: o4})
        assert o1.linked == [o2, o3, o4]
        assert o2.linked == [o1]
        assert o3.linked == [o1]
        assert o4.linked == [o1]
        o1.add_links([o5, o6])
        assert o1.linked == [o2, o3, o4, o5, o6]
        assert o2.linked == [o1]
        assert o3.linked == [o1]
        assert o4.linked == [o1]
        assert o5.linked == [o1]
        assert o6.linked == [o1]

    def test_remove_one_to_n_link(self):
        a = self.c1.association(self.c2, name="l", multiplicity="*")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        set_links({o1: [o2, o3]})
        set_links({o1: o2})
        assert o1.linked == [o2]
        assert o2.linked == [o1]
        assert o3.linked == []
        with pytest.raises(CException) as exc_info:
            set_links({o1: []})
        e = exc_info.value
        assert e.value == "matching association not found for source 'o1' and targets '[]'"
        set_links({o1: []}, association=a)
        assert o1.linked == []
        assert o2.linked == []
        assert o3.linked == []

    def test_n_to_n_link(self):
        a = self.c1.association(self.c2, name="l", source_multiplicity="*")
        o1a = CObject(self.c1, "o1a")
        o1b = CObject(self.c1, "o1b")
        o1c = CObject(self.c1, "o1c")
        o2a = CObject(self.c2, "o2a")
        o2b = CObject(self.c2, "o2b")

        set_links({o1a: [o2a, o2b], o1b: [o2a], o1c: [o2b]})

        assert o1a.linked == [o2a, o2b]
        assert o1b.linked == [o2a]
        assert o1c.linked == [o2b]
        assert o2a.linked == [o1a, o1b]
        assert o2b.linked == [o1a, o1c]

        set_links({o2a: [o1a, o1b]})
        with pytest.raises(CException) as exc_info:
            set_links({o2b: []})
        e = exc_info.value
        assert e.value == "matching association not found for source 'o2b' and targets '[]'"
        set_links({o2b: []}, association=a)

        assert o1a.linked == [o2a]
        assert o1b.linked == [o2a]
        assert o1c.linked == []
        assert o2a.linked == [o1a, o1b]
        assert o2b.linked == []

    def test_remove_n_to_n_link(self):
        self.c1.association(self.c2, name="l", source_multiplicity="*", multiplicity="*")
        o1 = CObject(self.c1, "o2")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c1, "o4")
        set_links({o1: [o2, o3], o4: o2})
        set_links({o1: o2, o4: [o3, o2]})
        assert o1.linked == [o2]
        assert o2.linked == [o1, o4]
        assert o3.linked == [o4]
        assert o4.linked == [o3, o2]

    def test_n_to_n_set_self_link(self):
        self.c1.association(self.c1, name="a", source_multiplicity="*", multiplicity="*", source_role_name="super",
                            role_name="sub")

        top = CObject(self.c1, "Top")
        mid1 = CObject(self.c1, "Mid1")
        mid2 = CObject(self.c1, "Mid2")
        mid3 = CObject(self.c1, "Mid3")
        bottom1 = CObject(self.c1, "Bottom1")
        bottom2 = CObject(self.c1, "Bottom2")

        set_links({top: [mid1, mid2, mid3]}, role_name="sub")
        add_links({mid1: [bottom1, bottom2]}, role_name="sub")

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
        self.c1.association(self.c1, name="a", source_multiplicity="*", multiplicity="*", source_role_name="super",
                            role_name="sub")

        top = CObject(self.c1, "Top")
        mid1 = CObject(self.c1, "Mid1")
        mid2 = CObject(self.c1, "Mid2")
        mid3 = CObject(self.c1, "Mid3")
        bottom1 = CObject(self.c1, "Bottom1")
        bottom2 = CObject(self.c1, "Bottom2")

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
        self.c1.association(self.c2, name="l", multiplicity="*")
        cl = CClass(self.mcl, "CLX")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(cl, "o3")
        with pytest.raises(CException) as exc_info:
            set_links({o1: [o2, o3]})
        e = exc_info.value
        assert e.value == "object 'o3' has an incompatible classifier"
        with pytest.raises(CException) as exc_info:
            set_links({o1: o3})
        e = exc_info.value
        assert e.value == "matching association not found for source 'o1' and targets '['o3']'"

    def test_duplicate_assignment(self):
        a = self.c1.association(self.c2, "l: *->*")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        with pytest.raises(CException) as exc_info:
            set_links({o1: [o2, o2]})
        e = exc_info.value
        assert e.value == "trying to link the same link twice 'o1 -> o2'' twice for the same association"
        assert o1.get_linked() == []
        assert o2.get_linked() == []
        b = self.c1.association(self.c2, "l: *->*")
        o1.add_links(o2, association=a)
        o1.add_links(o2, association=b)
        assert o1.get_linked() == [o2, o2]
        assert o2.get_linked() == [o1, o1]

    def test_non_existing_role_name(self):
        self.c1.association(self.c1, role_name="next", source_role_name="prior",
                            source_multiplicity="1", multiplicity="1")
        o1 = CObject(self.c1, "o1")
        with pytest.raises(CException) as exc_info:
            set_links({o1: o1}, role_name="target")
        e = exc_info.value
        assert e.value == "matching association not found for source 'o1' and targets '['o1']'"

    def test_link_association_ambiguous(self):
        self.c1.association(self.c2, name="a1", role_name="c2", multiplicity="*")
        self.c1.association(self.c2, name="a2", role_name="c2", multiplicity="*")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        with pytest.raises(CException) as exc_info:
            set_links({o1: o2})
        e = exc_info.value
        assert e.value == "link specification ambiguous, multiple matching associations " + "found for source 'o1' and targets '['o2']'"
        with pytest.raises(CException) as exc_info:
            set_links({o1: o2}, role_name="c2")
        e = exc_info.value
        assert e.value == "link specification ambiguous, multiple matching associations " + "found for source 'o1' and targets '['o2']'"

    def test_link_and_get_links_by_association(self):
        a1 = self.c1.association(self.c2, name="a1", multiplicity="*")
        a2 = self.c1.association(self.c2, name="a2", multiplicity="*")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")

        links_a1 = set_links({o1: o2}, association=a1)
        links_a2 = set_links({o1: [o2, o3]}, association=a2)

        assert o1.get_linked() == [o2, o2, o3]
        assert o1.linked == [o2, o2, o3]

        assert o1.get_linked(association=a1) == [o2]
        assert o1.get_linked(association=a2) == [o2, o3]

        assert o1.get_links_for_association(a1) == links_a1
        assert o1.get_links_for_association(a2) == links_a2

    def test_link_with_inheritance_in_classifier_targets(self):
        sub_class = CClass(self.mcl, superclasses=self.c2)
        a1 = self.c1.association(sub_class, name="a1", multiplicity="*")
        a2 = self.c1.association(self.c2, name="a2", multiplicity="*")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o_sub_1 = CObject(sub_class, "o_sub_1")
        o_sub_2 = CObject(sub_class, "o_sub_2")
        o_super_1 = CObject(self.c2, "o_super_1")
        o_super_2 = CObject(self.c2, "o_super_2")
        with pytest.raises(CException) as exc_info:
            # ambiguous, list works for both associations 
            set_links({o1: [o_sub_1, o_sub_2]})
        e = exc_info.value
        assert e.value == "link specification ambiguous, multiple matching associations " + "found for source 'o1' and targets '['o_sub_1', 'o_sub_2']'"
        set_links({o1: [o_sub_1, o_sub_2]}, association=a1)
        set_links({o1: [o_sub_1]}, association=a2)
        set_links({o2: [o_super_1, o_super_2]})

        assert o1.linked == [o_sub_1, o_sub_2, o_sub_1]
        assert o1.get_linked() == [o_sub_1, o_sub_2, o_sub_1]
        assert o2.get_linked() == [o_super_1, o_super_2]
        assert o1.get_linked(association=a1) == [o_sub_1, o_sub_2]
        assert o1.get_linked(association=a2) == [o_sub_1]
        assert o2.get_linked(association=a1) == []
        assert o2.get_linked(association=a2) == [o_super_1, o_super_2]

        # this mixed list is applicable only for a2
        set_links({o2: [o_sub_1, o_super_1]})
        assert o2.get_linked(association=a1) == []
        assert o2.get_linked(association=a2) == [o_sub_1, o_super_1]

    def test_link_with_inheritance_in_classifier_targets_using_role_names(self):
        sub_class = CClass(self.mcl, superclasses=self.c2)
        a1 = self.c1.association(sub_class, "a1: * -> [sub_class] *")
        a2 = self.c1.association(self.c2, "a2: * -> [c2] *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o_sub_1 = CObject(sub_class, "o_sub_1")
        o_sub_2 = CObject(sub_class, "o_sub_2")
        o_super_1 = CObject(self.c2, "o_super_1")
        o_super_2 = CObject(self.c2, "o_super_2")
        set_links({o1: [o_sub_1, o_sub_2]}, role_name="sub_class")
        set_links({o1: [o_sub_1]}, role_name="c2")
        set_links({o2: [o_super_1, o_super_2]})

        assert o1.linked == [o_sub_1, o_sub_2, o_sub_1]
        assert o1.get_linked() == [o_sub_1, o_sub_2, o_sub_1]
        assert o2.get_linked() == [o_super_1, o_super_2]
        assert o1.get_linked(association=a1) == [o_sub_1, o_sub_2]
        assert o1.get_linked(association=a2) == [o_sub_1]
        assert o2.get_linked(association=a1) == []
        assert o2.get_linked(association=a2) == [o_super_1, o_super_2]
        assert o1.get_linked(role_name="sub_class") == [o_sub_1, o_sub_2]
        assert o1.get_linked(role_name="c2") == [o_sub_1]
        assert o2.get_linked(role_name="sub_class") == []
        assert o2.get_linked(role_name="c2") == [o_super_1, o_super_2]

    def test_link_delete_association(self):
        a = self.c1.association(self.c2, name="l", source_multiplicity="*", multiplicity="*")
        o1 = CObject(self.c1, "o2")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c1, "o4")
        set_links({o1: [o2, o3]})
        set_links({o4: [o2]})
        set_links({o1: [o2]})
        set_links({o4: [o3, o2]})
        a.delete()
        assert o1.linked == []
        assert o2.linked == []
        assert o3.linked == []
        assert o4.linked == []
        with pytest.raises(CException) as exc_info:
            set_links({o1: [o2, o3]})
        e = exc_info.value
        assert e.value == "matching association not found for source 'o2' and targets '['o2', 'o3']'"

    def test_link_delete_object(self):
        self.c1.association(self.c2, name="l", source_multiplicity="*", multiplicity="*")
        o1 = CObject(self.c1, "o2")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c1, "o4")
        add_links({o1: [o2, o3]})
        add_links({o4: [o3, o2]})
        o2.delete()
        assert o1.linked == [o3]
        assert o3.linked == [o1, o4]
        assert o4.linked == [o3]
        with pytest.raises(CException) as exc_info:
            add_links({o1: [o2]})
        e = exc_info.value
        assert e.value == "cannot link to deleted target"
        with pytest.raises(CException) as exc_info:
            add_links({o2: [o1]})
        e = exc_info.value
        assert e.value == "cannot link to deleted source"

    def test_one_to_one_link_multiplicity(self):
        a = self.c1.association(self.c2, name="l", multiplicity="1", source_multiplicity="1..1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c1, "o4")

        with pytest.raises(CException) as exc_info:
            set_links({o1: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '0': should be '1'"
        with pytest.raises(CException) as exc_info:
            set_links({o1: [o2, o3]})
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '2': should be '1'"

        with pytest.raises(CException) as exc_info:
            set_links({o2: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'o2' have wrong multiplicity '0': should be '1..1'"
        with pytest.raises(CException) as exc_info:
            set_links({o2: [o1, o4]})
        e = exc_info.value
        assert e.value == "links of object 'o2' have wrong multiplicity '2': should be '1..1'"

    def test_one_to_n_link_multiplicity(self):
        a = self.c1.association(self.c2, name="l", source_multiplicity="1", multiplicity="1..*")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c1, "o4")

        with pytest.raises(CException) as exc_info:
            set_links({o1: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '0': should be '1..*'"

        set_links({o1: [o2, o3]})
        assert o1.get_linked(association=a) == [o2, o3]

        with pytest.raises(CException) as exc_info:
            set_links({o2: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'o2' have wrong multiplicity '0': should be '1'"
        with pytest.raises(CException) as exc_info:
            set_links({o2: [o1, o4]})
        e = exc_info.value
        assert e.value == "links of object 'o2' have wrong multiplicity '2': should be '1'"

    def test_specific_n_to_n_link_multiplicity(self):
        a = self.c1.association(self.c2, name="l", source_multiplicity="1..2", multiplicity="2")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c1, "o4")
        o5 = CObject(self.c1, "o5")
        o6 = CObject(self.c2, "o6")

        with pytest.raises(CException) as exc_info:
            set_links({o1: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '0': should be '2'"
        with pytest.raises(CException) as exc_info:
            set_links({o1: [o2]}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '1': should be '2'"
        with pytest.raises(CException) as exc_info:
            set_links({o1: [o2, o3, o6]}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '3': should be '2'"

        set_links({o1: [o2, o3]})
        assert o1.get_linked(association=a) == [o2, o3]
        set_links({o2: [o1, o4], o1: o3, o4: o3})
        assert o2.get_linked(association=a) == [o1, o4]

        with pytest.raises(CException) as exc_info:
            set_links({o2: []}, association=a)
        e = exc_info.value
        assert e.value == "links of object 'o2' have wrong multiplicity '0': should be '1..2'"
        with pytest.raises(CException) as exc_info:
            set_links({o2: [o1, o4, o5]})
        e = exc_info.value
        assert e.value == "links of object 'o2' have wrong multiplicity '3': should be '1..2'"

    def test_get_links(self):
        c1_sub_class = CClass(self.mcl, "C1Sub", superclasses=self.c1)
        c2_sub_class = CClass(self.mcl, "C2Sub", superclasses=self.c2)
        a1 = self.c1.association(self.c2, role_name="c2", source_role_name="c1",
                                 source_multiplicity="*", multiplicity="*")
        a2 = self.c1.association(self.c1, role_name="next", source_role_name="prior",
                                 source_multiplicity="1", multiplicity="0..1")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o1_sub = CObject(c1_sub_class, "o1_sub")
        o2_sub = CObject(c2_sub_class, "o2_sub")

        links1 = set_links({o1: o2})
        assert links1 == o1.links
        link1 = o1.links[0]
        link2 = [o for o in o1.links if o.association == a1][0]
        assert link1 == link2
        assert link1.association == a1
        assert link1.source == o1
        assert link1.target == o2

        links2 = set_links({o1: o2_sub})
        assert links2 == o1.links
        assert len(o1.links) == 1
        link1 = o1.links[0]
        link2 = [o for o in o1.links if o.association == a1][0]
        assert link1 == link2
        assert link1.association == a1
        assert link1.source == o1
        assert link1.target == o2_sub

        links3 = set_links({o1: o2})
        assert links3 == o1.links
        assert len(o1.links) == 1
        link1 = o1.links[0]
        link2 = [o for o in o1.links if o.association == a1][0]
        assert link1 == link2
        assert link1.association == a1
        assert link1.source == o1
        assert link1.target == o2

        links4 = set_links({o1: o1}, role_name="next")
        assert links3 + links4 == o1.links
        assert len(o1.links) == 2
        link1 = o1.links[1]
        link2 = [o for o in o1.links if o.association == a2][0]
        assert link1 == link2
        assert link1.association == a2
        assert link1.source == o1
        assert link1.target == o1

        links5 = set_links({o1: o1_sub}, role_name="next")
        assert links3 + links5 == o1.links
        assert len(o1.links) == 2
        link1 = o1.links[1]
        link2 = [o for o in o1.links if o.association == a2][0]
        assert link1 == link2
        assert link1.association == a2
        assert link1.source == o1
        assert link1.target == o1_sub

        set_links({o1: o1}, role_name="next")
        assert len(o1.links) == 2
        link1 = o1.links[1]
        link2 = [o for o in o1.links if o.association == a2][0]
        assert link1 == link2
        assert link1.association == a2
        assert link1.source == o1
        assert link1.target == o1

        set_links({o1: []}, association=a1)
        set_links({o1: []}, association=a2)
        assert len(o1.links) == 0

        set_links({o1_sub: o1}, role_name="next")
        assert len(o1_sub.links) == 1
        link1 = o1_sub.links[0]
        link2 = [o for o in o1_sub.links if o.association == a2][0]
        assert link1 == link2
        assert link1.association == a2
        assert link1.source == o1_sub
        assert link1.target == o1

    def test_get_links_self_link(self):
        a1 = self.c1.association(self.c1, role_name="to", source_role_name="from",
                                 source_multiplicity="*", multiplicity="*")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c1, "o3")
        o4 = CObject(self.c1, "o4")

        set_links({o1: [o2, o3, o1]})
        o4.add_links([o1, o3])
        link1 = o1.links[0]
        link2 = [o for o in o1.links if o.association == a1][0]
        link3 = [o for o in o1.links if o.role_name == "to"][0]
        link4 = [o for o in o1.links if o.source_role_name == "from"][0]
        assert link1 == link2
        assert link1 == link3
        assert link1 == link4
        assert link1.association == a1
        assert link1.source == o1
        assert link1.target == o2

        assert len(o1.links) == 4
        assert len(o2.links) == 1
        assert len(o3.links) == 2
        assert len(o4.links) == 2

    def test_add_links(self):
        self.c1.association(self.c2, "1 -> [role1] *")
        self.c1.association(self.c2, "* -> [role2] *")
        self.c1.association(self.c2, "1 -> [role3] 1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")

        add_links({o1: o2}, role_name="role1")
        assert o1.get_linked(role_name="role1") == [o2]
        add_links({o1: [o3, o4]}, role_name="role1")
        o1.get_linked(role_name="role1")
        assert o1.get_linked(role_name="role1") == [o2, o3, o4]

        o1.add_links(o2, role_name="role2")
        assert o1.get_linked(role_name="role2") == [o2]
        o1.add_links([o3, o4], role_name="role2")
        o1.get_linked(role_name="role2")
        assert o1.get_linked(role_name="role2") == [o2, o3, o4]

        add_links({o1: o2}, role_name="role3")
        assert o1.get_linked(role_name="role3") == [o2]
        with pytest.raises(CException) as exc_info:
            add_links({o1: [o3, o4]}, role_name="role3")
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '3': should be '1'"

        with pytest.raises(CException) as exc_info:
            add_links({o1: [o3]}, role_name="role3")
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '2': should be '1'"
        assert o1.get_linked(role_name="role3") == [o2]

    def test_link_source_multiplicity(self):
        self.c1.association(self.c2, "[sourceRole1] 1 -> [role1] *")
        self.c1.association(self.c2, "[sourceRole2] 1 -> [role2] 1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c2, "o3")
        CObject(self.c2, "o4")
        CObject(self.c2, "o5")

        set_links({o1: o3}, role_name="role1")
        set_links({o2: o3}, role_name="role1")

        assert o3.get_linked(role_name="sourceRole1") == [o2]

    def test_add_links_source_multiplicity(self):
        self.c1.association(self.c2, "[sourceRole1] 1 -> [role1] *")
        self.c1.association(self.c2, "[sourceRole2] 1 -> [role2] 1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")
        o5 = CObject(self.c2, "o5")
        o6 = CObject(self.c2, "o6")

        add_links({o2: o3}, role_name="role1")
        add_links({o2: o4}, role_name="role1")

        assert o3.get_linked(role_name="sourceRole1") == [o2]

        add_links({o2: o5}, role_name="role1")
        assert o2.get_linked(role_name="role1") == [o3, o4, o5]

        with pytest.raises(CException) as exc_info:
            add_links({o1: [o4]}, role_name="role1")
        e = exc_info.value
        assert e.value == "links of object 'o4' have wrong multiplicity '2': should be '1'"

        add_links({o1: o6}, role_name="role2")
        assert o1.get_linked(role_name="role2") == [o6]
        with pytest.raises(CException) as exc_info:
            add_links({o1: [o3, o4]}, role_name="role2")
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '3': should be '1'"
        assert o1.get_linked(role_name="role2") == [o6]

    def test_set_links_multiple_links_in_definition(self):
        self.c1.association(self.c2, "[sourceRole1] * -> [role1] *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c1, "o3")
        o4 = CObject(self.c2, "o4")
        o5 = CObject(self.c2, "o5")

        set_links({o1: o4, o2: [o4], o5: [o1, o2, o3]})
        assert o1.get_linked() == [o4, o5]
        assert o2.get_linked() == [o4, o5]
        assert o3.get_linked() == [o5]
        assert o4.get_linked() == [o1, o2]
        assert o5.get_linked() == [o1, o2, o3]

    def test_add_links_multiple_links_in_definition(self):
        self.c1.association(self.c2, "[sourceRole1] * -> [role1] *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c1, "o3")
        o4 = CObject(self.c2, "o4")
        o5 = CObject(self.c2, "o5")

        add_links({o1: o4, o2: [o4], o5: [o1, o2, o3]})
        assert o1.get_linked() == [o4, o5]
        assert o2.get_linked() == [o4, o5]
        assert o3.get_linked() == [o5]
        assert o4.get_linked() == [o1, o2]
        assert o5.get_linked() == [o1, o2, o3]

    def test_wrong_types_delete_links(self):
        self.c1.association(self.c2, name="l", multiplicity="1")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            delete_links(o1)
        e = exc_info.value
        assert e.value == "link definitions should be of the form " + "{<link source 1>: <link target(s) 1>, ..., <link source n>: <link target(s) n>}"
        with pytest.raises(CException) as exc_info:
            delete_links({o1: self.mcl})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            delete_links({o1: [o2, self.mcl]})
        e = exc_info.value
        assert e.value == "link target 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            delete_links({o1: [o2, None]})
        e = exc_info.value
        assert e.value == "link target 'None' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            delete_links({self.mcl: o2})
        e = exc_info.value
        assert e.value == "link source 'MCL' is not an object, class, or link"
        with pytest.raises(CException) as exc_info:
            delete_links({None: o2})
        e = exc_info.value
        assert e.value == "link should not contain an empty source"

    def test_delete_one_to_one_link(self):
        self.c1.association(self.c2, "l: 1 -> [c2] 0..1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c1, "o3")
        o4 = CObject(self.c2, "o4")

        links = add_links({o1: o2, o3: o4})
        o1.delete_links(o2)
        assert o1.linked == []
        assert o2.linked == []
        assert o3.linked == [o4]
        assert o4.linked == [o3]
        assert o1.links == []
        assert o2.links == []
        assert o3.links == [links[1]]
        assert o4.links == [links[1]]
        delete_links({o3: o4})
        assert o1.linked == []
        assert o2.linked == []
        assert o3.linked == []
        assert o4.linked == []
        assert o1.links == []
        assert o2.links == []
        assert o3.links == []
        assert o4.links == []

    def test_delete_one_to_one_link_wrong_multiplicity(self):
        self.c1.association(self.c2, "l: 1 -> [c2] 1")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        add_links({o1: o2})
        with pytest.raises(CException) as exc_info:
            o1.delete_links(o2)
        e = exc_info.value
        assert e.value == "links of object 'o1' have wrong multiplicity '0': should be '1'"
        assert o1.linked == [o2]
        assert o2.linked == [o1]

    def test_delete_one_to_n_links(self):
        self.c1.association(self.c2, "l: 0..1 -> *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")
        o5 = CObject(self.c2, "o5")

        add_links({o1: [o3, o4], o2: [o5]})
        o4.delete_links([o1])
        assert o1.linked == [o3]
        assert o2.linked == [o5]
        assert o3.linked == [o1]
        assert o4.linked == []
        assert o5.linked == [o2]

        o4.add_links([o2])
        assert o2.linked == [o5, o4]
        delete_links({o1: o3, o2: o2.linked})
        assert o1.linked == []
        assert o2.linked == []
        assert o3.linked == []
        assert o4.linked == []
        assert o5.linked == []

    def test_delete_one_to_n_links_wrong_multiplicity(self):
        self.c1.association(self.c2, "l: 1 -> *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")
        o5 = CObject(self.c2, "o5")

        add_links({o1: [o3, o4], o2: [o5]})

        with pytest.raises(CException) as exc_info:
            o4.delete_links([o1])
        e = exc_info.value
        assert e.value == "links of object 'o4' have wrong multiplicity '0': should be '1'"

    def test_delete_n_to_n_links(self):
        self.c1.association(self.c2, "l: * -> *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")
        o5 = CObject(self.c2, "o5")
        o6 = CObject(self.c2, "o6")

        add_links({o1: [o3, o4], o2: [o4, o5]})
        o4.delete_links([o1, o2])
        assert o1.linked == [o3]
        assert o2.linked == [o5]
        assert o3.linked == [o1]
        assert o4.linked == []
        assert o5.linked == [o2]

        add_links({o4: [o1, o2], o6: [o2, o1]})
        delete_links({o1: o6, o2: [o4, o5]})
        assert o1.linked == [o3, o4]
        assert o2.linked == [o6]
        assert o3.linked == [o1]
        assert o4.linked == [o1]
        assert o5.linked == []
        assert o6.linked == [o2]

    def test_delete_link_no_matching_link(self):
        a = self.c1.association(self.c2, "l: 0..1 -> *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")
        o5 = CObject(self.c2, "o5")

        add_links({o1: [o3, o4], o2: [o5]}, association=a)

        with pytest.raises(CException) as exc_info:
            delete_links({o1: o5})
        e = exc_info.value
        assert e.value == "no link found for 'o1 -> o5' in delete links"

        b = self.c1.association(self.c2, "l: 0..1 -> *")
        with pytest.raises(CException) as exc_info:
            delete_links({o1: o5})
        e = exc_info.value
        assert e.value == "no link found for 'o1 -> o5' in delete links"

        with pytest.raises(CException) as exc_info:
            o4.delete_links([o1], association=b)
        e = exc_info.value
        assert e.value == "no link found for 'o4 -> o1' in delete links for given association"

    def test_delete_link_select_by_association(self):
        a = self.c1.association(self.c2, "a: * -> *")
        b = self.c1.association(self.c2, "b: * -> *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")

        add_links({o1: [o3], o2: [o3, o4]}, association=b)
        delete_links({o2: o3})
        assert o1.linked == [o3]
        assert o2.linked == [o4]
        assert o3.linked == [o1]
        assert o4.linked == [o2]
        add_links({o1: [o3], o2: [o3, o4]}, association=a)

        with pytest.raises(CException) as exc_info:
            delete_links({o1: o3})
        e = exc_info.value
        assert e.value == "link definition in delete links ambiguous for link 'o1->o3': found multiple matches"

        delete_links({o1: o3, o2: o4}, association=b)
        assert o1.linked == [o3]
        assert o2.linked == [o3, o4]
        assert o3.linked == [o1, o2]
        assert o4.linked == [o2]
        for o in [o1, o2, o3, o4]:
            for lo in o.links:
                assert lo.association == a

        o1.add_links(o3, association=b)
        with pytest.raises(CException) as exc_info:
            o1.delete_links(o3)
        e = exc_info.value
        assert e.value == "link definition in delete links ambiguous for link 'o1->o3': found multiple matches"

        assert o1.linked == [o3, o3]
        assert o2.linked == [o3, o4]
        assert o3.linked == [o1, o2, o1]
        assert o4.linked == [o2]

        o1.delete_links(o3, association=a)
        assert o1.linked == [o3]
        assert o2.linked == [o3, o4]
        assert o3.linked == [o2, o1]
        assert o4.linked == [o2]

    def test_delete_link_select_by_role_name(self):
        a = self.c1.association(self.c2, "a: [sourceA] * -> [targetA] *")
        self.c1.association(self.c2, "b: [sourceB] * -> [targetB] *")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c1, "o2")
        o3 = CObject(self.c2, "o3")
        o4 = CObject(self.c2, "o4")

        add_links({o1: [o3], o2: [o3, o4]}, role_name="targetB")
        delete_links({o2: o3})
        assert o1.linked == [o3]
        assert o2.linked == [o4]
        assert o3.linked == [o1]
        assert o4.linked == [o2]
        add_links({o1: [o3], o2: [o3, o4]}, role_name="targetA")

        delete_links({o1: o3, o2: o4}, role_name="targetB")
        assert o1.linked == [o3]
        assert o2.linked == [o3, o4]
        assert o3.linked == [o1, o2]
        assert o4.linked == [o2]
        for o in [o1, o2, o3, o4]:
            for lo in o.links:
                assert lo.association == a

        add_links({o1: [o3], o2: [o3, o4]}, role_name="targetB")
        o3.delete_links([o1, o2], role_name="sourceB")
        delete_links({o4: o2}, role_name="sourceB")

        assert o1.linked == [o3]
        assert o2.linked == [o3, o4]
        assert o3.linked == [o1, o2]
        assert o4.linked == [o2]
        for o in [o1, o2, o3, o4]:
            for lo in o.links:
                assert lo.association == a

    def test_delete_links_wrong_role_name(self):
        self.c1.association(self.c2, "a: [sourceA] * -> [targetA] *")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o1.add_links(o2)
        with pytest.raises(CException) as exc_info:
            o1.delete_links(o2, role_name="target")
        e = exc_info.value
        assert e.value == "no link found for 'o1 -> o2' in delete links for given role name 'target'"

    def test_delete_links_wrong_association(self):
        self.c1.association(self.c2, "a: [sourceA] * -> [targetA] *")
        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o1.add_links(o2)
        with pytest.raises(CException) as exc_info:
            o1.delete_links(o2, association=o1)
        e = exc_info.value
        assert e.value == "'o1' is not a association"
        b = self.c1.association(self.c2, "b: [sourceB] * -> [targetB] *")
        with pytest.raises(CException) as exc_info:
            o1.delete_links(o2, association=b)
        e = exc_info.value
        assert e.value == "no link found for 'o1 -> o2' in delete links for given association"
        with pytest.raises(CException) as exc_info:
            o1.delete_links(o2, association=b, role_name="x")
        e = exc_info.value
        assert e.value == "no link found for 'o1 -> o2' in delete links for given role name 'x' and for given association"

    def test_link_label_none_default(self):
        a1 = self.c1.association(self.c2, name="a1", multiplicity="*")
        a2 = self.c1.association(self.c2, multiplicity="*")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")

        l1 = set_links({o1: o2}, association=a1)
        l2 = set_links({o1: [o2, o3]}, association=a2)

        assert l1[0].label == None
        assert l2[0].label == None
        assert l2[1].label == None

    def test_link_label_get_set(self):
        a1 = self.c1.association(self.c2, name="a1", multiplicity="*")
        a2 = self.c1.association(self.c2, multiplicity="*")

        o1 = CObject(self.c1, "o1")
        o2 = CObject(self.c2, "o2")
        o3 = CObject(self.c2, "o3")

        l1 = set_links({o1: o2}, association=a1, label="l1")
        l2 = add_links({o1: [o2, o3]}, association=a2, label="l2")

        assert l1[0].label == "l1"
        assert l2[0].label == "l2"
        assert l2[1].label == "l2"

        l2[1].label = "l3"
        assert l2[0].label == "l2"
        assert l2[1].label == "l3"

        l3 = o1.add_links(o3, association=a1, label="x1")
        assert l3[0].label == "x1"

    def test_add_links_with_inherited_common_classifiers(self):
        mcl = CMetaclass("MCL")
        super_a = CClass(mcl, "SuperA")
        super_b = CClass(mcl, "SuperB")
        super_a.association(super_b, "[a] 1 -> [b] *")

        sub_b1 = CClass(mcl, "SubB1", superclasses=[super_b])
        sub_b2 = CClass(mcl, "SubB2", superclasses=[super_b])
        sub_a = CClass(mcl, "SubA", superclasses=[super_a])

        obj_a = CObject(sub_a, "a")
        obj_b1 = CObject(sub_b1, "b1")
        obj_b2 = CObject(sub_b2, "b2")

        add_links({obj_a: [obj_b1, obj_b2]}, role_name="b")
        assert set(obj_a.get_linked(role_name="b")) == {obj_b1, obj_b2}


