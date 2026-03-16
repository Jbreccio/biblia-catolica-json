#!/usr/bin/env python3
"""
Limpa os JSONs da Biblia — remove lixo do scraping
- Remove versiculos duplicados (mesmo numero)
- Remove versiculos com texto muito longo (menu de navegacao)
- Remove versiculos com texto que e lixo do site
- Mantem apenas o primeiro versiculo de cada numero (o texto real vem depois do titulo)

Rode na pasta biblia-catolica-json\biblia-catolica-json\
"""
import json, os, re

PALAVRAS_LIXO = [
    'Selecionar livro', 'Selecionar capítulo', 'Ler Genesis completo',
    'Ler Exodo completo', 'Ler Mateus completo', 'Ler Lucas completo',
    'Gerar Imagem', 'Gerador de imagem', 'Escolher Arquivo',
    'Tamanho da Fonte', 'Tipo de Background', 'Gradientes',
    'Dancing Script', 'Comic Sans', 'Instagram', 'Facebook',
    'Baixar Imagem', 'Compartilhar', 'Bíblia Católica Pastoral',
    'Início da Bíblia', 'Capítulo', 'São Mateus', 'São Marcos',
    'Gênesis Êxodo Levítico', 'Ler ', 'completo',
]

def eh_lixo(texto):
    """Verifica se o texto e lixo do site"""
    if len(texto) > 400:  # textos muito longos sao menus/lixo
        return True
    for palavra in PALAVRAS_LIXO:
        if palavra.lower() in texto.lower():
            return True
    return False

def limpar_arquivo(path):
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except:
        return False, 0, 0

    versiculos_raw = data.get('versiculos', [])
    if not versiculos_raw:
        return False, 0, 0

    total_antes = len(versiculos_raw)

    # Remove lixo e duplicatas
    # Quando ha versiculos com mesmo numero, o segundo geralmente e o real
    # (o primeiro e o titulo da pagina)
    vistos = {}
    versiculos_limpos = []

    for v in versiculos_raw:
        num = v.get('number') or v.get('numero')
        txt = (v.get('text') or v.get('texto') or '').strip()

        if not num or not txt:
            continue
        if eh_lixo(txt):
            continue

        # Se ja vimos este numero, substitui pelo novo (o real vem depois)
        vistos[num] = txt

    # Reconstroi lista ordenada
    for num in sorted(vistos.keys()):
        versiculos_limpos.append({'number': num, 'text': vistos[num]})

    total_depois = len(versiculos_limpos)

    if total_depois == total_antes and total_depois > 0:
        return False, total_antes, total_depois  # nada mudou

    if total_depois == 0:
        return False, total_antes, 0  # ficou vazio, nao salva

    data['versiculos'] = versiculos_limpos
    data['total_versiculos'] = total_depois
    data.pop('status', None)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return True, total_antes, total_depois

def main():
    print('Limpando JSONs da Biblia...')
    print()

    total_arquivos = 0
    total_limpos = 0
    total_removidos = 0

    for raiz, dirs, arquivos in os.walk('livros'):
        dirs.sort()
        for arquivo in sorted(arquivos):
            if not arquivo.endswith('.json'):
                continue
            path = os.path.join(raiz, arquivo)
            total_arquivos += 1
            modificado, antes, depois = limpar_arquivo(path)
            if modificado:
                total_limpos += 1
                removidos = antes - depois
                total_removidos += removidos
                livro = raiz.split(os.sep)[-1]
                cap = arquivo.replace('.json', '')
                print(f'  ✅ {livro}/{cap}: {antes} -> {depois} versiculos ({removidos} removidos)')

    print()
    print('=' * 50)
    print(f'Total de arquivos: {total_arquivos}')
    print(f'Arquivos limpos:   {total_limpos}')
    print(f'Versiculos removidos: {total_removidos}')
    print()
    if total_limpos > 0:
        print('Agora rode:')
        print('  git add .')
        print('  git commit -m "fix: remove lixo do scraping dos versiculos"')
        print('  git push')
    else:
        print('Nenhum arquivo precisou de limpeza.')

if __name__ == '__main__':
    main()