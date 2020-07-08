#!/usr/bin/env python

"""
Post-process files in the AWS CLI v2 documentation in HTML-compiled form.

WARNING: All HTML sources will be overwritten.
"""
from bs4 import BeautifulSoup
from glob2 import glob
from multiprocessing.pool import Pool
import sys
from os import path
from urllib.parse import quote as url_quote


def main():
    if len(sys.argv) < 2:
        soup = transform(str(sys.stdin.read()))
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
        soup = transform(fp)

    with open(html_file, 'w') as fp:
        fp.write(str(soup))


def transform(fp) -> BeautifulSoup:
    soup = BeautifulSoup(fp, 'html5lib')

    # create section anchors
    for tag in soup.find_all('a', attrs={'class': 'headerlink'}):
        if tag.parent.name == 'h1':
            continue

        tag['name'] = '//apple_ref/cpp/Section/' + url_quote(tag.parent.contents[0])
        tag['class'] += ['dashAnchor']

    # create option anchors
    for span in soup.select('div.section#options > p > code.docutils.literal:first-child > span'):
        anchor = soup.new_tag('a')
        anchor['name'] = '//apple_ref/cpp/Option/' + url_quote(span.string)
        anchor['class'] = ['dashAnchor']
        span.insert_before(anchor)

    # create example anchors
    for strong in soup.select('div.section#examples > p > strong:first-child'):
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

    return soup


if __name__ == '__main__':
    main()
