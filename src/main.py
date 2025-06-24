import sys

from util import copy_files_from_to_directory, generate_pages_recursive

def main(basepath):
  copy_files_from_to_directory("static", "docs")
  generate_pages_recursive("content", "template.html", "docs", basepath)




if __name__ == "__main__":
  basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
  main(basepath=basepath)