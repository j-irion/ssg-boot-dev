from htmlnode import LeafNode, HTMLNode, ParentNode
from textnode import TextType, TextNode
import re
from enum import Enum
import os
import shutil


def text_node_to_html_node(text_node):
  match text_node.text_type:
    case TextType.TEXT:
      return LeafNode(None, text_node.text)
    case TextType.BOLD:
      return LeafNode("b", text_node.text)
    case TextType.ITALIC:
      return LeafNode("i", text_node.text)
    case TextType.CODE:
      return LeafNode("code", text_node.text)
    case TextType.LINK:
      return LeafNode("a", text_node.text, props={"href": text_node.url})
    case TextType.IMAGE:
      return LeafNode("img", props={"src": text_node.url})
    case _:
      raise ValueError("Invalid text type")


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter, text_type):
  new_nodes = []
  for node in old_nodes:
    if node.text_type != TextType.TEXT:
      new_nodes.append(node)
      continue

    parts = node.text.split(delimiter)

    if len(parts) % 2 == 0:
      raise ValueError(f"Unclosed delimiter '{delimiter}' in text: {node.text}")

    is_open = False
    for i, part in enumerate(parts):
      if is_open:
        new_nodes.append(TextNode(part, text_type))
      else:
        new_nodes.append(TextNode(part, TextType.TEXT))
      is_open = not is_open

  return new_nodes


def extract_markdown_images(text):
  images = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
  return images

def extract_markdown_links(text):
  links = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
  return links


def split_nodes_link(old_nodes):
  new_nodes = []
  for node in old_nodes:
    if node.text_type != TextType.TEXT:
      new_nodes.append(node)
      continue

    text = node.text
    result = []
    last_end = 0

    for match in re.finditer(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text):
      if match.start() > last_end:
        result.append(TextNode(text[last_end:match.start()], TextType.TEXT))

      link_text = match.group(1)
      url = match.group(2)
      result.append(TextNode(link_text, TextType.LINK, url))

      last_end = match.end()

    if last_end < len(text):
      result.append(TextNode(text[last_end:], TextType.TEXT))

    new_nodes.extend(result)

  return new_nodes


def split_nodes_image(old_nodes):
  new_nodes = []
  for node in old_nodes:
    if node.text_type != TextType.TEXT:
      new_nodes.append(node)
      continue

    text = node.text
    result = []
    last_end = 0

    for match in re.finditer(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text):
      if match.start() > last_end:
        result.append(TextNode(text[last_end:match.start()], TextType.TEXT))

      alt_text = match.group(1)
      url = match.group(2)
      result.append(TextNode(alt_text, TextType.IMAGE, url))

      last_end = match.end()

    if last_end < len(text):
      result.append(TextNode(text[last_end:], TextType.TEXT))

    new_nodes.extend(result)

  return new_nodes

def text_to_textnodes(text):
  nodes = []
  if not text:
    return nodes

  # Split by newlines first
  lines = text.splitlines()
  for i, line in enumerate(lines):
    if i == len(lines) - 1:
      nodes.append(TextNode(line, TextType.TEXT))
    else:
      nodes.append(TextNode(line + " ", TextType.TEXT))

  # Now handle links and images
  nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
  nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
  nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
  nodes = split_nodes_link(nodes)
  nodes = split_nodes_image(nodes)

  return nodes


def markdown_to_blocks(markdown):
  markdown = markdown.strip()

  result = []
  blocks = re.split(r"\n\n", markdown)

  for block in blocks:
    lines = block.split("\n")
    cleaned_lines = [line.strip() for line in lines]
    cleaned_block = "\n".join(cleaned_lines)
    if cleaned_block:
      result.append(cleaned_block)

  return result

class BlockType(Enum):
  PARAGRAPH = "paragraph"
  HEADING = "heading"
  CODE = "code"
  QUOTE = "quote"
  UNORDERED_LIST = "unordered_list"
  ORDERED_LIST = "ordered_list"


def block_to_block_type(block):
  if re.match(r"^#{1,6} ", block):
    return BlockType.HEADING

  if block.startswith("```") and block.endswith("```"):
    return BlockType.CODE

  lines = block.split("\n")
  if all(line.startswith(">") for line in lines):
    return BlockType.QUOTE

  if all(line.startswith("- ") for line in lines):
    return BlockType.UNORDERED_LIST

  if all(re.match(r"^\d+\. ", line) for line in lines):
    numbers = [int(re.match(r"^(\d+)\. ", line).group(1)) for line in lines]
    expected = list(range(1, len(numbers) + 1))
    if numbers == expected:
      return BlockType.ORDERED_LIST

  return BlockType.PARAGRAPH

def text_to_children(text):
  """Convert markdown text to a list of HTMLNode objects by parsing inline elements"""
  text_nodes = text_to_textnodes(text)
  print(text_nodes)
  return [text_node_to_html_node(node) for node in text_nodes]


def markdown_to_html_node(markdown):
  blocks = markdown_to_blocks(markdown)
  block_nodes = []

  for block in blocks:
    block_type = block_to_block_type(block)
    html_node = None

    if block_type == BlockType.PARAGRAPH:
      children = text_to_children(block)
      html_node = ParentNode("p", children=children)

    elif block_type == BlockType.HEADING:
      level = len(re.match(r"^(#+)", block).group(1))
      content = block.lstrip("# ").strip()
      children = text_to_children(content)
      html_node = ParentNode(f"h{level}", children=children)

    elif block_type == BlockType.CODE:
      code_content = block.strip("```").strip()
      text_node = TextNode(code_content + "\n", TextType.TEXT)
      code_node = text_node_to_html_node(text_node)
      html_node = ParentNode("pre", children=[ParentNode("code", children=[code_node])])

    elif block_type == BlockType.QUOTE:
      lines = block.split("\n")
      cleaned_lines = [line.lstrip("> ").strip() for line in lines]
      quote_content = "\n".join(cleaned_lines)
      children = text_to_children(quote_content)
      html_node = ParentNode("blockquote", children=children)

    elif block_type == BlockType.UNORDERED_LIST:
      items = block.split("\n")
      list_items = []
      for item in items:
        item_content = item.lstrip("- ").strip()
        item_children = text_to_children(item_content)
        list_items.append(ParentNode("li", children=item_children))
      html_node = ParentNode("ul", children=list_items)

    elif block_type == BlockType.ORDERED_LIST:
      items = block.split("\n")
      list_items = []
      for item in items:
        item_content = re.sub(r"^\d+\.\s*", "", item).strip()
        item_children = text_to_children(item_content)
        list_items.append(ParentNode("li", children=item_children))
      html_node = ParentNode("ol", children=list_items)

    if html_node is not None:
      block_nodes.append(html_node)

  return ParentNode("div", children=block_nodes)


def copy_files_from_to_directory(src_dir, dest_dir):
  """Recursively copy files from source directory to destination directory.

  First deletes all contents of destination directory for a clean copy.

  Args:
      src_dir: Source directory path
      dest_dir: Destination directory path
  """
  src_dir = os.path.abspath(src_dir)
  dest_dir = os.path.abspath(dest_dir)
  if os.path.exists(dest_dir):
    shutil.rmtree(dest_dir)

  os.makedirs(dest_dir)

  for item in os.listdir(src_dir):
    src_path = os.path.join(src_dir, item)
    dest_path = os.path.join(dest_dir, item)

    if os.path.isdir(src_path):
      print(f"Copying directory: {src_path} -> {dest_path}")
      copy_files_from_to_directory(src_path, dest_path)
    else:
      print(f"Copying file: {src_path} -> {dest_path}")
      shutil.copy2(src_path, dest_path)


