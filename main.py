from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import sympy as sy
import math


app = Flask(__name__) #explicar pq


dados_conectar = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=(LocalDB)\MSSQLLocalDB;"
    "Database=pythonsiteSQL;"
    "Trusted_Connection=yes"
)

conectar = pyodbc.connect(dados_conectar)
print("Conexão Bem sucedida!")

cursor = conectar.cursor()
#ter como globais para as usar em varias funções
r = None
#expessura do estrato superior
h = None
#comprimento da vara em string
valor_l_s = None
#resistividade superior
rs = None
#resistividade média
rs = None

@app.route("/verTabela")
def tabela():
    cursor.execute("Select TipoSolo, ResistividadeTipica, LimiteNormaisMin, LimiteNormalMax  From solo")
    tabela = cursor.fetchall()
    return render_template("tabela.html", tabela=tabela)
@app.route("/")
def menu():
    return render_template("MenuIncial.html")
#criar a homepage
#route -> link da página/caminho depois do dominio xxxx.com/utilizador
@app.route("/home") #nome do site é app, route definir a página
#função -> o que quero fazer na homepage
def homepage():
    return render_template("VerificarSolo.html")
#rodar site

def supinf(array):
    resistividadeInf = min(array)
    resistividadeSup = max(array)
    #1.1 pois se fizermos os 10% do array[0] vamos obter o valor extra desse aumento ou diminuição, depois somado ao array0 vamos obter os 1.1, isto é 110%, o aumento ou diminuição de 10%

    indice_max = array.index(resistividadeSup)
    indice_min = array.index(resistividadeInf)

    # Verificar se o ponto máximo tem aumento ou diminuição de 10%
    if indice_max > 0 and (resistividadeSup <= 1.1 * array[indice_max - 1] or resistividadeSup >= 0.9 * array[indice_max - 1]):
        # Calcular a média entre o ponto máximo e seu adjacente
        ponto_adjacente = array[indice_max - 1]
        media_maximo = (resistividadeSup + ponto_adjacente) / 2
    else:
        media_maximo = resistividadeSup

        # Verificar se o ponto mínimo tem aumento ou diminuição de 10%
        if indice_min < len(array) - 1 and (
                resistividadeInf <= 1.1 * array[indice_min + 1] or resistividadeInf >= 0.9 * array[indice_min + 1]):
            # Calcular a média entre o ponto mínimo e seu adjacente
            ponto_adjacente = array[indice_min + 1]
            media_minimo = (resistividadeInf + ponto_adjacente) / 2
        else:
            media_minimo = resistividadeInf

    print("Resistividade Superior:", resistividadeSup)
    print("Resistividade Inferir:", resistividadeInf)

    return resistividadeSup, resistividadeInf

@app.route("/SoloHomogeneo", methods=['POST'])
def soloHomogenio():
    global valor_l_s, rs
    formula = request.form['formula']
    d = 0.08
    xn = 1.5
    # resistencia do solo
    r = 20

    # verificar
    v = sy.Symbol('v')

    # verificar o tipo de geometria escolhida pelo utilizador
    if formula == 'vara':
        equacao = (rs / (4 * math.pi * v)) * sy.log((2 * v) / d) - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 4
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Comprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == 'varas':
        return render_template("calculoGeometriaVaras.html")

    elif formula == 'varas2':
        return render_template("calculoGeometriaVaras2.html")

    elif formula == 'cabo':

        parte1 = (rs / (4 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((4 * v) / d) + sy.log((4 * v) / d) - 2 + (d / (2 * v)) - (d ** 2 / 16 * v ** 2) + (
                    d ** 2 / 512 * v ** 4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 5
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Comprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == 'caboReto':

        parte1 = (rs / (4 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v) / d) + sy.log((2 * v) / d) - 0.2373 + 0.2146 * (d / (v)) + 0.1035 * (
                    d ** 2 / v ** 2) - 0.0424 * (d ** 4 / v ** 4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Comprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == 'tres_pontas':

        parte1 = (rs / (6 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v) / d) + sy.log((2 * v) / d) + 1.071 - 0.2009 * (d / (v)) + 0.238 * (
                    d ** 2 / v ** 2) - 0.054 * (d ** 4 / v ** 4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Comprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == '4_pontas':

        parte1 = (rs / (8 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v) / d) + sy.log((2 * v) / d) + 2.912 - 1.071 * (d / (v)) + 0.645 * (
                    d ** 2 / v ** 2) - 0.145 * (d ** 4 / v ** 4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Comprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == '6_pontas':

        parte1 = (rs / (12 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v) / d) + sy.log((2 * v) / d) + 6.851 - 3.128 * (d / (v)) + 1.758 * (
                    d ** 2 / v ** 2) - 0.490 * (d ** 4 / v ** 4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Comprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == '8_pontas':

        parte1 = (rs / (16 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v) / d) + sy.log((2 * v) / d) + 10.98 - 5.51 * (d / (v)) + 3.26 * (
                    d ** 2 / v ** 2) - 1.17 * (d ** 4 / v ** 4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Comprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == 'circulo':
        return render_template("calculoGeometriaCirculo.html")

    texto = f"O comprimento necessário para a {formula} é de {valor_l_s} metros"

    return render_template("calculoGeometriaVaras2.html", texto=texto, valor_l_s=valor_l_s)

@app.route("/verificarsolo", methods=['POST'])
def calculaSoloHomogeneo():
    global r, h
    ...
    #criar array para manipular mais facilmente as coordenadas
    p = []
    r = []

    p1 = float(request.form.get('profundidade1'))#ir buscar o ponto ao form da pagina
    p.append(p1)#adicionar o ponto ao array
    p2 = float(request.form.get('profundidade2'))
    p.append(p2)
    p3 = float(request.form.get('profundidade3'))
    p.append(p3)
    p4 = float(request.form.get('profundidade4'))
    p.append(p4)

    r1 = float(request.form.get('resistividade1'))
    r.append(r1)
    r2 = float(request.form.get('resistividade2'))
    r.append(r2)
    r3 = float(request.form.get('resistividade3'))
    r.append(r3)
    r4 = float(request.form.get('resistividade4'))
    r.append(r4)

    rmedia = (r1 + r2 + r3 + r4)/4
    print(f"Resistividade média {rmedia}")

    # calcular o declive dos pontos
    declive = np.gradient(r, p)

    # comparar para ver se realmente existe declives com um aumento acima de 20%, que seja bastante considravel
    # inicialmente consideralas falsas
    d_acima = False
    d_abaixo = False
    ponto_diferenca = []  # guardar os pontos(abcissa) num array para depois descobrir os pontos com esse aumento ou diminuição

    # calcular e comparar
    for i in range(len(declive) - 1):
        diferenca = (declive[i + 1] - declive[i]) / declive[i]
        # print("diferença: ", diferenca)
        if (diferenca > 0.33) and (diferenca < 0.9) or (diferenca > 1):
            d_acima = True
            ponto_acima = (p[i])  # ir buscar o ponto(abcissa) onde registou o aumento
            ponto_diferenca.append(ponto_acima)  # Guardar esses pontos no array
            print("ponto para calcular o h:", ponto_acima)
            # passar esse ponto para a folha html depois!!!!!!!
        elif (diferenca < -0.33) and (diferenca > -0.9) or (diferenca < -1):
            d_abaixo = True
            ponto_acima = (p[i])  # ir buscar o ponto(abcissa) onde registou o aumento
            ponto_diferenca.append(ponto_acima)  # Guardar esses pontos no array
            print("ponto para calcular o h:", ponto_acima)


    # Encontrar os pontos de inflexão
    ponto_inflexao = []
    if (d_abaixo==True) or (d_acima==True):
        for i in range(1, len(p) - 1):
            if (declive[i] > 0 and declive[i + 1] < 0) or (declive[i] < 0 and declive[i + 1] > 0):
                y = p[i]
                x = r[i]
                ponto_inflexao.append((x, y))

        coordenadasX = p.copy()
        coordenadasY = r.copy()

        # Remover pontos duplicados
        coordenadasX, indices = np.unique(coordenadasX, return_index=True)
        coordenadasY = np.array(coordenadasY)[indices]

        # Interpolar os pontos para obter uma curva suave
        f = interp1d(coordenadasX, coordenadasY, kind='cubic')
        p_interp = np.linspace(min(coordenadasX), max(coordenadasX), 100)
        r_interp = f(p_interp)

        # Cálculo dos pontos de inflexão usando a segunda derivada
        df_interp = np.gradient(np.gradient(r_interp, p_interp), p_interp)

        tolerancia = 0.9
        # Cálculo das coordenadas dos pontos de inflexão
        pontos_inflexao = []
        for i in range(1, len(p_interp) - 1):
            if (df_interp[i] > 0 and df_interp[i + 1] < 0) or (df_interp[i] < 0 and df_interp[i + 1] > 0):
                x = p_interp[i]
                y = f(x)
                # Verificar proximidade com outros pontos de inflexão
                adicionar_ponto = True
                for ponto in pontos_inflexao:
                    if abs(x - ponto[0]) < tolerancia and abs(y - ponto[1]) < tolerancia:
                        adicionar_ponto = False
                        break

                if adicionar_ponto:
                    pontos_inflexao.append((x, y))
        #print("Pontos inflexão:", pontos_inflexao)

    if (r1 <= 0.15*rmedia) and len(ponto_inflexao) == 0 and d_acima==False and d_abaixo==False:
        print(r1)
        print(rmedia)
        print("O solo é Homogénio")
        # Interpolar os pontos para obter uma curva suave

        #modar a interpolação!!!!!!!!!!!!!!
        f = interp1d(p, r, kind='cubic')
        p_interp = np.linspace(min(p), max(p), 100)
        r_interp = f(p_interp)

        # Plotar a curva suave e os pontos de inflexão
        plt.plot(p_interp, r_interp, '-')
        plt.plot(p, r, 'ro')
        plt.xlabel('profundidade')
        plt.ylabel('resistência')
        plt.title('Gráfico')
        plt.grid(True)
        plt.show()

        rmedio_s = str(rmedia)
        texto = "O Solo é Homogéneo"
        texto2 = f"A resistividade do Solo é de {rmedio_s} ohm"

        return render_template("SoverificadoHomogeneo.html", texto=texto, texto2=texto2)  # Não há ponto de inflexão

    elif (len(ponto_inflexao) > 0) & (r1 >= 0.15*rmedia):

        # Imprimir os pontos de inflexão
        print("Pontos de inflexão:")
        for ponto in pontos_inflexao:
            y, x = ponto
            print(f"Coordenadas: ({y}, {x}")

        # calcular h - expessura do extrato superior
        h = ((2 / 3) * y)  # Confirmar coordenada!!!!-------------
        print(f"h é igual {h}")

        supinf(r)

        # Plotar a curva interpolada e a sua derivada
        plt.plot(p_interp, r_interp, label='Curva Interpolada')
        plt.plot(p_interp, df_interp, label='Derivada')
        plt.scatter(coordenadasX, coordenadasY, color='red', label='Pontos Dados')
        plt.scatter(y, x, color='green', label='Pontos de Inflexão')
        plt.xlabel('Profundidade')
        plt.ylabel('Resistividade')
        plt.title('Resistividade do Terreno')
        plt.legend()
        plt.grid(True)
        plt.show()

        texto = "O Solo não é Homogeneo"

        return render_template("ComprimentovaraCabo.html", texto=texto)

    elif (len(ponto_inflexao) == 0) and (r1 > 0.15 * rmedia) or (d_acima == True or d_abaixo == True):
        print("O solo não é homogénio")
        supinf(r)
        # ir buscar o ponto onde o declive aumentou ou diminuio
        h = (2/3) * ponto_diferenca[0]
        print("valor h = ", h)
        coordenadasX = p.copy()
        coordenadasY = r.copy()

        # Remover pontos duplicados
        coordenadasX, indices = np.unique(coordenadasX, return_index=True)
        coordenadasY = np.array(coordenadasY)[indices]

        # Interpolar os pontos para obter uma curva suave
        f = interp1d(coordenadasX, coordenadasY, kind='cubic')
        p_interp = np.linspace(min(coordenadasX), max(coordenadasX), 100)
        r_interp = f(p_interp)

        # Plotar a curva interpolada e a sua derivada
        plt.plot(p_interp, r_interp, '-')
        plt.scatter(coordenadasX, coordenadasY, color='red', label='Pontos dados')
        plt.xlabel('Profundidade')
        plt.ylabel('Resistividade')
        plt.title('Resistividade do Terreno')
        plt.legend()
        plt.grid(True)
        plt.show()

        texto = "O Solo não é Homogéneo"
        return render_template("ComprimentovaraCabo.html", texto=texto)  # Não há ponto de inflexão

@app.route("/calculocabo", methods= ['GET' ,'POST'])
def cabo():
    global r, h
    if request.method == 'POST':
        raioExterno = request.form.get('raioExterno')
        raioExternoF = float(raioExterno)
        print("raio externo", raioExternoF)

        raioInterno = request.form.get('raioInterno')
        raioInternoF = float(raioInterno)
        print("raio Interno", raioInternoF)

        resistividadeCondutor = request.form.get('resistividadecabo')
        resistividadeCondutorF = float(resistividadeCondutor)
    print("Passou Aqui 2")
    a = math.pi * (raioExternoF**2 - raioInternoF**2)
    print("a: ", a)
    rhom = (resistividadeCondutorF/a)*(1/np.log(raioExternoF/raioInternoF))
    print("rhom: ", rhom)
    valor_l = calculoResistividadeCabo(rhom)
    return valor_l, h
def calculoResistividadeCabo(rhom):
    print("Passei aqui 3 cabo")
    # Chamar a função supinf() para obter resistividade superior e inferior
    rs, ri = supinf(r)
    # resistencia da vara para dois extratos diferentes
    xn = 2.0  # comprimento minimo da vara
    # declara a variável simbólica
    l = sy.Symbol('l')
    k = round((ri - rs) / (ri + rs), 1)
    print("K = ", k)
    n = 1
    # resistencia da vara
    rv = 20
    # Parte 1 da equação de Tagg
    parte1 = rhom
    parte2 = ((2 * rs) / (math.pi * l))
    # Parte 2 da equação de Tagg (soma finita)
    parte3 = k**n * np.log((1 + (math.sqrt(((2 * n * h)/(1)) + 1)))/(2*n*(h/1))) + ((2*n*h)/(1)) - math.sqrt(((2*n*h)/(1)) + 1)
    print("parte3: ", parte3)

    termo = k**n * np.log((1 + (math.sqrt(((2 * n * h)/(1)) + 1)))/(2*n*(h/1))) + ((2*n*h)/(1)) - math.sqrt(((2*n*h)/(1)) + 1)
    tolerancia_soma = parte3 * 0.05
    print("Passou aqui cabo")

    while (n < 9):
        parte3 += termo
        n += 1
        termo = k**n * np.log((1 + (math.sqrt(((2 * n * h)/(1)) + 1)))/(2*n*(h/1))) + ((2*n*h)/(1)) - math.sqrt(((2*n*h)/(1)) + 1)
        print(n)
        tolerancia_soma = parte3 * 0.01

    # Equação de Tagg
    equacao = (parte1 + parte2 * parte3) - rv
    print("Equação : ", equacao)

    # Derivada da função em relação a l
    derivada = sy.diff(equacao, l)
    print(derivada)

    # Configuração do método de Newton-Raphson
    tolerancia = 1e-6
    max_iteracoes = 3
    l_aproximado = 2.0  # Valor inicial de l

    equacao_numerica = sy.lambdify(l, equacao)
    derivada_numerica = sy.lambdify(l, derivada)

    for _ in range(1, max_iteracoes):
        l_anterior = l_aproximado
        l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
        print("L_aproximado", l_aproximado)
        if abs(l_aproximado - l_anterior) < tolerancia:
            break
    valor_l = round(l_aproximado)
    print("O comprimento necessário para o cabo é de", round(valor_l))
    return valor_l


#incluir os parametros url para passar as variáveis r e h
@app.route("/calculo1", methods=['GET', 'POST'])
def calculoResistividade1():
    print("Passou Aqui 1")
    global r, h
    print(h)
    print(r)
    escolha = request.form['tipo']
    print(escolha)
    if escolha == 'vara':
        valor_l, h, comprimentoF = calculaResistividadeVara(r, h)
        valor_l_s = str(round(valor_l, 1)) #é necessátio converte-los para string para depois redirecionar o texto para a minha página
        h_s = str(round(h, 1))
        cumprimentoF_s = str(comprimentoF)
        texto = f"O comprimento de uma Vara é de {cumprimentoF_s} metros."
        texto2 = f"O comprimento necessário é de {valor_l_s} metros"
        texto3 = f"O estrato superior tem uma espessura de {h_s} metros."
        return render_template("VerificarSolo.html", texto=texto, texto2=texto2, texto3=texto3)
    elif escolha == 'cabo':
        valor_l, h = cabo()
        valor_l_s = str(valor_l)
        h_s = str(round(h, 1))
        texto2 = f"O comprimento necessário para o cabo é de {valor_l_s} metros"
        texto3 = f"O estrato superior tem uma espessura de {h_s} metros."
        return render_template("VerificarSolo.html", texto2=texto2, texto3=texto3)

def calculaResistividadeVara(r, h):
    print("Passei aqui 3")
    if request.method == 'POST':
        comprimento = request.form.get('distanciaVaras')
        print(comprimento)
        comprimentoF = float(comprimento)
    print("Distancia F:", comprimentoF)
    # Chamar a função supinf() para obter resistividade superior e inferior
    rs, ri = supinf(r)
    #resistencia da vara para dois extratos diferentes
    xn = 2.0 #comprimento minimo da vara
    # declara a variável simbólica
    l = sy.Symbol('l')
    k = round((ri-rs)/(ri+rs), 1)
    print("K = ", k)
    a = comprimentoF
    n = 1
    # resistencia da vara
    rv = 20

    # Parte 1 da equação de Tagg
    parte1 = (rs / (2 * math.pi * l)) * ((1 + k) / (1 - k + 2 * k * (h / l)))
    parte2 = (np.log(2) + sy.log(l) - np.log(a))
    # Parte 3 da equação de Tagg (soma finita)
    parte3 = (k ** n) * (np.log(2) + np.log(n) + np.log(1 + 1 / (2 * n * h))) / ((2 * n - 2) * h + 1)
    print("parte3: ", parte3)
    
    termo = (k ** n) * (sy.log(2) + sy.log(n) + sy.log(1 + 1 / (2 * n * h))) / ((2 * n - 2) * h + 1)
    """
    # Parte 1 da equação de Tagg
    parte1 = (rs / (2 * math.pi * l))
    parte2 = (np.log(4) + sy.log(l) - np.log(a)) - 1
    # Parte 3 da equação de Tagg (soma finita)
    parte3 = ((k ** n)/2) * (np.log(n * h + 1) - np.log(n * h - 1))
    print("parte3: ", parte3)

    termo = ((k ** n)/2) * (np.log(n * h + 1) - np.log(n * h - 1))
    """
    tolerancia_soma = parte3 * 0.01
    print("Passou aqui")
    #Soma infinita
    while (n < 9):
        parte3 += termo
        n += 1
        termo = ((k ** n)/2) * (np.log(n * h + 1) - np.log(n * h - 1))
        print(n)
        tolerancia_soma = parte3 * 0.01

    #Equação de Tagg
    equacao = parte1 * (parte2 + parte3) - rv
    print("Equação : ", equacao)

    #Derivada da função em relação a l
    derivada = sy.diff(equacao, l)
    print(derivada)

    #Configuração do método de Newton-Raphson
    tolerancia = 1e-6
    max_iteracoes = 3
    l_aproximado = 2.0  # Valor inicial de l

    #Converter expressões para funções numéricas
    equacao_numerica = sy.lambdify(l, equacao)
    derivada_numerica = sy.lambdify(l, derivada)

    for _ in range(1, max_iteracoes):
        l_anterior = l_aproximado
        l_aproximado = l_anterior - (equacao_numerica(l_anterior) / abs(derivada_numerica(l_anterior)))
        print("L_aproximado", l_aproximado)
        if abs(l_aproximado - l_anterior) < tolerancia:
            break
    valor_l = l_aproximado
    print("O comprimento necessário para a vara é de", round(valor_l, 1))
    return valor_l, h, comprimentoF


@app.route("/homogénio")
def homogenio():
    return render_template("SoloHomogeneo.html", valor_l_s=valor_l_s)

@app.route("/GeometriaVara2", methods=['POST'])
def GeometriaVara2():
    if request.method == 'POST':
        d_varas = float(request.form.get('distancia'))

    global valor_l_s, rs
    r_s = str(rs)
    print("resistividade do solo: ", r_s)
    d = 0.08
    xn = 1.5
    # resistencia do solo
    r = 20
    # verificar
    v = sy.Symbol('v')
    parte1 = (rs / (4 * math.pi * v))
    print("parte1 ", parte1)
    parte2 = sy.log((4 * v) / d) + sy.log((4 * v) / d) - 2 + (d / (2 * v)) - (d ** 2 / 16 * v ** 2) + (
                d ** 2 / 512 * v ** 4)
    print("parte2 ", parte2)

    equacao = parte1 * parte2 - r

    # derivada da função
    derivada = sy.diff(equacao, v)
    print("derivada : ", derivada)

    # método de Newton-Raphson
    tolerancia = 1e-6
    max_iteracoes = 5
    l_aproximado = xn

    # Converter expressões para funções numéricas
    equacao_numerica = sy.lambdify(v, equacao)
    derivada_numerica = sy.lambdify(v, derivada)

    for _ in range(max_iteracoes):
        l_anterior = l_aproximado
        l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
        if abs(l_aproximado - l_anterior) < tolerancia:
            break

    valor_l = l_aproximado
    print("Cumprimento necessário:", valor_l)
    valor_l_s = str(round(valor_l, 1))
    print("Valor em string: ", valor_l)
    texto = f"O comprimento necessário é de {valor_l_s} metros."

    return render_template("SoloHomogeneo.html", texto=texto)

@app.route("/GeometriaVaras", methods=['POST'])
def GeometriaVaras():
    if request.method == 'POST':
        d_varas = float(request.form.get('distancia'))

    global valor_l_s, rs
    r_s = str(rs)
    print("resistividade do solo: ", r_s)
    d = 0.08
    xn = 1.5
    # resistencia do solo
    r = 20
    # verificar
    v = sy.Symbol('v')
    parte1 = (rs/ (4 * math.pi * v))
    print("parte1 ", parte1)
    parte2 = (sy.log((4 * v) / d) - 1) + (rs / (4 * math.pi * d_varas))
    print("parte2 ", parte2)
    parte4 = (1 - (v ** 2 / (3 * (d_varas ** 2))) + ((2 * (v ** 4)) / (5 * (d_varas ** 4)))) - r
    print("parte4 ", parte4)

    equacao = parte1 * parte2 * parte4

    # derivada da função
    derivada = sy.diff(equacao, v)
    print("derivada : ", derivada)

    # método de Newton-Raphson
    tolerancia = 1e-6
    max_iteracoes = 4
    l_aproximado = xn

    # Converter expressões para funções numéricas
    equacao_numerica = sy.lambdify(v, equacao)
    derivada_numerica = sy.lambdify(v, derivada)

    for _ in range(max_iteracoes):
        l_anterior = l_aproximado
        l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
        if abs(l_aproximado - l_anterior) < tolerancia:
            break

    valor_l = l_aproximado
    print("Cumprimento necessário:", valor_l)
    valor_l_s = str(round(valor_l, 1))
    print("Valor em string: ", valor_l)
    texto = f"O comprimento necessário é de {valor_l_s} metros."

    return render_template("SoloHomogeneo.html", texto=texto)

@app.route("/GeometriaCirculo", methods=['POST'])
def GeometriaCirculo():
    if request.method == 'POST':
        diametroCabo = float(request.form.get('diametroCabo'))

    global valor_l_s, rs
    rmedio_s = str(rs)
    print("resistividade do solo: ", rmedio_s)
    d = 0.08
    xn = 1.5
    # resistencia do solo
    r = 20
    diametroCirculo = sy.Symbol('diametroCirculo')
    parte1 = (rs / ((2 * math.pi) ** 2 * diametroCirculo))
    print("parte1 ", parte1)
    parte2 = np.log(8) + sy.log(diametroCirculo) - np.log(diametroCabo) + np.log(4) + sy.log(diametroCirculo) - np.log(
        d)
    print("parte2 ", parte2)

    equacao = (parte1 * parte2) - r
    print("Equação", equacao)
    # derivada da função
    derivada = sy.diff(equacao, diametroCirculo)
    print("derivada : ", derivada)

    # método de Newton-Raphson
    tolerancia = 1e-6
    max_iteracoes = 3
    l_aproximado = xn

    # Converter expressões para funções numéricas
    equacao_numerica = sy.lambdify(diametroCirculo, equacao)
    derivada_numerica = sy.lambdify(diametroCirculo, derivada)

    for _ in range(max_iteracoes):
        l_anterior = l_aproximado
        l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
        if abs(l_aproximado - l_anterior) < tolerancia:
            break

    valor_l = l_aproximado
    print("Cumprimento necessário:", valor_l)
    valor_l_s = str(valor_l)
    print("Valor em string: ", valor_l)
    texto = f"O comprimento necessário é de {valor_l_s} metros."

    return render_template("SoloHomogeneo.html", texto=texto)

@app.route("/homogénio", methods=['GET', 'POST'])
def calculoResistividadeSoloHomogenio():
    global  valor_l_s, rs
    print("passou aqui 1")
    d = 0.08
    xn = 1.5
    #resistencia do solo
    r = 20

    #verificar
    v = sy.Symbol('v')
    tipoSolo = request.form['solo']
    cursor.execute(f"select ResistividadeTipica from Solo where TipoSolo like (?)", tipoSolo)
    print(tipoSolo)
    rs = cursor.fetchone()[0]  # ir buscar á BD  a resistividade do Solo selecionado
    print(rs)
    rs_s = str(rs)
    formula = request.form['formula']
    # distancia entre as varas

    #verificar o tipo de geometria escolhida pelo utilizador
    if formula == 'vara':
        equacao = (rs / (4 * math.pi * v)) * sy.log((2 * v) / d) - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 4
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Cumprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == 'varas':
        return render_template("calculoGeometriaVaras.html")

    elif formula == 'varas2':
        return render_template("calculoGeometriaVaras2.html")

    elif formula == 'cabo':

        parte1 = (rs/(4 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((4 * v)/d) + sy.log((4 * v)/d) - 2 + (d/(2 * v)) - (d**2/16 * v**2) + (d**2/512 * v**4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 5
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Cumprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == 'caboReto':

        parte1 = (rs/(4 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v)/d) + sy.log((2 * v)/d) - 0.2373 + 0.2146 * (d/(v)) + 0.1035 * (d**2/v**2) - 0.0424 * (d**4/v**4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Cumprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == 'tres_pontas':

        parte1 = (rs/(6 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v)/d) + sy.log((2 * v)/d) + 1.071 - 0.2009 * (d/(v)) + 0.238 * (d**2/v**2) - 0.054 * (d**4/v**4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Cumprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == '4_pontas':

        parte1 = (rs/(8 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v)/d) + sy.log((2 * v)/d) + 2.912 - 1.071 * (d/(v)) + 0.645 * (d**2/v**2) - 0.145 * (d**4/v**4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Cumprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == '6_pontas':

        parte1 = (rs/(12 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v)/d) + sy.log((2 * v)/d) + 6.851 - 3.128 * (d/(v)) + 1.758 * (d**2/v**2) - 0.490 * (d**4/v**4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Cumprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == '8_pontas':

        parte1 = (rs/(16 * math.pi * v))
        print("parte1 ", parte1)
        parte2 = sy.log((2 * v)/d) + sy.log((2 * v)/d) + 10.98 - 5.51 * (d/(v)) + 3.26 * (d**2/v**2) - 1.17 * (d**4/v**4)
        print("parte2 ", parte2)

        equacao = parte1 * parte2 - r

        # derivada da função
        derivada = sy.diff(equacao, v)
        print("derivada : ", derivada)

        # método de Newton-Raphson
        tolerancia = 1e-6
        max_iteracoes = 3
        l_aproximado = xn

        # Converter expressões para funções numéricas
        equacao_numerica = sy.lambdify(v, equacao)
        derivada_numerica = sy.lambdify(v, derivada)

        for _ in range(max_iteracoes):
            l_anterior = l_aproximado
            l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
            if abs(l_aproximado - l_anterior) < tolerancia:
                break

        valor_l = l_aproximado
        print("Cumprimento necessário:", valor_l)
        valor_l_s = str(valor_l)
        print("Valor em string: ", valor_l)
        return valor_l_s

    elif formula == 'circulo':
        return  render_template("calculoGeometriaCirculo.html")

    texto = f"O comprimento necessário para a {formula} é de {valor_l_s} metros"
    texto2 = f"A resistividade do {tipoSolo} é de {rs} ohm"

    return render_template("calculoGeometriaVaras2.html", texto=texto, texto2=texto2, valor_l_s=valor_l_s)

if __name__ == "__main__": #vai rodar se executarmos este ficheiro diretamente por ele
    app.run(debug=True) #todas as alterações vão ser mostradas automáticamente, debug=True
