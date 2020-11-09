from typing import Union, Optional

from wechaty_puppet import get_logger
from tokenizers import BertWordPieceTokenizer, Tokenizer
import requests

log = get_logger('GptChitChat')
__tokenizer__: Optional[Tokenizer] = None


def get_tokenizer() -> Tokenizer:
    global __tokenizer__
    if not __tokenizer__:
        log.info('GprChitchatPlugin get_tokenizer()')
        __tokenizer__ = BertWordPieceTokenizer.from_file('./skills/gpt_chitchat/clue-vocab.txt')
    return __tokenizer__


def get_gpt_response(sentence: str, length: 30) -> Union[str, None]:
    log.info('GprChitchatPlugin getGptResponse(%s, %s)', sentence, length)

    # 1. get the tokenizer
    tokenizer = get_tokenizer()

    # 2. encode the sentence
    encode_result = tokenizer.encode(sentence)

    # 3. send the encoded sentence result
    data = {
        "instances": [{
            "inp": encode_result.ids,
            "length": length
        }]
    }
    res = requests.post('http://dev.chatie.io:8506/v1/models/gpt:predict', json=data)

    # 4. decode the response from the gpt
    data = res.json()
    if 'predictions' not in data:
        return None
    decoded_text = tokenizer.decode_batch(data['predictions'])[0]

    # 5. remove the blanks in decoded text
    decoded_text = decoded_text.replace(' ', '')
    return decoded_text
