#/usr/bin/env python3

import re
import requests
from pathlib import Path
from datetime import date
from fpdf import FPDF

archives = Path('./archives')

def make_pdf(name, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Courier', size=12)
    pdf.write(5, content)
    pdf.output(str(name))


def get_html(url):
    req = requests.get(url)
    if req.status_code == 404: 
        print('Oops!! 404')
        exit(1)
    html = req.text
    head = re.search('class="cnnBodyText">(.*)<\\/P>', html).groups()[0]
    body = re.search('class="cnnBodyText">(.*\n.*)<\\/div>', html).groups()[0]
    body = re.sub('<br>', '\n', body)
    content = head + '\n\n' + body
    return content


def check_file_exist(fn):
    return fn.exists()


def pull():
    today = str(date.today()).split('-')
    # script-2019-03-07.pdf
    fn = 'script-' + '-'.join(x for x in today) + '.pdf'
    print('Pulling %s' % fn)
    fn = archives / fn
    if check_file_exist(fn): 
        print('File already exist')
        exit(1)

    partial = today[0][2:] + today[1] + '/' + today[2]
    url = 'http://transcripts.cnn.com/TRANSCRIPTS/' + partial + '/sn.01.html'
    print('Url %s' % url)
    content = get_html(url)
    make_pdf(fn, content)
    print('Pulling script %s job done.' % fn)


if __name__ == '__main__':
    pull()

