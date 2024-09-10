import sys
import random
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, 
                             QWidget, QComboBox, QMessageBox, QRadioButton, QButtonGroup, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from PIL import Image
import os
import colorsys
import math
import numpy as np

class SpriteMixer(QMainWindow):
    def __init__(self):
        super().__init__()
         # Window Tile, Size, Appearance
        self.setWindowTitle("Sprite Mixer")
        self.setGeometry(200, 200, 600, 700)
        self.setStyleSheet("background-color: white;")  # White background

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Upload Image Button
        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.clicked.connect(self.upload_image)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #6495ED;
                border: none;
                color: white;
                padding: 15px 32px;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #4169E1;
            }
        """)
        main_layout.addWidget(self.upload_button)

        # Image Display Section
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px;")
        main_layout.addWidget(self.image_label)

        # Buttons for Image Type (Standard, Pixelated, or High-Res)
        radio_layout = QHBoxLayout()
        self.image_type_group = QButtonGroup(self)
        for text in ["Standard Image", "Pixelated Sprite", "High-Res Image"]:
            radio = QRadioButton(text)
            radio.setStyleSheet("QRadioButton { font-size: 14px; }")
            self.image_type_group.addButton(radio)
            radio_layout.addWidget(radio)
        self.image_type_group.buttons()[0].setChecked(True)  # Default selection
        main_layout.addLayout(radio_layout)

        # Color Palette Dropdown
        self.palette_combo = QComboBox(self)
        self.palette_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #6495ED;
                border-radius: 10px;
                padding: 5px;
                background-color: 6495ED;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #6495ED;
                background-color: white;
                selection-background-color: #6495ED;
            }
            QComboBox QAbstractItemView::item {
                background-color: transparent;
                color: black;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #6495ED;
                color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #4169E1;
                color: white;
            }
        """)
        main_layout.addWidget(self.palette_combo)

        # Buttons
        self.scramble_button = QPushButton("Scramble Colors", self)
        self.scramble_button.clicked.connect(self.scramble_image)
        self.scramble_button.setEnabled(False)
        self.save_button = QPushButton("Save Scrambled Image", self)
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)

        for button in [self.scramble_button, self.save_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #6495ED;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    font-size: 16px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #4169E1;
                }
                QPushButton:disabled {
                    background-color: #D3D3D3;
                    color: #808080;
                }
            """)
            main_layout.addWidget(button)

        # Central Widget
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Image Variables
        self.original_image = None
        self.scrambled_image = None
        self.image_path = None

        self.load_palettes()

    def load_palettes(self):
        try:
            # Load JSON File Colors
            with open("color-palettes.json", "r") as f:
                self.palettes = json.load(f)

            # Add Palette Scheme Names
            for palette_name in self.palettes.keys():
                self.palette_combo.addItem(palette_name)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "color-palettes.json file not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Invalid JSON format in color-palettes.json.")
            sys.exit(1)
	# Image Upload Function
    def upload_image(self):
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        
        if self.image_path:
            try:
                self.original_image = Image.open(self.image_path)
                # Convert palette-based images (mode "P") to RGB
                if self.original_image.mode == "P":
                    self.original_image = self.original_image.convert("RGB")
                # Ensure the image is in RGB or RGBA mode
                if self.original_image.mode not in ["RGB", "RGBA"]:
                    self.original_image = self.original_image.convert("RGB")
                
                # Resize Large Images
                max_size = 1000  # Maximum width or height
                if max(self.original_image.size) > max_size:
                    self.original_image.thumbnail((max_size, max_size), Image.LANCZOS)
                
                self.display_image(self.original_image)
                self.scramble_button.setEnabled(True)
                self.save_button.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def display_image(self, img):
        # Convert PIL Image to QPixmap
        qimage = self.pil2pixmap(img)
        self.image_label.setPixmap(qimage.scaled(400, 400, Qt.KeepAspectRatio))

    def scramble_image(self):
        if self.original_image:
            # Get the selected palette
            selected_palette = self.palette_combo.currentText()
            palette_colors = self.palettes[selected_palette]
            
            # Choose Scrambling Method
            if self.image_type_group.buttons()[0].isChecked():
                self.scrambled_image = self.replace_colors_with_palette_regular(self.original_image.copy(), palette_colors)
            elif self.image_type_group.buttons()[1].isChecked():
                self.scrambled_image = self.replace_colors_with_palette_sprite(self.original_image.copy(), palette_colors)
            else:  # Hi-res image
                self.scrambled_image = self.replace_colors_with_palette_hi_res(self.original_image.copy(), palette_colors)
            
            self.display_image(self.scrambled_image)
            self.save_button.setEnabled(True)

    def replace_colors_with_palette_regular(self, img, palette_colors):
        pixels = img.load()  # Load pixel data
        width, height = img.size
        has_alpha = img.mode == 'RGBA'

        # Convert palette colors to CIELAB
        lab_palette = [self.rgb_to_lab(self.hex_to_rgb(color)) for color in palette_colors]

        # Create a shuffled version of the palette
        shuffled_lab_palette = lab_palette.copy()
        random.shuffle(shuffled_lab_palette)

        # Create a mapping between original palette colors and shuffled palette colors
        color_mapping = dict(zip(lab_palette, shuffled_lab_palette))

        # Step 1: Replace colors
        for y in range(height):
            for x in range(width):
                if has_alpha:
                    r, g, b, a = pixels[x, y]  # Unpack RGBA values
                else:
                    r, g, b = pixels[x, y]  # Unpack RGB values
                    a = 255  # Set alpha to fully opaque for RGB images

                lab = self.rgb_to_lab((r, g, b))
                closest_color = self.find_closest_color(lab, lab_palette)
                new_color = color_mapping[closest_color]
                new_r, new_g, new_b = self.lab_to_rgb(new_color)
                
                if has_alpha:
                    pixels[x, y] = (int(new_r), int(new_g), int(new_b), a)
                else:
                    pixels[x, y] = (int(new_r), int(new_g), int(new_b))

        return img

    def replace_colors_with_palette_sprite(self, img, palette_colors):
        pixels = img.load()  # Load pixel data
        width, height = img.size
        has_alpha = img.mode == 'RGBA'

        # Find Unique Colors
        unique_colors = set()
        for y in range(height):
            for x in range(width):
                if has_alpha:
                    r, g, b, a = pixels[x, y]  # Unpack RGBA values
                else:
                    r, g, b = pixels[x, y]  # Unpack RGB values
                    a = 255  # Set alpha to fully opaque for RGB images
                unique_colors.add((r, g, b, a))

        # Make New Color Mapping
        color_mapping = {}
        palette_length = len(palette_colors)
        shuffled_palette = palette_colors.copy()
        random.shuffle(shuffled_palette)
        
        for idx, color in enumerate(unique_colors):
            hex_color = shuffled_palette[idx % palette_length]
            r, g, b = self.hex_to_rgb(hex_color)
            color_mapping[color] = (r, g, b, color[3])  # Keep alpha unchanged

        # Replace Original Colors
        for y in range(height):
            for x in range(width):
                if has_alpha:
                    r, g, b, a = pixels[x, y]  # Unpack RGBA values
                else:
                    r, g, b = pixels[x, y]  # Unpack RGB values
                    a = 255  # Set alpha to fully opaque for RGB images
                if (r, g, b, a) in color_mapping:
                    new_color = color_mapping[(r, g, b, a)]
                    if has_alpha:
                        pixels[x, y] = new_color
                    else:
                        pixels[x, y] = new_color[:3]

        return img

    def replace_colors_with_palette_hi_res(self, img, palette_colors):
        # Convert image to numpy array
        img_array = np.array(img)
        
        # Convert to CIELAB
        lab_palette = np.array([self.rgb_to_lab(self.hex_to_rgb(color)) for color in palette_colors])
        
        # Convert image to CIELAB color space
        lab_image = self.rgb_to_lab_array(img_array)
        
        # Find Closest Palette Color For Each Pixel
        distances = np.sqrt(((lab_image[:, :, np.newaxis, :] - lab_palette[np.newaxis, np.newaxis, :, :]) ** 2).sum(axis=3))
        closest_palette_indices = distances.argmin(axis=2)
        
        # Create Shuffled Palette
        shuffled_palette = np.random.permutation(lab_palette)
        
        # Apply Shuffled Palette Colors
        new_lab_image = shuffled_palette[closest_palette_indices]
        
        # Revert to RGB
        new_rgb_image = self.lab_to_rgb_array(new_lab_image)
        
        # Create New PIL Image
        new_img = Image.fromarray(np.uint8(new_rgb_image))
        
        # Add Original Alpha Channel
        if img.mode == 'RGBA':
            r, g, b, a = img.split()
            new_img.putalpha(a)
        
        return new_img

    def rgb_to_lab_array(self, rgb_array):
        if rgb_array.shape[2] == 4:
            rgb_array = rgb_array[:, :, :3]  # Remove alpha channel for conversion
        
        # Normalize RGB Values
        rgb_normalized = rgb_array / 255.0
        
        # Gamma Correction
        mask = rgb_normalized > 0.04045
        rgb_normalized[mask] = ((rgb_normalized[mask] + 0.055) / 1.055) ** 2.4
        rgb_normalized[~mask] /= 12.92
        
        # Convert to XYZ
        xyz = np.dot(rgb_normalized, np.array([
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041]
        ]).T)
        
        # Normalize XYZ Values
        xyz[:,:,0] /= 0.95047
        xyz[:,:,1] /= 1.00000
        xyz[:,:,2] /= 1.08883
        
        # Convert to LAB 
        mask = xyz > 0.008856
        xyz[mask] = xyz[mask] ** (1/3)
        xyz[~mask] = 7.787 * xyz[~mask] + 16/116
        
        x, y, z = xyz[:,:,0], xyz[:,:,1], xyz[:,:,2]
        L = (116 * y) - 16
        a = 500 * (x - y)
        b = 200 * (y - z)
        
        return np.stack([L, a, b], axis=-1)

    def lab_to_rgb_array(self, lab_array):
        L, a, b = lab_array[:,:,0], lab_array[:,:,1], lab_array[:,:,2]
        
        y = (L + 16) / 116
        x = a / 500 + y
        z = y - b / 200
        
        xyz = np.stack([x, y, z], axis=-1)
        
        mask = xyz > 0.2068966
        xyz[mask] = xyz[mask]**3
        xyz[~mask] = (xyz[~mask] - 16/116) / 7.787
        
        xyz[:,:,0] *= 0.95047
        xyz[:,:,1] *= 1.00000
        xyz[:,:,2] *= 1.08883
        
        rgb = np.dot(xyz, np.array([
            [ 3.2404542, -1.5371385, -0.4985314],
            [-0.9692660,  1.8760108,  0.0415560],
            [ 0.0556434, -0.2040259,  1.0572252]
        ]).T)
        
        mask = rgb > 0.0031308
        rgb[mask] = 1.055 * rgb[mask]**(1/2.4) - 0.055
        rgb[~mask] *= 12.92
        
        rgb = np.clip(rgb, 0, 1)
        
        return rgb * 255

    def hex_to_rgb(self, hex_color):
        return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    def rgb_to_lab(self, rgb):
        r, g, b = [x / 255.0 for x in rgb]
        x, y, z = self.rgb_to_xyz(r, g, b)
        return self.xyz_to_lab(x, y, z)

    def rgb_to_xyz(self, r, g, b):
        r = self.gamma_correct(r)
        g = self.gamma_correct(g)
        b = self.gamma_correct(b)
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        return x, y, z

    def gamma_correct(self, c):
        if c > 0.04045:
            return ((c + 0.055) / 1.055) ** 2.4
        else:
            return c / 12.92

    def xyz_to_lab(self, x, y, z):
        x = x / 0.95047
        y = y / 1.00000
        z = z / 1.08883
        x = self.lab_f(x)
        y = self.lab_f(y)
        z = self.lab_f(z)
        L = 116 * y - 16
        a = 500 * (x - y)
        b = 200 * (y - z)
        return L, a, b

    def lab_f(self, t):
        if t > 0.008856:
            return t ** (1/3)
        else:
            return (903.3 * t + 16) / 116

    def lab_to_rgb(self, lab):
        L, a, b = lab
        y = (L + 16) / 116
        x = a / 500 + y
        z = y - b / 200
        x = 0.95047 * self.lab_f_inv(x)
        y = self.lab_f_inv(y)
        z = 1.08883 * self.lab_f_inv(z)
        r, g, b = self.xyz_to_rgb(x, y, z)
        return r * 255, g * 255, b * 255

    def lab_f_inv(self, t):
        if t > 0.206893:
            return t ** 3
        else:
            return (t - 16 / 116) * 3 * 0.008856

    def xyz_to_rgb(self, x, y, z):
        r = x *  3.2404542 + y * -1.5371385 + z * -0.4985314
        g = x * -0.9692660 + y *  1.8760108 + z *  0.0415560
        b = x *  0.0556434 + y * -0.2040259 + z *  1.0572252
        r = self.gamma_correct_inv(r)
        g = self.gamma_correct_inv(g)
        b = self.gamma_correct_inv(b)
        return r, g, b

    def gamma_correct_inv(self, c):
        if c > 0.0031308:
            return 1.055 * (c ** (1 / 2.4)) - 0.055
        else:
            return 12.92 * c

    def find_closest_color(self, target_color, color_list):
        min_distance = float('inf')
        closest_color = None
        for color in color_list:
            distance = self.color_distance(target_color, color)
            if distance < min_distance:
                min_distance = distance
                closest_color = color
        return closest_color

    def color_distance(self, color1, color2):
        l1, a1, b1 = color1
        l2, a2, b2 = color2
        return math.sqrt((l1 - l2)**2 + (a1 - a2)**2 + (b1 - b2)**2)

    def save_image(self):
        if self.scrambled_image and self.image_path:
            # Generate the new file name
            file_dir, file_name = os.path.split(self.image_path)
            name, ext = os.path.splitext(file_name)
            base_new_name = f"{name}-sprite-mix{ext}"
            new_name = base_new_name
            counter = 1

            # Check & Change File Name Incrementally
            while os.path.exists(os.path.join(file_dir, new_name)):
                new_name = f"{name}-sprite-mix-{counter}{ext}"
                counter += 1

            save_path = os.path.join(file_dir, new_name)

            # Save Scrambled Image
            self.scrambled_image.save(save_path)
            print(f"Image saved as: {save_path}")

    def pil2pixmap(self, image):
        """Convert PIL Image to QPixmap for display in QLabel."""
        if image.mode == "RGB":
            qim = QImage(image.tobytes("raw", "RGB"), image.size[0], image.size[1], QImage.Format_RGB888)
        elif image.mode == "RGBA":
            qim = QImage(image.tobytes("raw", "RGBA"), image.size[0], image.size[1], QImage.Format_RGBA8888)
        else:
            # Convert Any Other Mode to RGBA
            image = image.convert("RGBA")
            qim = QImage(image.tobytes("raw", "RGBA"), image.size[0], image.size[1], QImage.Format_RGBA8888)
        
        pixmap = QPixmap.fromImage(qim)
        return pixmap

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpriteMixer()
    window.show()
    sys.exit(app.exec_())
