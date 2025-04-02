import unittest
from util import text_node_to_html_node, split_nodes_delimiter
from textnode import TextNode, TextType


class TestUtil(unittest.TestCase):
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

  def test_split_nodes_delimiter(self):
    node = TextNode("This is a **bold text** node", TextType.TEXT)
    split_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    self.assertEqual(split_nodes[0].text, "This is a ")
    self.assertEqual(split_nodes[1].text, "bold text")
    self.assertEqual(split_nodes[1].text_type, TextType.BOLD)
    self.assertEqual(split_nodes[2].text, " node")

  def test_split_nodes_delimiter_multiple(self):
    node = TextNode("This is a **bold text** node with *italic text*", TextType.TEXT)
    split_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    split_nodes = split_nodes_delimiter(split_nodes, "*", TextType.ITALIC)
    print(split_nodes)
    self.assertEqual(split_nodes[0].text, "This is a ")
    self.assertEqual(split_nodes[1].text, "bold text")
    self.assertEqual(split_nodes[1].text_type, TextType.BOLD)
    self.assertEqual(split_nodes[2].text, " node with ")
    self.assertEqual(split_nodes[3].text, "italic text")
    self.assertEqual(split_nodes[3].text_type, TextType.ITALIC)

  def test_split_nodes_delimiter_unclosed(self):
    node = TextNode("This is a **bold text node", TextType.TEXT)
    with self.assertRaises(ValueError):
      split_nodes_delimiter([node], "**", TextType.BOLD)

  def test_split_nodes_delimiter_two_bold_blocks(self):
    node = TextNode("**bold text** and **more bold text**", TextType.TEXT)
    split_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    self.assertEqual(split_nodes[1].text, "bold text")
    self.assertEqual(split_nodes[1].text_type, TextType.BOLD)
    self.assertEqual(split_nodes[2].text, " and ")
    self.assertEqual(split_nodes[3].text, "more bold text")
    self.assertEqual(split_nodes[3].text_type, TextType.BOLD)

  def test_split_nodes_delimiter_code(self):
    node = TextNode("This is a `code` block", TextType.TEXT)
    split_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
    self.assertEqual(split_nodes[1].text, "code")
    self.assertEqual(split_nodes[1].text_type, TextType.CODE)





