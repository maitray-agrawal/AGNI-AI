import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np

# Load cropped reference
ref_im = Image.open('d:/AGNI-AI/docs/brand_reference/agni_symbol_only.png')

# Let's inspect the exact lines and shapes of Agni:
# 1. Top Diamond: centered at (50, 7)
# 2. Hollow Diamond: centered at (50, 15)
# 3. Spire: (49.2, 19) to (50.8, 19) down to (50.4, 57) and (49.6, 57)
# 4. Bindu: center at (50, 67), top at (50, 58), bottom at (50, 78), left at (43, 67), right at (57, 67)
# 5. Inner Sails:
#    Left sail: top (47.6, 29), outer vertex (33.5, 47), bottom (47.6, 61), crease to (47.6, 45)
#    Right sail: top (52.4, 29), outer vertex (66.5, 47), bottom (52.4, 61), crease to (52.4, 45)
# 6. Lower Swept Wings:
#    Left wing: inner top (45, 65), outer tip (13.5, 81), inner bottom (47.5, 73), midline to (44, 70)
#    Right wing: inner top (55, 65), outer tip (86.5, 81), inner bottom (52.5, 73), midline to (56, 70)
# 7. Coordinate lines and satellite diamonds:
#    Left satellite diamond: center at (11.5, 68)
#    Right satellite diamond: center at (88.5, 68)
#    Rays from hollow diamond (50, 15):
#      to (11.5, 68)
#      to (88.5, 68)
#      to lower wing (24, 76)
#      to lower wing (76, 76)

print("Comparison script ready")
