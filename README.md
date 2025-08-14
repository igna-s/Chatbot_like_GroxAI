# Interactive 3D AI Assistant

Welcome to the **Interactive 3D AI Assistant**, a project that brings a conversational AI to life in a 3D environment. This application combines a powerful language model with a fully animated avatar, creating an engaging and interactive user experience. Speak to the avatar through your microphone, and it will listen, think, and respond to you using a custom-cloned voice, complete with real-time animations and 'lip-sync'.

The entire project is designed to be **concurrent**, highly customizable, **100% free**, and runs easily in a Google Colab notebook if you don´t have a graphic card , making it accessible from any web browser without local setup.

---
## 🖼️ Avatar Preview

<p align="center">
  <img src="assets/image.png" alt="Avatar Preview" width="400"/>
</p>


# Video Preview

<p align="center">
  <a href="https://igna-s.github.io/Realtime_Avatar_AI_Companion/video_player.html" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/Ver%20Video-▶-2d3748?style=for-the-badge&logo=youtube" alt="Ver Video"/>
  </a>
</p>
---

## ✨ Core Features

- **🎤 Voice Interaction** Engage in seamless conversations. The assistant listens to your voice, transcribes it to text, and generates a spoken response.
- **🧠 Conversational AI** Powered by the Google Gemini API, the assistant can hold natural, context-aware conversations and remember previous parts of your dialogue for a more personalized experience.
- **🗣️ Custom Voice Cloning** Using OpenVoice, the assistant can clone the timbre of any voice from a reference audio file (`reference.mp3`), giving your character a unique vocal identity.
- **💃 Interactive 3D Avatar** The frontend, built with Three.js, renders a custom `.vrm` avatar. The character features idle and talking animations, automatic blinking, and audio-driven lip-sync.
- **🎨 Fully Customizable** Easily swap out the avatar (`.vrm`), animations (`.fbx`), 3D background (`.hdr`), reference voice (`.mp3`), and the AI’s personality to create your own unique assistant.
- **🌐 Web-Accessible** Runs in a Google Colab notebook and uses Ngrok to generate a public URL, allowing you to access the assistant from your browser on any device.

## 🚀 Getting Started

1. **Gather Your Assets** Before you begin, you will need all the necessary 3D and audio files. You can use your own or download them from the recommended sources below.
- **3D Avatar** (`waifu.vrm`)
- **Animations** (`idle.fbx`, `anim_1.fbx`, `anim_2.fbx`, `anim_3.fbx`)
- **3D Background** (`background.hdr`)
- **Reference Voice** (`reference.mp3`)
- **Web Client** (`cliente_final.html`)

2. **Prepare Your Files** Create a single `.zip` file containing all the assets from the previous step. The Colab notebook will prompt you to upload this file.

3. **Set Up the Environment** - Open the `main.ipynb` file in Google Colab.
   - Run the **General Environment Setup** cells to install all required dependencies and libraries.

4. **Configure Your Keys and Personality** In the **API Key, AI Personality & Language Configuration** cell, enter your keys:
   ```python
   GOOGLE_API_KEY = "<your_google_api_key>"
   NGROK_AUTHTOKEN = "<your_ngrok_authtoken>"
   ```
   Also customize the AI's personality by editing `SYSTEM_PROMPT_EN` or `SYSTEM_PROMPT_ES`.
   Run the cell, and it will prompt you to upload the `.zip` file you created in Step 2.

5. **Launch the Server** Run the final cell: **Run Web Server & Application**.
   This will start the web server and generate a public Ngrok URL in the output. Open that URL in your browser to start interacting with your assistant!

## 🔗 Asset Sources

* **VRM Models**: [VRoid Hub](https://hub.vroid.com/)
* **3D Backgrounds (.hdr)**: [Poly Haven](https://polyhaven.com/)
* **Animations (.fbx)**: [Mixamo](https://www.mixamo.com/)
* **Online Viewer for Testing**: [VRM Viewer](https://vrm-viewer.glitch.me/)

## 📜 License

This project has no usage restrictions (Uses MIT or Apache libraries), except for the terms and conditions of the respective API providers. From my side, feel free to use and evolve it :D !

