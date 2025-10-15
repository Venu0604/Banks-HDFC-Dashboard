"""
Optimize images for faster loading in dashboard
Reduces file size while maintaining quality
"""

from PIL import Image
import os

def optimize_image(input_path, output_path=None, max_width=800, quality=85):
    """
    Optimize an image by resizing and compressing

    Args:
        input_path: Path to input image
        output_path: Path to save optimized image (if None, overwrites input)
        max_width: Maximum width in pixels (maintains aspect ratio)
        quality: JPEG quality (1-100, higher is better)
    """
    if output_path is None:
        output_path = input_path

    # Open image
    img = Image.open(input_path)

    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Resize if too large
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Save with optimization
    img.save(output_path, 'PNG', optimize=True, quality=quality)

    # Show file size reduction
    original_size = os.path.getsize(input_path) / 1024  # KB
    new_size = os.path.getsize(output_path) / 1024  # KB
    reduction = ((original_size - new_size) / original_size) * 100

    print(f"✅ Optimized: {os.path.basename(input_path)}")
    print(f"   Original: {original_size:.1f} KB")
    print(f"   Optimized: {new_size:.1f} KB")
    print(f"   Reduction: {reduction:.1f}%\n")


if __name__ == "__main__":
    # Optimize campaign image (the large one)
    print("🔧 Optimizing images for faster dashboard loading...\n")

    public_dir = "Public"

    # Optimize the large campaign analysis image
    campaign_image = os.path.join(public_dir, "HDFC campaign Analysis.png")
    if os.path.exists(campaign_image):
        # Create backup first
        backup = campaign_image.replace(".png", "_original.png")
        if not os.path.exists(backup):
            os.rename(campaign_image, backup)
            print(f"📦 Created backup: {os.path.basename(backup)}\n")

        # Optimize (resize to 600px width for header display)
        optimize_image(backup, campaign_image, max_width=600, quality=90)

    print("✅ All images optimized!")
    print("\nYour dashboard will now load faster! 🚀")
