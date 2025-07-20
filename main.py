import os
import json
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

# Configurações
VIVAREAL_URL = "https://www.vivareal.com.br/venda/sp/campinas/bairros/barao-geraldo/casa_residencial/?onde=%2CSão+Paulo%2CCampinas%2CBairros%2CBarão+Geraldo%2C%2C%2Cneighborhood%2CBR>Sao+Paulo>NULL>Campinas>Barrios>Barao+Geraldo%2C-22.832419%2C-47.080202%2C&tipos=casa_residencial&precoMaximo=1000000&transacao=venda"
NOTIFIED_FILE = "notified_ads.json"

EMAIL_FROM = "mapeadorvivareal@gmail.com"
EMAIL_PASSWORD = "A1b2c3d4@#"
EMAIL_TO = "elianejobhunter@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


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
    soup = BeautifulSoup(resp.text, "html.parser")
    ads = []
    for card in soup.select('[data-type="property"]'):
        link_tag = card.select_one('a[data-type="link"]')
        if not link_tag:
            continue
        link = link_tag['href']
        if not link.startswith('http'):
            link = 'https://www.vivareal.com.br' + link
        title = card.select_one('span.property-card__title')
        title = title.text.strip() if title else 'Sem título'
        price = card.select_one('div.property-card__price')
        price = price.text.strip() if price else 'Sem preço'
        address = card.select_one('span.property-card__address')
        address = address.text.strip() if address else 'Sem endereço'
        ad_id = link.split('/')[-2] if '/' in link else link
        ads.append({
            'id': ad_id,
            'title': title,
            'price': price,
            'address': address,
            'link': link
        })
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

def main():
    notified_ads = load_notified_ads()
    ads = fetch_ads()
    new_ads = [ad for ad in ads if ad['id'] not in notified_ads]
    if new_ads:
        send_email(new_ads)
        notified_ads.update(ad['id'] for ad in new_ads)
        save_notified_ads(notified_ads)
    else:
        print("Nenhum anúncio novo encontrado.")

if __name__ == "__main__":
    main() 