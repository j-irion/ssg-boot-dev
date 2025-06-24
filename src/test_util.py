import unittest
from util import *
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
    self.assertEqual(html_node.tag, "b")
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

  def test_text_to_textnodes(self):
    text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
    nodes = text_to_textnodes(text)
    self.assertListEqual([
        TextNode("This is ", TextType.TEXT),
        TextNode("text", TextType.BOLD),
        TextNode(" with an ", TextType.TEXT),
        TextNode("italic", TextType.ITALIC),
        TextNode(" word and a ", TextType.TEXT),
        TextNode("code block", TextType.CODE),
        TextNode(" and an ", TextType.TEXT),
        TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        TextNode(" and a ", TextType.TEXT),
        TextNode("link", TextType.LINK, "https://boot.dev"),
      ], nodes)

  def test_markdown_to_blocks(self):
      md = """
  This is **bolded** paragraph

  This is another paragraph with _italic_ text and `code` here
  This is the same paragraph on a new line

  - This is a list
  - with items
  """
      blocks = markdown_to_blocks(md)
      self.assertEqual(
        [
          "This is **bolded** paragraph",
          "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
          "- This is a list\n- with items",
        ], blocks
      )

  def test_splits_markdown_into_blocks_correctly(self):
    markdown = "This is a block.\n\nThis is another block."
    result = markdown_to_blocks(markdown)
    self.assertListEqual(["This is a block.", "This is another block."], result)

  def test_handles_single_block_without_newlines(self):
    markdown = "This is a single block."
    result = markdown_to_blocks(markdown)
    self.assertListEqual(["This is a single block."], result)

  def test_removes_leading_and_trailing_whitespace_from_blocks(self):
    markdown = "   This is a block.   \n\n   This is another block.   "
    result = markdown_to_blocks(markdown)
    self.assertListEqual(["This is a block.", "This is another block."], result)

  def test_handles_empty_markdown_gracefully(self):
    markdown = ""
    result = markdown_to_blocks(markdown)
    self.assertListEqual([], result)

  def test_ignores_consecutive_newlines_between_blocks(self):
    markdown = "Block one.\n\n\n\nBlock two."
    result = markdown_to_blocks(markdown)
    self.assertListEqual(["Block one.", "Block two."], result)

  def test_handles_blocks_with_multiple_lines(self):
    markdown = "Line one of block one.\nLine two of block one.\n\nLine one of block two."
    result = markdown_to_blocks(markdown)
    self.assertListEqual(["Line one of block one.\nLine two of block one.", "Line one of block two."], result)

  def test_identifies_heading_block_correctly(self):
    block = "# Heading"
    result = block_to_block_type(block)
    self.assertEqual(result, BlockType.HEADING)

  def test_identifies_code_block_correctly(self):
    block = "```\ncode block\n```"
    result = block_to_block_type(block)
    self.assertEqual(result, BlockType.CODE)

  def test_identifies_quote_block_correctly(self):
    block = "> This is a quote\n> Another line of quote"
    result = block_to_block_type(block)
    self.assertEqual(result, BlockType.QUOTE)

  def test_identifies_unordered_list_block_correctly(self):
    block = "- Item 1\n- Item 2\n- Item 3"
    result = block_to_block_type(block)
    self.assertEqual(result, BlockType.UNORDERED_LIST)

  def test_identifies_ordered_list_block_correctly(self):
    block = "1. First item\n2. Second item\n3. Third item"
    result = block_to_block_type(block)
    self.assertEqual(result, BlockType.ORDERED_LIST)

  def test_identifies_paragraph_block_correctly(self):
    block = "This is a paragraph with multiple lines.\nIt continues here."
    result = block_to_block_type(block)
    self.assertEqual(result, BlockType.PARAGRAPH)

  def test_handles_malformed_ordered_list_gracefully(self):
    block = "1. First item\n3. Second item\n2. Third item"
    result = block_to_block_type(block)
    self.assertEqual(result, BlockType.PARAGRAPH)

  def test_handles_empty_block_gracefully(self):
    block = ""
    result = block_to_block_type(block)
    self.assertEqual(result, BlockType.PARAGRAPH)

  def test_paragraphs(self):
      md = """
  This is **bolded** paragraph
  text in a p
  tag here

  This is another paragraph with _italic_ text and `code` here

  """

      node = markdown_to_html_node(md)
      html = node.to_html()
      self.assertEqual(
        html,
        "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
      )

  def test_codeblock(self):
    md = """
  ```
  This is text that _should_ remain
  the **same** even with inline stuff
  ```
  """

    node = markdown_to_html_node(md)
    html = node.to_html()
    self.assertEqual(
      "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
      html,
    )

  def test_extracts_title_from_valid_markdown(self):
    markdown = "# Title\n\nThis is the content."
    result = extract_title(markdown)
    self.assertEqual(result, "Title")

  def test_ignores_non_h1_headings(self):
    markdown = "## Subtitle\n\n# Title\n\nContent."
    result = extract_title(markdown)
    self.assertEqual(result, "Title")

  def test_raises_exception_for_missing_title(self):
    markdown = "## Subtitle\n\nContent."
    with self.assertRaises(Exception) as context:
      extract_title(markdown)
    self.assertEqual(str(context.exception), "No title found in ## Subtitle\n\nContent.")

  def test_handles_markdown_with_only_title(self):
    markdown = "# Title"
    result = extract_title(markdown)
    self.assertEqual(result, "Title")

  def test_handles_title_with_extra_whitespace(self):
    markdown = "#   Title   \n\nContent."
    result = extract_title(markdown)
    self.assertEqual(result, "Title")






