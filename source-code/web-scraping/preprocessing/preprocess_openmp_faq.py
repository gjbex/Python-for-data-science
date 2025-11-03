#!/usr/bin/env python
# coding: utf-8
# Script that reads the OpenMP FAQ HTML file and extracts the questions and answers.
# The output is a JSONL file with the following format:
# {"input": "question", "output": "answer"}
#
# Usage: python preprocess_faq.py openmp_faq.html > openmp_faq.jsonl
# ------------------------------------------------------------------------

import argparse
from bs4 import BeautifulSoup


def is_question_header(tag):
    return tag.name == 'h4' and tag.has_attr('id') and tag.attrs['id'].startswith('OMP')

def get_question(h4_tag):
    return h4_tag.span.text

def get_answer(h4_tag):
    answer = ''
    next_tag = h4_tag.find_next('p')
    while next_tag and next_tag.name == 'p':
        answer += next_tag.text.strip() + ' '
        next_tag = next_tag.find_next('p')
    return clean_answer(answer)

def clean_answer(text):
    text = text.replace('\n', ' ').strip()
    pos = text.find('Version 3.0 Last updated:')
    text = text[:pos]
    pos = text.find('(Quote from:')
    return text[:pos].strip()

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('html_file', help='OpenMP FAQ HTML file')
    args = arg_parser.parse_args()
    with open(args.html_file) as html_file:
        doc = BeautifulSoup(html_file, features='html.parser')
    json_strs = []
    for tag in doc.find_all(is_question_header):
        json_strs.append(f'{{"input": "{get_question(tag)}", "output": "{get_answer(tag)}"}}')
    print('\n'.join(json_strs))

if __name__ == '__main__':
    main()
