from flask import Flask, request, jsonify, Response
import subprocess
import re
import random

app = Flask(__name__)

# Função para mapear a consulta para categorias
def map_query_to_category(query):
    query = query.lower()

    mappings = {
        'compras': ['compras', 'compra', 'pedido', 'pedidos'],
        'pontos acumulados': ['pontos', 'desconto', 'pontos de desconto'],
        'dicas de pontos de desconto': ['dicas', 'dica'],
        'curiosidades sobre os produtos': ['curiosidades', 'produtos'],
        'saudacoes': ['olá', 'oi', 'tudo bem', 'como você está', 'bom dia', 'boa tarde', 'boa noite']
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
            return num1 + num2
        elif operator == '-':
            return num1 - num2
        elif operator == '*':
            return num1 * num2
        elif operator == '/':
            if num2 != 0:
                return num1 / num2
            else:
                return None  # Divisão por zero

    return None

# Rota principal para renderizar o template PHP
@app.route('/')
def index():
    try:
        result = subprocess.run(
            ["C:/xampp/php/php-cgi.exe", "C:/xampp/htdocs/Toranjinha-3/templates/index.php"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return Response(result.stdout, mimetype='text/html')
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
            calculation = handle_calculations(query)
            if calculation is not None:
                return jsonify({'response': f'O resultado é: {calculation}'})

            random_responses = [
                "Hmm, não entendi sua consulta.",
                "Você sabia que os programadores bebem em média 4 xícaras de café por dia?",
                "70% dos desenvolvedores preferem tabs em vez de espaços.",
                "O termo 'bug' foi inspirado quando um inseto causou um problema no computador de Grace Hopper.",
                "O primeiro emoji foi criado por um engenheiro japonês no final dos anos 90."
            ]
            return jsonify({'response': random.choice(random_responses)})

        user_id = 1  # Suponha que o ID do usuário seja 1 para este exemplo

        response = []
        for category in categories:
            if category == 'compras':
                response.append('Consulta de compras aqui...')
            elif category == 'pontos acumulados':
                response.append('Consulta de pontos acumulados aqui...')
            elif category == 'dicas de pontos de desconto':
                response.append('Dicas de pontos de desconto aqui...')
            elif category == 'curiosidades sobre os produtos':
                response.append('Curiosidades sobre os produtos aqui...')
            elif category == 'saudacoes':
                response.append('Saudações aqui...')
        
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'response': f'Erro ao executar consulta: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
