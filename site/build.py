"""Generate produk.html from index.html (header/footer) and products.json. Run: python build.py"""
import json, re, html, urllib.parse as u

s = open('index.html', encoding='utf-8').read()
P = json.load(open('products.json', encoding='utf-8'))

def clean(n):  # Tokopedia titles are SEO keyword lists; keep the first phrase
    n = re.split(r'\s+[|/]\s*|/', n.strip())[0].strip()
    return n[:1].upper() + n[1:]

LBL = {k: f'<img class="tag-ex" src="img/{k}.png" alt="{k.capitalize()}" height="24">' for k in ('ofamed', 'ofahusada')}
cards = ''
for p in P:
    n = clean(p['name'])
    wa = 'https://wa.me/6282258475758?text=' + u.quote(f'Halo, saya ingin meminta penawaran untuk {n}')
    tp = f'<a class="alt" href="{p["url"]}" rel="noopener">Lihat di Tokopedia<span class="sr"> : {html.escape(n)}</span></a>' if p['url'] else ''
    cards += f'''<li class="card" data-name="{html.escape(n.lower())}" data-cat="{p['cat']}">{LBL.get(p['cat'], '')}<img src="{p['img']}" alt="{html.escape(n)}" width="200" height="200" loading="lazy"><h2>{html.escape(n)}</h2><p>Hubungi untuk harga</p><a class="btn" href="{wa}">Minta Penawaran</a>{tp}</li>\n'''

css = '''.cat{padding-block:clamp(2.5rem,6vw,4.5rem)}
.cat h1{font-size:clamp(2.25rem,4.5vw,3.5rem)}.cat .lead{color:var(--muted);margin-top:.75rem;max-width:60ch}
.cat label{display:block;margin-top:1.75rem;font-weight:600;color:var(--navy)}
.cat input{display:block;width:min(100%,420px);min-height:48px;margin-top:.4rem;padding:0 1rem;border:1.5px solid var(--navy);border-radius:2px;font:inherit}
.grid{list-style:none;padding:0;margin-top:2rem;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1.25rem}
.card{display:flex;flex-direction:column;gap:.5rem;border:1px solid var(--line);padding:1rem}
.card[hidden]{display:none}
.card img{width:100%;height:auto;aspect-ratio:1;object-fit:contain;background:#fff}
.card h2{font:600 1.0625rem/1.3 var(--serif);color:var(--navy)}
.card p{font-size:.875rem;color:var(--muted)}
.card .btn{margin-top:auto;justify-content:center;white-space:nowrap;padding-inline:1rem}
.card .alt{display:inline-flex;align-items:center;min-height:44px;font-size:.875rem;color:var(--navy)}
.card img.tag-ex{align-self:flex-start;width:auto;height:24px;aspect-ratio:auto}
.cat select{display:block;width:min(100%,420px);min-height:48px;margin-top:.4rem;padding:0 1rem;border:1.5px solid var(--navy);border-radius:2px;font:inherit;background:#fff}
.sr{position:absolute;left:-9999px}
#empty{margin-top:2rem;color:var(--muted)}
'''

arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
wa = lambda t: 'https://wa.me/6282258475758?text=' + u.quote(f'Halo, saya ingin menanyakan produk {t}')
def row(href, inner, sub):
    return f'<a href="{href}"><span>{inner}<small>{sub}</small></span>{arrow}</a>'
exc = ''.join([
    row('?cat=ofamed#katalog', '<img src="img/ofamed.png" alt="Ofamed" width="160" height="50">', 'Lihat produk'),
    row('?cat=ofahusada#katalog', '<img src="img/ofahusada.png" alt="Ofahusada" width="200" height="56">', 'Lihat produk'),
    row(wa('Ofafa Beauty Care'), '<img class="dark" src="img/beauty.png" alt="Ofafa Beauty Care" width="200" height="56">', 'Tanyakan produk')])
non = row('?cat=habis#katalog', '<b>Barang Habis Pakai</b>', 'Lihat produk') + ''.join(row(wa(n), f'<b>{n}</b>', 'Tanyakan produk') for n in ['Unit', 'Furniture Hospital'])
tiers = f'''<section class="products"><div class="wrap">
<div class="head"><h2>Exclusive Product by Ofamed</h2><p class="lead">Produk kami dikembangkan dengan kualitas tinggi dengan berbagai jenis dan kategori unggulan yang diciptakan untuk kepuasan pelanggan.</p></div>
<div class="index">{exc}</div></div></section>
<section class="products" style="padding-top:0"><div class="wrap">
<div class="head"><h2>Non Exclusive Product</h2></div>
<div class="index">{non}</div></div></section>'''
main = f'''<main id="main">{tiers}<section class="cat" id="katalog"><div class="wrap">
<h1>Katalog</h1>
<p class="lead">Perlengkapan medis dan habis pakai yang tersedia melalui Ofamed. Harga dan ketersediaan, silakan tanyakan lewat WhatsApp.</p>
<label for="q">Cari produk</label><input id="q" type="search" autocomplete="off">
<label for="f">Kategori</label><select id="f"><option value="">Semua</option><option value="ofamed">Ofamed (Exclusive)</option><option value="ofahusada">Ofahusada (Exclusive)</option><option value="habis">Barang Habis Pakai (Non Exclusive)</option></select>
<p id="empty" role="status" hidden>Produk tidak ditemukan. Hubungi kami, kami bantu carikan.</p>
<ul class="grid">
{cards}</ul>
</div></section></main>
<script>
const q=document.getElementById('q'),f=document.getElementById('f'),cs=[...document.querySelectorAll('.card')],em=document.getElementById('empty');
const go=()=>{{const v=q.value.trim().toLowerCase();let n=0;for(const c of cs){{const h=!c.dataset.name.includes(v)||(f.value&&c.dataset.cat!==f.value);c.hidden=h;n+=!h}}em.hidden=n>0}};
q.addEventListener('input',go);f.addEventListener('change',go);
f.value=new URLSearchParams(location.search).get('cat')||'';go();
</script>'''

a, b = s.index('<main'), s.index('</main>') + 7
out = s[:a] + main + s[b:]
# drop index-only script (reel) and fix nav state
out = re.sub(r'<script>\n// auto-advance.*?</script>\n', '', out, flags=re.S)
out = out.replace('<a href="index.html" aria-current="page">Beranda', '<a href="index.html">Beranda').replace('<a href="produk.html">Produk', '<a href="produk.html" aria-current="page">Produk', 1)
out = out.replace('</style>', css + '</style>', 1)
out = re.sub(r'<title>.*?</title>', '<title>Produk | Ofamed</title>', out)
assert 'aria-current="page">Produk' in out and out.count('<main') == 1
open('produk.html', 'w', encoding='utf-8').write(out)
print(len(P), 'products')
