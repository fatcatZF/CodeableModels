
import pytest
from codeable_models import CBundle, CMetaclass, CClass, CException, CLayer, CPackage


class TestBundles:
    def setup_method(self):
        self.mcl = CMetaclass("MCL")
        self.b1 = CBundle("B1")

    def test_bundle_name_fail(self):
        with pytest.raises(CException) as exc_info:
            # noinspection PyTypeChecker
            CBundle(self.mcl)
        e = exc_info.value
        assert e.value.startswith("is not a name string: '")
        assert e.value.endswith(" MCL'")

    def test_get_elements_wrong_kw_arg(self):
        with pytest.raises(CException) as exc_info:
            self.b1.get_elements(x=CBundle)
        e = exc_info.value
        assert e.value == "unknown argument to getElements: 'x'"

    def test_get_element_wrong_kw_arg(self):
        with pytest.raises(CException) as exc_info:
            self.b1.get_element(x=CBundle)
        e = exc_info.value
        assert e.value == "unknown argument to getElements: 'x'"

    def test_package_and_layer_subclasses(self):
        layer1 = CLayer("L1")
        layer2 = CLayer("L2", sub_layer=layer1)
        package1 = CPackage("P1")
        c1 = CClass(self.mcl, "C1")
        c2 = CClass(self.mcl, "C2")
        c3 = CClass(self.mcl, "C3")
        layer1.elements = [c1, c2]
        layer2.elements = [c3]
        package1.elements = [layer1, layer2] + layer1.elements + layer2.elements
        assert set(package1.elements) == {layer1, layer2, c1, c2, c3}
        assert set(layer1.elements) == {c1, c2}
        assert set(layer2.elements) == {c3}
        assert set(c1.bundles) == {layer1, package1}
        assert set(c2.bundles) == {layer1, package1}
        assert set(c3.bundles) == {layer2, package1}

    def test_layer_sub_layers(self):
        layer1 = CLayer("L1")
        assert layer1.super_layer == None
        assert layer1.sub_layer == None

        layer1 = CLayer("L1", sub_layer=None)
        assert layer1.super_layer == None
        assert layer1.sub_layer == None

        layer2 = CLayer("L2", sub_layer=layer1)
        assert layer1.super_layer == layer2
        assert layer1.sub_layer == None
        assert layer2.super_layer == None
        assert layer2.sub_layer == layer1

        layer3 = CLayer("L3", sub_layer=layer1)
        assert layer1.super_layer == layer3
        assert layer1.sub_layer == None
        assert layer2.super_layer == None
        assert layer2.sub_layer == None
        assert layer3.super_layer == None
        assert layer3.sub_layer == layer1

        layer3.sub_layer = layer2
        assert layer1.super_layer == None
        assert layer1.sub_layer == None
        assert layer2.super_layer == layer3
        assert layer2.sub_layer == None
        assert layer3.super_layer == None
        assert layer3.sub_layer == layer2

        layer2.sub_layer = layer1
        assert layer1.super_layer == layer2
        assert layer1.sub_layer == None
        assert layer2.super_layer == layer3
        assert layer2.sub_layer == layer1
        assert layer3.super_layer == None
        assert layer3.sub_layer == layer2

    def test_layer_super_layers(self):
        layer1 = CLayer("L1")
        assert layer1.super_layer == None
        assert layer1.sub_layer == None

        layer1 = CLayer("L1", super_layer=None)
        assert layer1.super_layer == None
        assert layer1.sub_layer == None

        layer2 = CLayer("L2", super_layer=layer1)
        assert layer1.super_layer == None
        assert layer1.sub_layer == layer2
        assert layer2.super_layer == layer1
        assert layer2.sub_layer == None

        layer3 = CLayer("L3", super_layer=layer1)
        assert layer1.super_layer == None
        assert layer1.sub_layer == layer3
        assert layer2.super_layer == None
        assert layer2.sub_layer == None
        assert layer3.super_layer == layer1
        assert layer3.sub_layer == None

        layer3.super_layer = layer2
        assert layer1.super_layer == None
        assert layer1.sub_layer == None
        assert layer2.super_layer == None
        assert layer2.sub_layer == layer3
        assert layer3.super_layer == layer2
        assert layer3.sub_layer == None

        layer2.super_layer = layer1
        assert layer1.super_layer == None
        assert layer1.sub_layer == layer2
        assert layer2.super_layer == layer1
        assert layer2.sub_layer == layer3
        assert layer3.super_layer == layer2
        assert layer3.sub_layer == None


