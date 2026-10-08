# Copy-paste prompts

## For the user, in any image generator (ChatGPT, Gemini, Midjourney…)

When the user wants to make an image themselves, give them this. They keep the rules and fill in the
last five lines.

```
Create an image for the task below. Rules:
1. Text: write ONLY the text in quotes, exactly as given, letter by letter. No extra words, no made-up text, no watermarks. Arabic must read right to left with correctly connected letters and every dot and hamza in place. Make text large, clean and easy to read.
2. Attached photos: keep people, faces, logos and products exactly as they are. Don't redraw, beautify or change them; only crop, place and lightly color-match them.
3. Layout: one clear focal point and a clear hierarchy, and keep anything important away from the edges.
4. Style: consistent colors, light and style across the whole image. No random extra objects, icons or logos.
5. Before finishing, check every word against my text and check that faces and logos are unchanged. Fix anything that's wrong.

TASK: <what to make, for whom, and why>
SIZE: <e.g. 1080×1920 / 1:1>
TEXT (exact): "<line 1>" / "<line 2>"
STYLE: <mood, colors, reference>
ATTACHED: <which photos/logos and how to use them>
```

Tips to tell them: less text means fewer mistakes. If the text still comes out wrong, ask for the
same image with no text and add the text in Canva. When a face must stay exact, place the real
photo in Canva afterwards, because image generators redraw the whole picture.

## Brush word in ChatGPT (when Codex isn't available)

```
Hand-painted Arabic brush lettering of «<WORD>» only, very bold dark forest green #1E3A2B with dry-brush texture and light scratches inside the strokes, on a perfectly flat pure white background, nothing else. Spell exactly: «<WORD>». <letter-by-letter spec: dots, ة vs ت, hamza, joins>
```

Ask the user to upload the result, then verify it letter by letter like any sheet.

## Texture and scene prompts that worked (for gen.sh)

- **Paper plate:** "Vertical 9:16 background plate … warm off-white cream textured paper with subtle
  fibers and faint aged stains, very faint thin beige topographic contour lines, a small elegant
  muted-gold compass rose … a thin muted-gold dashed route line … The central area must stay plain
  paper. Flat front-on scan, even soft light, no vignette, no border, absolutely no letters or words."
  Attach a style reference poster as the second argument.
- **Gold foil:** "Seamless flat top-down texture of a muted antique-gold metallic scratch-off lottery
  foil, satin brushed sheen, subtle paper grain and fine micro-speckles … #B8975A to #D8BE84,
  completely uniform, no text, no scratches, no borders, square 1024x1024."
- **Scene:** "Photorealistic landscape photograph of the Austrian Alps at golden hour, landscape
  1536x1024 … a grassy rocky ridge across the lower third with NO people … No text, no logos, no
  watermark, no borders."
- **Silhouette to key out:** "A single solid flat pure black silhouette of <who/pose>, full body …
  Perfectly flat pure white (#FFFFFF) background. No ground, no shadow, no gradient, no inner
  details, no text. Clean crisp edges."

Codex sometimes tries to fabricate a PNG with code: `gen.sh` already tells it to use the
image_generation tool only.
