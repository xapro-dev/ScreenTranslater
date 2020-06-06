import pip._vendor.requests as r
import re
from error import RequesterError

class JsonFromImg:
    status: str
    data: {
        'blocks': {
            'boxes': []
        }
    }

class TranslateRequester:

    def imgToJson(self, data):
        files = {'files': ('chat.jpg', data, 'image/jpeg')}
        res = r.post("https://translate.yandex.net/ocr/v1.1/recognize?srv=tr-image&sid=10e43d82.5ed3d833.512f68a8&lang=*", files=files, verify=False)
        return res.json()

    def translate(self, data) -> list:
        json = self.imgToJson(data)
        text = self.jsonToText(json)
        translatedText = self.translateText(text)
        return translatedText.split("\n")


    def translateText(self, text) -> str:
        if not text:
            raise RequesterError('No text to translate')

        data = {'text': text, 'options': 0}
        res = r.post("https://translate.yandex.net/api/v1/tr.json/translate?id=10e43d82.5ed3d833.512f68a8-0-0&srv=tr-image&lang=en-ru&reason=ocr&format=text", data=data, verify=False)
        return res.json()['text'][0]


    def jsonToText(self, json):

        try:
            json['data']
        except:
            raise RequesterError('No json from image parser')
        
        parts = []
        for block in json['data']['blocks']:
            for box in block['boxes']:
                text = box['text']
                match = re.search("([\[\]\s\d:]*)?([^\[\]]*)", text)
                timestamp = match.groups()[0]

                if not match.groups()[1]:
                    continue
                
                searchSpeaker = re.search("([^:]+):(.+)", match.groups()[1])
                if not searchSpeaker:
                    speaker = None
                else:
                    speaker = searchSpeaker.groups()[0]
                
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
    file = open('tmp.jpg', 'rb')
    t = TranslateRequester()
    print(t.translate(file))
