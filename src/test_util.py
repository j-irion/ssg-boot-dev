import unittest
from util import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link
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

  def test_extract_markdown_images(self):
    matches = extract_markdown_images(
        "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
    )
    self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

  def test_extracts_single_image_correctly(self):
      text = "![alt text](http://example.com/image.png)"
      result = extract_markdown_images(text)
      self.assertListEqual([("alt text", "http://example.com/image.png")], result)

  def test_extracts_multiple_images_correctly(self):
    text = "![image1](http://example.com/1.png) and ![image2](http://example.com/2.png)"
    result = extract_markdown_images(text)
    self.assertListEqual([("image1", "http://example.com/1.png"), ("image2", "http://example.com/2.png")], result)

  def test_ignores_text_without_images(self):
    text = "This is a text without images."
    result = extract_markdown_images(text)
    self.assertListEqual([], result)

  def test_handles_malformed_image_syntax_gracefully(self):
    text = "![alt text(http://example.com/image.png)"
    result = extract_markdown_images(text)
    self.assertListEqual([], result)

  def test_extracts_image_with_special_characters_in_url(self):
    text = "![alt text](http://example.com/image%20with%20spaces.png)"
    result = extract_markdown_images(text)
    self.assertListEqual([("alt text", "http://example.com/image%20with%20spaces.png")], result)

  def test_extracts_image_with_empty_alt_text(self):
    text = "![](http://example.com/image.png)"
    result = extract_markdown_images(text)
    self.assertListEqual([("", "http://example.com/image.png")], result)

  def test_extracts_single_link_correctly(self):
    text = "[link](http://example.com)"
    result = extract_markdown_links(text)
    self.assertListEqual([("link", "http://example.com")], result)

  def test_extracts_multiple_links_correctly(self):
    text = "[link1](http://example.com) and [link2](http://example.org)"
    result = extract_markdown_links(text)
    self.assertListEqual([("link1", "http://example.com"), ("link2", "http://example.org")], result)

  def test_ignores_exclamation_mark_in_links(self):
    text = "![image](http://example.com/image.png) and [link](http://example.com)"
    result = extract_markdown_links(text)
    self.assertListEqual([("link", "http://example.com")], result)

  def test_handles_empty_text_gracefully(self):
    text = ""
    result = extract_markdown_links(text)
    self.assertListEqual([], result)

  def test_ignores_malformed_links(self):
    text = "[link(http://example.com)"
    result = extract_markdown_links(text)
    self.assertListEqual([], result)

  def test_extracts_link_with_special_characters_in_url(self):
    text = "[link](http://example.com/path%20with%20spaces)"
    result = extract_markdown_links(text)
    self.assertListEqual([("link", "http://example.com/path%20with%20spaces")], result)

  def test_extracts_link_with_empty_text(self):
    text = "[](http://example.com)"
    result = extract_markdown_links(text)
    self.assertListEqual([("", "http://example.com")], result)

  def test_split_images(self):
    node = TextNode(
      "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
      TextType.TEXT,
    )
    new_nodes = split_nodes_image([node])
    self.assertListEqual(
      [
        TextNode("This is text with an ", TextType.TEXT),
        TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
        TextNode(" and another ", TextType.TEXT),
        TextNode(
          "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
        ),
      ],
      new_nodes,
    )

  def test_split_links(self):
    node = TextNode(
      "This is text with an [link 1](https://example.com/df345ds) and another [link two](https://example.com/sd43sd)",
      TextType.TEXT,
    )
    new_nodes = split_nodes_link([node])
    self.assertListEqual(
      [
        TextNode("This is text with an ", TextType.TEXT),
        TextNode("link 1", TextType.LINK, "https://example.com/df345ds"),
        TextNode(" and another ", TextType.TEXT),
        TextNode(
          "link two", TextType.LINK, "https://example.com/sd43sd"
        ),
      ],
      new_nodes,
    )

  def test_extracts_single_link_node_correctly(self):
    old_nodes = [TextNode("This is [link](http://example.com)", TextType.TEXT)]
    result = split_nodes_link(old_nodes)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[0].text, "This is ")
    self.assertEqual(result[0].text_type, TextType.TEXT)
    self.assertEqual(result[1].text, "link")
    self.assertEqual(result[1].text_type, TextType.LINK)
    self.assertEqual(result[1].url, "http://example.com")

  def test_handles_multiple_links_in_text(self):
    old_nodes = [TextNode("Visit [link1](http://example.com) and [link2](http://example.org)", TextType.TEXT)]
    result = split_nodes_link(old_nodes)
    self.assertEqual(len(result), 4)
    self.assertEqual(result[0].text, "Visit ")
    self.assertEqual(result[1].text, "link1")
    self.assertEqual(result[1].url, "http://example.com")
    self.assertEqual(result[2].text, " and ")
    self.assertEqual(result[3].text, "link2")
    self.assertEqual(result[3].url, "http://example.org")

  def test_ignores_text_without_links(self):
    old_nodes = [TextNode("This is plain text.", TextType.TEXT)]
    result = split_nodes_link(old_nodes)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].text, "This is plain text.")
    self.assertEqual(result[0].text_type, TextType.TEXT)

  def test_handles_malformed_links_gracefully(self):
    old_nodes = [TextNode("This is [malformed link(http://example.com)", TextType.TEXT)]
    result = split_nodes_link(old_nodes)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].text, "This is [malformed link(http://example.com)")
    self.assertEqual(result[0].text_type, TextType.TEXT)

  def test_extracts_link_with_special_characters_in_url(self):
    old_nodes = [TextNode("Check [link](http://example.com/path%20with%20spaces)", TextType.TEXT)]
    result = split_nodes_link(old_nodes)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[1].text, "link")
    self.assertEqual(result[1].url, "http://example.com/path%20with%20spaces")

  def test_handles_text_with_no_closing_bracket(self):
    old_nodes = [TextNode("This is [link(http://example.com", TextType.TEXT)]
    result = split_nodes_link(old_nodes)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].text, "This is [link(http://example.com")
    self.assertEqual(result[0].text_type, TextType.TEXT)

  def test_extracts_single_image_node_correctly(self):
    old_nodes = [TextNode("This is ![alt text](http://example.com/image.png)", TextType.TEXT)]
    result = split_nodes_image(old_nodes)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[0].text, "This is ")
    self.assertEqual(result[0].text_type, TextType.TEXT)
    self.assertEqual(result[1].text, "alt text")
    self.assertEqual(result[1].text_type, TextType.IMAGE)
    self.assertEqual(result[1].url, "http://example.com/image.png")

  def test_handles_multiple_images_in_text(self):
    old_nodes = [
      TextNode("Here is ![image1](http://example.com/1.png) and ![image2](http://example.com/2.png)", TextType.TEXT)]
    result = split_nodes_image(old_nodes)
    self.assertEqual(len(result), 4)
    self.assertEqual(result[0].text, "Here is ")
    self.assertEqual(result[1].text, "image1")
    self.assertEqual(result[1].url, "http://example.com/1.png")
    self.assertEqual(result[2].text, " and ")
    self.assertEqual(result[3].text, "image2")
    self.assertEqual(result[3].url, "http://example.com/2.png")

  def test_ignores_text_without_images(self):
    old_nodes = [TextNode("This is plain text.", TextType.TEXT)]
    result = split_nodes_image(old_nodes)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].text, "This is plain text.")
    self.assertEqual(result[0].text_type, TextType.TEXT)

  def test_handles_malformed_image_syntax_gracefully(self):
    old_nodes = [TextNode("This is ![alt text(http://example.com/image.png)", TextType.TEXT)]
    result = split_nodes_image(old_nodes)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].text, "This is ![alt text(http://example.com/image.png)")
    self.assertEqual(result[0].text_type, TextType.TEXT)

  def test_extracts_image_with_special_characters_in_url(self):
    old_nodes = [TextNode("Check ![alt text](http://example.com/image%20with%20spaces.png)", TextType.TEXT)]
    result = split_nodes_image(old_nodes)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[1].text, "alt text")
    self.assertEqual(result[1].url, "http://example.com/image%20with%20spaces.png")

  def test_handles_text_with_no_closing_parenthesis(self):
    old_nodes = [TextNode("This is ![alt text(http://example.com/image.png", TextType.TEXT)]
    result = split_nodes_image(old_nodes)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].text, "This is ![alt text(http://example.com/image.png")
    self.assertEqual(result[0].text_type, TextType.TEXT)






