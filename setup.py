import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("="*60)
    print(" 🔮 B I E N V E N I D O   A L   O R Á C U L O   Q U A N T 🔮")
    print("="*60)
    print("\nIniciando asistente de configuración...\n")
    time.sleep(1)

    print("1. Configuración de Google Gemini AI")
    print("-" * 40)
    print("Para funcionar, el Oráculo necesita una API Key de Google AI Studio.")
    print("Puedes conseguirla gratis en: https://aistudio.google.com/app/apikey\n")
    
    api_key = input("👉 Pega tu GEMINI API KEY (o presiona Enter para dejar en blanco): ").strip()

    print("\n2. Selección de Modelo Base")
    print("-" * 40)
    print("¿Qué modelo quieres usar por defecto en tu servidor?")
    print(" [1] gemini-3.1-pro-preview (Recomendado - Máxima Inteligencia)")
    print(" [2] gemini-2.5-flash (Alta Velocidad)")
    
    model_choice = input("\n👉 Elige una opción [1/2] (por defecto 1): ").strip()
    
    model_name = "gemini-3.1-pro-preview"
    if model_choice == "2":
        model_name = "gemini-2.5-flash"

    # Generamos el archivo .env
    print("\n⚙️ Generando archivo de configuración (.env)...")
    with open(".env", "w") as env_file:
        env_file.write(f"GEMINI_API_KEY={api_key}\n")
        env_file.write(f"GEMINI_MODEL={model_name}\n")
    
    time.sleep(1)
    print("✅ Archivo .env creado con éxito.")

    print("\n" + "="*60)
    print(" 🎉 ¡I N S T A L A C I Ó N   C O M P L E T A D A ! 🎉")
    print("="*60)
    print("\nYa puedes levantar tu servidor Oráculo. Ejecuta el siguiente comando:\n")
    print("   🚀 docker-compose up --build -d\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada por el usuario.")