import unittest

from htmlnode import HTMLNode


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