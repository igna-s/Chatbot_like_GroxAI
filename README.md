# 🤖 Real-Time Conversational Chatbot with Gemini and RVC 🎙️

An advanced conversational AI prototype that uses Google Gemini 2.5 Flash for intelligent interaction and Applio for real-time voice cloning (TTS + RVC).

---

### ✨ Key Features

- **Real-Time Interaction:** Fluid conversations powered by Gemini 2.5 Flash.
- **Advanced Voice Cloning:** Utilizes Applio to generate responses in a custom voice, combining Text-to-Speech (TTS) with Retrieval-based Voice Conversion (RVC).
- **Modular Architecture:** The code is organized to allow for independent testing of components (installation, voice tests, final demo).

---

### 📂 Project Structure

Here’s how the main repository files are organized:

- `Final_Test.ipynb`: The main notebook to run a full demonstration of the system, integrating voice input, Gemini, and cloned voice output.
- `Links.txt`: A curated list of useful links and resources for the technologies used in the project.

**`Extra/` Folder:**

- `preprosessing_audio_RVC_training.ipynb`: A crucial notebook containing the process for preparing your audio datasets. **This is the first step to training a custom voice model in Applio.**

**`Tests/` Folder:**

*(These are functional tests of different alternatives but are not necessary to run the main demo in `Final_Test.ipynb`)*

- `1_instalation_applio_main.py`: A script to automate the installation of Applio and its dependencies from the main branch (Not recommended) (Part 1/2).
- `2_applio_test_TTS&RVC_local.py`: A script for a quick, local test of Applio's TTS and RVC capabilities to ensure the voice model is working correctly (Part 2/2).
- `AI_with_scrrenshots.ipynb`: A demonstration notebook that can include screen and camera captures, as well as audio recording, for a more comprehensive model.
- `test_gemini_live_v2_EN.py` / `test_gemini_live_v2_ES.py`: Scripts to test the connection and real-time response with the Gemini Live API in English and Spanish.

---

### ⚙️ How It Works

1.  **RVC Model:** You can train your model from scratch or find a pre-trained RVC model in `Links.txt` (Easier).
2.  **Text Input:** The user types the text.
3.  **AI Processing:** The transcribed text is sent to **Gemini 1.5 Flash**.
4.  **Intelligent Response:** Gemini processes the input and generates a coherent text response.
5.  **Voice Generation and Cloning:**
    - The text from Gemini is sent to the **Applio TTS engine** to create a base audio file.
    - Immediately, the **RVC model** transforms that base audio, applying the characteristics of the cloned voice.
6.  **Audio Output:** The system plays the final audio response, which sounds as if the AI is speaking with the trained voice.

---

### 🚀 Getting Started

Simply run `Final_Test.ipynb` to perform TTS + RVC and interact with a simple AI.

---

### 🎯 To-Do

- Acquire a better graphics card to run `AI_with_scrrenshots.ipynb` locally.
- Increase processing speed.
- Integrate a VTuber model.

---

### 🤝 Contributing

Contributions are welcome! If you have ideas to improve the dialogue flow, latency, or model integration, feel free to fork the repository and submit a Pull Request.

---

### 📜 License

This project is distributed under the MIT License. Applio also uses the MIT license. The Google Gemini API is governed by the Google AI Gemini API Terms of Service.
