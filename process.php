<?php
session_start();
ob_start();
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

include_once('conexao.php'); // Certifique-se de que este arquivo define a variável $mysqli

header('Content-Type: application/json');

function respondWithError($message)
{
    ob_clean();
    echo json_encode(['response' => $message]);
    exit;
}

function mapQueryToCategory($query)
{
    $query = strtolower($query);

    $mappings = [
        'compras' => ['compras', 'compra', 'pedido', 'pedidos'],
        'pontos acumulados' => ['pontos', 'desconto', 'pontos de desconto'],
        'dicas de pontos de desconto' => ['dicas', 'dica'],
        'curiosidades sobre os produtos' => ['curiosidades', 'produtos'],
        'saudacoes' => ['olá', 'oi', 'tudo bem', 'como você está', 'bom dia', 'boa tarde', 'boa noite']
    ];

    $detectedCategories = [];
    foreach ($mappings as $category => $keywords) {
        foreach ($keywords as $keyword) {
            if (strpos($query, $keyword) !== false) {
                $detectedCategories[] = $category;
                break;
            }
        }
    }

    return empty($detectedCategories) ? ['desconhecido'] : $detectedCategories;
}

function handleCalculations($query)
{
    // Simples calculadora
    if (preg_match('/(\d+)\s*([\+\-\*\/])\s*(\d+)/', $query, $matches)) {
        $num1 = $matches[1];
        $operator = $matches[2];
        $num2 = $matches[3];
        switch ($operator) {
            case '+':
                return $num1 + $num2;
            case '-':
                return $num1 - $num2;
            case '*':
                return $num1 * $num2;
            case '/':
                return $num1 / $num2;
        }
    }
    return null;
}

try {
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // Operações de Login
        if (isset($_POST['email']) && isset($_POST['senha'])) {
            if (!isset($mysqli)) {
                respondWithError('Erro na conexão com o banco de dados');
            }

            $email = $mysqli->real_escape_string($_POST['email']);
            $senha = $mysqli->real_escape_string($_POST['senha']);

            $sql_code = "SELECT * FROM usuarios WHERE email = '$email'";
            $sql_query = $mysqli->query($sql_code);
            if (!$sql_query) {
                respondWithError("Falha na execução do código: " . $mysqli->error);
            }
            $quantidade = $sql_query->num_rows;

            if ($quantidade == 1) {
                $usuario = $sql_query->fetch_assoc();

                if (password_verify($senha, $usuario['senha'])) {
                    // Iniciar a sessão e armazenar informações relevantes
                    $_SESSION['email'] = $usuario['email'];
                    $_SESSION['nome'] = $usuario['nome'];
                    $_SESSION['image'] = $usuario['image'];
                    $_SESSION['user_id'] = $usuario['User_id'];

                    // Redirecionar para a página home
                    header("Location: meu primeiro site.php");
                    exit();
                } else {
                    // Defina a mensagem de erro para senha incorreta
                    $_SESSION['error_message'] = "Senha incorreta -_-";
                    header('Location: LoginToranjão.php');
                    exit();
                }
            } else {
                // Defina a mensagem de erro para email não encontrado
                $_SESSION['error_message'] = "E-mail não Existente";
                header('Location: LoginToranjão.php');
                exit();
            }
        }
    }

    // Logout
    if (isset($_POST['type']) && $_POST['type'] == "logout") {
        $_SESSION['email'] = "";
        $_SESSION['nome'] = "";
        $_SESSION['usuario_id'] = "";
        // Redirecionar para a página inicial
        header("Location: meu primeiro site.php");
        exit();
    }

    $input = json_decode(file_get_contents('php://input'), true);
    if (!isset($input['query'])) {
        respondWithError('Consulta não fornecida');
    }

    $query = strtolower($input['query']);
    error_log("Received query: " . $query); // Adicione esta linha para depuração
    $categories = mapQueryToCategory($query);

    if (in_array('desconhecido', $categories)) {
        // Tentativa de cálculo
        $calculation = handleCalculations($query);
        if ($calculation !== null) {
            echo json_encode(['response' => ["O resultado é: $calculation"]]);
            exit;
        }

        // Resposta padrão
        $random_responses = [
            "Hmm, não entendi sua consulta. Mas sabia que os programadores bebem em média 4 xícaras de café por dia? ☕",
            "Hmm, não entendi sua consulta. Mas sabia que 70% dos desenvolvedores preferem tabs em vez de espaços? 🔍",
            "Hmm, não entendi sua consulta. Sabia que o termo 'bug' foi inspirado quando um inseto causou um problema no computador de Grace Hopper? 🐞",
            "Hmm, não entendi sua consulta. Você sabia que o primeiro emoji foi criado por um engenheiro japonês no final dos anos 90? 🤯"
        ];
        echo json_encode(['response' => [$random_responses[array_rand($random_responses)]]]);
        exit;
    }

    $response = [];
    $user_id = $_SESSION['user_id'] ?? 0;
    error_log("User ID: " . $user_id); // Adicione esta linha para depuração

    foreach ($categories as $category) {
        switch ($category) {
            case 'compras':
                $sql = "SELECT * FROM carrinho WHERE user_id = $user_id";
                $result = $mysqli->query($sql);
                if ($result->num_rows > 0) {
                    while ($row = $result->fetch_assoc()) {
                        $response[] = "Produto: " . $row['produto'] . " - Quantidade: " . $row['quantidade'];
                    }
                } else {
                    $response[] = 'Olha, infelizmente você ainda não efetuou uma compra, e nem um carrinho 😒😒😒';
                }
                break;
            case 'pontos acumulados':
                $sql = "SELECT pontos_desconto FROM usuarios WHERE user_id = $user_id";
                $result = $mysqli->query($sql);
                if ($result->num_rows > 0) {
                    $row = $result->fetch_assoc();
                    $response[] = "Você tem " . $row['pontos_desconto'] . " pontos de desconto.";
                } else {
                    $response[] = 'Nenhum ponto acumulado encontrado';
                }
                break;
            case 'dicas de pontos de desconto':
                $response[] = "Faça compras frequentemente para acumular mais pontos!";
                $response[] = "Participe de promoções especiais para ganhar pontos de desconto extras!";
                break;
            case 'curiosidades sobre os produtos':
                $response[] = "Nosso produto mais vendido é o Toranjão 3000!";
                $response[] = "Os produtos da linha Eco são feitos com materiais reciclados!";
                break;
            case 'saudacoes':
                $response[] = "Olá! Como posso ajudar você hoje?";
                $response[] = "Oi! Tudo bem com você?";
                break;
            default:
                $response[] = 'Consulta não reconhecida';
        }
    }

    echo json_encode(['response' => $response]);
    exit;
} catch (Exception $e) {
    respondWithError('Erro ao executar consulta: ' . $e->getMessage());
}

ob_end_flush();
