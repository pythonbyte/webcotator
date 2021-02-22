import requests

from lxml import html
from typing import Dict


def get_picchioni_quotation() -> Dict[str, float]:
    PICCHIONI_IDS = {
        'dolar': 'USD',
        'euro': 'EUR',
        'libra': 'GBP',
        'dolar_cad': 'CAD',
        'dolar_au': 'AUD',
        'dolar_nz': 'AUD'
    }

    picchioni_url = 'https://loja.picchioni.com.br/api/integra/picchionimoedaslojavirtual?token=845c6cfa-bccb-449b-9df9-27083b306980&praca=MG&tipo=PM'
    picchioni_response = requests.get(picchioni_url)
    picchioni_json = picchioni_response.json()
    
    picchioni_data = {}
    for k, v in PICCHIONI_IDS.items():
        picchioni_data[k] = picchioni_json[v]['PM_venda']

    return picchioni_data


def get_confidence_quotation() -> Dict[str, float]:
    CONFIDENCE_IDS = {
        'dolar': 29,
        'euro': 35,
        'libra': 57,
        'dolar_cad': 43,
        'dolar_au': 45,
        'dolar_nz': 47
    }
    confidence_url = 'https://23hu4n4gq0.execute-api.sa-east-1.amazonaws.com/production/api/v1/cotacoes?idProduto={}&idCidade=4854'
    
    cofidence_data =  {}
    for k, v in CONFIDENCE_IDS.items():
        response = requests.get(
            confidence_url.format(v), 
            headers={'auth': 'ecommerce.confidence|ECommerce|null|2760|MCwCFHR9v54Zh3NSStFTH6qZQNcjRZbwAhRBcNjWyU7ufGJw62q/uN8acQL+vg=='}
        )
        cofidence_data[k] = response.json()['cotacao']

    return cofidence_data


def get_stb_quotation() -> Dict[str, float]:
    STB_IDS = {
        'dolar': '//*[@id="body-container"]/div[2]/div/section[2]/table/tbody/tr[2]/td[3]',
        'euro': '//*[@id="body-container"]/div[2]/div/section[2]/table/tbody/tr[6]/td[3]',
        'libra': '//*[@id="body-container"]/div[2]/div/section[2]/table/tbody/tr[9]/td[3]',
        'dolar_cad': '//*[@id="body-container"]/div[2]/div/section[2]/table/tbody/tr[4]/td[3]',
        'dolar_au': '//*[@id="body-container"]/div[2]/div/section[2]/table/tbody/tr[3]/td[3]',
        'dolar_nz': '//*[@id="body-container"]/div[2]/div/section[2]/table/tbody/tr[5]/td[3]'
    }
    stb_url = 'https://www.stb.com.br/servicos/conversor-de-moedas'

    stb_response = requests.get(stb_url)
    stb_tree = html.fromstring(stb_response.content)

    stb_data = {}    
    for k, v in STB_IDS.items():
        string_quotation = stb_tree.xpath(v)[0].text
        stb_data[k] = clean_quotation(string_quotation)

    return stb_data


def clean_quotation(quotation_value: str) -> float:
    return float(quotation_value.strip().replace(',', '.'))


def process_all_data():
    confidence_data = get_confidence_quotation()
    picchioni_data = get_picchioni_quotation()
    

    green_data = {}
    for k,v in picchioni_data.items():
        green_data[k] = (picchioni_data[k] + confidence_data[k]) / 2

    green_data_minus = {}
    for k,v in picchioni_data.items():
        if k == 'dolar' or k == 'euro':
            green_data_minus[k] = ((picchioni_data[k] + confidence_data[k]) / 2) - 0.02
        else:
            green_data_minus[k] = ((picchioni_data[k] + confidence_data[k]) / 2) - 0.05


    context = (
        ('picchioni', picchioni_data),
        ('confidence', confidence_data),
        ('stb', get_stb_quotation()),
        ('green', green_data),
        ('green_minus', green_data_minus),
    )

    return context