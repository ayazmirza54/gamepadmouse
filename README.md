<div align="center">

# 🎮 GamepadMouse

### Your controller. Your cursor. Your coding agents.

**Turn a gaming controller into a hands-on way to navigate Windows and delegate coding tasks with your voice.**

[![Latest release](https://img.shields.io/github/v/release/ayazmirza54/gamepadmouse?label=Latest%20release&style=for-the-badge)](https://github.com/ayazmirza54/gamepadmouse/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows)](https://github.com/ayazmirza54/gamepadmouse/releases/latest)
[![Download](https://img.shields.io/badge/Download-GamepadMouse-2ea44f?style=for-the-badge&logo=github)](https://github.com/ayazmirza54/gamepadmouse/releases/latest)

**[⬇️ Download GamepadMouse](https://github.com/ayazmirza54/gamepadmouse/releases/latest)** · **[🐛 Report an issue](https://github.com/ayazmirza54/gamepadmouse/issues/new)**

</div>

---

## ✨ Why I built this

I love building software, but I also wanted to keep the gamer in me alive.

I already owned an **EvoFox controller** and wondered: *what if I could use it to work with my AI coding agents?*

That experiment became **GamepadMouse** — a Windows application for controlling the mouse with a gamepad. Pair it with [Hex by Anomaly](https://anoma.ly/hex/) for voice dictation, and you can navigate your desktop with a controller, speak your coding instructions, and let your preferred AI coding agent handle the implementation.

> **The developer in me built the workflow. The gamer in me made sure it was fun.**

## 🚀 Download & install

1. Open **[the latest GamepadMouse release](https://github.com/ayazmirza54/gamepadmouse/releases/latest)**.
2. Under **Assets**, download the Windows setup executable (currently `GamepadMouse.Setup.2.0.2.exe`).
3. Run the installer and follow its prompts.
4. Connect your controller over USB or Bluetooth, then open GamepadMouse.
5. Test mouse control before adding voice dictation.

**Platform:** Windows. The workflow was built around an **EvoFox** gamepad; compatibility with other controllers may vary.

> **Security tip:** Download installers from this repository's **Releases** page, and check the publisher/signature and any Windows security prompts before running them.

## 🎙️ Turn it into a voice-powered coding workflow

GamepadMouse handles the controller/mouse side. **Hex** handles speech-to-text. **Your AI coding agent** receives the prompt. These are separate tools working together.

### 1. Install Hex

Download the Windows version from **[anoma.ly/hex](https://anoma.ly/hex/)** and complete its setup, including any microphone permissions or initial speech-model download.

### 2. Configure your controller

Use GamepadMouse to navigate your desktop. If your controller-mapping setup supports keyboard shortcuts, bind a convenient button to **the dictation shortcut configured in Hex**. The exact button and shortcut depend on your settings; there is no universal default mapping documented here.

### 3. Delegate a coding task

1. Open your favorite AI coding agent or coding environment.
2. Focus the agent's prompt/input field.
3. Trigger Hex dictation using your configured button or keyboard shortcut.
4. Speak your instruction — for example: *“Add input validation and tests to this endpoint.”*
5. Finish dictation, review the transcribed prompt, and submit it to your agent.

### 🧩 How the workflow fits together

```text
  🎮 Gaming controller
          |
          v
  🖱️ GamepadMouse --------> Navigate Windows / focus input
          |
          v
  🎙️ Hex voice dictation --> Convert speech into text
          |
          v
  🤖 Your coding agent ----> Plan / edit / implement code
          |
          v
  ✅ You review the result
```

This is a **controller-driven workflow**, not an AI model or coding agent built into GamepadMouse.

## 💡 What you can do with it

- 🕹️ **Navigate using a controller** instead of always reaching for a mouse.
- 🎙️ **Dictate coding prompts** when paired with Hex.
- 🤖 **Work with the coding agent of your choice** by focusing its text input.
- 🧪 **Experiment with controller-driven productivity** — whether it's the most efficient way to work or simply the most fun.

## 🛠️ Troubleshooting

| Problem | Things to check |
| --- | --- |
| Controller isn't detected | Reconnect it, try USB, and check Windows' Game Controllers panel (`joy.cpl`). |
| Mouse doesn't respond | Make sure GamepadMouse is running and the controller is connected. |
| Hex doesn't transcribe | Check microphone access, initial setup, and Hex's selected dictation shortcut. |
| Dictation appears in the wrong app | Focus your coding agent's prompt field before speaking. |
| A button doesn't trigger dictation | Check the mapping in your controller setup and the shortcut configured in Hex. |
| Windows warns about the installer | Verify it came from this repository's Releases page and assess the security prompt; don't bypass warnings blindly. |

For bugs or feature ideas, **[open an issue](https://github.com/ayazmirza54/gamepadmouse/issues)** and include your Windows version, controller model, GamepadMouse version, and steps to reproduce.

## 📦 Releases & project status

Prebuilt Windows installers are available under **[GitHub Releases](https://github.com/ayazmirza54/gamepadmouse/releases)**. The initial published installer is **v2.0.2**. You don't need to clone the repository to install the app.

**Source / licensing:** This repository currently distributes the application as a release binary. Source code and a project license have not been published here yet; availability of a public download does not by itself grant reuse or redistribution rights.

## 🙌 Credits

- **[Hex by Anomaly](https://anoma.ly/hex/)** — local voice dictation for Windows, macOS, and Linux.
- **EvoFox** — the controller that inspired this experiment.
- **You** — for finding creative ways to make development more fun.

GamepadMouse is an independent project and is **not affiliated with or endorsed by Hex or EvoFox**.

---

<div align="center">

**Built by [Ayaz Mirza](https://github.com/ayazmirza54)**

*Press. Speak. Delegate. Build.* 🎮💻

If you find this project interesting, consider giving the repository a ⭐!

</div>
