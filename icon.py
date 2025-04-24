from PIL import Image, ImageDraw
import os

# Criar uma nova imagem com fundo transparente
size = (256, 256)
image = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Cores
azul_escuro = (41, 128, 185)
branco = (255, 255, 255)

# Desenhar um quadrado arredondado (representando uma caixa)
margin = 40
box_bounds = [margin, margin, size[0]-margin, size[1]-margin]
draw.rounded_rectangle(box_bounds, radius=20, fill=azul_escuro)

# Desenhar linhas horizontais (representando itens na lista)
line_spacing = 30
start_y = 80
for i in range(4):
    y = start_y + (i * line_spacing)
    draw.line([(margin+30, y), (size[0]-margin-30, y)], fill=branco, width=4)

# Salvar como PNG primeiro
png_path = "icon.png"
image.save(png_path)

# Converter para ICO
ico_path = "icon.ico"
img = Image.open(png_path)
img.save(ico_path, format='ICO', sizes=[(256, 256)])

# Remover o arquivo PNG temporário
os.remove(png_path)

print("Ícone criado com sucesso!")