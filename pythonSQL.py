"""
import pyodbc

dados_conectar = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=(LocalDB)\MSSQLLocalDB;"
    "Database=pythonsiteSQL;"
    "Trusted_Connection=yes"
)

conectar = pyodbc.connect(dados_conectar)
print("Conexão Bem sucedida!")

cursor = conectar.cursor()

cursor.execute('executar um código em SQL')
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from numpy import log as ln
import sympy as sy
import math


# Chamar a função supinf() para obter resistividade superior e inferior
rs = 1700
ri = 100
h = 1.3333
# resistencia da vara para dois extratos diferentes
xn = 1.5  # comprimento minimo da vara
# declara a variável simbólica
l = sy.Symbol('l')
k = (ri - rs) / (ri + rs)
print("K = ", k)
a = 1.5
n = 1
# resolver em ordem a l
parte1 = (rs / (2 * math.pi * l)) * ((1 + k) / (1 - k + 2 * k * (h / l)))
parte2 = sy.log(2) + sy.log(l) - sy.log(a)

"""
parte3 = sum((k ** n) * (sy.log(((2 * n * h) + l) / ((2 * n - 2) * h + l)))
            for n in range(1, 3)
             )

# Somatório
parte3 = sy.Sum((k ** n) * sy.log((2 * n * h + l) / ((2 * n - 2) * h + l)), (n, 1, sy.oo))

N = 200
# Somatório
parte3 = sum((k ** n) * sy.log((2 * n * h + l) / ((2 * n - 2) * h + l)) for n in range(1, N+1))
"""

parte3 = (k ** n) * (sy.log(2) + sy.log(n) + sy.log(1 + l / (2 * n * h))) / ((2 * n - 2) * h + l)

#math.log((2 * n * h + l)
# iniciar o somatorio
somatorio = 1
contador = 1

# Calcular o primeiro termo
termo_atual = parte3.subs(n, contador)
somatorio += termo_atual

# Realizar o somatório até que o próximo termo seja maior em módulo que 0.01 do valor acumulado
while (abs(termo_atual.subs(l, 1)) >= 0.01 * abs(somatorio)):
    contador += 1
    termo_atual = parte3.subs(n, contador).evalf()
    somatorio += termo_atual
"""
# Realizar o somatório até que o termo seja maior que o limite
while parte3.subs(l, 1) >= 0.01 * somatorio:
    parte3 = (k ** n) * (sy.log(2) + sy.log(n) + sy.log(1 + l / (2 * n * h))) / ((2 * n - 2) * h + l)
    n = n + 1
    somatorio += parte3
    contador += 1
    parte3 = parte3.subs(n, contador)
"""
parte3 = somatorio
print("Somatório :", somatorio)

print("Parte1:", parte1)
print("Parte2:", parte2)
print("Parte3:", parte3)

# resistencia da vara
rv = 20

# equação
equacao = parte1 * (parte2 + parte3) - rv
print("Equação: ", equacao)

# derivada da função
derivada = sy.diff(equacao, l)
print("derivada: ", derivada)


# método de Newton-Raphson
tolerancia = 1e-6
max_iteracoes = 4
l_aproximado = xn

"""
# Converter expressões para funções numéricas
equacao_numerica = sy.lambdify(l, equacao, modules='numpy')
derivada_numerica = sy.lambdify(l, derivada, modules='numpy')


for _ in range(max_iteracoes):
    l_anterior = l_aproximado
    l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
    if abs(l_aproximado - l_anterior) < tolerancia:
        break
"""

for _ in range(max_iteracoes):
    # Avaliar a equação e sua derivada no ponto atual
    valor_equacao = equacao.subs(l, l_aproximado).evalf()
    valor_derivada = derivada.subs(l, l_aproximado).evalf()

    # Calcular o próximo ponto usando a fórmula do método de Newton-Raphson
    l_proximo = l_aproximado - (valor_equacao / valor_derivada)

    # Verificar a condição de convergência
    if abs(l_proximo - l_aproximado) < tolerancia:
        break

    l_aproximado = l_proximo

valor_l = l_aproximado
print("O cumprimento necessário para a vara é de ", round(valor_l, 1))

