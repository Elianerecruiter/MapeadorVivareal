import os
import json
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from twilio.rest import Client

# Configurações
VIVAREAL_URL = "https://www.vivareal.com.br/venda/sp/campinas/bairros/barao-geraldo/casa_residencial/?onde=%2CSão+Paulo%2CCampinas%2CBairros%2CBarão+Geraldo%2C%2C%2Cneighborhood%2CBR>Sao+Paulo>NULL>Campinas>Barrios>Barao+Geraldo%2C-22.832419%2C-47.080202%2C&tipos=casa_residencial&precoMaximo=1000000&transacao=venda"
NOTIFIED_FILE = "notified_ads.json"

EMAIL_FROM = "mapeadorvivareal@gmail.com"
EMAIL_PASSWORD = "A1b2c3d4@#"
EMAIL_TO = "elianejobhunter@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Configurações do Twilio
TWILIO_ACCOUNT_SID = "AC665d6f67533ca19ec087c9c84b57dff6"
TWILIO_AUTH_TOKEN = "4c622b4f8b29236e04af9307c14131b8"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_WHATSAPP_TO = "whatsapp:+5519997454332"


def load_notified_ads():
    if not os.path.exists(NOTIFIED_FILE):
        return set()
    with open(NOTIFIED_FILE, "r") as f:
        try:
            data = json.load(f)
            return set(data)
        except Exception:
            return set()

def save_notified_ads(ad_ids):
    with open(NOTIFIED_FILE, "w") as f:
        json.dump(list(ad_ids), f)

def fetch_ads():
    resp = requests.get(VIVAREAL_URL, headers={"User-Agent": "Mozilla/5.0"})
    print(f"[LOG] Status code: {resp.status_code}")
    print(f"[LOG] Primeiros 500 caracteres do HTML: {resp.text[:500]}")
    soup = BeautifulSoup(resp.text, "html.parser")
    ads = []
    for li in soup.select('li[data-cy="rp-property-cd"]'):
        a_tag = li.find('a', href=True)
        if not a_tag:
            continue
        link = a_tag['href']
        if not link.startswith('http'):
            link = 'https://www.vivareal.com.br' + link
        title_tag = li.find('h2', {'data-cy': 'rp-cardProperty-location-txt'})
        title = title_tag.get_text(strip=True) if title_tag else 'Sem título'
        address_tag = li.find('p', {'data-cy': 'rp-cardProperty-street-txt'})
        address = address_tag.get_text(strip=True) if address_tag else 'Sem endereço'
        price_tag = li.find('p', {'data-cy': 'rp-cardProperty-price-txt'})
        price = price_tag.get_text(strip=True) if price_tag else 'Sem preço'
        ad_id = link.split('/')[-2] if '/' in link else link
        ads.append({
            'id': ad_id,
            'title': title,
            'price': price,
            'address': address,
            'link': link
        })
    print(f"[LOG] {len(ads)} anúncios encontrados no scraping:")
    for ad in ads:
        print(f"- {ad['title']} | {ad['price']} | {ad['address']} | {ad['link']}")
    return ads

def send_email(new_ads):
    if not new_ads:
        return
    subject = f"Novos imóveis em Barão Geraldo ({len(new_ads)}) - {datetime.now().strftime('%d/%m/%Y')}"
    body = ""
    for ad in new_ads:
        body += f"<b>{ad['title']}</b><br>"
        body += f"Preço: {ad['price']}<br>"
        body += f"Endereço: {ad['address']}<br>"
        body += f"<a href='{ad['link']}'>Ver anúncio</a><br><br>"
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = Header(subject, 'utf-8')
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

def send_whatsapp_message(new_ads):
    if not new_ads:
        return
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    messages = []
    current_msg = ""
    for ad in new_ads:
        ad_text = f"{ad['title']}\nPreço: {ad['price']}\nEndereço: {ad['address']}\n{ad['link']}\n\n"
        if len(current_msg) + len(ad_text) > 1500:
            messages.append(current_msg)
            current_msg = ""
        current_msg += ad_text
    if current_msg:
        messages.append(current_msg)
    for idx, msg in enumerate(messages):
        message = client.messages.create(
            body=msg,
            from_=TWILIO_WHATSAPP_FROM,
            to=TWILIO_WHATSAPP_TO
        )
        print(f"[LOG] Mensagem {idx+1}/{len(messages)} enviada para WhatsApp com {msg.count('Preço:')} anúncios.")

def main():
    notified_ads = load_notified_ads()
    ads = fetch_ads()
    new_ads = [ad for ad in ads if ad['id'] not in notified_ads]
    if new_ads:
        notified_ads.update(ad['id'] for ad in new_ads)
        save_notified_ads(notified_ads)
        print(f"[LOG] {len(new_ads)} novos anúncios salvos em {NOTIFIED_FILE}.")
        send_whatsapp_message(new_ads)
    else:
        print("Nenhum anúncio novo encontrado.")

if __name__ == "__main__":
    main() 