#!/usr/bin/env python

"""
Post-process files in the AWS CLI v2 documentation in HTML-compiled form.

WARNING: All HTML sources will be overwritten.
"""
import itertools

from bs4 import BeautifulSoup, ResultSet
from glob2 import glob
from multiprocessing.pool import Pool
import re
import sys
from os import path
from urllib.parse import quote as url_quote


def main():
    if len(sys.argv) < 2:
        soup = BeautifulSoup(str(sys.stdin.read()))
        transform(soup)
        transform_config_vars(soup)
        print(soup.prettify())
        return

    doc_path = sys.argv[1]
    html_files = (
        glob(path.join(doc_path, 'reference/**/*.html')) +
        glob(path.join(doc_path, 'topic/**/*.html')))
    assert html_files, 'no transformable files found'

    with Pool() as pool:
        pool.imap_unordered(transform_one, html_files)
        pool.close()
        pool.join()


def transform_one(html_file):
    print(f'process {html_file}...')

    with open(html_file) as fp:
        soup = BeautifulSoup(fp, 'html5lib')

    transform(soup)

    if html_file.endswith('topic/config-vars.html'):
        transform_config_vars(soup)

    with open(html_file, 'w') as fp:
        fp.write(str(soup))


def transform(soup: BeautifulSoup):
    # create section anchors
    for tag in soup.find_all('a', attrs={'class': 'headerlink'}):
        if tag.parent.name == 'h1':
            continue

        tag['name'] = '//apple_ref/cpp/Section/' + url_quote(tag.parent.contents[0])
        tag['class'] += ['dashAnchor']

    def select_section(section: str, rest: str):
        """
        At some point, the AWS CLI documentation started using <span id="section">
        instead of <div class="section" id="section">. This helper provides
        support for both at the same time.
        """

        return itertools.chain(
            soup.select(f'div.section#{section} {rest}'),
            soup.select(f'section#{section} {rest}'),
        )

    # create option anchors
    for span in select_section('options', '> p > code.docutils.literal:first-child > span'):
        anchor = soup.new_tag('a')
        anchor['name'] = '//apple_ref/cpp/Option/' + url_quote(span.string)
        anchor['class'] = ['dashAnchor']
        span.insert_before(anchor)

    # create example anchors
    for strong in select_section('examples', '> p > strong:first-child'):
        anchor = soup.new_tag('a')
        anchor['name'] = '//apple_ref/cpp/Guide/' + url_quote(strong.string)
        anchor['class'] = ['dashAnchor']
        strong.insert_before(anchor)

    # remove navbar
    soup.find('div', attrs={'class': 'navbar-fixed-top'}).clear()
    body_tag = soup.find('body')
    body_tag['style'] = body_tag.get('style', []) + ['padding-top: 0;']

    # remove sidebar
    soup.find('div', attrs={'class': 'sphinxsidebar'}).clear()
    body_div = soup.find('div', attrs={'class': 'body'})
    body_div['style'] = body_div.get('style', []) + ['width: 100%']

    # override title (drop the initial "aws" prefix)
    breadcrumbs = [
        span.string
        for span in soup.select('div.body > p:first-child a span')]
    if len(breadcrumbs) > 0 and breadcrumbs[0] == 'aws':
        breadcrumbs = breadcrumbs[1:]
    title = soup.find('title')
    breadcrumbs.append(title.string.split('—')[0].strip())
    title.string = ' '.join(breadcrumbs)


def transform_config_vars(soup: BeautifulSoup):
    # link the first occurrence of each variable
    # manually maintain the set to ensure ordering
    visited = set()
    for tag in soup.find_all(string=re.compile('^AWS_[A-Z_]+$')):
        if tag.string in visited:
            continue
        else:
            visited.add(tag.string)

        anchor = soup.new_tag('a')
        anchor['id'] = tag.string  # anchor from index
        anchor['name'] = '//apple_ref/cpp/Environment/' + url_quote(tag.string)
        anchor['class'] = ['dashAnchor']
        tag.insert_before(anchor)


if __name__ == '__main__':
    main()
