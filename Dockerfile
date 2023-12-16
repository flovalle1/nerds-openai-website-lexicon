# Verwenden Sie ein Python-Basisimage
FROM python:3.9

# Setzen Sie das Arbeitsverzeichnis innerhalb des Containers
WORKDIR /app

# Kopieren Sie die Anwendungsdateien in das Arbeitsverzeichnis
COPY . /app

ENV PORT=7863

EXPOSE 7863

# Installieren Sie die Anwendungsabhängigkeiten
RUN pip install openai gradio

# Starten Sie die Anwendung
CMD ["python3", "app.py"]
