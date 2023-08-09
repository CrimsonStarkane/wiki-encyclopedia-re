from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django import forms

from . import util

import random as rnd


class SearchForm(forms.Form):
    searchbar = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'search', 'placeholder': 'Search Encyclopedia...',
            'required': 'required'}),
        label="Search"
    )


class InputForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'title-input', 'placeholder': 'Insert Title Here...',
            'autofocus': 'autofocus'}),
        label="Title"
    )
    textarea = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'input-area', 'placeholder': 'Write Content...'}),
        label="InputArea"
    )


def index(request):
    return render(request, "encyclopedia/index.html", {
        "title": "Encyclopedia",
        "header": "All Pages",
        "entries": util.list_entries(),
        "form": SearchForm(request.session.pop("form_data", None))
    })


def entry(request, entry):
    for e in util.list_entries():
        if e.lower() == entry.lower():
            return render(request, "encyclopedia/entry.html", {
                "title": entry,
                "content": util.parse_content(util.get_entry(e)),
                "form": SearchForm(request.session.pop("form_data", None))
            })

    return render(request, "encyclopedia/error.html", {
        "title": "Not Found",
        "form": SearchForm(request.session.pop("form_data", None))
    })


def add(request):
    if request.method == "POST":
        form = InputForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["textarea"]

            for entry in util.list_entries():
                if title.lower() == entry.lower():
                    messages.error(request, "An entry with this title already exists.")
                    return render(request, "encyclopedia/input.html", {
                        "title": "Add",
                        "header": "Add New Page",
                        "form": SearchForm(),
                        "inputForm": form
                    })
                
            util.save_entry(title, content)
            return redirect(reverse("entry", args=[title]))
        else:
            return render(request, "encyclopedia/input.html", {
                "title": "Add",
                "header": "Add New Page",
                "form": SearchForm(),
                "inputForm": form
            })

    return render(request, "encyclopedia/input.html", {
        "title": "Add",
        "header": "Add New Page",
        "form": SearchForm(request.session.pop("form_data", None)),
        "inputForm": InputForm()
    })


def edit(request, entry):
    if request.method == "POST":
        form = InputForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["textarea"]
            util.save_entry(entry, content)
            return redirect(reverse("entry", args=[entry]))
        else:
            return render(request, "encyclopedia/input.html", {
                "title": "Edit",
                "header": "Edit Page",
                "form": SearchForm(request.session.pop("form_data", None)),
                "inputForm": form
            })

    inputForm = InputForm(initial={"title": entry, "textarea": util.get_entry(entry)})
    inputForm['textarea'].field.widget.attrs['autofocus'] = 'autofocus'

    return render(request, "encyclopedia/input.html", {
        "title": "Edit",
        "header": "Edit Page",
        "form": SearchForm(request.session.pop("form_data", None)),
        "inputForm": inputForm
    })


def init_search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data["searchbar"]
            entries = util.list_entries()

            for entry in entries:
                if search.lower() == entry.lower():
                    return redirect(reverse("entry", args=[entry]))

            return redirect(reverse("search") + f"?q={search}")
        else:
            request.session["form_data"] = request.POST
            return redirect(request.META.get('HTTP_REFERER'))

    return redirect(reverse("index"))


def search(request):
    query = request.GET.get('q')
    if query not in ['', None]:
        return render(request, "encyclopedia/index.html", {
            "title": "Search",
            "header": "Search Results",
            "entries": util.search_entries(query),
            "search": query,
            "form": SearchForm(),
        })

    return redirect(reverse("index"))


def random(request):
    entries = util.list_entries()
    entry = rnd.choice(entries)
    return redirect(reverse("entry", args=[entry]))

