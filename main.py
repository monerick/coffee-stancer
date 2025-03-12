import telebot
import serial

# Configuración del bot de Telegram
TOKEN = "7660314148:AAE6K-ZtorvzszmvaSM7yXc1R3lgmbkkYNk"
bot = telebot.TeleBot(TOKEN)

target_temperature = None  # Temperatura objetivo
bluetooth_connected = False  # Estado de conexión Bluetooth

# Configuración del puerto Bluetooth (ajusta el puerto según tu dispositivo)
try:
    ser = serial.Serial("COM3", 9600, timeout=1)  # Cambia "COM3" por el puerto correcto
except Exception as e:
    print("No se pudo conectar al Bluetooth: ", e)
    ser = None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 ¡Bienvenido! Usa /help para ver los comandos disponibles.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """
/start - Inicia el bot
/set_temp <valor> - Configura la temperatura deseada (°C)
/get_temp - Muestra la temperatura actual
/status - Indica si la temperatura deseada ha sido alcanzada
/connect_bluetooth - Conecta el dispositivo Bluetooth
/disconnect_bluetooth - Desconecta el dispositivo Bluetooth
    """)

@bot.message_handler(commands=['set_temp'])
def set_temperature(message):
    global target_temperature
    try:
        target_temperature = float(message.text.split()[1])
        bot.reply_to(message, f"✅ Temperatura establecida en {target_temperature}°C")
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Usa el comando así: /set_temp <valor>")

@bot.message_handler(commands=['get_temp'])
def get_temperature(message):
    if ser and ser.is_open:
        ser.write(b"TEMP\n")  # Enviar comando al sensor
        temp = ser.readline().decode().strip()
        bot.reply_to(message, f"🌡️ Temperatura actual: {temp}°C")
    else:
        bot.reply_to(message, "⚠️ No se pudo leer la temperatura (Bluetooth no conectado).")

@bot.message_handler(commands=['status'])
def check_status(message):
    if target_temperature is None:
        bot.reply_to(message, "⚠️ No has establecido una temperatura objetivo.")
        return
    
    if ser and ser.is_open:
        ser.write(b"TEMP\n")
        temp = ser.readline().decode().strip()
        try:
            temp = float(temp)
            if temp >= target_temperature:
                bot.reply_to(message, "✅ ¡Se ha alcanzado la temperatura deseada!")
            else:
                bot.reply_to(message, f"🌡️ Aún no se alcanza la temperatura. Actual: {temp}°C")
        except ValueError:
            bot.reply_to(message, "⚠️ Error al leer la temperatura.")
    else:
        bot.reply_to(message, "⚠️ No se pudo verificar el estado (Bluetooth no conectado).")

@bot.message_handler(commands=['connect_bluetooth'])
def connect_bluetooth(message):
    global ser, bluetooth_connected
    try:
        if ser and ser.is_open:
            bot.reply_to(message, "✅ Bluetooth ya está conectado.")
        else:
            ser = serial.Serial("COM3", 9600, timeout=1)  # Reintentar conexión
            bluetooth_connected = True
            bot.reply_to(message, "✅ Bluetooth conectado exitosamente.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error al conectar Bluetooth: {e}")

@bot.message_handler(commands=['disconnect_bluetooth'])
def disconnect_bluetooth(message):
    global ser, bluetooth_connected
    if ser:
        ser.close()
        bluetooth_connected = False
        bot.reply_to(message, "✅ Bluetooth desconectado.")
    else:
        bot.reply_to(message, "⚠️ No hay conexión Bluetooth activa.")

@bot.message_handler(func=lambda message: True)
def default_response(message):
    bot.reply_to(message, "⚠️ Comando no reconocido. Usa /help para ver los comandos disponibles.")

if __name__ == "__main__":
    print("🤖 Bot en funcionamiento...")
    bot.polling(none_stop=True)
