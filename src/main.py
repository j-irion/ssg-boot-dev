from src.textnode import TextNode, TextType

def main():
  print("hello world")

  text_node = TextNode("Hello", TextType.LINK, "https://www.example.com")

  print(text_node)


if __name__ == "__main__":
  main()