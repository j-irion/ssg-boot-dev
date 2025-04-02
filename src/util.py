from htmlnode import LeafNode
from textnode import TextType


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