#!/usr/bin/env python3
"""
Scraping Biblia Pastoral Paulus — liriocatolico.com.br
URLs confirmadas via busca real no site.

Como usar:
  1. Coloque na pasta biblia-catolica-json\biblia-catolica-json\
  2. python scraping_paulus_v2.py
  3. git add . && git commit -m "feat: Biblia Pastoral Paulus completa" && git push
"""

import json, os, re, time, urllib.request, urllib.error

BASE = "https://www.liriocatolico.com.br/biblia_online/biblia_pastoral"

# (abbrev_repo, nome_url_CORRETO, nome_livro, total_caps)
# URLs confirmadas pelo site real
LIVROS = [
    # ANTIGO TESTAMENTO
    ("gn",   "genesis",                   "Genesis",                50),
    ("ex",   "exodo",                     "Exodo",                  40),
    ("lv",   "levitico",                  "Levitico",               27),
    ("nm",   "numeros",                   "Numeros",                36),
    ("dt",   "deuteronomio",              "Deuteronomio",           34),
    ("js",   "josue",                     "Josue",                  24),
    ("jz",   "juizes",                    "Juizes",                 21),
    ("rt",   "rute",                      "Rute",                    4),
    ("1sm",  "i-samuel",                  "1 Samuel",               31),
    ("2sm",  "ii-samuel",                 "2 Samuel",               24),
    ("1rs",  "i-reis",                    "1 Reis",                 22),
    ("2rs",  "ii-reis",                   "2 Reis",                 25),
    ("1cr",  "i-cronicas",                "1 Cronicas",             29),
    ("2cr",  "ii-cronicas",               "2 Cronicas",             36),
    ("ed",   "esdras",                    "Esdras",                 10),
    ("ne",   "neemias",                   "Neemias",                13),
    ("tb",   "tobias",                    "Tobias",                 14),
    ("jt",   "judite",                    "Judite",                 16),
    ("et",   "ester",                     "Ester",                  10),
    ("1mc",  "i-macabeus",                "1 Macabeus",             16),
    ("2mc",  "ii-macabeus",               "2 Macabeus",             15),
    ("jo",   "jo",                        "Jo",                     42),
    ("sl",   "salmos",                    "Salmos",                150),
    ("pv",   "proverbios",                "Proverbios",             31),
    ("ec",   "eclesiastes",               "Eclesiastes",            12),
    ("ct",   "cantico-dos-canticos",      "Cantico dos Canticos",    8),
    ("sb",   "sabedoria",                 "Sabedoria",              19),
    ("eclo", "eclesiastico",              "Eclesiastico",           51),
    ("is",   "isaias",                    "Isaias",                 66),
    ("jr",   "jeremias",                  "Jeremias",               52),
    ("lm",   "lamentacoes",               "Lamentacoes",             5),
    ("br",   "baruc",                     "Baruc",                   6),
    ("ez",   "ezequiel",                  "Ezequiel",               48),
    ("dn",   "daniel",                    "Daniel",                 14),
    ("os",   "oseias",                    "Oseias",                 14),
    ("jl",   "joel",                      "Joel",                    3),
    ("am",   "amos",                      "Amos",                    9),
    ("ob",   "abdias",                    "Abdias",                  1),
    ("jn",   "jonas",                     "Jonas",                   4),
    ("mq",   "miqueias",                  "Miqueias",                7),
    ("na",   "naum",                      "Naum",                    3),
    ("hc",   "habacuque",                 "Habacuque",               3),
    ("sf",   "sofonias",                  "Sofonias",                3),
    ("ag",   "ageu",                      "Ageu",                    2),
    ("zc",   "zacarias",                  "Zacarias",               14),
    ("ml",   "malaquias",                 "Malaquias",               4),
    # NOVO TESTAMENTO — usa prefixo "sao-" e numeracao romana
    ("mt",   "sao-mateus",                "Mateus",                 28),
    ("mc",   "sao-marcos",                "Marcos",                 16),
    ("lc",   "sao-lucas",                 "Lucas",                  24),
    ("jo2",  "sao-joao",                  "Joao",                   21),
    ("at",   "atos-dos-apostolos",        "Atos dos Apostolos",     28),
    ("rm",   "romanos",                   "Romanos",                16),
    ("1co",  "i-corintios",               "1 Corintios",            16),
    ("2co",  "ii-corintios",              "2 Corintios",            13),
    ("gl",   "galatas",                   "Galatas",                 6),
    ("ef",   "efesios",                   "Efesios",                 6),
    ("fp",   "filipenses",                "Filipenses",              4),
    ("cl",   "colossenses",               "Colossenses",             4),
    ("1ts",  "i-tessalonicenses",         "1 Tessalonicenses",       5),
    ("2ts",  "ii-tessalonicenses",        "2 Tessalonicenses",       3),
    ("1tm",  "i-timoteo",                 "1 Timoteo",               6),
    ("2tm",  "ii-timoteo",                "2 Timoteo",               4),
    ("tt",   "tito",                      "Tito",                    3),
    ("fm",   "filemon",                   "Filemon",                 1),
    ("hb",   "hebreus",                   "Hebreus",                13),
    ("tg",   "sao-tiago",                 "Tiago",                   5),
    ("1pe",  "i-sao-pedro",               "1 Pedro",                 5),
    ("2pe",  "ii-sao-pedro",              "2 Pedro",                 3),
    ("1jo",  "i-sao-joao",                "1 Joao",                  5),
    ("2jo",  "ii-sao-joao",               "2 Joao",                  1),
    ("3jo",  "iii-sao-joao",              "3 Joao",                  1),
    ("jd",   "sao-judas",                 "Judas",                   1),
    ("ap",   "apocalipse",                "Apocalipse",             22),
]

def limpar_html(texto):
    texto = re.sub(r'<script[\s\S]*?</script>', '', texto, flags=re.I)
    texto = re.sub(r'<style[\s\S]*?</style>', '', texto, flags=re.I)
    texto = re.sub(r'<br\s*/?>', '\n', texto, flags=re.I)
    texto = re.sub(r'<[^>]+>', ' ', texto)
    for ent, rep in [('&nbsp;',' '),('&quot;','"'),('&amp;','&'),
                     ('&lt;','<'),('&gt;','>'),('&#8220;','"'),
                     ('&#8221;','"'),('&#8216;',"'"),('&#8217;',"'"),
                     ('&#173;',''),('&#8211;','–'),('&#8212;','—')]:
        texto = texto.replace(ent, rep)
    return re.sub(r'\s+', ' ', texto).strip()

def extrair_versiculos(html):
    verses = []

    # Tenta encontrar bloco principal de conteudo
    for pat in [
        r'<div[^>]*class="[^"]*entry-content[^"]*"[^>]*>([\s\S]*?)</div>\s*(?:<div[^>]*class="[^"]*(?:sharedaddy|jp-|wpcnt|post-nav)|</article>)',
        r'<article[^>]*>([\s\S]*?)</article>',
        r'<div[^>]*id="content"[^>]*>([\s\S]*?)</div>',
    ]:
        m = re.search(pat, html, re.I)
        if m:
            bloco = m.group(1)
            break
    else:
        bloco = html

    texto = limpar_html(bloco)

    # Estrategia 1: versiculos em linhas separadas
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha:
            continue
        m = re.match(r'^(\d{1,3})[.\s]\s*(.{5,})', linha)
        if m:
            num = int(m.group(1))
            txt = m.group(2).strip()
            if 1 <= num <= 300:
                if not verses or verses[-1]['number'] != num:
                    verses.append({'number': num, 'text': txt})

    # Estrategia 2: texto corrido com numeros inline
    if len(verses) < 2:
        verses = []
        tc = ' '.join(texto.split())
        partes = re.split(r'(?<!\d)(\d{1,3})(?!\d)\s+', tc)
        i = 1
        while i < len(partes) - 1:
            try:
                num = int(partes[i])
                txt = partes[i+1].strip()[:500]
                if 1 <= num <= 300 and len(txt) > 8:
                    if not verses or verses[-1]['number'] != num:
                        verses.append({'number': num, 'text': txt})
                i += 2
            except:
                i += 1

    verses.sort(key=lambda v: v['number'])
    return verses

def ja_preenchido(path):
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        vv = data.get('versiculos', [])
        return len(vv) > 0 and data.get('status') != 'pendente'
    except:
        return False

def buscar(url, tentativas=3):
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            })
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f'     HTTP {e.code}, tentativa {t+1}...', end=' ')
            time.sleep(3 * (t + 1))
        except Exception as ex:
            print(f'     Erro: {ex}, tentativa {t+1}...', end=' ')
            time.sleep(3 * (t + 1))
    return None

def salvar(abbrev, nome, cap, total_caps, verses):
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
    print('=' * 65)
    print('Scraping Biblia Pastoral Paulus — liriocatolico.com.br')
    print('73 livros catolicos completos')
    print('=' * 65)
    print()

    total_ok = total_pulado = total_erro = 0
    total_geral = sum(c for _, _, _, c in LIVROS)

    for abbrev, nome_url, nome, total_caps in LIVROS:
        caps_ok = caps_pulado = caps_erro = 0
        print(f'📖 {nome} ({total_caps})...', end=' ', flush=True)

        for cap in range(1, total_caps + 1):
            path = os.path.join('livros', abbrev, f'{cap}.json')

            if ja_preenchido(path):
                caps_pulado += 1
                total_pulado += 1
                continue

            url = f'{BASE}/{nome_url}/{cap}/'
            html = buscar(url)

            if html:
                verses = extrair_versiculos(html)
                salvar(abbrev, nome, cap, total_caps, verses)
                if verses:
                    caps_ok += 1
                    total_ok += 1
                else:
                    caps_erro += 1
                    total_erro += 1
            else:
                salvar(abbrev, nome, cap, total_caps, [])
                caps_erro += 1
                total_erro += 1

            time.sleep(0.4)  # respeita o servidor

        partes = [f'✅ {caps_ok} novos']
        if caps_pulado: partes.append(f'{caps_pulado} ja ok')
        if caps_erro:   partes.append(f'⚠️ {caps_erro} erro')
        print(', '.join(partes))

    print()
    print('=' * 65)
    print(f'✅ Novos:     {total_ok}/{total_geral}')
    print(f'⏭️  Ja tinham: {total_pulado}')
    if total_erro:
        print(f'⚠️  Erros:     {total_erro} — rode novamente para tentar')
    print()
    print('Agora rode:')
    print('  git add .')
    print('  git commit -m "feat: Biblia Pastoral Paulus 73 livros completos"')
    print('  git push')
    print('=' * 65)

if __name__ == '__main__':
    main()