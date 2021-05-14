from typing import Union, Optional, List

from wechaty_puppet import get_logger
import requests

log = get_logger('GptChitChat')

def get_gpt_response(sentence: str, length: 30) -> Union[str, None]:
    log.info('GprChitchatPlugin getGptResponse(%s, %s)', sentence, length)

    # 3. send the encoded sentence result
    data = {
        "instances": [{
        "length": len(sentence) + length + 3,
        "tokens": ['<S1>'] + list(sentence) + ['</S1>', '<S2>']
        }],
    }
    res = requests.post('http://dev.chatie.io:8501/v1/models/chat:predict', json=data)

    # 4. decode the response from the gpt
    data = res.json()
    if 'predictions' not in data:
        return None
    
    tokens: List[str] = data['predictions'][0]['tokens']

    start_index = tokens.index('<S2>')
    end_index = tokens.index('</S2>')
    decoded_text = tokens[start_index + 1: end_index]
    decoded_text = ''.join(decoded_text)
    decoded_text = decoded_text.replace('</s>', '')
    return decoded_text
