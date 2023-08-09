import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
	"""
	Returns a list of all names of encyclopedia entries.
	"""
	_, filenames = default_storage.listdir("entries")
	return list(sorted(re.sub(r"\.md$", "", filename)
				for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
	"""
	Saves an encyclopedia entry, given its title and Markdown
	content. If an existing entry with the same title already exists,
	it is replaced.
	"""
	filename = f"entries/{title}.md"
	if default_storage.exists(filename):
		default_storage.delete(filename)
	default_storage.save(filename, ContentFile(content))


def get_entry(title):
	"""
	Retrieves an encyclopedia entry by its title. If no such
	entry exists, the function returns None.
	"""
	try:
		f = default_storage.open(f"entries/{title}.md")
		return f.read().decode("utf-8")
	except FileNotFoundError:
		return None


def search_entries(search):
	selected = []
	for entry in list_entries():
		if search.lower() in entry.lower():
			selected.append(entry)

	return selected


def parse_heading(attr, regex):
	text = re.search(regex, attr["text"])
	if text:
		lvl = text.group(1).count("#")
		attr["text"] = f"\n<h{lvl} class=\"entry-header\">{text.group(2).strip()}</h{lvl}>\n"


def parse_list_item(regex, attr):
	item = re.search(regex, attr["text"])
	if not item:
		return False

	attr["text"] = "\n<ul class=\"item-list\">\n" if not attr["list_seq"] else ""
	attr["text"] += f"\t<li>{item.group(1).strip()}</li>\n"
	attr["list_seq"] = True
	attr["parsed_html"] += attr["text"]
	
	return True


def parse_content(content):
	LIST_RX = r"^\*([^\n]*[^\n ]+)"
	HEADING_RX = r"^(#{1,6})([^\n]*[^\n ]+)"
	STRONG_RX = r"\*\*([\t ]*[^\s*]+[^\n*]*)\*\*"
	LINK_RX = r"\[([^\n\[\]]+)\]\(([\S]+)\)"

	attr = {"text": "", "parsed_html": "", "list_seq": False}

	for line in content.splitlines():
		if not line.strip():
			continue

		# Checks for bold text
		attr["text"] = re.sub(STRONG_RX, r"<strong>\1</strong>", line)
		# Checks for links
		attr["text"] = re.sub(LINK_RX, "<a class=\"page-link\" href=\"\\2\">\\1</a>", attr["text"])

		# Checks for list item
		if parse_list_item(LIST_RX, attr):
			continue

		prefix = ""
		if attr["list_seq"]:
			prefix = "</ul>\n"
			attr["list_seq"] = False

		# Checks for heading
		parse_heading(attr, HEADING_RX)

		attr["parsed_html"] += prefix + attr["text"]

	return attr["parsed_html"]

