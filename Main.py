from flask import Flask, request, jsonify, Response
import subprocess
import re
import random
from datetime import datetime
import requests

app = Flask(__name__)

# Configure a chave de API do Bing Search
BING_API_KEY = 'YOUR_BING_API_KEY'
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"

def bing_search(query, api_key):
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    return search_results.get("webPages", {}).get("value", [])

# Função para mapear a consulta para categorias
def map_query_to_category(query):
    query = query.lower()

    mappings = {
        'compras': ['compras', 'compra', 'pedido', 'pedidos'],
        'pontos acumulados': ['pontos', 'desconto', 'pontos de desconto'],
        'dicas de pontos de desconto': ['dicas', 'dica'],
        'curiosidades sobre os produtos': ['curiosidades', 'produtos'],
        'saudacoes': ['olá', 'oi', 'tudo bem', 'como você está', 'bom dia', 'boa tarde', 'boa noite'],
        'horario': ['que horas são', 'horas', 'hora', 'que hora é'],
        'data': ['que dia é hoje', 'data', 'dia', 'hoje']
    }

    detected_categories = []
    for category, keywords in mappings.items():
        for keyword in keywords:
            if keyword in query:
                detected_categories.append(category)
                break

    return detected_categories if detected_categories else ['desconhecido']

# Função para lidar com cálculos
def handle_calculations(query):
    pattern = r'(\d+)\s*([\+\-\*\/])\s*(\d+)'
    match = re.match(pattern, query)
    if match:
        num1 = float(match.group(1))
        operator = match.group(2)
        num2 = float(match.group(3))

        if operator == '+':
            return f"O resultado do cálculo {num1} + {num2} é: {num1 + num2}"
        elif operator == '-':
            return f"O resultado do cálculo {num1} - {num2} é: {num1 - num2}"
        elif operator == '*':
            return f"O resultado do cálculo {num1} * {num2} é: {num1 * num2}"
        elif operator == '/':
            if num2 != 0:
                return f"O resultado do cálculo {num1} / {num2} é: {num1 / num2}"
            else:
                return 'Erro: Divisão por zero não permitida'

    return 'Erro: Cálculo não reconhecido'

# Função para responder a perguntas gerais
def handle_general_queries(categories):
    if 'horario' in categories:
        return f"Agora são {datetime.now().strftime('%H:%M:%S')}."
    elif 'data' in categories:
        return f"Hoje é {datetime.now().strftime('%d/%m/%Y')}."
    return None

# Função para pesquisar no Bing
def search_bing(query):
    try:
        results = bing_search(query, BING_API_KEY)
        if results:
            top_result = results[0]
            return f"Encontrei isso para você: {top_result['name']} - {top_result['snippet']} ({top_result['url']})"
        else:
            return "Desculpe, não encontrei resultados relevantes."
    except Exception as e:
        return f"Erro ao pesquisar no Bing: {str(e)}"

# Rota principal para renderizar o template PHP
@app.route('/')
def index():
    try:
        result = subprocess.run(
            ["C:/xampp/php/php-cgi.exe", "C:/xampp/htdocs/Toranjinha-3/templates/index.php"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            response = Response(result.stdout, mimetype='text/html')
            response.headers['X-Powered-By'] = 'PHP/8.0.28'
            print(response.headers.get('X-Powered-By'))  # Log the header to the console
            return response
        else:
            return Response(f"Erro ao executar o script PHP: {result.stderr}", mimetype='text/plain')
    except Exception as e:
        return Response(f"Erro ao executar o script PHP: {str(e)}", mimetype='text/plain')

# Rota para lidar com as requisições POST do chatbot
@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        if 'query' not in data:
            return jsonify({'response': 'Consulta não fornecida'}), 400

        query = data['query'].lower()
        categories = map_query_to_category(query)

        if 'desconhecido' in categories:
            general_response = handle_general_queries(categories)
            if general_response:
                return jsonify({'response': general_response})
            
            calculation = handle_calculations(query)
            if calculation != 'Erro: Cálculo não reconhecido':
                return jsonify({'response': calculation})

            bing_response = search_bing(query)
            return jsonify({'response': bing_response})

        user_id = 1  # Suponha que o ID do usuário seja 1 para este exemplo

        response = []
        for category in categories:
            if category == 'compras':
                response.append(random.choice([
                    'Ah, quer saber sobre suas compras? Claro, vamos lá...',
                    'Consultando suas compras, só um segundo...',
                    'Deixe-me ver suas compras. Já te mostro...',
                    'Vamos conferir suas compras. Um momento, por favor...',
                    'Aqui estão os detalhes das suas compras...'
                ]))
            elif category == 'pontos acumulados':
                response.append(random.choice([
                    'Os pontos acumulados que você tem são...',
                    'Vamos ver quantos pontos você acumulou...',
                    'Aqui estão os seus pontos acumulados...',
                    'Verificando seus pontos acumulados, aguarde um instante...',
                    'Você tem um total de pontos acumulados de...'
                ]))
            elif category == 'dicas de pontos de desconto':
                response.append(random.choice([
                    'Dicas sobre pontos de desconto? Aqui estão algumas...',
                    'Vou te dar algumas dicas sobre como acumular mais pontos de desconto...',
                    'Aqui vão algumas dicas para você acumular mais pontos de desconto...',
                    'Quer saber como ganhar mais pontos de desconto? Veja estas dicas...',
                    'Algumas dicas úteis para acumular pontos de desconto...'
                ]))
            elif category == 'curiosidades sobre os produtos':
                response.append(random.choice([
                    'Quer saber algumas curiosidades sobre os produtos? Legal, aqui vão algumas...',
                    'Algumas curiosidades interessantes sobre os produtos para você...',
                    'Vou te contar algumas curiosidades sobre os nossos produtos...',
                    'Aqui estão algumas curiosidades sobre os produtos que temos...',
                    'Descubra algumas curiosidades sobre os produtos...'
                ]))
            elif category == 'saudacoes':
                response.append(random.choice([
                    'Oi! Tudo bem com você? Em que posso ajudar hoje?',
                    'Olá! Como você está? Posso te ajudar com alguma coisa?',
                    'Oi, tudo certo? Precisa de alguma ajuda?',
                    'Olá! Como vai? O que posso fazer por você hoje?',
                    'Oi! Como está? Me diga como posso te ajudar.'
                ]))

        general_response = handle_general_queries(categories)
        if general_response:
            response.append(general_response)

        return jsonify({'response': ' '.join(response)})

    except Exception as e:
        return jsonify({'response': f'Erro ao executar consulta: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
