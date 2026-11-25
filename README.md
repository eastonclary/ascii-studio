# ASCII Studio

A desktop creative-coding application that transforms images and videos into full-color ASCII artwork. Built with Python, OpenCV, NumPy, Pillow, Tkinter, and FFmpeg.

## Features

- Import images (PNG, JPEG, WebP, BMP) and videos (MP4, MOV, AVI, MKV, WebM)
- Reconstruct frames from monospaced text glyphs using pixel luminance
- Preserve original RGB colors or select monochrome or custom palettes
- Adjust character density, brightness, contrast, saturation, and character mapping
- Live preview with optional glitch, flicker, and trail effects
- Export PNG stills, animated GIFs, and silent MP4 files
- Vertical 1080 × 1920, square 1080 × 1080, and landscape 1920 × 1080 layouts
- Looping playback and ping-pong video exports

## Get started (Windows)

1. Install Python 3.11 or 3.12 from [python.org](https://www.python.org/downloads/). Enable **Add Python to PATH** during installation.
2. Download the repository as a ZIP using **Code → Download ZIP** and extract the files.
3. Open the extracted folder in File Explorer, click the address bar, type `cmd`, and press Enter.
4. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Run the app:

   ```powershell
   python app.py
   ```

6. Click **Open image or video** to import media, adjust the controls, and export your artwork.

For video or GIF exports, install [FFmpeg](https://ffmpeg.org/download.html) and make sure `ffmpeg -version` works in a new terminal. On Windows, one option is `winget install Gyan.FFmpeg`.

## macOS / Linux

Install Python 3.11 or 3.12, Tkinter, and FFmpeg. In the project directory:

```sh
python3 -m pip install -r requirements.txt
python3 app.py
```

On macOS with Homebrew, install FFmpeg with `brew install ffmpeg`. On Ubuntu, use `sudo apt install ffmpeg python3-tk`.

## Settings

- **Columns:** Number of ASCII character columns. Higher values give finer detail and take longer to render.
- **Characters:** A string of glyphs ordered from dark to light, such as ` .,:;irsXA253hMHGS#9B&@`.
- **Brightness / Contrast / Saturation:** Change luminance and color appearance.
- **Palette:** Original RGB, Monochrome, or a custom color.
- **Glitch / Flicker / Trail:** Procedural digital effects.
- **Loop:** Repeats the preview. For video exports, creates a forward-and-reverse animation.

## Limitations

This is an early desktop prototype. It does not automatically remove image backgrounds or add audio to MP4 files. GIF colors are limited. For long or high-resolution videos, frame rendering and temporary PNG storage can be slow and use substantial disk space. Loop effects may not be perfectly seamless, especially trails. The preview runs at reduced resolution. FFmpeg is required for animated exports, and video playback depends on machine performance.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Tkinter user interface, file loading, preview, and export |
| `engine.py` | Luminance-to-glyph rendering and effects |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Excludes local Python artifacts |

## Privacy

All media processing runs locally on your computer. Your photos and videos are not uploaded to a server by the application.
