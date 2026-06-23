from PIL import Image
from rembg import remove

def create_flawless_ico(input_path, output_path):
    try:
        print("🪄 Tracing edges and removing background...")
        # Load the original image
        img = Image.open(input_path).convert("RGBA")
        
        # Use AI to perfectly isolate the galaxy from the fake checkerboard
        img_no_bg = remove(img)
        
        # Crop out the empty space left behind
        bbox = img_no_bg.getbbox()
        if bbox:
            img_no_bg = img_no_bg.crop(bbox)
            
        # Create a perfectly square, 100% transparent canvas
        width, height = img_no_bg.size
        max_dim = max(width, height)
        square_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
        
        # Center the galaxy onto the transparent square
        offset_x = (max_dim - width) // 2
        offset_y = (max_dim - height) // 2
        square_img.paste(img_no_bg, (offset_x, offset_y), img_no_bg)

        # Save it as a multi-size Windows icon
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        square_img.save(output_path, format="ICO", sizes=icon_sizes)
        print(f"\n[✦] Success! Flawless transparent asset created: '{output_path}'")
        
    except FileNotFoundError:
        print(f"\n[!] Error: Could not find '{input_path}'.")
    except Exception as e:
        print(f"\n[!] An error occurred: {e}")

if __name__ == "__main__":
    # Replace the input name if your downloaded image has a different name
    create_flawless_ico("ClusterAI-Logo(U+1F30C).png", "clusterAI.ico")