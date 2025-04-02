import unittest

from src.htmlnode import LeafNode
from src.node_conversion import text_node_to_html_node
from textnode import TextNode, TextType


class TestNodeConversion(unittest.TestCase):
  def test_text_node_to_html_node(self):
    node = TextNode("This is a text node", TextType.TEXT)
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, None)
    self.assertEqual(html_node.value, "This is a text node")

  def test_text_node_to_html_node_bold(self):
    node = TextNode("This is a text node", TextType.BOLD)
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, "strong")
    self.assertEqual(html_node.value, "This is a text node")

  def test_text_node_to_html_node_invalid_text_type(self):
    node = TextNode("This is a text node", "invalid")
    with self.assertRaises(ValueError):
      text_node_to_html_node(node)



