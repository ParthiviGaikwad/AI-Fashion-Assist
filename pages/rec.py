import streamlit as st
import cv2
import numpy as np
import math
import requests
from collections import Counter
from PIL import Image
import torch
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet101
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
from io import BytesIO
from duckduckgo_search import DDGS

# Set page config
st.set_page_config(page_title="Fashion Analyzer", layout="wide")

# White Balance
def white_balance(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = cv2.split(lab)
    avg_a = np.average(A)
    avg_b = np.average(B)
    A = A - ((avg_a - 128) * (L / 255.0) * 1.1)
    B = B - ((avg_b - 128) * (L / 255.0) * 1.1)
    lab = cv2.merge([L, A, B])
    lab = np.clip(lab, 0, 255).astype(np.uint8)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

# CLAHE Enhancement
def enhance_image(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)

# Skin Color Detection
def most_frequent_color(original_img, mask):
    pixels = original_img[mask > 0].reshape(-1, 3)
    pixel_counts = Counter(map(tuple, pixels))
    most_common_color = pixel_counts.most_common(1)[0][0]
    hex_color = "#{:02x}{:02x}{:02x}".format(*most_common_color[::-1])
    return most_common_color, hex_color

def color_distance(c1, c2):
    return np.sqrt(np.sum((np.array(c1) - np.array(c2)) ** 2))

skin_color_scale = [
    (234, 216, 196), (224, 200, 174), (210, 184, 151), (196, 166, 130),
    (180, 151, 111), (165, 133, 94), (160, 131, 95), (128, 100, 61),
    (109, 85, 51), (89, 68, 39), (69, 52, 32)
]

def nearest_skin_color(detected_color):
    closest_color = min(skin_color_scale, key=lambda c: color_distance(detected_color, c))
    return "#{:02x}{:02x}{:02x}".format(*closest_color)

# Load Detectron2 Keypoint Detection Model
def load_detectron2_model():
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml")
    cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    return DefaultPredictor(cfg)

# Perform Keypoint Detection
def detect_keypoints(model, image):
    outputs = model(image)
    keypoints = outputs["instances"].pred_keypoints.cpu().numpy()
    return image, keypoints

# Extract keypoints and calculate distances
def extract_measurements(keypoints):
    keypoint_names = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]
    keypoints_dict = {name: (int(x), int(y)) for name, (x, y, _) in zip(keypoint_names, keypoints[0])}

    left_shoulder = keypoints_dict["left_shoulder"]
    right_shoulder = keypoints_dict["right_shoulder"]
    left_breast = (keypoints_dict["left_shoulder"][0], (keypoints_dict["left_shoulder"][1] + keypoints_dict["left_elbow"][1]) // 2)
    right_breast = (keypoints_dict["right_shoulder"][0], (keypoints_dict["right_shoulder"][1] + keypoints_dict["right_elbow"][1]) // 2)
    left_waist = (keypoints_dict["left_hip"][0], keypoints_dict["left_elbow"][1])
    right_waist = (keypoints_dict["right_hip"][0], keypoints_dict["right_elbow"][1])
    left_hip = keypoints_dict["left_hip"]
    right_hip = keypoints_dict["right_hip"]
    return {
        "shoulders": calculate_width(left_shoulder, right_shoulder),
        "bust": calculate_width(left_breast, right_breast),
        "waist": calculate_width(left_waist, right_waist),
        "hips": calculate_width(left_hip, right_hip)
    }

# Calculate Euclidean distance between two points
def calculate_width(point1, point2):
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def classify_body_shape(measurements):
    bust, waist, hips, shoulders = measurements["bust"], measurements["waist"], measurements["hips"], measurements["shoulders"]

    if waist <= bust * 0.65 and waist <= shoulders * 0.65:
        return "hourglass"
    elif shoulders / hips >= 1.5 or bust / hips >= 1.5:
        return "inverted triangle"
    elif hips / bust >= 1.1 and hips / shoulders >= 1.1:
        return "pear"
    else:
        return "rectangle"

def recommend_fashion(season, body_shape):
    recs = {
        "hourglass": {
            "Spring": {
                "clothing": "Fitted dresses, A-line skirts, pastel-colored tops with bold accessories.",
                "jewelry": "Gold jewelry, light pink or rose gold for a soft and feminine look.",
                "casual": "Tailored jeans with fitted t-shirts or blouse, statement belt.",
                "formal": "Long evening gowns with a waist-cinching belt, diamond jewelry with a touch of rose gold."
            },
            "Summer": {
                "clothing": "V-neck tops, high-waisted shorts, peplum blouses to emphasize the waist.",
                "jewelry": "Silver or platinum jewelry, soft pastels like lavender or baby blue.",
                "casual": "Casual V-neck t-shirts with denim shorts, layered jewelry.",
                "formal": "Elegant long dresses, silver jewelry with a chic and modern look."
            },
            "Autumn": {
                "clothing": "Wrap dresses, belted coats, earth-toned fitted blazers.",
                "jewelry": "Copper, bronze, or earthy-toned jewelry like amber and topaz.",
                "casual": "Chic trench coat with comfortable jeans, rose gold accessories.",
                "formal": "Sleek fitted dresses in warm tones with a statement necklace."
            },
            "Winter": {
                "clothing": "Monochromatic outfits with structured jackets and bold accessories.",
                "jewelry": "Bold silver, platinum, and dark jewel tones like sapphire or ruby.",
                "casual": "Oversized sweater with slim-fit pants, silver hoop earrings.",
                "formal": "Fitted wool coats with dramatic jewelry pieces like emerald necklaces."
            }
        },
        "inverted triangle": {
            "Spring": {
                "clothing": "A-line skirts, high-waisted pants, and soft draping tops.",
                "jewelry": "Silver jewelry, with light tones like turquoise or pastel shades to balance the upper body.",
                "casual": "Fitted t-shirt with high-waisted denim jeans.",
                "formal": "Tailored blazers and flowy wide-legged trousers, platinum jewelry with diamond studs."
            },
            "Summer": {
                "clothing": "Flowy blouses, boat neck tops, and full skirts.",
                "jewelry": "Gold jewelry with vibrant gemstone accents, like emerald or coral.",
                "casual": "Loose-fitting blouse with denim skirt, gold bracelets.",
                "formal": "Chic jumpsuit with bold earrings and a sleek necklace."
            },
            "Autumn": {
                "clothing": "Asymmetrical tops, flared jeans, knee-high boots.",
                "jewelry": "Brass or copper jewelry with warmer tones like tiger's eye or brown topaz.",
                "casual": "Turtleneck sweaters with tailored pants, silver or rose gold hoops.",
                "formal": "Flared midi skirt with fitted top and statement jewelry."
            },
            "Winter": {
                "clothing": "Structured jackets with defined waistlines, oversized scarves.",
                "jewelry": "Silver or platinum with dark colors like onyx, garnet, or deep emerald.",
                "casual": "Sleek jacket with straight-leg jeans, small silver studs.",
                "formal": "Long coat with fitted waist, silver jewelry with matching gemstones."
            }
        },
        "pear": {
            "Spring": {
                "clothing": "Bright tops, asymmetrical designs, and empire waist dresses.",
                "jewelry": "Gold jewelry, with warm tones like amber and citrine for a radiant appearance.",
                "casual": "Ruffle tops, slim-fit trousers, and a colorful scarf.",
                "formal": "Empire-waist gowns with matching jewelry in gold."
            },
            "Summer": {
                "clothing": "Ruffle tops, cropped jackets, wide-legged pants.",
                "jewelry": "Rose gold jewelry to complement soft summer tones, and delicate chains.",
                "casual": "Comfortable blouse with wide-leg pants, layered rose gold rings.",
                "formal": "Maxi dress with a belt to define the waist, with a subtle gemstone necklace."
            },
            "Autumn": {
                "clothing": "Flared trousers, wrap skirts, dresses that accentuate the waist.",
                "jewelry": "Bronze and copper, with deep colors like ruby and garnet to complement warm hues.",
                "casual": "High-waisted skirts with chunky sweaters, bronze earrings.",
                "formal": "Tailored wrap dresses with bold copper jewelry."
            },
            "Winter": {
                "clothing": "Dark-colored pants, tailored blazers, long trench coats.",
                "jewelry": "Platinum and silver jewelry, with rich jewel tones like amethyst, sapphire, and emerald.",
                "casual": "Cozy sweater with straight-leg jeans, silver hoops.",
                "formal": "Floor-length gowns with dramatic jewelry pieces like sapphire earrings."
            }
        },
        "rectangle": {
            "Spring": {
                "clothing": "Layered outfits, belts to create the illusion of curves, colorful printed tops.",
                "jewelry": "Silver jewelry, accentuated with emeralds or peridot to add a touch of contrast.",
                "casual": "Layered top with tailored trousers, minimalist jewelry.",
                "formal": "Fitted dresses with belt, statement necklace."
            },
            "Summer": {
                "clothing": "Soft, flowing dresses, tailored shorts, boatneck tops.",
                "jewelry": "Gold jewelry with soft gemstone accents like aquamarine or light sapphire.",
                "casual": "Casual dress with accessories, gold bangles.",
                "formal": "Sheath dress with a sleek necklace and earrings."
            },
            "Autumn": {
                "clothing": "Structured coats, pleated skirts, bold colors.",
                "jewelry": "Bronze and brass jewelry, with statement pieces like large turquoise or amber stones.",
                "casual": "Structured cardigan with fitted pants, bold rings.",
                "formal": "Fitted skirts with statement necklaces and bracelets."
            },
            "Winter": {
                "clothing": "Oversized sweaters, straight-leg jeans, bold patterns.",
                "jewelry": "Platinum or silver jewelry with bold gemstones like ruby or sapphire.",
                "casual": "Comfy sweater with skinny jeans, chunky rings.",
                "formal": "Fitted sweater dress with statement jewelry."
            }
        }
    }
    return recs.get(body_shape, {}).get(season, {"clothing": "No recommendation available.", "jewelry": "No recommendation available."})

def display_color_palette(season):
    season_palettes = {
        "Spring": [
            '#FFDAB9', '#FFE4B5', '#FFFACD', '#E6E6FA',
            '#F0FFF0', '#FFEFD5', '#FFF5EE', '#F5F5DC',
            '#FAF0E6', '#FFEBCD', '#F0F8FF', '#FFF8DC'
        ],
        "Summer": [
            '#87CEFA', '#D8BFD8', '#AFEEEE', '#E0FFFF',
            '#FFF0F5', '#F0E68C', '#E6E6FA', '#B0E0E6',
            '#ADD8E6', '#F5F5F5', '#D3D3D3', '#F8F1F1'
        ],
        "Autumn": [
            '#D2B48C', '#CD853F', '#DEB887', '#BC8F8F',
            '#F4A460', '#DAA520', '#B8860B', '#A0522D',
            '#8B4513', '#DEB4A5', '#E3A869', '#CC9966'
        ],
        "Winter": [
            '#708090', '#778899', '#2F4F4F', '#000080',
            '#4B0082', '#483D8B', '#191970', '#4682B4',
            '#5F9EA0', '#B0C4DE', '#6A5ACD', '#3C2F2F'
        ]
    }
    palette = season_palettes.get(season, season_palettes["Winter"])
    
    cols = st.columns(4)
    for i, color in enumerate(palette):
        with cols[i % 4]:
            st.markdown(f"""<div style="height: 80px; background-color: {color}; 
                        display: flex; justify-content: center; align-items: center;
                        border-radius: 5px; margin-bottom: 10px;">
                        </div>""", unsafe_allow_html=True)
            st.caption(color)

import streamlit as st
import numpy as np
import cv2
import os

def main():
    st.title("Fashion Analyzer")
    st.write("Analyzing image for skin tone and body shape for fashion recommendations")

    # Read image path from file
    try:
        with open(r'img\uploaded_image_path.txt', 'r') as f:
            path = f.read().strip()
    except FileNotFoundError:
        st.error("Image path file not found.")
        return

    if not os.path.exists(path):
        st.error(f"Image not found at path: {path}")
        return

    # Load image from the path
    original = cv2.imread(path)
    if original is None:
        st.error("Failed to load image.")
        return

    # Display original image
    st.subheader("Original Image")
    st.image(cv2.cvtColor(original, cv2.COLOR_BGR2RGB), use_container_width=True)

    # --- Skin Tone Detection ---
    with st.spinner("Analyzing skin tone..."):
        wb_img = white_balance(original.copy())
        enhanced_img = enhance_image(wb_img)
        ycrcb = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2YCrCb)
        mask = cv2.inRange(ycrcb, np.array([0, 135, 85]), np.array([255, 180, 135]))
        detected_color, hex_color = most_frequent_color(wb_img, mask)

        def find_nearest_skin_color(detected_rgb):
            palette_map = {
                "#ead8c4": "Spring", "#e0c8ae": "Spring",
                "#d2b897": "Summer", "#c4a682": "Summer",
                "#b4976f": "Autumn", "#a5855e": "Autumn", "#a7835f": "Autumn",
                "#80643d": "Winter", "#6d5533": "Winter", "#594427": "Winter", "#453420": "Winter"
            }
            min_dist = float('inf')
            closest_hex = None
            for hex_code in palette_map:
                palette_rgb = np.array([int(hex_code[1:3], 16), int(hex_code[3:5], 16), int(hex_code[5:7], 16)])
                dist = np.linalg.norm(np.array(detected_rgb) - palette_rgb)
                if dist < min_dist:
                    min_dist = dist
                    closest_hex = hex_code
            return closest_hex, palette_map.get(closest_hex, "Winter")

        rounded_hex, season = find_nearest_skin_color(detected_color)

        # Display skin tone results
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Skin Tone Analysis")
            st.markdown(f"**Detected Skin Tone:** <span style='color:{hex_color}; font-weight:bold'>{hex_color}</span>", unsafe_allow_html=True)
            st.markdown(f"**Nearest Tone:** <span style='color:{rounded_hex}; font-weight:bold'>{rounded_hex}</span>", unsafe_allow_html=True)
            st.markdown(f"**Season Palette:** {season}")

            # Display color swatch
            st.markdown("**Your Skin Tone:**")
            st.markdown(f"""<div style="height: 50px; width: 100%; background-color: {hex_color}; 
                        border-radius: 5px; margin-bottom: 10px;"></div>""", unsafe_allow_html=True)

        with col2:
            st.subheader(f"{season} Color Palette")
            display_color_palette(season)

        # --- Body Shape Detection ---
        with st.spinner("Analyzing body shape..."):
            det_model = load_detectron2_model()
            _, keypoints = detect_keypoints(det_model, original)
            measures = extract_measurements(keypoints)
            shape = classify_body_shape(measures)
            
            # Display body shape results
            st.subheader("Body Shape Analysis")
            st.markdown(f"**Body Shape:** {shape.title()}")
            
            # Get recommendations
            fashion_tip = recommend_fashion(season, shape)
            
            # Display recommendations in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Clothing", "Jewelry", "Casual", "Formal"])
            
            with tab1:
                st.subheader("Clothing Recommendations")
                st.write(fashion_tip["clothing"])
            
            with tab2:
                st.subheader("Jewelry Recommendations")
                st.write(fashion_tip["jewelry"])
            
            with tab3:
                st.subheader("Casual Outfits")
                st.write(fashion_tip["casual"])
            
            with tab4:
                st.subheader("Formal Outfits")
                st.write(fashion_tip["formal"])
        
        # --- Suggested Outfit ---
        st.subheader("Suggested Outfit Inspiration")
        with st.spinner("Finding outfit inspiration..."):
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.images(f"{season} {shape} outfit", max_results=3))
                    if results:
                        cols = st.columns(min(3, len(results)))
                        for i, result in enumerate(results[:3]):
                            with cols[i]:
                                try:
                                    img_data = requests.get(result['image'], timeout=5).content
                                    outfit_img = Image.open(BytesIO(img_data))
                                    st.image(outfit_img, caption=f"Outfit {i+1}", use_container_width =True)
                                except:
                                    st.warning("Couldn't load this outfit image")
                    else:
                        st.warning("No outfit images found for this combination")
            except Exception as e:
                st.error(f"Error fetching outfit images: {e}")

if __name__ == "__main__":
    main()