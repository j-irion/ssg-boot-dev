from htmlnode import LeafNode
from src.htmlnode import HTMLNode
from textnode import TextType, TextNode
import re


def text_node_to_html_node(text_node):
  match text_node.text_type:
    case TextType.TEXT:
      return LeafNode(None, text_node.text)
    case TextType.BOLD:
      return LeafNode("strong", text_node.text)
    case TextType.ITALIC:
      return LeafNode("em", text_node.text)
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
  for line in lines:
    if not line.strip():
      continue
    nodes.append(TextNode(line.strip(), TextType.TEXT))

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
