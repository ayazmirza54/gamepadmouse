# GamepadMouse promo video

`gamepadmouse-promo.mp4` is a 30-second, 1920×1080, 30fps motion graphic (no audio). `gamepadmouse-promo-9x16.mp4` is the same video in a 1080×1920 vertical layout for Reels, Shorts and TikTok. It ends with a fade to black so stock footage can follow it.

| Time | Scene |
| --- | --- |
| 0–3s | Hook: "What if your gamepad could run your coding agents?" |
| 3–7s | Logo reveal and tagline |
| 7–12s | 01 Navigate: the left stick moves the cursor and A clicks the agent's input |
| 12–16.5s | 02 Speak: RB starts Hex dictation and the prompt is typed in |
| 16.5–21s | 03 Delegate: the prompt is sent and the agent writes code and tests |
| 21–26s | Pipeline: Controller → GamepadMouse → Hex → Coding agent → You |
| 26–30s | "Press. Speak. Delegate. Build." Download call to action, then fade out |

## Add your stock footage at the end

```bash
./add-footage.sh path/to/footage.mp4            # -> gamepadmouse-promo-full.mp4
```

Any resolution or frame rate works: the footage is scaled and padded to the promo's size at 30fps, and its audio is kept.

For the vertical version:

```bash
./add-footage.sh path/to/footage.mp4 gamepadmouse-promo-9x16-full.mp4 gamepadmouse-promo-9x16.mp4
```

## Edit and re-render

The animation is plain HTML in `promo.html`, drawn by `window.seek(t)`. To preview it in a browser, open `promo.html?play`. Re-render with:

```bash
node render.js                                        # 16:9, needs Playwright and ffmpeg
PORTRAIT=1 node render.js gamepadmouse-promo-9x16.mp4  # 9:16
```
