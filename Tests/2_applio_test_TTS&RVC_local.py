# Import necessary libraries
import os
import sys

# ----------------------------------------------------------------------------------
# STEP 1: ENVIRONMENT SETUP ⚙️
# ----------------------------------------------------------------------------------

# Note, this script assumes it is located in the same directory as the 'Applio' folder, you will need a folder 
# named "Archivos" with subfolders "Modelos" and "Resultados"  (in one you have the RVC model and index file,
# and in the other you want to save the audio results).


print("🐍 Setting up the Python environment...")
script_dir = os.path.dirname(os.path.abspath(__file__))
applio_dir = os.path.join(script_dir, "Applio")

if not os.path.isdir(applio_dir):
    print(f"❌ Error: 'Applio' directory not found.")
    print("   Please make sure this script is located in the same directory that contains the 'Applio' folder.")
    sys.exit(1)

print(f"✅ 'Applio' folder located. Changing working directory to: {applio_dir}")
os.chdir(applio_dir)
sys.path.append(applio_dir)

# ----------------------------------------------------------------------------------
# STEP 2: IMPORTING CORE FUNCTIONALITY 🔑
# ----------------------------------------------------------------------------------
try:
    from core import run_tts_script  # Maybe it will say that the module is not found, but it works anyway
    print("✅ Applio core function imported successfully.")
except ImportError as e:
    print(f"❌ Import error: Unable to load Applio core functions: {e}")
    sys.exit(1)

# ----------------------------------------------------------------------------------
# STEP 3: MAIN CONVERSION FUNCTION 🛠️
# ----------------------------------------------------------------------------------

def ejecutar_conversion_completa(texto, voz_tts_base, modelo_rvc, index_rvc, ruta_tts_intermedio, ruta_salida_final):
    """
    Executes the entire TTS + RVC pipeline:
    1. Generates speech audio from input text (TTS).
    2. Applies the selected voice model (RVC) to the generated audio.
    """
    print("\n--- 🚀 STARTING FULL PIPELINE (TTS + RVC) ---")

    try:
        # Define the argument list in the expected positional order
        args_proceso = [
            None,  # input_tts_path (not used; using direct text input)
            texto,  # tts_text
            voz_tts_base,  # tts_voice
            0,  # tts_rate
            0,  # pitch
            0.8,  # index_rate
            1.0,  # rms_mix_rate
            0.5,  # protect
            "rmvpe",  # f0_method
            ruta_tts_intermedio,  # output_tts_path (intermediate TTS audio)
            ruta_salida_final,    # output_rvc_path (final processed audio)
            modelo_rvc,  # model_file
            index_rvc,  # index_file
            False,  # split_audio
            False,  # autotune
            1.0,  # autotune_strength
            False,  # proposed_pitch
            155.0,  # proposed_pitch_threshold
            False,  # clean_audio
            0.5,  # clean_strength
            "WAV",  # export_format
            "contentvec",  # embedder_model
            None,  # embedder_model_custom
            0,  # sid
        ]
        
        resultado = run_tts_script(*args_proceso)
        
        if "successfully" in resultado[0]:
            print(f"✅ Success: {resultado[0]}")
            print(f"🗣️  Base audio (TTS) saved at: {ruta_tts_intermedio}")
            print(f"🤖 Final audio (RVC) saved at: {ruta_salida_final}")
            return True
        else:
            print(f"⚠️  Warning: {resultado[0]}")
            return False
    except Exception as e:
        print(f"❌ Critical error during execution: {e}")
        return False

# ========================================================================================
# 🚀 CONFIGURATION SECTION: MODIFY THESE VALUES TO CUSTOMIZE EXECUTION 🚀
# ========================================================================================

if __name__ == "__main__":
    # 📝 1. Input text to synthesize
    texto_a_convertir = "Agus necesita un iphone nuevo.."

    # 🗣️ 2. TTS voice preset
    voz_tts_generica = "es-AR-ElenaNeural"  # or "es-ES-ElviraNeural", "en-US-JennyNeural"

    # 🤖 3. Paths to the RVC model and index file
    ruta_modelo_rel = "../Archivos/Modelos/a.pth"
    ruta_index_rel = "../Archivos/Modelos/a.index"

    # 📁 4. Output filenames for the audio results
    nombre_audio_base_tts = "audio_para_comparar_(base_tts).wav"
    nombre_audio_final_rvc = "audio_para_comparar_(final_rvc).wav"
    
# ========================================================================================
# 🛑 DO NOT MODIFY ANYTHING BELOW THIS LINE 🛑
# ========================================================================================
    
    # --- Build Absolute Paths ---
    print("\n--- 🗺️  BUILDING FILE PATHS ---")

    # Define the output folder for generated audio
    carpeta_resultados = os.path.abspath(os.path.join("..", "Archivos", "Resultados"))
    
    # Create output folder if it doesn't exist
    os.makedirs(carpeta_resultados, exist_ok=True)

    # Construct absolute paths for intermediate and final audio files
    ruta_audio_intermedio_abs = os.path.join(carpeta_resultados, nombre_audio_base_tts)
    ruta_audio_final_abs = os.path.join(carpeta_resultados, nombre_audio_final_rvc)

    # Resolve model and index paths to absolute
    ruta_modelo_abs = os.path.abspath(ruta_modelo_rel)
    ruta_index_abs = os.path.abspath(ruta_index_rel)
    
    print(f"Model path: {ruta_modelo_abs}")
    print(f"TTS audio will be saved at: {ruta_audio_intermedio_abs}")
    print(f"Final RVC audio will be saved at: {ruta_audio_final_abs}")

    # --- Execute the Full Pipeline ---
    ejecutar_conversion_completa(
        texto=texto_a_convertir,
        voz_tts_base=voz_tts_generica,
        modelo_rvc=ruta_modelo_abs,
        index_rvc=ruta_index_abs,
        ruta_tts_intermedio=ruta_audio_intermedio_abs,
        ruta_salida_final=ruta_audio_final_abs
    )
    
    print("\n\n🎉 Process completed successfully. 🎉")
