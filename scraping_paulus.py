#!/usr/bin/env python3
"""
Scraping da Biblia Pastoral Paulus via liriocatolico.com.br
Preenche o repositorio Jbreccio/biblia-catolica-json

Como usar:
  1. Coloque este arquivo na pasta biblia-catolica-json\biblia-catolica-json\
  2. No PowerShell rode: python scraping_paulus.py
  3. Aguarde (pode demorar algumas horas para todos os livros)
  4. git add . && git commit -m "feat: Biblia Pastoral Paulus completa" && git push

O script:
- Pula capitulos ja preenchidos (retoma de onde parou)
- Busca capitulo inteiro de uma vez pela URL /{livro}/{cap}/
- Extrai todos os versiculos do HTML
- Salva no formato do repositorio
"""

import json, os, re, time, urllib.request, urllib.error
from html.parser import HTMLParser

BASE = "https://www.liriocatolico.com.br/biblia_online/biblia_pastoral"

# (abbrev_repo, nome_url, nome_livro, total_caps)
LIVROS = [
    ("gn",   "genesis",               "Genesis",                50),
    ("ex",   "exodo",                 "Exodo",                  40),
    ("lv",   "levitico",              "Levitico",               27),
    ("nm",   "numeros",               "Numeros",                36),
    ("dt",   "deuteronomio",          "Deuteronomio",           34),
    ("js",   "josue",                 "Josue",                  24),
    ("jz",   "juizes",                "Juizes",                 21),
    ("rt",   "rute",                  "Rute",                    4),
    ("1sm",  "1-samuel",              "1 Samuel",               31),
    ("2sm",  "2-samuel",              "2 Samuel",               24),
    ("1rs",  "1-reis",                "1 Reis",                 22),
    ("2rs",  "2-reis",                "2 Reis",                 25),
    ("1cr",  "1-cronicas",            "1 Cronicas",             29),
    ("2cr",  "2-cronicas",            "2 Cronicas",             36),
    ("ed",   "esdras",                "Esdras",                 10),
    ("ne",   "neemias",               "Neemias",                13),
    ("tb",   "tobias",                "Tobias",                 14),
    ("jt",   "judite",                "Judite",                 16),
    ("et",   "ester",                 "Ester",                  10),
    ("1mc",  "1-macabeus",            "1 Macabeus",             16),
    ("2mc",  "2-macabeus",            "2 Macabeus",             15),
    ("jo",   "jo",                    "Jo",                     42),
    ("sl",   "salmos",                "Salmos",                150),
    ("pv",   "proverbios",            "Proverbios",             31),
    ("ec",   "eclesiastes",           "Eclesiastes",            12),
    ("ct",   "cantico-dos-canticos",  "Cantico dos Canticos",    8),
    ("sb",   "sabedoria",             "Sabedoria",              19),
    ("eclo", "eclesiastico",          "Eclesiastico",           51),
    ("is",   "isaias",                "Isaias",                 66),
    ("jr",   "jeremias",              "Jeremias",               52),
    ("lm",   "lamentacoes",           "Lamentacoes",             5),
    ("br",   "baruc",                 "Baruc",                   6),
    ("ez",   "ezequiel",              "Ezequiel",               48),
    ("dn",   "daniel",                "Daniel",                 14),
    ("os",   "oseias",                "Oseias",                 14),
    ("jl",   "joel",                  "Joel",                    3),
    ("am",   "amos",                  "Amos",                    9),
    ("ob",   "abdias",                "Abdias",                  1),
    ("jn",   "jonas",                 "Jonas",                   4),
    ("mq",   "miqueias",              "Miqueias",                7),
    ("na",   "naum",                  "Naum",                    3),
    ("hc",   "habacuque",             "Habacuque",               3),
    ("sf",   "sofonias",              "Sofonias",                3),
    ("ag",   "ageu",                  "Ageu",                    2),
    ("zc",   "zacarias",              "Zacarias",               14),
    ("ml",   "malaquias",             "Malaquias",               4),
    ("mt",   "mateus",                "Mateus",                 28),
    ("mc",   "marcos",                "Marcos",                 16),
    ("lc",   "lucas",                 "Lucas",                  24),
    ("jo2",  "joao",                  "Joao",                   21),
    ("at",   "atos-dos-apostolos",    "Atos dos Apostolos",     28),
    ("rm",   "romanos",               "Romanos",                16),
    ("1co",  "1-corintios",           "1 Corintios",            16),
    ("2co",  "2-corintios",           "2 Corintios",            13),
    ("gl",   "galatas",               "Galatas",                 6),
    ("ef",   "efesios",               "Efesios",                 6),
    ("fp",   "filipenses",            "Filipenses",              4),
    ("cl",   "colossenses",           "Colossenses",             4),
    ("1ts",  "1-tessalonicenses",     "1 Tessalonicenses",       5),
    ("2ts",  "2-tessalonicenses",     "2 Tessalonicenses",       3),
    ("1tm",  "1-timoteo",             "1 Timoteo",               6),
    ("2tm",  "2-timoteo",             "2 Timoteo",               4),
    ("tt",   "tito",                  "Tito",                    3),
    ("fm",   "filemon",               "Filemon",                 1),
    ("hb",   "hebreus",               "Hebreus",                13),
    ("tg",   "tiago",                 "Tiago",                   5),
    ("1pe",  "1-pedro",               "1 Pedro",                 5),
    ("2pe",  "2-pedro",               "2 Pedro",                 3),
    ("1jo",  "1-joao",                "1 Joao",                  5),
    ("2jo",  "2-joao",                "2 Joao",                  1),
    ("3jo",  "3-joao",                "3 Joao",                  1),
    ("jd",   "judas",                 "Judas",                   1),
    ("ap",   "apocalipse",            "Apocalipse",             22),
]

def limpar_html(texto):
    """Remove tags HTML e limpa o texto"""
    texto = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', texto, flags=re.I)
    texto = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', texto, flags=re.I)
    texto = re.sub(r'<br\s*/?>', '\n', texto, flags=re.I)
    texto = re.sub(r'<[^>]+>', ' ', texto)
    texto = texto.replace('&nbsp;', ' ')
    texto = texto.replace('&quot;', '"')
    texto = texto.replace('&amp;', '&')
    texto = texto.replace('&lt;', '<')
    texto = texto.replace('&gt;', '>')
    texto = texto.replace('&#8220;', '"').replace('&#8221;', '"')
    texto = texto.replace('&#8216;', "'").replace('&#8217;', "'")
    texto = texto.replace('&#173;', '')
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def extrair_versiculos(html):
    """Extrai versiculos do HTML da pagina do liriocatolico"""
    verses = []

    # Tenta encontrar o conteudo principal
    # O liriocatolico usa WordPress — conteudo fica em .entry-content ou article
    blocos = [
        re.search(r'<div[^>]*class="[^"]*entry-content[^"]*"[^>]*>([\s\S]*?)</div>\s*<div[^>]*class="[^"]*(?:sharedaddy|post-tags|nav)', html, re.I),
        re.search(r'<article[^>]*>([\s\S]*?)</article>', html, re.I),
        re.search(r'<div[^>]*class="[^"]*post[^"]*"[^>]*>([\s\S]*?)</div>\s*(?:<div[^>]*class="[^"]*comment|<footer)', html, re.I),
    ]

    bloco = next((b.group(1) for b in blocos if b), html)
    texto = limpar_html(bloco)

    # Divide em linhas e procura padrao de versiculo
    # Formato: "1 Texto..." ou "1. Texto..."
    linhas = texto.split('\n')
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        m = re.match(r'^(\d{1,3})[.\s]\s*(.{5,})', linha)
        if m:
            num = int(m.group(1))
            txt = m.group(2).strip()
            if 1 <= num <= 250:
                # Evita duplicatas
                if not verses or verses[-1]['number'] != num:
                    verses.append({'number': num, 'text': txt})

    # Se nao encontrou com quebras de linha, tenta no texto corrido
    if len(verses) < 2:
        verses = []
        texto_corrido = ' '.join(texto.split())
        # Procura padrao: numero seguido de texto ate o proximo numero
        partes = re.split(r'\s+(\d{1,3})\s+', texto_corrido)
        i = 1
        while i < len(partes) - 1:
            try:
                num = int(partes[i])
                txt = partes[i+1].strip()
                if 1 <= num <= 250 and len(txt) > 10:
                    if not verses or verses[-1]['number'] != num:
                        verses.append({'number': num, 'text': txt})
                i += 2
            except:
                i += 1

    verses.sort(key=lambda v: v['number'])
    return verses

def ja_preenchido(path):
    """Verifica se o arquivo ja tem versiculos reais"""
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        vv = data.get('versiculos', [])
        # Considera preenchido se tem versiculos E nao tem status pendente
        return len(vv) > 0 and data.get('status') != 'pendente'
    except:
        return False

def buscar_capitulo(nome_url, cap, tentativas=3):
    """Busca o HTML de um capitulo com retry"""
    url = f"{BASE}/{nome_url}/{cap}/"
    for t in range(tentativas):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'pt-BR,pt;q=0.9',
                }
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # Capitulo nao existe
            time.sleep(2 * (t + 1))
        except Exception:
            time.sleep(2 * (t + 1))
    return None

def salvar_capitulo(abbrev, nome, cap, total_caps, verses):
    path = os.path.join('livros', abbrev, f'{cap}.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        'livro': nome,
        'abbrev': abbrev,
        'capitulo': cap,
        'total_capitulos': total_caps,
        'total_versiculos': len(verses),
        'fonte': 'Biblia Pastoral — Ed. Paulus',
        'versiculos': verses
    }
    if not verses:
        data['status'] = 'pendente'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print('=' * 60)
    print('Scraping Biblia Pastoral Paulus — liriocatolico.com.br')
    print('=' * 60)
    print()

    total_ok = 0
    total_pulado = 0
    total_erro = 0
    total_geral = sum(c for _, _, _, c in LIVROS)

    for abbrev, nome_url, nome, total_caps in LIVROS:
        caps_ok = 0
        caps_pulado = 0
        caps_erro = 0

        print(f'📖 {nome} ({total_caps} caps)...', end=' ', flush=True)

        for cap in range(1, total_caps + 1):
            path = os.path.join('livros', abbrev, f'{cap}.json')

            # Pula se ja preenchido
            if ja_preenchido(path):
                caps_pulado += 1
                total_pulado += 1
                continue

            html = buscar_capitulo(nome_url, cap)

            if html:
                verses = extrair_versiculos(html)
                salvar_capitulo(abbrev, nome, cap, total_caps, verses)
                if verses:
                    caps_ok += 1
                    total_ok += 1
                else:
                    caps_erro += 1
                    total_erro += 1
            else:
                salvar_capitulo(abbrev, nome, cap, total_caps, [])
                caps_erro += 1
                total_erro += 1

            # Delay para nao sobrecarregar o servidor
            time.sleep(0.3)

        status = f'✅ {caps_ok} novos'
        if caps_pulado:
            status += f', {caps_pulado} ja ok'
        if caps_erro:
            status += f', ⚠️ {caps_erro} erro'
        print(status)

    print()
    print('=' * 60)
    print(f'✅ Novos preenchidos: {total_ok}')
    print(f'⏭️  Ja existiam:       {total_pulado}')
    if total_erro:
        print(f'⚠️  Com erro:          {total_erro}')
    print()
    print('Agora rode:')
    print('  git add .')
    print('  git commit -m "feat: Biblia Pastoral Paulus completa"')
    print('  git push')
    print('=' * 60)

if __name__ == '__main__':
    main()