from typing import List
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import openai
import os
from PIL import Image, ImageTk
import logging
import re
import stanza
import inflect

# Otras configuraciones globales y variables
conversation = []
conversation_lemas = []
logging.basicConfig(level=logging.INFO)
nlp = stanza.Pipeline('es', model_dir='stanza_resources')
p = inflect.engine()
os.environ['TQDM_DISABLE'] = '1'
openai.api_key = 'Copia tu clave Api Aquí'

iconos_seleccionados = []

# Declarar image_window en el ámbito global
image_window = None

# Directorio donde se encuentran las imágenes de los pictogramas
DIRECTORIO_PICTOGRAMAS = "Images"

# Diccionario de verbos irregulares y sus formas conjugadas
verbos_irregulares = {
    "estoy": "estar",
    "estás": "estar",
    "está": "estar",
    "estamos": "estar",
    "estáis": "estar",
    "están": "estar",
    "soy": "ser",
    "eres": "ser",
    "es": "ser",
    "somos": "ser",
    "sois": "ser",
    "son": "ser",
    "salta": "saltar",
    "salto": "saltar",
    "come": "comer",
    "vale": "vale",
    "sabes": "saber",
    "dolor": "doler",
    "regalado": "regalar",
    "hiciste": "hacer",
    "escondido": "esconder",
    "comiste": "comer",
    "mejores": "mejorar",
    "huele": "oler",
    "holer": "oler",
}
# Diccionario de palabras numéricas y sus representaciones en palabras
word_to_number = {
    "cero": 0, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
    "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12,
    "trece": 13, "catorce": 14, "quince": 15, "dieciséis": 16, "diecisiete": 17,
    "dieciocho": 18, "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidós": 22,
    "veintitrés": 23, "veinticuatro": 24, "veinticinco": 25, "veintiséis": 26, "veintisiete": 27,
    "veintiocho": 28, "veintinueve": 29, "treinta": 30, "treinta y uno": 31, "treinta y dos": 32,
    "treinta y tres": 33, "treinta y cuatro": 34, "treinta y cinco": 35, "treinta y seis": 36,
    "treinta y siete": 37, "treinta y ocho": 38, "treinta y nueve": 39, "cuarenta": 40,
    "cuarenta y uno": 41, "cuarenta y dos": 42, "cuarenta y tres": 43, "cuarenta y cuatro": 44,
    "cuarenta y cinco": 45, "cuarenta y seis": 46, "cuarenta y siete": 47, "cuarenta y ocho": 48,
    "cuarenta y nueve": 49, "cincuenta": 50
}

# Obtener la lista de archivos PNG en el directorio
archivos_png = [archivo for archivo in os.listdir(
    DIRECTORIO_PICTOGRAMAS) if archivo.endswith(".png")]

# Método para obtener palabras importantes y lemas de un texto


def obtener_palabras_importantes_con_lemas(texto: str) -> List[str]:

    palabras_no_omitir = ['genial', 'contigo', 'ok',
                          'sí', 'gracias', 'cumpleaños', 'cuándo', 'claro', 'cuántas', 'cuántos', 'tú', 'poco']
    palabras_importantes = []
    numero_actual = None

    doc = nlp(texto)
    for sent in doc.sentences:
        for word in sent.words:
            if word.text.lower() in palabras_no_omitir:
                palabras_importantes.append(word.text)
            else:
                lema = word.lemma.lower()

                if word.text.lower() == "qué":
                    palabras_importantes.append(word.text)
                elif word.text in ["?", "¿"]:
                    palabras_importantes.append(
                        "interrogación" if word.text == "?" else "interrogación1")
                elif word.text in ["!", "¡"]:
                    palabras_importantes.append(
                        "exclamación" if word.text == "¡" else "exclamación1")
                elif word.text == ".":
                    palabras_importantes.append(".")
                elif word.text.lower() == "con qué":
                    palabras_importantes.append("qué más")
                elif word.text.lower() == "cómo":
                    palabras_importantes.append("cómo")
                elif word.text.lower() == "lastimar":
                    palabras_importantes.append("doler")
                elif word.text.lower() == "cuál":
                    palabras_importantes.append(word.text)
                elif word.text.lower() == "sí":
                    palabras_importantes.append(word.text)
                elif word.text.lower() == "o":
                    palabras_importantes.append(word.text)
                elif word.text.lower() == "hola":
                    palabras_importantes.append(word.text)
                elif word.text.lower() == "ti":
                    palabras_importantes.append("ti")
                elif word.text.lower() == "cuántas":
                    palabras_importantes.append("cuántos")
                elif word.text.lower() == "emocionante":
                    palabras_importantes.append("genial")
                elif word.text.lower() == "disfrutar":
                    palabras_importantes.append("alegrar")
                elif word.text.lower() == "vas":
                    palabras_importantes.append("ir")
                elif word.text.lower() == "divértetar":
                    palabras_importantes.append("divertir")
                elif word.text.lower() in ["contigo", "y tú", "tú"]:
                    palabras_importantes.append("tú")
                elif word.text.lower() in ["claro", "ok", "genial", "parecer", "estupendo"]:
                    palabras_importantes.append("vale")
                elif word.upos in ['VERB', 'AUX']:
                    # Obtiene el infinitivo del verbo.
                    lema_infinitivo = obtener_infinitivo_verbo(word.text)
                    if lema_infinitivo:
                        palabras_importantes.append(lema_infinitivo)
                    else:
                        palabras_importantes.append(lema)
                elif word.upos in ['NOUN', 'ADJ', 'ADV', 'NUM']:
                    if lema in word_to_number:
                        numero_actual = word_to_number[lema]
                    elif re.match(r'^\d+$', word.text):
                        numero_actual = int(word.text)
                    else:
                        if numero_actual is not None:
                            palabras_importantes.append(str(numero_actual))
                            numero_actual = None

                        palabras_importantes.append(lema)
                        if word.text.lower() == "y":
                            numero_actual = None

    if numero_actual is not None:
        palabras_importantes.append(str(numero_actual))

    return palabras_importantes


def pluralizar(palabra: str) -> str:

    if palabra.endswith(("s", "x", "z", "l")):
        return palabra + "es"
    elif palabra.endswith("y") and len(palabra) > 1 and palabra[-2] not in "aeiou":
        return palabra[:-1] + "ies"
    else:
        return palabra + "s"

# Método para obtener el infinitivo de un verbo, tratando verbos irregulares


def obtener_infinitivo_verbo(verbo):
    if verbo in verbos_irregulares:
        return verbos_irregulares[verbo]
    try:
        doc = nlp(verbo)
        lema_infinitivo = doc.sentences[0].words[0].lemma
        if lema_infinitivo != verbo:
            return lema_infinitivo.lower()
    except:
        pass
    return None

# Método para obtener la ruta de una imagen de pictograma según una palabra clave


def obtener_pictograma(palabra_clave: str, palabra_anterior: str = None, palabra_siguiente: str = None) -> str:

    combinaciones = [palabra_clave]

    if palabra_anterior:
        combinaciones.append(f"{palabra_anterior} {palabra_clave}")

    if palabra_siguiente:
        combinaciones.append(f"{palabra_clave} {palabra_siguiente}")

    for combinacion in combinaciones:
        imagen_path = os.path.join(
            DIRECTORIO_PICTOGRAMAS, f"{combinacion}.png")
        if os.path.exists(imagen_path):
            logging.info(
                "Imagen encontrada para la combinación de palabras '%s': %s", combinacion, imagen_path)
            return imagen_path

    logging.warning(
        "No se encontró ninguna imagen para la palabra clave '%s'.", palabra_clave)
    return None


def obtener_respuesta_GPt(messages):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages
    )
    return response['choices'][0]['message']['content']


def lanzar_chatbot():

    tipo_chat = tipo_chat_combobox.get()
# respóndeme como un niño de 8 años con autismo con una frase muy corta, máximo 5 palabras básicas y continúes la conversación con una sola frase corta y máximo 5 palabras básicas.
    if tipo_chat == 'Sencilla':
        mensaje_sencillo = {'role': 'system',
                            'content': 'respóndeme como un niño de 8 años con autismo con una frase muy corta, máximo 5 palabras básicas y continúes la conversación de la misma forma.'}
        conversation.append(mensaje_sencillo)
    else:
        mensaje_complejo = {'role': 'system',
                            'content': 'respóndeme como un niño de 8 años con autismo con una frase corta y sencilla y continúes la conversación con una sola frase corta.'}
        conversation.append(mensaje_complejo)

    entrada_usuario = chatbot_text.get()

    palabras_iconos_seleccionados = [obtener_palabras_iconos_selccionados(
        archivo_png) for archivo_png in iconos_seleccionados]

    if palabras_iconos_seleccionados:
        palabras_iconos_seleccionados = " ".join(palabras_iconos_seleccionados)

        chatbot_text.delete(0, tk.END)
        chatbot_text.insert(0, palabras_iconos_seleccionados)

        palabras_iconos = {'role': 'user',
                           'content': palabras_iconos_seleccionados}
        respuesta_iconos = obtener_respuesta_GPt(
            conversation + [palabras_iconos])
        agregar_mensaje_a_conversacion(palabras_iconos)
        agregar_mensaje_a_conversacion(
            {'role': 'assistant', 'content': respuesta_iconos})
        chatbot_text.delete(0, tk.END)

    elif not entrada_usuario.strip():
        messagebox.showinfo("Mensaje", "Por favor, introduzca un texto.")
    else:

        mensaje_usuario = {'role': 'user', 'content': entrada_usuario}

        respuesta = obtener_respuesta_GPt(conversation + [mensaje_usuario])

        agregar_mensaje_a_conversacion(mensaje_usuario)
        agregar_mensaje_a_conversacion(
            {'role': 'assistant', 'content': respuesta})

        chatbot_text.delete(0, tk.END)

    conversacion_lemas_chat()
    mostrar_pictogramas_desde_archivo()
    iconos_seleccionados.clear()
    mostrar_iconos_seleccionados()


def obtener_palabras_iconos_selccionados(archivo_png: str) -> str:

    # Eliminar la extensión del archivo del nombre del archivo
    nombre_archivo, _ = os.path.splitext(archivo_png)

    # Elimina el sufijo "_BN" del nombre del archivo
    nombre_archivo = nombre_archivo.replace("_BN", "")

    # Dividir el nombre del archivo en palabras usando "_" como separador
    palabras = nombre_archivo.split("_")

    # Unir las palabras en una cadena separada por espacios
    frase = " ".join(palabras)

    return frase


def conversacion_lemas_chat():

    global conversation_lemas

    archivo_txt = "conversacion_lemas.txt"

    conversation_lemas = []

    with open(archivo_txt, "w") as archivo:
        for mensaje in conversation:
            if mensaje['role'] != 'system':
                frase = obtener_palabras_importantes_con_lemas(
                    mensaje['content'])
                conversation_lemas.append(frase)

                # Convertir la lista de lemas en una cadena separada por espacios y escribirla en el archivo
                frase_lemas = " ".join(frase)
                archivo.write(frase_lemas + "\n")

                # Procesar y mostrar los pictogramas del mensaje actual.
                mostrar_pictogramas_frase(frase, i)


def agregar_mensaje_a_conversacion(mensaje):

    respuesta_chatbot_text.delete("1.0", tk.END)
    conversation.append(mensaje)
    chat_lines = [message['content']
                  for message in conversation if message['role'] != 'system']
    respuesta_chatbot_text.insert(tk.END, "\n".join(chat_lines))


def limpiar_chat():
    global conversation
    chatbot_text.delete(0, tk.END)
    respuesta_chatbot_text.delete("1.0", tk.END)
    for widget in marco_combinado.winfo_children():
        widget.destroy()

    conversation = []


def limpiar_marco_seleccionados():
    iconos_seleccionados.clear()
    mostrar_iconos_seleccionados()


def mostrar_pictogramas_frase(frase, row):

    nivel = nivel_combobox.get()
    lemas_texto = " ".join(frase)
    palabras = lemas_texto.split()

    palabra_anterior = None
    i = 0

    marco_fila = tk.Frame(ventana_pictogramas)
    marco_fila.grid(row=row, column=0, padx=5, pady=5, sticky="nsew")

    while i < len(palabras):

        # Verificar si la palabra actual y la siguiente forman una combinación
        if i < len(palabras) - 1:
            if nivel == "B/N":
                combined_word = f"{palabras[i]} {palabras[i + 1]}"
                pictogram = obtener_pictograma(combined_word + "_BN")
                if not pictogram:
                    plural1 = pluralizar(palabras[i])
                    combined_word_plural = f"{plural1} {palabras[i + 1]}"
                    pictogram = obtener_pictograma(
                        combined_word_plural + "_BN")
                if not pictogram:
                    plural2 = pluralizar(palabras[i + 1])
                    combined_word_plural1 = f"{palabras[i]} {plural2}"
                    pictogram = obtener_pictograma(
                        combined_word_plural1 + "_BN")
                if not pictogram:
                    plural1 = pluralizar(palabras[i])
                    plural2 = pluralizar(palabras[i + 1])
                    combined_word_plural2 = f"{plural1} {plural2}"
                    pictogram = obtener_pictograma(
                        combined_word_plural2 + "_BN")

            else:  # Color:
                combined_word = f"{palabras[i]} {palabras[i + 1]}"
                pictogram = obtener_pictograma(combined_word)

                if not pictogram:
                    plural1 = pluralizar(palabras[i])
                    combined_word_plural = f"{plural1} {palabras[i + 1]}"
                    pictogram = obtener_pictograma(
                        combined_word_plural)

                if not pictogram:
                    plural2 = pluralizar(palabras[i + 1])
                    combined_word_plural1 = f"{palabras[i]} {plural2}"
                    pictogram = obtener_pictograma(
                        combined_word_plural1)

                if not pictogram:
                    plural1 = pluralizar(palabras[i])
                    plural2 = pluralizar(palabras[i + 1])
                    combined_word_plural2 = f"{plural1} {plural2}"
                    pictogram = obtener_pictograma(
                        combined_word_plural2)

            if pictogram:
                try:
                    img_data = Image.open(pictogram)
                    # Redimensionar la imagen
                    img_data.thumbnail((50, 50))
                    img = ImageTk.PhotoImage(img_data)
                    label = tk.Label(marco_fila, image=img)
                    label.image = img  # Conservar una referencia para evitar que la imagen se borre
                    label.grid(row=0, column=i, padx=5, pady=5)
                    i += 2  # Saltar la siguiente palabra
                    continue  # Saltar al siguiente ciclo
                except Exception as error:
                    logging.error(
                        "Error al procesar la imagen:", error)

        # Si no se encontró una combinación, buscar la palabra individualmente
        palabra_actual = palabras[i]
        if nivel == "B/N":
            pictogram = obtener_pictograma(
                palabra_actual + "_BN", palabra_anterior)

            if not pictogram:
                palabra_actual_plural = pluralizar(palabra_actual)
                pictogram = obtener_pictograma(
                    palabra_actual_plural + "_BN", palabra_anterior)

            if not pictogram:
                pictogram = obtener_pictograma(
                    palabra_actual_plural, palabra_anterior)

            if not pictogram:
                pictogram = obtener_pictograma(palabra_actual)
        else:  # Color
            pictogram = obtener_pictograma(
                palabra_actual, palabra_anterior)

            if not pictogram:
                palabra_actual_plural = pluralizar(palabra_actual)
                pictogram = obtener_pictograma(
                    palabra_actual_plural, palabra_anterior)

        if pictogram:
            try:
                img_data = Image.open(pictogram)
                # Redimensionar la imagen
                img_data.thumbnail((50, 50))
                img = ImageTk.PhotoImage(img_data)
                label = tk.Label(marco_fila, image=img)
                label.image = img  # Conservar una referencia para evitar que la imagen se borre
                label.grid(row=0, column=i, padx=5, pady=5)

            except Exception as error:
                logging.error("Error al procesar la imagen:", error)

        palabra_anterior = palabra_actual
        i += 1

# Función para seleccionar o deseleccionar un icono


def seleccionar_icono(archivo_png):
    if archivo_png in iconos_seleccionados:
        iconos_seleccionados.remove(archivo_png)
    else:
        iconos_seleccionados.append(archivo_png)
    mostrar_iconos_seleccionados()

# Función para mostrar los iconos seleccionados en el marco lateral


def mostrar_iconos_seleccionados():
    for widget in marco_seleccionados.winfo_children():
        widget.destroy()

    for i, archivo_png in enumerate(iconos_seleccionados):
        ruta_completa = os.path.join(DIRECTORIO_PICTOGRAMAS, archivo_png)
        imagen = Image.open(ruta_completa)
        imagen = imagen.resize((50, 50))
        imagen_tk = ImageTk.PhotoImage(imagen)

        etiqueta_imagen = tk.Label(marco_seleccionados, image=imagen_tk)
        etiqueta_imagen.image = imagen_tk
        etiqueta_imagen.grid(row=0, column=i, padx=5, pady=5, sticky="w")


def mostrar_iconos():
    nivel = nivel_combobox.get()
    # Limpiar todos los iconos actuales en el marco_iconos
    for widget in marco_iconos.winfo_children():
        widget.destroy()

    archivos_bn = []
    archivos_color = []

    for archivo in archivos_png:
        # Si el archivo actual termina en "_BN", agrégalo a la lista "archivos_bn".
        if archivo.endswith("_BN.png"):
            archivos_bn.append(archivo)
        else:
            # Si el archivo actual NO termina en "_BN", agrégalo a la lista "archivos_color".
            archivos_color.append(archivo)

    if nivel == "B/N":
        archivos = archivos_bn
    else:
        archivos = archivos_color

    for i, archivo_png in enumerate(archivos):
        ruta_completa = os.path.join(DIRECTORIO_PICTOGRAMAS, archivo_png)
        imagen = Image.open(ruta_completa)
        imagen = imagen.resize((50, 50))
        imagen_tk = ImageTk.PhotoImage(imagen)

        etiqueta_imagen = tk.Label(marco_iconos, image=imagen_tk)
        etiqueta_imagen.image = imagen_tk
        etiqueta_imagen.grid(row=i // 8, column=i % 8, padx=5, pady=5)
        etiqueta_imagen.bind("<Button-1>", lambda event,
                             archivo=archivo_png: seleccionar_icono(archivo))

    # Actualizar el tamaño del marco dentro del canvas
    marco_iconos.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


# Crear una nueva ventana para mostrar los pictogramas
def mostrar_ventana_pictogramas(pictogramas):

    for i, pictograma in enumerate(pictogramas):
        ruta_completa = os.path.join(DIRECTORIO_PICTOGRAMAS, pictograma)
        imagen = Image.open(ruta_completa)
        imagen = imagen.resize((50, 50))
        imagen_tk = ImageTk.PhotoImage(imagen)

        etiqueta_imagen = tk.Label(ventana_pictogramas, image=imagen_tk)
        etiqueta_imagen.image = imagen_tk
        etiqueta_imagen.grid(row=i // 8, column=i % 8, padx=5, pady=5)

# Función para mostrar los pictogramas en una ventana aparte


def mostrar_pictogramas_desde_archivo():
    with open("conversacion_lemas.txt", "r") as archivo:
        lineas = archivo.readlines()

    for widget in ventana_pictogramas.winfo_children():
        widget.destroy()

    for i, linea in enumerate(lineas, start=1):
        frase = linea.strip().split()  # Dividir la línea en palabras
        mostrar_pictogramas_frase(frase, i)


def salir():
    resultado = messagebox.askquestion(
        "Salir", "¿Estás seguro de que quieres salir?")
    if resultado == "yes":
        root.destroy()
        root.quit()

# ----------------------------------------------------------------------------------------


def on_canvas_ventana_pictogramas_configure(event):
    canvas_ventana_pictogramas.configure(
        scrollregion=canvas_ventana_pictogramas.bbox("all"))


root = tk.Tk()
root.title("ChatBotTEA")
root.iconbitmap("iconos\chat.ico")

# Configurar el estilo personalizado para el botón

style = tk.ttk.Style()
style.configure("Salir.TButton", background="red",
                foreground="#ff0000", border=10, width=10, font=("Arial", 12))
style.configure("Botones.TButton", background="SkyBlue1", foreground="black")

# Crear un marco principal ---------------------------------------------------------------

marco_principal = tk.Frame(root)
marco_principal.pack(fill=tk.BOTH, expand=True)

# Crear sub-marcos ---------------------------------------------------------------

marco_1 = tk.LabelFrame(marco_principal, padx=5, pady=5, bg='powder blue')
marco_1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
marco_2 = tk.LabelFrame(marco_principal, padx=5, pady=5, bg='powder blue')
marco_2.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
marco_3 = tk.LabelFrame(marco_principal, padx=5, pady=5, bg='powder blue')
marco_3.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
marco_4 = tk.LabelFrame(marco_principal, padx=5, pady=5)
# Hacer que el marco se expanda horizontalmente
marco_4.columnconfigure(0, weight=1)
marco_5 = tk.LabelFrame(marco_principal, padx=5, pady=5)
marco_6 = tk.LabelFrame(marco_principal, padx=5, pady=5)
marco_iconos = tk.Frame(marco_principal, padx=5, pady=5, bg='powder blue')
marco_iconos.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
marco_iconos_label = tk.Label(marco_iconos, text="Pictogramas",
                              bg="powder blue", font=("Arial", 12))
marco_iconos_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

# Configurar la geometría de la cuadrícula para que los marcos se expandan
for i in range(6):
    marco_principal.rowconfigure(i, weight=1)
    marco_principal.columnconfigure(i, weight=1)

# Unir los marcos marco_7, marco_8 y marco_9 en uno solo (marco_combinado)
marco_combinado = tk.Frame(marco_principal, padx=5, pady=5)
marco_combinado.grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky="nsew")
marco_seleccionados = tk.Frame(marco_principal, padx=5, pady=5)
marco_seleccionados.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

# Configurar la geometría de la cuadrícula para el marco combinado
marco_combinado.grid_rowconfigure(0, weight=1)
marco_combinado.grid_columnconfigure(0, weight=1)

# Copiar elementos de marco_7, marco_8 y marco_9 al marco_combinado
for widget in marco_4.winfo_children():
    widget.grid_configure(sticky="nsew")
    widget.grid_forget()  # Retira los widgets de sus marcos originales
    widget.master = marco_combinado

for widget in marco_5.winfo_children():
    widget.grid_configure(sticky="nsew")
    widget.grid_forget()
    widget.master = marco_combinado

for widget in marco_6.winfo_children():
    widget.grid_configure(sticky="nsew")
    widget.grid_forget()
    widget.master = marco_combinado

# Elementos de marco_4 ---------------------------------------------------------------

chatbot_label = tk.Label(marco_1, text="Escribe una frase: ",
                         bg="powder blue", font=("Arial", 12))
chatbot_text = tk.Entry(marco_1, width=60, font=("Arial", 12))
respuesta_chatbot_label = tk.Label(
    marco_1, text="Chatbot: ", bg="powder blue", font=("Arial", 12))
respuesta_chatbot_text = scrolledtext.ScrolledText(
    marco_1, width=65, height=12)

chatbot_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
chatbot_text.grid(row=1, column=0, padx=5, pady=5, sticky="w")
respuesta_chatbot_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
respuesta_chatbot_text.grid(row=3, column=0, padx=5, pady=5, sticky="w")

chatbot_text.bind("<Return>", lambda event=None: lanzar_chatbot())

# Elementos de marco_5 ---------------------------------------------------------------

nivel_label = tk.Label(marco_2, text="Color pictogramas:",
                       bg="powder blue", font=("Arial", 12))
nivel_combobox = ttk.Combobox(
    marco_2, state="readonly", values=['B/N', 'Color'])
nivel_combobox.current(1)

tipo_chat_label = tk.Label(marco_2, text="Tipo Conversación:",
                           bg="powder blue", font=("Arial", 12))
tipo_chat_combobox = ttk.Combobox(
    marco_2, state="readonly", values=['Sencilla', 'Compleja'])
tipo_chat_combobox.current(0)

# Vincular la función mostrar_iconos al evento de cambio en el nivel_combobox
nivel_combobox.bind("<<ComboboxSelected>>",
                    lambda event=None: mostrar_iconos())

nivel_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
nivel_combobox.grid(row=3, column=0, padx=5, pady=5, sticky="w")
tipo_chat_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
tipo_chat_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Elementos de marco_6 ---------------------------------------------------------------

lanzar_button = ttk.Button(marco_3, text="Lanzar",
                           command=lanzar_chatbot, style="Botones.TButton")
limpiar_chat_button = ttk.Button(
    marco_3, text="Limpiar", command=limpiar_chat, style="Botones.TButton")
chat_pictogramas_button = ttk.Button(marco_3, text="Actualizar",
                                     command=lambda: mostrar_pictogramas_desde_archivo(), style="Botones.TButton")
borrar_iconos = ttk.Button(marco_3, text="Borrar iconos",
                           command=limpiar_marco_seleccionados, style="Botones.TButton")
salir_button = ttk.Button(marco_3, text="Salir",
                          command=lambda: salir(), style="Salir.TButton")

lanzar_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
limpiar_chat_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

chat_pictogramas_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
borrar_iconos.grid(row=0, column=5, padx=5, pady=5, sticky="w")
salir_button.grid(row=0, column=7, padx=5, pady=5, sticky="w")

# Agregar una barra de desplazamiento vertical
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Crear un canvas en la ventana principal con la barra de desplazamiento
canvas = tk.Canvas(root, yscrollcommand=scrollbar.set)
canvas.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=canvas.yview)

# Crear un frame dentro del canvas para contener los iconos
marco_iconos = tk.Frame(canvas)
canvas.create_window((0, 0), window=marco_iconos, anchor=tk.NW)

# -------------------------------------------------------------------------------------

ventana_pictogramas = tk.Toplevel(root, bg="powder blue")
ventana_pictogramas.title("Pictogramas")
ventana_pictogramas.iconbitmap("iconos\globo-de-chat.ico")

# Crear un Canvas en la ventana para contener los pictogramas
canvas_ventana_pictogramas = tk.Canvas(
    ventana_pictogramas, yscrollcommand=scrollbar.set)
canvas_ventana_pictogramas.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

# Agregar una barra de desplazamiento vertical al Canvas de la ventana de pictogramas
scrollbar_ventana_pictogramas = ttk.Scrollbar(
    ventana_pictogramas, orient="vertical", command=canvas_ventana_pictogramas.yview)
scrollbar_ventana_pictogramas.grid(row=0, column=1, sticky="ns")
canvas_ventana_pictogramas.configure(
    yscrollcommand=scrollbar_ventana_pictogramas.set)

# Configurar la barra de desplazamiento para el Canvas de la ventana de pictogramas
canvas_ventana_pictogramas.bind(
    "<Configure>", on_canvas_ventana_pictogramas_configure)

# -------------------------------------------------------------------------------------
root.after(0, mostrar_iconos())

root.mainloop()
