import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode("div", "Hello, World!", props={"class": "container"})
        self.assertEqual(node.props_to_html(), 'class="container"')

    def test_props_to_html_empty(self):
        node = HTMLNode("div", "Hello, World!")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_multiple(self):
        node = HTMLNode("div", "Hello, World!", props={"class": "container", "id": "main"})
        self.assertEqual(node.props_to_html(), 'class="container" id="main"')


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", props={"href": "https://www.example.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.example.com">Click me!</a>')

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Hello, world!")
        self.assertEqual(node.to_html(), "Hello, world!")

    def test_leaf_to_html_no_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()


class TestParentNode(unittest.TestCase):
    def test_parent_to_html_div(self):
        child1 = LeafNode("p", "Hello, world!")
        child2 = LeafNode("p", "Goodbye, world!")
        node = ParentNode("div", children=[child1, child2])
        self.assertEqual(node.to_html(), "<div><p>Hello, world!</p><p>Goodbye, world!</p></div>")

    def test_parent_to_html_ul(self):
        child1 = LeafNode("li", "Item 1")
        child2 = LeafNode("li", "Item 2")
        node = ParentNode("ul", children=[child1, child2])
        self.assertEqual(node.to_html(), "<ul><li>Item 1</li><li>Item 2</li></ul>")

    def test_parent_to_html_no_tag(self):
        child1 = LeafNode("p", "Hello, world!")
        child2 = LeafNode("p", "Goodbye, world!")
        node = ParentNode(None, children=[child1, child2])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_to_html_no_children(self):
        node = ParentNode("div", children=[])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_parent_to_html_nested_parents(self):
        child1 = LeafNode("p", "Hello, world!")
        child2 = LeafNode("p", "Goodbye, world!")
        parent = ParentNode("div", children=[child1, child2])
        node = ParentNode("div", children=[parent])
        self.assertEqual(node.to_html(), "<div><div><p>Hello, world!</p><p>Goodbye, world!</p></div></div>")