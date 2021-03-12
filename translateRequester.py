import json as js
import re
from typing import List

import requests as r
from PIL import Image

from container import Container
from error import *
import pytesseract as ocr


class JsonFromImg:
    status: str


yxResponse = {
    'blocks': {
        'boxes': []
    }
}

ocr.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class TranslateRequester:

    def __init__(self, c: Container):
        try:
            stored_sid = c.config['sid']
        except Exception:
            stored_sid = ''

        if stored_sid:
            self.revSid = stored_sid
            return

        res: r.Response = r.get("https://translate.yandex.ru/?lang=en-ru&text=his")
        sid_matching = re.search('SID:\s?\'([^\']+)\'', res.content.decode('utf8'))
        if not sid_matching:
            self.revSid = 'b7787584.5fa58e04.22563b21.74722d696d616765'
            return

        sid_val = sid_matching.groups()[0]
        sid_split = sid_val.split('.')
        sid_split = map(lambda x: x[::-1], sid_split)
        self.revSid = '.'.join(sid_split)
        c.config['sid'] = self.revSid

    def img_to_txt(self, img):
        img = Image.fromarray(img)
        txt: str = ocr.image_to_string(img, config=r'--psm 6', lang='eng')
        txt = txt.replace('|', 'l')
        txt = txt.replace('l]', 'll')
        canonical_text = ''
        rows: List[str] = txt.split("\n")
        for i in range(len(rows)):
            row = rows[i]
            row = re.sub(r'.FC.<([^>]+)>', r'\1: ', row)
            row = re.sub(r'\(@([^)]+)\)', r'\1: ', row)
            row = re.sub(r'[^\w()[\]\s.,`\'":!?-]', '', row)
            row = re.sub(r's{3,}', 's', row)
            is_new_sentence = re.search('\d+:\d+', row)

            if is_new_sentence:
                row = "\n" + row
            else:
                row = ' ' + row

            canonical_text += row

        canonical_text = canonical_text.strip()
        if len(canonical_text) < 25:
            return ''

        return canonical_text

    def img_to_json(self, data):
        img = Image.fromarray(data)
        files = {'files': ('chat.jpg', img.tobytes(), 'image/jpeg')}
        res = r.post(f"https://translate.yandex.net/ocr/v1.1/recognize?srv=tr-image&sid={self.revSid}&lang=en",
                     files=files)
        try:
            return res.json()
        except BaseException:
            raise RequesterError

    def translate_image(self, data) -> list:
        # json = self.img_to_json(data)
        # text = self.json_to_text(json)
        text = self.img_to_txt(data)
        print(text)
        # translated_text = text
        translated_text = self.translate_text(text)
        return translated_text.split("\n")

    def translate_text(self, text) -> str:
        if not text:
            raise NoTextError('No text to translate')

        data = {'text': text, 'options': 0}
        res = r.post(
            f"https://translate.yandex.net/api/v1/tr.json/translate?id={self.revSid}\
            -0-0&srv=tr-image&lang=en-ru&reason=ocr&format=text",
            data=data)
        return res.json()['text'][0]

    def json_to_text(self, json):

        try:
            json['data']
        except BaseException as e:
            if str(e).find('Bad argument: file'):
                raise BadFile
            raise RequesterError('Invalid json from image parser. Given: ' + js.dumps(json))

        parts = []
        for block in json['data']['blocks']:
            for box in block['boxes']:
                text = box['text']
                match = re.search("([\[\]\s\d:]*)?([^\[\]]*)", text)
                timestamp = match.groups()[0]

                if not match.groups()[1]:
                    continue

                search_speaker = re.search("([^:]+):(.+)", match.groups()[1])
                if not search_speaker:
                    speaker = None
                else:
                    speaker = search_speaker.groups()[0]

                if timestamp and not speaker:
                    continue

                if not speaker:
                    row = " "
                else:
                    row = "\n"

                row += match.groups()[1]
                if not len(parts):
                    parts = [row]
                else:
                    parts.append(row)

        text = ''
        for part in parts:
            if not text:
                text = part
                continue
            text += part

        return text


if __name__ == "__main__":
    t = TranslateRequester()
