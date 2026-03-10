import re

template_file = r'f:\Techcart\techcart\customer_app\templates\customer_app\category.html'
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add ?v=1 to the end of all {% static ... %} tags for images
content = re.sub(r'\{%\s*static\s+\'([^\']+)\'\s*%\}', r"{% static '\1' %}?v=1", content)

with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated category.html with cache busting.")
