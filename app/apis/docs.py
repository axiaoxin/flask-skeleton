#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import render_template
from services import flatpages

docs = Blueprint('docs', __name__)


@docs.route('/')
def index():
    return render_template('docs/index.html', docs=flatpages)


@docs.route('/<path:path>/')
def doc(path):
    doc = flatpages.get_or_404(path)
    return render_template('docs/doc.html', doc=doc)


@docs.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in flatpages if tag in p.meta.get('tags', [])]
    return render_template('docs/tag.html', docs=tagged, tag=tag)
