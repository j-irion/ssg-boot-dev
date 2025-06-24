from util import copy_files_from_to_directory, generate_page

def main():
  copy_files_from_to_directory("static", "public")
  generate_page("content/index.md", "template.html", "public/index.html")




if __name__ == "__main__":
  main()