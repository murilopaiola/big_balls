from itertools import combinations
from multiprocessing import Pool
from tinydb import TinyDB, Query
from colorama import Fore, Style
import random
import os
import sys

quadrantes = [
    ( 1,  2, 11, 12), ( 3,  4, 13, 14), ( 5,  6, 15, 16), ( 7,  8, 17, 18), ( 9, 10, 19, 20), 
    (21, 22, 31, 32), (23, 24, 33, 34), (25, 26, 35, 36), (27, 28, 37, 38), (29, 30, 39, 40),
    (41, 42, 51, 52), (43, 44, 53, 54), (45, 46, 55, 56), (47, 48, 57, 58), (49, 50, 59, 60),
    (61, 62, 71, 72), (63, 64, 73, 74), (65, 66, 75, 76), (67, 68, 77, 78), (69, 70, 79, 80),
    (81, 82, 91, 92), (83, 84, 93, 94), (85, 86, 95, 96), (87, 88, 97, 98), (89, 90, 99, 00)
]

def calcular_cartoes(filtro, quads_com_dezenas_fixas, quad_selecionados, max_quad_linha, max_quad_coluna):
    filtro2 = []
    for comb in filtro:
        if quads_com_dezenas_fixas in comb:
            continue
        quad_por_linha = {1:0, 2:0, 3:0, 4:0, 5:0}
        quad_por_coluna = {1:0, 2:0, 3:0, 4:0, 5:0}
        comb_com_fixos = list(comb) + quad_selecionados
        mapping = [{[0, 5] : 1, [5, 10] : 2, [10, 15] : 3, [15,20] : 4, [20, 25] : 5}, 
                   {[1, 6, 11, 16, 21] : 1, [2, 7, 12, 17, 22] : 2, [3, 8, 13, 18, 23] : 3, [4, 9, 14, 19, 24] : 4, [5, 10, 15, 20, 25] : 5}]
        for i in comb_com_fixos:
            if i <= 5:
                quad_por_linha[1] += 1
            elif i <= 10:
                quad_por_linha[2] += 1
            elif i <= 15:
                quad_por_linha[3] += 1
            elif i <= 20:
                quad_por_linha[4] += 1
            elif i <= 25:
                quad_por_linha[5] += 1
            if i in [1, 6, 11, 16, 21]:
                quad_por_coluna[1] += 1
            elif i in [2, 7, 12, 17, 22]:
                quad_por_coluna[2] += 1
            elif i in [3, 8, 13, 18, 23]:
                quad_por_coluna[3] += 1
            elif i in [4, 9, 14, 19, 24]:
                quad_por_coluna[4] += 1
            elif i in [5, 10, 15, 20, 25]:
                quad_por_coluna[5] += 1
        e = any((quad_por_coluna[i] > max_quad_coluna[i]) or (quad_por_linha[i] > max_quad_linha[i]) for i in range(1, 6))
        if not e:
            filtro2.append(sorted(comb_com_fixos))
    return filtro2

def quads_para_dezenas(cartoes, dezenas_fixas):
    results = []
    for cartao in cartoes:
        s = [dezena for quad in cartao for dezena in quadrantes[quad-1]]
        results.append(sorted(s + dezenas_fixas))
    return results

def jogo():  # sourcery no-metrics
    quad_selecionados = []
    dezenas_fixas = []
    max_quad_linha = {}
    max_quad_coluna = {}
    dezena_fixa_ok = False
    while not dezena_fixa_ok:
        quad_selecionados = [int(i) for i in str.split(str(input('\nQuadrantes fixos (ex: 1,2,25): ')), ',') if int(i) < 26 and int(i) != 0]
        quad_exclusos = [int(i) for i in str.split(str(input('Quadrantes exclusos (ex: 1,2,25): ')), ',') if int(i) < 26 and int(i) != 0]
        dezenas_fixas = [int(i) for i in str.split(str(input('Duas dezenas fixas (ex: 0,10): ')), ',') if int(i) < 100]
        quads_com_dezenas_fixas = [quadrantes.index(tup)+1 for tup in quadrantes if any(i in tup for i in dezenas_fixas)]
        if (((set(quads_com_dezenas_fixas).issubset(set(quad_selecionados))) 
        or (set(quads_com_dezenas_fixas).issubset(set(quad_exclusos))))
        and dezenas_fixas):
            print('Dezena fixada em quadrante já fixo ou excluso! tente novamente')
        elif (len(quad_exclusos) > 0 and set(quad_exclusos).issubset(set(quad_selecionados))):
            print('Quadrantes fixos não podem ser exclusos, tente novamente')
        else:
            dezena_fixa_ok = True
            for i in range(1, 6):
                k = int(input('Quadrantes linha ' + str(i) + ': '))
                max_quad_linha[i] = k
            for i in range(1, 6):
                k = int(input('Quadrantes coluna ' + str(i) + ': '))
                max_quad_coluna[i] = k
            filtro = combinations([i for i in range(1, 26) if i not in quad_selecionados + quad_exclusos
            and all(j not in quadrantes[i - 1] for j in dezenas_fixas)], 12 - len(quad_selecionados), )
    print('\nCalculando cartoes...\n')
    with Pool(6) as p:
        cartoes = calcular_cartoes(filtro, quads_com_dezenas_fixas, quad_selecionados, max_quad_linha, max_quad_coluna)
    print(str(len(cartoes)) + ' cartoes gerados')
    if (len(cartoes) > 0):
        li = quads_para_dezenas(cartoes, dezenas_fixas)
        r = str(input('Deseja ver todos resultados? (s|n): '))
        if r.lower() == 's':
            for i in li:
                print(i)
        else:
            r = int(input('Quantos cartoes devem ser sorteados? '))
            sample = random.sample(li, r)
            for i in sample:
                print(i)
        r = str(input('Deseja salvar os cartoes? (s|n): '))
        if r.lower() == 's':
            db = TinyDB('db.json')
            jogos = db.table('jogos')
            r = str(input('Nome do bolão: '))
            for s in sample:
                jogos.insert({
                    'id': r,
                    'qin': ', '.join(map(str, quad_selecionados)),
                    'qex': ', '.join(map(str, quad_exclusos)),
                    'dzs': ', '.join(map(str, dezenas_fixas)),
                    'n': ', '.join(map(str, s))
                })
            print('Bolão salvo!')
    input('\n---------Fim de execução---------\n')

def consultar_banco():
    from tabulate import tabulate
    db = TinyDB('db.json')
    jogos = db.table('jogos')
    ids = list({jogo['id'] for jogo in jogos.all()})
    print('| id |')
    for i in range(len(ids)):
        print(f'| {Fore.CYAN}{i}{Style.RESET_ALL} : {ids[i]}')
    r = input()
    try:
        if (int(r)+1 > len(ids)):
            print('Índice fora de alcance!')
            return
    except:
        print('Utilize numeros para acessar os indices!')
        return
    dataset = jogos.search(Query()['id'] == ids[int(r)])
    for data in dataset:
        new = ''
        a = data['n'].split(',')
        for i in range(0, len(a), 10):
            a[i] = a[i].strip()
            new += ','.join(a[i:]) if (i+10 > len(a)) else ','.join(a[i:i+10])+'\n'
        data['n'] = new
    print(tabulate([x.values() for x in dataset], dataset[0].keys(), tablefmt='grid', stralign='right', showindex='always'))
    r = input('Deseja conferir resultado? (s|n): ')
    if (r.lower() == 's'):
        r = str.split(input('Insira o resultado (ex: 1, 5, 8, 12...): '), ',')
        result = {}
        for data in dataset:
            listnums = [int(n.strip()) for n in str.split(data['n'].replace('\n', ','), ',') if n != '']
            result[f'{dataset.index(data)}'] = sum(int(i) in listnums for i in r)
        sort = {k: v for k, v in sorted(result.items(), key=lambda item: item[1])} 
        print('\nResultados:')
        for k, v in result.items():
            if (int(v) > 15):
                print(f'{k}: {Fore.GREEN}{v}{Style.RESET_ALL}', end="  ")
            else:
                print(f'{k}: {v}', end="  ")
            if (int(list(result.keys()).index(k)) % 5 == 0 and int(list(result.keys()).index(k)) != 0):
                print('')
        input('\n---------Fim de execução---------\n')

def executar_acao(arg):
    switcher = {
        1: jogo,
        2: consultar_banco
    }
    switcher[arg]()

def main():
    print('Selecione a opção do que deseja fazer:')
    executar_acao(int(input(f'| {Fore.CYAN}1{Style.RESET_ALL}- Gerar jogo | {Fore.CYAN}2{Style.RESET_ALL}- Consultar banco de dados |\n')))
        
if __name__ == '__main__':
    print('\n\n----1-------2----Gordao-----4-------5----')
    print('| 01 02 | 03 04 | 05 06 | 07 08 | 09 10 |')
    print('| 11 12 | 13 14 | 15 16 | 17 18 | 19 20 |')
    print('----6-------7-------8-------9-------10---')
    print('| 21 22 | 23 24 | 25 26 | 27 28 | 29 30 |')
    print('| 31 32 | 33 34 | 35 36 | 37 38 | 39 40 |')
    print('----11------12------13------14------15---')
    print('| 41 42 | 43 44 | 45 46 | 47 48 | 49 50 |')
    print('| 51 52 | 53 54 | 55 56 | 57 58 | 59 60 |')
    print('----16------17------18------19------20---')
    print('| 61 62 | 63 64 | 65 66 | 67 68 | 69 70 |')
    print('| 71 72 | 73 74 | 75 76 | 77 78 | 79 80 |')
    print('----21------22------23------24------25---')
    print('| 81 82 | 83 84 | 85 86 | 87 88 | 89 90 |')
    print('| 91 92 | 93 94 | 95 96 | 97 98 | 99 00 |')
    print('-----------------------------------------\n\n')
    while 1:
        main()