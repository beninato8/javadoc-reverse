from bs4 import BeautifulSoup
import bs4
import re
import os
from os import listdir
from os.path import isfile, join

nl = '\n'

def nest_contents(c):
    l = ''
    if c == None:
        return ''
    for x in c:
        if isinstance(x, bs4.element.NavigableString):
            l += x
        elif isinstance(x, bs4.element.Tag):
            l += nest_contents(x.contents)
    return l


def java_sub(s):
    s = re.sub('\s+', ' ', s)
    new_s = ''
    for x in re.split('\s', s):
        if re.search('java\.([^\.]+\.?)+', x):
            x = re.sub(r'java\.([^\.]+\.)+([^\.\n]+)',r'\2', x)
        new_s += x + ' '
    return new_s[:-1]

path_in = './jdoc_in/'
path_in = os.path.abspath(path_in) + '/'
try:
    files = [f for f in listdir(path_in) if isfile(join(path_in, f))]
except Exception as e:
    print(f'No files found in the input directory {path_in}')
    exit()

files = [f for f in files if len(f) > 4 and f[-5:] == '.html']
if not files:
    print(f'No javadoc (.html) files found in the input directory {path_in}')
    exit()

for name in files:
# name = 'BankAccount'
    path_out = 'jdoc_out/'
    with open(f'{path_in}{name}', 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    constructors = []

    methods = []



    for desc in soup.find_all('div', {'class':'description'}):
        class_title = nest_contents(desc.find('pre')).replace('\n', ' ').replace(' extends java.lang.Object', '')
        class_desc = nest_contents(desc.find('div'))

    class_header = f"""/**
 * {class_desc}
 */
{class_title} {{
"""
class_header = re.sub(r'\s+', ' ', class_header)

    for title in soup.find_all('h3'):
        if 'Constructor Detail' in title.contents:
            # print(title.parent)
            method = title.parent.find('pre')
            constructor = re.sub(' +', ' ', method.contents[0].replace('\n', ''))
            constructor = re.sub('java\.[a-z]+\.', '', constructor)
            description  = title.parent.find('div', {'class':'block'})
            description = re.sub('\n *', ' ', ''.join(nest_contents(description)))

            # print(constructor)
            ats = []

            if title.parent.find('dl'):
                at = [x for x in title.parent.find('dl').children if x != '\n']
                current_key = ''
                for child in at:
                    if child.name == 'dt':
                        current_key = child.contents[0]['class'][0].replace('Label', '')
                    else:
                        ats.append(f'@{current_key} {child.contents[0].contents[0]}{re.sub(f"{nl} +", " ", child.contents[1])}')

            # print(ats)
            # print(constructor)
            # print(description)
            txt = f"""/**
 * {description}
 * {f"{nl} * ".join(ats)}
 */
{constructor} {{

}}"""
            constructors.append(txt)
        if 'Method Detail' in title.contents:
            for i, method in enumerate(title.parent.find_all('li', {'class':'blockList'})):
                header = nest_contents(method.find('pre').contents)
                header = java_sub(header)
                # exit()
                desc = method.find('div', {'class':'block'}).contents[0]
                desc = re.sub('\n *', ' ', ''.join(desc))

                # print(method.prettify())
                # exit()
                at = [x for x in method.find('dl').children if x != '\n']
                ats = []
                current_key = ''
                for child in at:
                    if child.name == 'dt':
                        current_key = child.contents[0]['class'][0].replace('Label', '')
                    else:
                        if current_key == 'return':
                            ats.append(f'@{current_key} {re.sub(f"{nl} +", " ", child.contents[0])}')
                        else:
                            ats.append(f'@{current_key} {child.contents[0].contents[0]}{re.sub(f"{nl} +", " ", child.contents[1])}')
                # print(ats)
                # print(header)
                # print(desc)
                txt = f"""/**
 * {desc}
 * {f"{nl} * ".join(ats)}
 */
{header} {{

}}"""
                methods.append(txt)
                # exit()
    # print(soup.prettify())

    out_name = name.replace('.html', '')
    os.makedirs(os.path.dirname(f'{path_out}{out_name}.java'), exist_ok=True)
    with open(f'{path_out}{out_name}.java', 'w+') as f:
        f.write(f'{class_header}')
        f.write('\n')
        for x in constructors:
            for y in x.split('\n'):
                f.write(f'    {y}')
                f.write('\n')
            f.write('\n')

        for x in methods:
            for y in x.split('\n'):
                f.write(f'    {y}')
                f.write('\n')
            f.write('\n')
        f.write('\n')
        f.write(f'}}')

