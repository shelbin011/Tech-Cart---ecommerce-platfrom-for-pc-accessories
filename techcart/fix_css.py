import re

css_fix = '''
<style>
.category-area .col-lg-8.col-md-8 .single-deal { height: 250px; }
.category-area .col-lg-8.col-md-8 .single-deal img { height: 250px; object-fit: cover; width: 100%; border-radius: 8px; }
.category-area .col-lg-4.col-md-4 .single-deal { height: 250px; }
.category-area .col-lg-4.col-md-4 .single-deal img { height: 250px; object-fit: cover; width: 100%; border-radius: 8px; }
.category-area > .container > .row > .col-lg-4.col-md-6 .single-deal { height: 530px; }
.category-area > .container > .row > .col-lg-4.col-md-6 .single-deal img { height: 530px; object-fit: cover; width: 100%; border-radius: 8px; }
.single-deal { margin-bottom: 30px; border-radius: 8px; overflow: hidden; display: block; }
</style>
'''

def fix_css(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    if '<style>' not in html:
        if '{% block content %}' in html:
            html = html.replace('{% block content %}', '{% block content %}\n' + css_fix)
        else:
            html = css_fix + html
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)

fix_css(r'f:\Techcart\techcart\customer_app\templates\customer_app\category.html')

with open(r'f:\Techcart\techcart\customer_app\templates\customer_app\home.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

home_html = re.sub(r'<style>.*?</style>', '', home_html, flags=re.DOTALL)
home_html = home_html.replace('{% block content %}', '{% block content %}\n' + css_fix)

with open(r'f:\Techcart\techcart\customer_app\templates\customer_app\home.html', 'w', encoding='utf-8') as f:
    f.write(home_html)
