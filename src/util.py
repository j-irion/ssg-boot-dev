from htmlnode import LeafNode
from src.htmlnode import HTMLNode
from textnode import TextType, TextNode


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
