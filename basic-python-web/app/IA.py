from transformers import pipeline

chatbot = pipeline("text-generation", model="datificate/gpt2-small-spanish")

def respuesta_ia(mensaje_usuario):
    respuesta = chatbot(mensaje_usuario, max_length=100, do_sample=True)[0]["generated_text"]
    return respuesta.strip()