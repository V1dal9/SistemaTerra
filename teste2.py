import sympy as sy
import math
import numpy as np

# Valores conhecidos
rv = 20  # Resistência da vara
k = -0.9  # Razão de resistividade entre os extratos
h = 1.3333333333  # Espessura do extrato inferior
a = 1.5  # Parâmetro de ajuste
rs = 1734
# Variáveis simbólicas
l = sy.Symbol('l')
n = 1
# Parte 1 da equação de Tagg
parte1 = (rs / (2 * math.pi * l)) * ((1 + k) / (1 - k + 2 * k * (h / l)))
parte2 = (np.log(2) + sy.log(l) - np.log(a))
# Parte 2 da equação de Tagg (soma finita)
parte3 = (k ** n) * (np.log(2) + np.log(n) + np.log(1 + 1 / (2 * n * h))) / ((2 * n - 2) * h + 1)
print("parte2", parte3)

termo = (k ** n) * (sy.log(2) + sy.log(n) + sy.log(1 + 1 / (2 * n * h))) / ((2 * n - 2) * h + 1)
tolerancia_soma = parte3 * 0.01
print("Passou aqui")

while (abs(termo) > abs(tolerancia_soma)):
    termo = (k ** n) * (np.log(2) + np.log(n) + np.log(1 + 1 / (2 * n * h))) / ((2 * n - 2) * h + 1)
    parte3 += termo
    n += 1
    print(n)
    tolerancia_soma = parte3 * 0.01

# Equação de Tagg
equacao = parte1 * (parte2 + parte3) - rv
print("Equação : ", equacao)

# Derivada da função em relação a l
derivada = sy.diff(equacao, l)
print(derivada)

# Configuração do método de Newton-Raphson
tolerancia = 1e-6
max_iteracoes = 3
l_aproximado = 2.0  # Valor inicial de l

# Converter expressões para funções numéricas
equacao_numerica = sy.lambdify(l, equacao)
derivada_numerica = sy.lambdify(l, derivada)

for _ in range(1, max_iteracoes):
    l_anterior = l_aproximado
    l_aproximado = l_anterior - (equacao_numerica(l_anterior) / derivada_numerica(l_anterior))
    print("L_aproximado", l_aproximado)
    if abs(l_aproximado - l_anterior) < tolerancia:
        break
valor_l = l_aproximado
print("O comprimento necessário para a vara é de", round(valor_l))
