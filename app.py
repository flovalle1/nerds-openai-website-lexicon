import gradio as gr
import pandas as pd
import os
import openai
import requests
import io
import json

with open("config.json") as config-file:

    data = json.load(config-file)
    openai.api_key = data["openai-api-key"]
    wordpress_token = data["wordpress-token"]
    wordpress_user = data["wordpress-user"]


def answer_request(empty, file):
    data = pd.read_csv(file.name)

    sf = []

    csv_out = {
        'Begriff': [],
        'Eintrag': []
    }

    # Iterieren über die Zeilen des DataFrame
    for index, row in data.iterrows():
        # Führen Sie hier Ihren Code aus.
        # 'row' ist eine Series, die die Daten der aktuellen Zeile enthält.
        begriff = str(row['Begriff'])
        erk = str(row['Erklärung und/oder Definition'])
        
        if begriff != "nan" and erk != "nan":
            msg = [
              {"role": "user", "content": "Generiere mir einen ca. 300-500 Wörter langen Lexikoneintrag ohne Überschrift zu folgendem Begriff:" + str(begriff) + "\n Hier eine kurze Erklärung zu dem Begriff:" + str(erk) }
            ]

            completion = openai.ChatCompletion.create(
              model="gpt-3.5-turbo",
              messages=msg
            )
            print(completion)
            ans = completion["choices"][0]["message"]["content"]
            sf.append(ans)
            csv_out["Begriff"].append(begriff)
            csv_out["Eintrag"].append(ans)
            # String zum Returnen
            ret = ""
            for it in sf:
                ret = ret + "\n\n" + str(it)
            


    df = pd.DataFrame(csv_out)

    # Schreiben Sie den DataFrame in eine CSV-Datei
    df.to_csv('ergebnis.csv', index=False)
    return ret, "ergebnis.csv"


def push_to_wp(begriff,context):
    msg = [
      {"role": "user", "content": "Ich nutze dich als API-Endpoint, um einen Lexikoneintrag auf meine Website https://dienerds.com zu bringen. Löse deshalb folgende Anweisungen Schritt für Schritt: 1) Generiere einen ca. 400 - 600 Wörter langen deutschen Lexikoneintrag zu folgendem Begriff: " + str(begriff) + "\n Als Hilfestellung hier eine kurze Erläuterung:" + str(context) + "2) Erstelle passend zum Begriff des Lexikoneintrages 5 Fragen die einen möglichen Leser interessieren könnten und beantworte diese. 3) Erstelle aus dem Lexikoneintrag und den Fragen einen HTML Code, den ich direkt im Body meiner Website einsetzen kann. Verzichte auf den Header und lass die Body Tags weg. Halte dich an die Standards für HTML Code nach Schema.org. 4) Ergänze zu dem HTML Code JSON-LD Daten, damit die Seite möglichst gut auf Google rankt. 5) Gib mir ausschließlich den HTML Code inklusive JSON-LD Daten als Antwort zurück. Deine Antwort wird direkt auf meiner Website verwenden, deshalb verzichte auf Erklärungen und gib wirklich nur das verwendebare HTML mit JSON-LD als Antwort zurück." }
    ]
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=msg
    )
    ans = completion["choices"][0]["message"]["content"]

    # URL of your WordPress website
    url = 'https://dienerds.com/wp-json/wp/v2/pages'

    # Authentication details
    username = wordpress_user
    password = wordpress_token

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "title": begriff,
        "content": {
            "raw": ans
        },
        "status": "publish",
        "slug": begriff,
        "parent": 24434
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), auth = (username,password))
    print(response)
    if response.status_code == 201:
        return [f"Seite erfolgreich erstellt. Du findest die Seite unter folgender URL: https://dienerds.com/performance-marketing-lexikon/{begriff}",ans]
    else:
        return ["Runtime Error. Etwas ist schief gelaufen. Gib Flo Bescheid, er kann den Log der Applikation checken.",ans]
            

def test(empty,inp):
    return inp


with gr.Blocks() as admin:
    with gr.Tab(label = "WordPress Interface"):
        with gr.Column():
            gr.Markdown("# WordPress Interface \n Hier kann ein beliebiger Begriff und eine kurze Erläuterung zu dem Begriff angegeben werden. GPT3.5 generiert im Anschluss eine HTML Website mit einem Lexikoneintrag zu dem Begriff. \n Die neue Seite wird automatisch zur dienerds.com Wordpress-Installation hinzugefügt und ist erreichbar unter 'dienerds.com/lexikon/[BEGRIFFNAME]'")
            term = gr.Textbox(label="Begriff")
            context = gr.Textbox(label="Kurze Erklärung des Begriffs")
            go = gr.Button(value="Seite generieren")
        with gr. Column():
            ot = gr.Textbox(label="Console") 
            website = gr.Textbox(label="Generiertes HTML",lines=15) 
    with gr.Tab(label="CSV Tool"):
        gr.Markdown("# Nerds OpenAI CSV Tool \nDie OpenAI API braucht pro Promt (also Zeile in der CSV) ca. 20 Sekunden. Die Anfrage kann also etwas dauern.\n\n Die CSV Muss eine Spalte 'Begriff' und eine Spalte 'Erklärung und/oder Definition' enthalten, sonst entseht ein Runtime Error.")
        inpu=gr.File(label = "CSV hochladen!",file_types=['csv']),
        outputs=[gr.Textbox(label="Generierte Texte"), gr.File(label="Antwort")]
        go_csv = gr.Button(value="Generieren")
        #go_csv.click(answer_request, inputs=inpu, outputs=outputs)
    go.click(push_to_wp, inputs=[term,context], outputs=[ot,website])
    

'''demo = gr.Interface(
    fn=answer_request,
    inputs=[gr.Markdown("# Nerds OpenAI Tool \nDie OpenAI API braucht pro Promt (also Zeile in der CSV) ca. 20 Sekunden. Die Anfrage kann also etwas dauern.\n\n Die CSV Muss eine Spalte 'Begriff' und eine Spalte 'Erklärung und/oder Definition' enthalten, sonst entseht ein Runtime Error."), gr.File(label = "CSV hochladen!",file_types=['csv'])],
    outputs=[gr.Textbox(label="Generierte Texte"), gr.File(label="Antwort")]
)'''
'''tp = push_to_wp("Werbeanzeigenmanager","Der Werbeanzeigenmanager von Facebook.")
with open("test.html","w") as datei:
    datei.write(tp)'''

admin.launch(server_name='0.0.0.0',server_port = 7863, share = False)