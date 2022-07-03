from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

import random
from markdown2 import markdown

from . import util


def index(request):
    '''
    Home page. Renders template to display all entries.
    '''
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def display_page(request, name):
    '''
    Displays a single article and adds buttons to 
    edit, revert, and go home
    '''
    article = util.get_entry(name)
    # check if we actually found an article
    if not article:
        # Redirect user to home page
        messages.add_message(request, messages.INFO, 
                             f"The Wiki doesn't have an article titled {name}")
        return HttpResponseRedirect(reverse("encyclopedia:index"))
    else:
        context = {
            "title": name,
            "article": markdown(article)
        }
        return render(request, "encyclopedia/display.html", context)


def search(request):
    '''
    Search for an article by retrieving all titles and 
    looking for substrings in them. Then display list
    or (if 1 found) single article.
    '''
    if request.method == "POST":
        query = request.POST["q"]
        all_articles = util.list_entries()
        articles_list = [title for title in all_articles if query.lower() in title.lower()]
        if len(articles_list) == 0:
            messages.add_message(request, messages.INFO, 
                                 "The Wiki doesn't have any responsive articles")
            return HttpResponseRedirect(reverse("encyclopedia:index"))
        elif len(articles_list) == 1:
            return HttpResponseRedirect(reverse("encyclopedia:display_page", 
                                                kwargs={'name': articles_list[0]}))
        else:
            context = {
                "query": query,
                "articles": articles_list
            }
            return render(request, "encyclopedia/search_result.html", context)
    else:
        return HttpResponseRedirect(reverse("encyclopedia:index"))


def random_page(request):
    '''
    Display a random article.
    '''
    all_articles = util.list_entries()
    r = random.randrange(len(all_articles))
    return HttpResponseRedirect(reverse("encyclopedia:display_page", 
                                        kwargs={'name': all_articles[r]}))


def edit(request, name):
    '''
    Display edit template (get) and receive edited text (post)
    '''
    if request.method == "POST":
        if request.POST["myedit"]:
            # save entry after stripping out windows CR, which seems to be
            # incorrectly added by django windows server or python windows
            util.save_entry(name, request.POST["myedit"].replace('\r\n', '\n'))
            messages.add_message(request, messages.INFO, 
                                 "Edit saved")
            return HttpResponseRedirect(reverse("encyclopedia:display_page", 
                                                kwargs={'name': name}))
        # if blank fall through to edit again
    else:    
        article = util.get_entry(name)
        context = {
            "title": name,
            "article": article
        }
        return render(request, "encyclopedia/edit.html", context)


def new(request):
    '''
    Display new article template and save new article
    '''
    if request.method == "POST":
        # make sure we have filled-out fields
        if "myedit" in request.POST and "title" in request.POST:
            article = request.POST["myedit"]
            name = request.POST["title"]
            # check if already exists
            all_articles = util.list_entries()
            articles_list = [title for title in all_articles if name.lower() == title.lower()]
            # article doesn't already exist - we can save it
            if len(articles_list) == 0:
                # save entry after stripping out windows CR, which seems to be
                # incorrectly added by django windows server or python windows
                util.save_entry(name, article.replace('\r\n', '\n'))
                messages.add_message(request, messages.INFO, "Article saved")
                return HttpResponseRedirect(reverse("encyclopedia:display_page", 
                                                    kwargs={'name': name}))
            # article exists - give error message and fall though to edit again
            else:
                messages.add_message(request, messages.INFO, "That article exists and can't be added")
        # fall through to edit again
    else:
        name = ""
        article = ""
    context = {
        "title": name,
        "article": article
    }
    return render(request, "encyclopedia/new.html", context)