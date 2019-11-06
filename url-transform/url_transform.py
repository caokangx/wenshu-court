import execjs
import json

config_file = open('url-transform/config/constants.json', encoding='utf-8')

# config_file = open('config/constants.json', encoding='utf-8')

config_json = json.loads(config_file.read())

transform_url_method_name = config_json['transformUrlName']


def get_transformed_url(url: str) -> str:
    transformed_url = execjs.compile(open(r"url-transform/index.js").read()).call(
        transform_url_method_name, url)
    return transformed_url


print(get_transformed_url("test"))
