#!/usr/bin/env python
from bs4 import BeautifulSoup
import re
import sys
import sqlite3
from os.path import dirname, join


def main():
    doc_path = sys.argv[1]
    db_path = sys.argv[2]
    index = []  # tuples (name, type, link)

    index.extend(build_guides_index(doc_path, 'topic/index.html'))

    main_index = build_command_index(
        doc_path,
        'index.html',
        'toctree-l2',
    )

    index.extend(main_index)

    for name, _, path in main_index:
        if not path.endswith('index.html'):
            continue

        index.extend(build_command_index(
            doc_path,
            path,
            'toctree-l1',
            f'{name} ',
        ))

    write_db(index, db_path)


def build_command_index(basedir, filename, cls, prefix=''):
    index = []  # tuples (name, type, link)
    print(f'parse index from {filename}')

    with open(join(basedir, filename)) as fp:
        soup = BeautifulSoup(fp, 'html5lib')

    for tag in soup.find_all('li', attrs={'class': cls}):
        name = f'{prefix}{tag.a.string.strip()}'
        link = join(dirname(filename), tag.a.get('href'))
        index.append((name, 'Command', link))

    return index


def build_guides_index(basedir, filename):
    index = []  # tuples (name, type, link)
    print(f'parse help topics from {filename}')

    with open(join(basedir, filename)) as fp:
        soup = BeautifulSoup(fp, 'html5lib')

    for elem in soup.select('div.section#available-topics li p'):
        name = list(elem.children)[-1].lstrip(':').strip()
        link = join(dirname(filename), elem.a.get('href'))
        index.append((name, 'Guide', link))
        print(f'add guide {link}')

    return index


def write_db(index, db_path):
    print(f'write index to {db_path}')
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)')
        c.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)')
        c.executemany(
            '''INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)''',
            index)
        conn.commit()


if __name__ == '__main__':
    main()
