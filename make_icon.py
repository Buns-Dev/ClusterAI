from PIL import Image

def process_and_save_ico(input_path, output_path, target_rgb=(145, 179, 250)):
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()

        new_data = []
        for item in datas:
            r, g, b, a = item[:4]
            if r > 220 and g > 220 and b > 220:
                new_data.append((0, 0, 0, 0))
            elif r < 50 and g < 50 and b < 50:
                new_data.append((target_rgb[0], target_rgb[1], target_rgb[2], 255))
            else:
                new_data.append((target_rgb[0], target_rgb[1], target_rgb[2], max(0, 255 - r)))

        img.putdata(new_data)
        
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            
        width, height = img.size
        max_dim = max(width, height)
        square_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
        
        offset_x = (max_dim - width) // 2
        offset_y = (max_dim - height) // 2
        square_img.paste(img, (offset_x, offset_y))

        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        square_img.save(output_path, format="ICO", sizes=icon_sizes)
        print(f"\n[✦] Success! Maximized brand asset created: '{output_path}'")
        
    except FileNotFoundError:
        print(f"\n[!] Error: Could not find '{input_path}'.")

if __name__ == "__main__":
    process_and_save_ico("NOVA LOGO.png", "star.ico")