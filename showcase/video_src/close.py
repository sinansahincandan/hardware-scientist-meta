import sys
from PIL import Image, ImageDraw, ImageFont
V = sys.argv[1]
F = "/System/Library/Fonts/Supplemental/Arial.ttf"; FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"; FI = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
im = Image.new("RGB", (1920, 1080), (22, 32, 44)); d = ImageDraw.Draw(im)
d.text((96, 80), "HARDWARE SCIENTIST", font=ImageFont.truetype(FB, 26), fill=(120, 170, 240))
d.text((96, 124), "The engineer gives the what.", font=ImageFont.truetype(FB, 58), fill="white")
d.text((96, 204), "Hardware Scientist works out the how, and shows its proof.", font=ImageFont.truetype(FB, 58), fill="white")
d.text((96, 310), "Muse Spark 1.3 for the team, Evaluator and Manager · Muse Image 1.0 for pictures · SAM 3.1 for part maps · nothing else at run time", font=ImageFont.truetype(F, 26), fill=(201, 210, 220))
d.text((96, 400), "REFERENCES", font=ImageFont.truetype(FB, 24), fill=(120, 170, 240))
refs = [
 "Yuksekgonul et al. Optimizing generative AI by backpropagating language model feedback (TextGrad). Nature 639, 609–616 (2025).",
 "Zhou et al. Symbolic Learning Enables Self-Evolving Agents. arXiv:2406.18532 (2024).",
 "Cheng, Nie, Swaminathan. Trace is the Next AutoDiff. NeurIPS 2024, arXiv:2406.16218.",
 "Zhang et al. Agentic Context Engineering: Evolving Contexts for Self-Improving LMs. arXiv:2510.04618 (2025).",
 "Shinn et al. Reflexion: Language Agents with Verbal Reinforcement Learning. NeurIPS 2023.",
 "Mañas et al. (FAIR at Meta). Improving Text-to-Image Consistency via Automatic Prompt Optimization (OPT2I). TMLR 2024.",
 "Yang et al. Idea2Img: Iterative Self-Refinement with GPT-4V for Automatic Image Design. ECCV 2024.",
 "Du et al. Improving Factuality and Reasoning through Multiagent Debate. ICML 2024.",
 "Carion et al. (Meta). SAM 3: Segment Anything with Concepts. arXiv:2511.16719 (2025).",
 "Yang et al. Set-of-Mark Prompting Unleashes Visual Grounding in GPT-4V. arXiv:2310.11441 (2023).",
]
y = 446
for r in refs:
    d.text((96, y), r, font=ImageFont.truetype(F, 25), fill=(225, 231, 238)); y += 44
d.text((96, 1000), "Code, runs, whiteboards and judge reports: showcase/ in the project repository.", font=ImageFont.truetype(FI, 24), fill=(150, 165, 180))
im.save(f"{V}/close.png")
